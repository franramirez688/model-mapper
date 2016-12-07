
class QLineEdit(object):

    def __init__(self):
        self._text = None

    def setText(self, value):
        self._text = value

    def text(self):
        return self._text


class UI(object):

    def __init__(self):
        self.masa_bruta = QLineEdit()
        self.nombre = QLineEdit()
        self.expediente = QLineEdit()


def get_destination_model():
    return UI()
