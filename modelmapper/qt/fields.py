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


class MemoryListAccessor(QWidgetAccessor):

    def __init__(self, access, details=None):
        super(MemoryListAccessor, self).__init__(access)

        self.details = details

        if self.details:
            self.widget.clicked.connect(self.on_activated)

    def on_activated(self, index):
        item = self.widget.model().get_item(index.row())
        if item:
            for detail_name in self.details:
                self._set_detail(detail_name, item[1])
        else:
            self._clear_details()

    def get_value(self):
        return [row[1] for row in self.widget.model().get_objects()]

    def set_value(self, value):
        self.widget.model().set_source(value)

    def _propagate_activation(self, widget):
        widget.clicked.emit(widget.model()._index(0, 0))

    def _set_detail(self, detail_name, value):
        detail = self._get_detail(detail_name)
        detail.setter(value)
        self._propagate_activation(detail.widget)

    def _get_detail(self, detail_name):
        if detail_name in self.form.fields:
            return self.form.fields[detail_name]

        raise FieldAccessorError(u'El campo {} definido en details no existe en el formulario'.
                                 format(detail_name))

    def _clear_details(self):
        for detail_name in self.details:
            detail = self._get_detail(detail_name)
            self._set_detail(detail_name, {detail.source: []} if detail.source else [])
