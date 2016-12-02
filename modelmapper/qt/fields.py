from modelmapper.accessors import FieldAccessor
from modelmapper.exceptions import FieldAccessorError


class QWidgetAccessor(FieldAccessor):

    @property
    def widget(self):
        return self.field

    def get_value(self):
        return self.widget.metaObject().userProperty().read(self.widget)

    def set_value(self, value):
        self.widget.metaObject().userProperty().write(self.widget, value)


class QLineEditAccessor(QWidgetAccessor):

    def get_value(self):
        return self.widget.text()

    def set_value(self, value):
        self.widget.setText(value)
