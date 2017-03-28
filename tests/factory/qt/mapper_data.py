from modelmapper.declarations import Mapper, Field
from modelmapper.qt.fields import QLineEditAccessor


class String(QLineEditAccessor):

    def get_value(self):
        return str(self.widget.text())

    def set_value(self, value):
        self.widget.setText(str(value))


class Integer(QLineEditAccessor):

    def get_value(self):
        return int(self.widget.text())

    def set_value(self, value):
        self.widget.setText(int(value))


def get_child_x_mapper(x):
    return {
       '{}_link'.format(x): (x, 'val_{}'.format(x))
    }


def get_d_mapper():
    return {
        'expediente_link': Mapper('c[0]', 'val_c[0]', get_child_x_mapper('a')),
        'masa_bruta_link': Mapper('c[1]', 'val_c[1]', get_child_x_mapper('b')),
        'nombre_link': Field('cc', 'val_cc'),
    }


def get_model_mapper():
    return {
        'expediente_link': Field('expediente', String('expediente')),
        'masa_bruta_link': Field('masa_bruta', Integer('masa_bruta')),
        'nombre_link': Field('nombre', String('nombre'))
    }
