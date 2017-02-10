
# QtCore.QObject

class Listener(QtCore.QObject):

    def __init__(self, parent=None):
        super(Listener, self).__init__(parent=parent)
        self.__blocked = False
        self.__accessors = set()

    def wait(self, target, *args, **kwargs):
        self.__blocked = True
        ret = target(*args, **kwargs)
        self.__blocked = False
        return ret

    def append(self, accessor):
        self.__accessors.add(accessor)
        accessor.value_changed.connect(self.validate)

    def validate(self, val):
        if not self.__blocked:
            widget_to_validate = self.sender()
            accessor = self.__accessors.get(widget_to_validate)

            try:
                accessor.validator.validate(val)
            except ValidationError as errors:
                pass

    def emit_value_ok(self):
        self._listener.widget_ok.emit(self)
        self.widget.setStyleSheet('border: 1px solid lightgray;'
                                  'border-radius: 5px;')
        self.widget.setStatusTip('')
        self.widget.setToolTip('')

    def emit_value_error(self, error):
        self._listener.widget_with_errors.emit(self, error)
        self.widget.setStyleSheet('border: 1px solid red;'
                                  'border-radius: 5px')
        self.widget.setStatusTip(error.description)
        self.widget.setToolTip(error.description)




