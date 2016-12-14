from collections import MutableMapping
from copy import deepcopy

from modelmapper.exceptions import ModelMapperError
from modelmapper.accessors import ModelAccessor, ModelDictAccessor, FieldAccessor


class ModelMapper(object):
    """Linker class between an origin model and a destination one
    """

    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(mapper, MutableMapping), "Mapper must be a mutable mapping (dict, OrderedDict, etc)"

        self._origin_model = origin_model
        self._destination_model = destination_model
        self._mapper = mapper

        self._mapper_accessor = ModelDictAccessor(mapper)
        self._origin_accessor = ModelAccessor(origin_model)
        self._destination_accessor = ModelAccessor(destination_model)

        self._children_accesses = set()

    @staticmethod
    def factory(orig_model, dest_model, mapper, *args):
        if isinstance(orig_model, list) and isinstance(dest_model, list):
            return ListModelMapper(orig_model, dest_model, mapper, *args)
        elif isinstance(orig_model, list) or isinstance(dest_model, list):
            return UniformListModelMapper(orig_model, dest_model, mapper, *args)
        else:
            return ModelMapper(orig_model, dest_model, mapper)

    @property
    def origin_model(self):
        return self._origin_model

    @origin_model.setter
    def origin_model(self, val):
        self._origin_model = val
        self._origin_accessor = ModelAccessor(val)

    @property
    def destination_model(self):
        return self._destination_model

    @destination_model.setter
    def destination_model(self, val):
        self._destination_model = val
        self._destination_accessor = ModelAccessor(val)

    @property
    def mapper(self):
        return self._mapper

    @mapper.setter
    def mapper(self, val):
        self._mapper = val
        self._mapper_accessor = ModelDictAccessor(val)

    @property
    def origin_accessor(self):
        return self._origin_accessor

    @property
    def destination_accessor(self):
        return self._destination_accessor

    @property
    def mapper_accessor(self):
        return self._mapper_accessor

    def set_origin_model(self, model):
        self._origin_model = model
        self._origin_accessor = ModelAccessor(model)

        for origin_access, _, mapper in self._children_accesses:
            mapper.set_origin_model(self._origin_accessor[origin_access])

    def _get_new_model_mapper(self, *args):
        orig_access, dest_access = args[0], args[1]
        model_mapper = ModelMapper.factory(self._origin_accessor[orig_access],
                                       self._destination_accessor[dest_access],
                                       *args[2:])
        child = (orig_access, dest_access, model_mapper)

        self._children_accesses.add(child)
        return model_mapper

    def set_field_parent_accessor(self, orig_field, dest_field):

        def _set_parent_accessor(field, parent_accessor):
            if isinstance(field, FieldAccessor):
                field.parent_accessor = parent_accessor

        _set_parent_accessor(orig_field, self._origin_accessor)
        _set_parent_accessor(dest_field, self._destination_accessor)

    def _prepare_mapper_and_get_new_mappers(self):
        set_field_parent_accessor = self.set_field_parent_accessor
        get_new_model_mapper = self._get_new_model_mapper

        for link_name, link_args in self._mapper_accessor.iteritems():
            args_length = len(link_args)
            if args_length == 2:
                set_field_parent_accessor(*link_args)
            elif args_length >= 3:
                yield link_name, get_new_model_mapper(*link_args)

    def prepare_mapper(self):
        mapper = self._mapper_accessor
        new_model_mappers = self._prepare_mapper_and_get_new_mappers() or []

        for (link_name, model_mapper) in new_model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()

    def destination_to_origin(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.destination_to_origin()
            else:
                orig_accessor[link_value[0]] = dest_accessor[link_value[1]]

    def origin_to_destination(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.origin_to_destination()
            else:
                dest_accessor[link_value[1]] = orig_accessor[link_value[0]]

    def to_dict(self, only_origin=False, only_destination=False):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        ret = {}

        for link_name, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                ret[link_name] = link_value.to_dict(only_origin=only_origin, only_destination=only_destination)
            elif only_origin:
                ret[link_name] = orig_accessor[link_value[0]]
            elif only_destination:
                ret[link_name] = dest_accessor[link_value[1]]
            else:
                ret[link_name] = (orig_accessor[link_value[0]], dest_accessor[link_value[1]])
        return ret

    def __getitem__(self, item):
        return self._mapper_accessor[item]

    def __setitem__(self, key, value):
        self._mapper_accessor[key] = value

    __getattr__ = __getitem__  # If getattr(self, 'link')


class ListModelMapper(ModelMapper):

    LINK = '[{}].{}'

    def __init__(self, origin_model, destination_model, mapper, autoresize=True):
        self.autoresize = autoresize
        super(ListModelMapper, self).__init__(origin_model, destination_model, mapper)

    def destination_to_origin(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        model = self._destination_model
        link = ListModelMapper.LINK.format

        while self.autoresize and len(orig_accessor.model) < len(dest_accessor.model):
            orig_accessor.model.append(deepcopy(orig_accessor.model[-1]))

        for _, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                if isinstance(link_value, ModelMapper):
                    link_value.destination_to_origin()
                else:
                    orig_accessor[link(index, link_value[0])] = dest_accessor[link(index, link_value[1])]

    def origin_to_destination(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        model = self._origin_model
        link = ListModelMapper.LINK.format

        while self.autoresize and len(orig_accessor.model) > len(dest_accessor.model):
            dest_accessor.model.append(deepcopy(dest_accessor.model[-1]))

        for _, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                if isinstance(link_value, ModelMapper):
                    link_value.origin_to_destination()
                else:
                    dest_accessor[link(index, link_value[1])] = orig_accessor[link(index, link_value[0])]

    def to_dict(self, only_origin=False, only_destination=False):
        if only_origin:
            return self._to_dict_only_origin()
        elif only_destination:
            return self._to_dict_only_destination()
        else:
            return (self._to_dict_only_origin(), self._to_dict_only_destination())

    def _to_dict_only_destination(self):
        dest_accessor = self._destination_accessor
        model = self._destination_model
        ret = [dict() for _ in range(len(model))]
        link = ListModelMapper.LINK.format

        for link_name, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                if isinstance(link_value, ModelMapper):
                    ret[index][link_name] = link_value.to_dict(only_destination=True)
                else:
                    ret[index][link_name] = dest_accessor[link(index, link_value[1])]
        return ret

    def _to_dict_only_origin(self):
        orig_accessor = self._origin_accessor
        model = self._origin_model
        ret = [dict() for _ in range(len(model))]
        link = ListModelMapper.LINK.format

        for link_name, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                if isinstance(link_value, ModelMapper):
                    ret[index][link_name] = link_value.to_dict(only_origin=True)
                else:
                    ret[index][link_name] = orig_accessor[link(index, link_value[0])]
        return ret


# TODO: At this moment is only possible to be the origin a list


class UniformListModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper, index=0):
        assert isinstance(origin_model, list), "Origin model must be a list with uniform data"

        self._orig_data = origin_model
        self._index = index
        super(UniformListModelMapper, self).__init__(origin_model[index], destination_model, mapper)

    def set_origin_model(self, model):
        self._orig_data = model
        self._origin_model = model[self._index]
        self._origin_accessor = ModelAccessor(self._origin_model)

        for mapper, origin_access, _ in self._children_accesses:
            mapper.origin_model = self._origin_accessor[origin_access]

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        try:
            self._update_index(index)
            self.origin_to_destination()
        except IndexError:
            raise ModelMapperError("The index {} is out of range".format(index))

    def _update_index(self, index):
        if self._index == index:
            return
        self._index = index
        self._origin_model = self._orig_data[index]
        self._origin_accessor = ModelAccessor(self._origin_model)
        super(UniformListModelMapper, self).set_origin_model(self._origin_model)

    def to_dict(self, only_origin=False, only_destination=False):
        if only_origin:
            return self._to_dict_only_origin()
        elif only_destination:
            return super(UniformListModelMapper, self).to_dict(only_destination=True)
        else:
            return (self._to_dict_only_origin(), super(UniformListModelMapper, self).to_dict(only_destination=True))

    def _to_dict_only_origin(self):
        update_index = self._update_index
        model = self._orig_data
        ret = [dict() for _ in range(len(model))]
        current_index = self._index

        for link_name, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                update_index(index)
                if isinstance(link_value, ModelMapper):
                    ret[index][link_name] = link_value.to_dict(only_origin=True)
                else:
                    ret[index][link_name] = self._origin_accessor[link_value[0]]
        update_index(current_index)
        return ret
