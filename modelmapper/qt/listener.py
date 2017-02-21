from modelmapper import pubsub


class Listener(object):

    def __init__(self):
        self._combined_fields = []
        self.__cached_relations_map = dict()
        self.__accessors_without_relations = set()

        pubsub.subscribe(self.validate_changed_accessor, 'widget_value_changed')
        # pubsub.subscribe(self.validate_combined_accessor, 'widget_value_changed')

    def validate_changed_accessor(self, topic, accessor):
        value = accessor.get_value()
        validator = accessor.validator

        if validator is None:
            return

        try:
            validator.validate(value)
        # TODO: Exception to ValidationError de rome
        except Exception as errors:
            accessor.show_error(errors.error)
        else:
            accessor.clear_error()
            self.validate_combined_accessor(accessor)

    def validate_combined_accessor(self, accessor):
        for accessors, validator in self.get_accessor_relations(accessor):
            value = dict([(acc.access, acc.get_value()) for acc in accessors])
            try:
                print(value)
                validator.validate(value)
            # TODO: Exception to ValidationError de rome
            except Exception as errors:
                for acc in accessors:
                    print(unicode(errors))
                    acc.show_error(errors.error)
            else:
                for acc in accessors:
                    acc.clear_error()

    def get_accessor_relations(self, accessor):
        if accessor in self.__cached_relations_map:
            pass
        elif accessor not in self.__accessors_without_relations:
            _has_relations = False
            for accessors, combined_validator in self._combined_fields:
                if accessor in accessors:
                    _has_relations = True
                    self.__cached_relations_map.setdefault(accessor, [])
                    self.__cached_relations_map[accessor].append((accessors, combined_validator))
            if not _has_relations:
                self.__accessors_without_relations.add(accessor)
        return self.__cached_relations_map.get(accessor, ())

    def add_combined_fields(self, accessors, combined_validator):
        self._combined_fields.append((accessors, combined_validator))
