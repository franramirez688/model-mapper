from tests.factory.qt.mapper import QtModelMapperFactoryTest


class TestCompleteModelMapper(QtModelMapperFactoryTest):

    def test_destination_loads_data_from_origin(self):
        self._model_mapper.origin_to_destination()
        self.assert_all()

    def test_origin_loads_data_from_destination(self):
        self.update_destination_values()
        self._model_mapper.destination_to_origin()
        self.assert_all()
