import unittest

from modelmapper.core import ModelMapper

from tests.factory.qt.destination_data import get_destination_model
from tests.factory.qt.mapper_data import get_model_mapper
from tests.factory.qt.origin_data import get_origin_model


class QtModelMapperFactoryTest(unittest.TestCase):

    def setUp(self, orig_model=None, dest_model=None, mapper=None):
        self._origin_model = orig_model or get_origin_model()
        self._destination_model = dest_model or get_destination_model()
        self._mapper = mapper or get_model_mapper()

        self._model_mapper = ModelMapper(self._origin_model, self._destination_model, self._mapper)
        self._model_mapper.prepare_mapper()

    def update_destination_values(self):
        dest = self._destination_model
        dest.masa_bruta.setText(105)
        dest.expediente.setText("New expediente")
        dest.nombre.setText("New name")

    def assert_all(self, assert_equal=True):
        assert_ = self._get_assert(assert_equal)

        assert_(self._origin_model['masa_bruta'], self._destination_model.masa_bruta.text())
        assert_(self._origin_model['expediente'], self._destination_model.expediente.text())
        assert_(self._origin_model['nombre'], self._destination_model.nombre.text())

    def _get_assert(self, equal=True):
        return self.assertEqual if equal else self.assertNotEqual
