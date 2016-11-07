from modelform.base import ModelMapper, Form, SubForm, SubListForm
from modelform.fields import Field, ComposedField, ListComposedField


class ChildA(object):
    def __init__(self, val=None):
        self._value = val

    def set_value(self, val):
        self._value = val

    def get_value(self):
        return self._value


class ChildB(object):
    def __init__(self, text=None):
        self._text = text

    def set_text(self, text):
        self._text = text

    def get_text(self):
        return self._text


class ChildC(object):
    def __init__(self, val=None):
        self.value = val


class Parent(object):
    def __init__(self):
        self.child_a = ChildA()
        self.child_b = ChildB()

        self._no_model = None


class GrandParent(object):
    def __init__(self):
        self.parent = Parent()
        self.orphan = ChildA()
        self.children = ChildA()
        self.fake = 58


# DATA MODEL
grand_parent_data = {
    'parent_db': {
        'child_a_db': {'name_db': "Pablo", 'age_db': 10},
        'child_b_db': {'name_db': "Peter", 'age_db': 10}
    },
    'orphan_db': {'name_db': 'Juan', 'age_db': 4},
    'children_db': [
        {'name_db': "Juan", 'age_db': 9},
        {'name_db': "Sofia", 'age_db': 20}
    ]
}


# Mapper

# {FIELD_NAME: (DB_PATH, OBJ_PATH)}


def get_child(prefix_name, db_path, obj_path):
    return {
        '%s_name' % prefix_name: Field('%s.name_db' % db_path, '%s.name' % obj_path),
        '%s_age' % prefix_name: Field('%s.age_db' % db_path, '%s.age' % obj_path),
    }


child_a = get_child('child_a', 'parent_db.child_a_db', 'parent.child_a')
child_b = get_child('child_b', 'parent_db.child_b_db', 'parent.child_b')
orphan = get_child('orphan', 'orphan_db', 'orphan')
children = get_child('children', 'children_db', 'children')


mapper = {
    'child_a_name': ('parent_db.child_a_db.name', 'parent.child_a.age'),
    'child_a_age': ('parent_db.child_a_db.name', 'parent.child_a.age'),
    'child_b_name': ('parent_db.child_b_db.name', 'parent.child_b.age'),
    'child_b_age': ('parent_db.child_b_db.name', 'parent.child_b.age'),
    'orphan_name': ('orphan_db.name_db', 'orphan_db.age_db'),
}


# CLASS MODEL
# def get_child_mapper(path_to_object=None):
#     return {
#         'name': Field('name_db', path_to_object=path_to_object, setter='set'),
#         'age': Field('age_db', path_to_object=path_to_object, setter='setter')
#     }
#
#
# parent_mapper = {
#     'child_a': ComposedField('child_a_db', get_child_mapper(path_to_object='parent.child_a')),
#     'child_b': ComposedField('child_b_db', get_child_mapper(path_to_object='parent.child_b'))
# }
#
#
# mapper_data = {
#     'parent': ComposedField('parent_db', parent_mapper),
#     'orphan': Field('orphan_db', getter='getter'),
#     'children': ListComposedField('children_db', get_child_mapper(path_to_object='children'))
# }
#
# map = ModelMapper(mapper_data, GrandParent())
#
# map.from_dict(grand_parent_data)
# map.to_dict()
