from modelmapper.accessors import FieldAccessor


class WidgetAccessor(FieldAccessor):

    @property
    def widget(self):
        return self.field

    def get_value(self):
        return self.widget.metaObject().userProperty().read(self.widget)

    def set_value(self, value):
        self.widget.metaObject().userProperty().write(self.widget, value)
