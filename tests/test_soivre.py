import unittest
from collections import OrderedDict

from modelmapper.core import ModelMapper
from modelmapper.qt.fields import ReadOnlyAccessor, MemoryListAccessor, String


# ORIGIN
def get_origin_line_frutas():
    return {'pack_mark': None}


def get_sends_data():
    return {'lines': [], 'lote_number': None}


def get_sends_lines_data():
    return {'errors': [], 'num_request': None}


def get_sends_errors_data():
    return {'description': None}


def get_response_cert_data():
    return {'information': [], 'errors': [], 'send_date': None}


def get_response_cert_information_data():
    return {'oper_information': [], 'certificate': [], 'response': None}


def get_frutas_lineas_mapper():
    return {
        'pack_mark': ('pack_mark', String('pack_mark'))
    }


def get_origin_data():
    return {'custom_location': None, 'sends': [], 'agent': None, 'creation_date': None, 'transport_other_license': None,
            'response_cert': [get_response_cert_data()], 'code_pi': None, 'orig_country_code': None, 'modification_date': None, 'custom': None,
            'packer': None, 'annexs': [], 'location': None, 'username': None, 'id_': None, 'code_cice': None,
            'registered': False, 'row_type': u'requestfrutas', 'agent_id': None, 'transport_license': None,
            'request_type_code': None, 'reference': None, 'request_id_': None, 'lines': [], 'cice_pi': None,
            'dest_country_code': None, 'soivre_number': None, 'obsv': None, 'imex_code': None, 'transport_code': None}


# DESTINATION
class Model(object):
    def __init__(self, objects):
        self._objects = objects or []

    def get_objects(self):
        return [(i, obj) for i, obj in enumerate(self._objects)]

    def set_source(self, source):
        self._objects = source


class MemoryListWidget(object):

    def __init__(self, objects=None):
        self._model = Model(objects)

    def model(self):
        return self._model


class LineEdit(object):

    def __init__(self):
        self._text = None

    def text(self):
        return self._text

    def setText(self, value):
        self._text = value


class SendSoivre(object):

    def __init__(self):
        self.sends = MemoryListWidget()
        self.lines_sends = MemoryListWidget()
        self.lines_errors = MemoryListWidget()


class ResponseCertSoivre(object):

    def __init__(self):
        self.information = MemoryListWidget()
        self.oper_information = MemoryListWidget()


class ResumenSoivre(object):

    def __init__(self):
        self.resumen_mercancias = MemoryListWidget()


class LineSoivre(object):

    def __init__(self):
        self.pack_mark = LineEdit()


class Soivre(object):

    def __init__(self):
        self.response_cert = ResponseCertSoivre()
        self.sends = SendSoivre()
        self.lines = LineSoivre()
        self.resumen = ResumenSoivre()


# MAPPER
def get_envios_mapper():
    sends_mapper = OrderedDict()
    sends_mapper['sends'] = ('sends', MemoryListAccessor('sends.sends'))
    sends_mapper['lines_sends'] = ('sends[*].lines', MemoryListAccessor('sends.lines_sends'))
    sends_mapper['lines_errors'] = ('sends[*].lines[*].errors', MemoryListAccessor('sends.lines_errors'))
    return sends_mapper


def get_respuestas_mapper():
    responses_mapper = OrderedDict()
    responses_mapper['information'] = ('response_cert', MemoryListAccessor('information'))
    responses_mapper['oper_information'] = ('response_cert.oper_information', MemoryListAccessor('oper_information'))
    responses_mapper['certificate_detail'] = ('response_cert.certificate', MemoryListAccessor('certificate'))
    responses_mapper['certificate_line'] = ('response_cert.certificate.lines', MemoryListAccessor('certificate_line'))
    return responses_mapper


def get_frutas_mapper():
    mapper = OrderedDict()
    mapper.update(get_envios_mapper())
    mapper.update(get_respuestas_mapper())
    mapper['lines'] = ('lines', 'lines', get_frutas_lineas_mapper())
    mapper['resumen'] = (ReadOnlyAccessor('lines'), MemoryListAccessor('resumen.resumen_mercancias'))
    return mapper


class ModelMapperFactoryTest(unittest.TestCase):

    def setUp(self):
        self._origin_model = get_origin_data()
        self._destination_model = Soivre()
        self._mapper = get_frutas_mapper()

        self._model_mapper = ModelMapper(self._origin_model, self._destination_model, self._mapper)
        self._model_mapper.prepare_mapper()

    def test_destination_loads_data_from_origin(self):
        self._model_mapper.origin_to_destination()

    def test_origin_loads_data_from_destination(self):
        self.update_destination_values()
        self._model_mapper.destination_to_origin()

    def update_destination_values(self):
        self._destination_model.response_cert.information.model().set_source([1, 2, 3])
        self._destination_model.response_cert.oper_information.model().set_source([1, 2, 3])
        self._destination_model.sends.sends.model().set_source([1, 2, 3])
        self._destination_model.sends.lines_sends.model().set_source([1, 2, 3])
        self._destination_model.sends.lines_errors.model().set_source([1, 2, 3])
