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


def get_d_list_mapper():
    return {
        'a_link': ('a', 'val_a'),
        'aa_link': ('aa', 'val_aa'),
        'aaa_link': ('aaa', 'val_aaa')
    }


def get_d_mapper():
    return {
        'expediente_link': ('c[0]', 'val_c[0]', get_child_x_mapper('a')),
        'masa_bruta_link': ('c[1]', 'val_c[1]', get_child_x_mapper('b')),
        'nombre_link': ('cc', 'val_cc'),
    }


def get_model_mapper():
    return {
        'expediente_link': ('expediente', String('expediente')),
        'masa_bruta_link': ('masa_bruta', Integer('masa_bruta')),
        'nombre_link': ('nombre', String('nombre'))
    }
