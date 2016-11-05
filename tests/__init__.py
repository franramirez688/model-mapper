from modelmapper.base import ModelLink, Form, SubForm
from modelmapper.fields import Field


class WidgetA(object):

    def __init__(self, val):
        self._value = val

    def set_value(self, val):
        self._value = val

    def get_value(self):
        return self._value


class WidgetB(object):

    def __init__(self, text):
        self._text = text

    def set_text(self, text):
        self._text = text

    def get_text(self):
        return self._text


class WidgetD(object):

    def __init__(self, val):
        self.value = val


class SimpleUI(object):

    def __init__(self, **kwargs):
        self._name = "Fake"
        self._fake_attr = 5

        self.widget_a = WidgetA(kwargs.get('widget_a', 10))
        self.widget_b = WidgetB(kwargs.get('widget_b', 'Widget B value'))
        self.widget_d = WidgetD(kwargs.get('widget_d', 'Widget D value'))

    def get_values(self):
        return {
            'widget_a': self.widget_a.get_value(),
            'widget_b': self.widget_b.get_text(),
            'widget_d': self.widget_d.value
        }


class _SimpleModelLink(ModelLink):
    widget_a = Field(setter='set_value', getter='get_value')
    widget_b = Field(setter='set_text', getter='get_text')
    widget_c = Field(source='widget_a', setter='set_value', getter='get_value')


class SimpleModelLink(_SimpleModelLink):
    widget_d = Field(setter='value', getter='value')
    widget_e = Field()


class SimpleUI2(object):

    def __init__(self, **kwargs):
        self.widget_e = WidgetA(kwargs.get('widget_e', 10))
        self.widget_f = WidgetB(kwargs.get('widget_f', 'Widget F value'))

    def get_values(self):
        return {
            'widget_e': self.widget_e.get_value(),
            'widget_f': self.widget_f.get_text(),
        }


class ComplexUI(object):

    def __init__(self):
        data_1 = {
            'widget_a': 10,
            'widget_b': 'Text B',
            'widget_d': 'Text D'
        }
        data_2 = {
            'widget_e': 0,
            'widget_f': 'Another text F',
        }
        self.main_ui = SimpleUI(**data_1)
        self.main_widget = WidgetB("Main Widget")
        self.secondary_ui = SimpleUI2(**data_2)

    def get_values(self):
        data = {}
        data.update(self.main_ui.get_values())
        data['main_widget'] = self.main_widget.get_text()
        data.update(self.secondary_ui.get_values())
        return data


class SimpleUIModelLink(_SimpleModelLink):
    widget_a = Field(setter='set_value', getter='get_value')
    widget_b = Field(setter='set_text', getter='get_text')
    widget_d = Field(setter='value', getter='value')


class SimpleUI2ModelLink(ModelLink):
    widget_e = Field(setter='set_value', getter='get_value')
    widget_f = Field(setter='set_text', getter='get_text')


class MainWidgetModelLink(ModelLink):
    main_widget = Field(setter='set_text', getter='get_text')


class UIForm(Form):
    main_ui = SubForm(SimpleUIModelLink)
    secondary_ui = SubForm(SimpleUI2ModelLink)

