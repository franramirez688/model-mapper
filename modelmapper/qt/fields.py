from datetime import datetime

from modelmapper import compat
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


class String(QLineEditAccessor):

    def get_value(self):
        value = super(String, self).get_value()
        return value if value else None

    def set_value(self, value):
        super(String, self).set_value(value if value is not None else '')


class Autocomplete(QLineEditAccessor):

    def get_value(self):
        value = self.widget.value
        return value if value else None

    def set_value(self, value):
        self.widget.value = value if value is not None else ''

    def reset(self):
        self.widget.clear()


class LineDate(QLineEditAccessor):

    def __init__(self, access, from_format='%Y-%m-%dT%H:%M:%S'):
        self.from_format = from_format
        super(LineDate, self).__init__(access)

    def set_value(self, value):
        if value and isinstance(value, compat.basestring):
            super(LineDate, self).set_value(datetime.strptime(value, self.from_format))


class CheckBoxList(QWidgetAccessor):

    def get_value(self):
        return [item.text() for _, item in self.widget.checkedItems()]

    def set_value(self, value):
        pass


# class Operador(Autocomplete):
#
#     def __init__(self, accesss, pk=u'id', text=u'nombre'):
#         self._pk = pk
#         self._text = text
#         super(Operador, self).__init__(accesss)
#
#     def get_value(self):
#         value = self.widget.value
#         if value and isinstance(value, dict) and value.get(self._text):
#             return value[self._pk]
#         return value
#
#     def set_value(self, value):
#         if value and value.get(self._text):
#             super(Operador, self).set_value(value)
