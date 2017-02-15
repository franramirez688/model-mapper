
# QtCore.QObject
from modelmapper import pubsub


class Listener(object):

    def __init__(self, model_mapper=None):
        # super(Listener, self).__init__(parent=parent)
        pubsub.publish(self.add_changed_accessor, 'widget_value_changed')
        self._model_mapper = model_mapper

    def add_changed_accessor(self, accessor):
        value = accessor.get_value()
        widget = accessor.widget
        validator = accessor.validator

        try:
            validator.validate(value)
        except Exception as errors:
            self.show_error(widget, errors.error)

    def clear_error(self, widget):
        widget.setStyleSheet('border: 1px solid lightgray;'
                             'border-radius: 5px;')
        widget.setToolTip('')
        widget.setStatusTip('')

    def show_error(self, widget, error):
        widget.setStyleSheet('border: 1px solid red;'
                             'border-radius: 5px')
        widget.setStatusTip(error.description)
        widget.setToolTip(error.description)
