class A(object):

    def __init__(self, **kwargs):
        self.set_all(**kwargs)

    def set_all(self, a=None, aa=None, aaa=None):
        self.val_a = a
        self.val_aa = aa
        self.val_aaa = aaa

    def get_all(self):
        return {'a': self.val_a, 'aa': self.val_aa, 'aaa': self.val_aaa}


class B(object):
    val_b = None


class C(object):
    val_c = [A(), B()]
    val_cc = None
    val_ccc = A()


class Complex(object):

    def __init__(self):
        self._val = None

    def set_val(self, value):
        self._val = value

    def get_val(self):
        return self._val


class D(object):
    val_d = C()
    val_dd = B()
    val_ddd = A()
    val_dddd = None
    val_complex = Complex()
    val_list = [
        A(),
        A(),
        A()
    ]


def get_destination_model():
    return D()
