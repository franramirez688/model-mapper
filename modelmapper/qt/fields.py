from __future__ import unicode_literals

from datetime import datetime

from modelmapper import compat
from modelmapper.accessors import FieldAccessor
from modelmapper.exceptions import FieldAccessorError


class QWidgetAccessor(FieldAccessor):

    def __init__(self, access):
        super(QWidgetAccessor, self).__init__(access)
        self.validator = None
        self.help_field = None

    @property
    def widget(self):
        return self.field

    def get_value(self):
        return self.widget.metaObject().userProperty().read(self.widget)

    def set_value(self, value):
        self.widget.metaObject().userProperty().write(self.widget, value)

    def validate(self):
        self.validator.validate(self.get_value())


class QLineEditAccessor(QWidgetAccessor):

    def get_value(self):
        return self.widget.text()

    def set_value(self, value):
        self.widget.setText(value)


class MemoryListAccessor(QWidgetAccessor):


    def __init__(self, access, details=None):
        super(MemoryListAccessor, self).__init__(access)

        self.details = details
        self.signals_activated = False

    def try_connect_signals(self):
        if self.details and not self.signals_activated:
            self.signals_activated = True
            self.widget.clicked.connect(self.on_activated)

    def on_activated(self, index):
        item = self.widget.model().get_item(index.row())
        if item:
            for detail_name in self.details:
                self._set_detail(detail_name, item[1])
        else:
            self._clear_details()

    def get_value(self):
        self.try_connect_signals()
        return [row[1] for row in self.widget.model().get_objects()]

    def set_value(self, value):
        self.try_connect_signals()
        self.widget.model().set_source(value)

    def _propagate_activation(self, widget):
        self.widget.clicked.emit(self.widget.model()._index(0, 0))

    def _set_detail(self, detail_name, value):
        detail = self._get_detail(detail_name)
        detail.set_value(value)
        self._propagate_activation(detail.widget)

    def _get_detail(self, detail_name):
        if detail_name in self.parent_accessor:
            return self.parent_accessor[detail_name]

        raise FieldAccessorError(u'El campo {} definido en details no existe en el formulario'.
                                 format(detail_name))

    def _clear_details(self):
        for detail_name in self.details:
            detail = self._get_detail(detail_name)
            self._set_detail(detail_name, {detail.source: []} if detail.source else [])


class String(QLineEditAccessor):

    def get_value(self):
        value = super(String, self).get_value()
        return value or None

    def set_value(self, value):
        super(String, self).set_value(value if value is not None else '')


class Autocomplete(QLineEditAccessor):

    def get_value(self):
        value = self.widget.value
        return value or None

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

    def get_value(self):
        value = super(LineDate, self).get_value()
        return datetime.strptime(value, '%d-%m-%Y') if value and value != 'dd-mm-aaaa' else None


class CheckBoxList(QWidgetAccessor):

    def get_value(self):
        return [item.text() for _, item in self.widget.checkedItems()]

    def set_value(self, value):
        pass


class SpinBox(QWidgetAccessor):

    def get_value(self):
        return self.widget.value()

    def set_value(self, value):
        if value is None:
            self.widget.clear()
        self.widget.setValue(str(value) or '')


class Integer(QLineEditAccessor):

    def get_value(self):
        value = super(Integer, self).get_value()
        return int(value) if value else None

    def set_value(self, value):
        super(Integer, self).set_value(value if value else '')


class ReadOnlyAccessor(FieldAccessor):

    def set_value(self, value):
        pass

    def get_value(self):
        return self._parent_accessor[self.access]


class PlainTextEdit(QWidgetAccessor):

    def set_value(self, value):
        self.widget.setPlainText(value if value is not None else '')

    def get_value(self):
        return self.widget.plainText or None
