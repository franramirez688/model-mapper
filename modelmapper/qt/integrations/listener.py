
# QtCore.QObject
from modelmapper.qt.fields import QWidgetAccessor


class Spy(QtCore.QObject):

    accessor_modified = QtCore.Signal(QWidgetAccessor)


class Listener(QtCore.QObject):

    def __init__(self, parent=None):
        super(Listener, self).__init__(parent=parent)
        self.__blocked = False
        self.__accessors = set()
        self.__dirty_accessors = set()
        # self.spy = Spy()

    def wait_blocked(self, target, *args, **kwargs):
        self.__blocked = True
        ret = target(*args, **kwargs)
        self.__blocked = False
        return ret

    def append(self, accessor):
        self.__accessors.add(accessor)
        accessor.spy.accessor_modified.connect(self.validate)

    @QtCore.Slot(QWidgetAccessor)
    def validate(self, accessor):
        self.__dirty_accessors.add(accessor)

        if not self.__blocked:
            try:
                accessor.validator.validate(accessor.value)
                self.clear_error(accessor)
            except ValidationError as errors:
                self.show_error(accessor, errors.error)
            else:
                combined_accessor, relations = self._get_combined_relations(accessor)
                if combined_accessor is not None:
                    self.validate_combined(combined_accessor, relations)

    def validate_combined(self, combined_accessor, relations):
        try:
            value_pairs = [(accessor.access, accessor.get_value()) for accessor in relations]
            combined_value = dict(value_pairs)

            combined_accessor.validator.validate(combined_value)
            for accessor in relations:
                self.clear_error(accessor)
        except ValidationError as errors:
            for accessor in relations:
                self.show_error(accessor, errors.error)


    def clear_error(self, accessor):
        accessor.widget.setStyleSheet('border: 1px solid lightgray;'
                                      'border-radius: 5px;')
        accessor.widget.setStatusTip('')
        accessor.widget.setToolTip('')

    def show_error(self, accessor, error):
        accessor.widget.setStyleSheet('border: 1px solid red;'
                                      'border-radius: 5px')
        accessor.widget.setStatusTip(error.description)
        accessor.widget.setToolTip(error.description)
