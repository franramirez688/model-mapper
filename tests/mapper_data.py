from modelmapper.accessors import FieldAccessor


class ComplexAccessor(FieldAccessor):

    def get_value(self):
        return self.field.get_val()

    def set_value(self, value):
        self.field.set_val(value)


class ReadOnlyAccess(FieldAccessor):

    def get_value(self):
        return self.field.get_val()

    def set_value(self, value):
        pass


def get_child_x_mapper(x):
    return {
       '{}_link'.format(x): (x, 'val_{}'.format(x))
    }


def get_d_list_mapper():
    return {
        'a_link': ('a', 'val_a'),
        'aa_link': ('aa', 'val_aa'),
        'aaa_link': ('aaa', 'val_aaa')
    }


def get_d_mapper():
    return {
        'c_0_link': ('c[0]', 'val_c[0]', get_child_x_mapper('a')),
        'c_1_link': ('c[1]', 'val_c[1]', get_child_x_mapper('b')),
        'cc_link': ('cc', 'val_cc'),
        'ccc_link': ('ccc', 'val_ccc', get_child_x_mapper('a'))  # UniformList
    }


def get_model_mapper():
    return {
        'd_link': ('d', 'val_d', get_d_mapper()),  # UniformList
        'dd_link': ('dd.b', 'val_dd.val_b'),
        'ddd_link': ('ddd.a', 'val_ddd.val_a'),
        'dddd_link': ('dddd', 'val_dddd'),
        'complex_link': ('complex', ComplexAccessor('val_complex')),
        'list_link': ('d_list', 'val_list', get_d_list_mapper())
    }


def get_list_model_mapper():
    return {
        'list_link': ('d_list', 'val_list', get_d_list_mapper())
    }

