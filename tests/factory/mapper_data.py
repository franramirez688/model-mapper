from modelmapper.accessors import FieldAccessor
from modelmapper.core import FieldDeclaration, ModelMapperDeclaration, ListMapperDeclaration, UniformMapperDeclaration


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
       '{}_link'.format(x): FieldDeclaration(x, 'val_{}'.format(x))
    }


def get_d_list_mapper():
    return {
        'a_link': FieldDeclaration('a', 'val_a'),
        'aa_link': FieldDeclaration('aa', 'val_aa'),
        'aaa_link': FieldDeclaration('aaa', 'val_aaa')
    }


def get_d_mapper():
    return {
        'c_0_link': ModelMapperDeclaration('c[0]', 'val_c[0]', get_child_x_mapper('a')),
        'c_1_link': ModelMapperDeclaration('c[1]', 'val_c[1]', get_child_x_mapper('b')),
        'cc_link': FieldDeclaration('cc', 'val_cc'),
        'ccc_link': UniformMapperDeclaration('ccc', 'val_ccc', get_child_x_mapper('a'))
    }


def get_model_mapper():
    return {
        'd_link': UniformMapperDeclaration('d', 'val_d', get_d_mapper()),
        'dd_link': FieldDeclaration('dd.b', 'val_dd.val_b'),
        'ddd_link': FieldDeclaration('ddd.a', 'val_ddd.val_a'),
        'dddd_link': FieldDeclaration('dddd', 'val_dddd'),
        'complex_link': FieldDeclaration('complex', ComplexAccessor('val_complex')),
        # 'list_link': ListMapperDeclaration('d_list', 'val_list', get_d_list_mapper())
    }
