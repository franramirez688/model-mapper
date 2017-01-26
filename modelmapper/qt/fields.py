from __future__ import unicode_literals

import numbers
from datetime import datetime

from modelmapper import compat
from modelmapper.accessors import FieldAccessor


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
        val = self.get_value()
        try:
            self.validator.validate(val)
        except Exception as errors:
            self.set_error(getattr(errors, 'error', errors))
            raise

    def set_error(self, error):
        self.widget.setStatusTip(error)
        self.widget.setToolTip(error)
        self.widget.setStyleSheet('border: 1px solid red;'
                                  'border-radius: 5px')

    def clear_error(self):
        self.widget.setStatusTip('')
        self.widget.setToolTip('')
        self.widget.setStyleSheet('border: 1px solid lightgray;'
                                  'border-radius: 5px;')


class QLineEditAccessor(QWidgetAccessor):

    def get_value(self):
        return self.widget.text()

    def set_value(self, value):
        val = str(value) if value else ''
        self.widget.setText(val)


class MemoryListAccessor(QWidgetAccessor):

    def get_value(self):
        return [row[1] for row in self.widget.model().get_objects()]

    def set_value(self, value):
        self.widget.model().set_source(value)


class String(QLineEditAccessor):

    def get_value(self):
        value = super(String, self).get_value()
        return str(value) if value else None


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
        return self.widget.value() if self.widget.text() else None

    def set_value(self, value):
        widget = self.widget
        if value is None:
            widget.setValue(widget.minimum())
            widget.clear()
        elif isinstance(value, numbers.Number):
            widget.setValue(value)
        else:
            widget.setValue(float(value) if '.' in value else int(value))


class Integer(QLineEditAccessor):

    def get_value(self):
        value = super(Integer, self).get_value()
        return int(value) if value else None


class ReadOnlyAccessor(FieldAccessor):

    def set_value(self, value):
        pass

    def get_value(self):
        return self._parent_accessor[self.access]


class PlainTextEdit(QWidgetAccessor):

    def set_value(self, value):
        val = value if value is not None else ''
        self.widget.setPlainText(val)

    def get_value(self):
        return self.widget.toPlainText() or None
