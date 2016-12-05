from nose_parameterized import parameterized

from modelmapper.exceptions import ModelAccessorIndexError

from tests.factory.mapper import ModelMapperFactoryTest


class TestCompleteModelMapper(ModelMapperFactoryTest):

    def test_destination_loads_data_from_origin(self):
        self._model_mapper.origin_to_destination()
        self.assert_all()

    def test_origin_loads_data_from_destination(self):
        self.update_destination_values()
        self._model_mapper.destination_to_origin()
        self.assert_all()

    @parameterized.expand([
        ("values are equal", 1, True),
        ("values are not equal", 0, False)
    ])
    def test_destination_updates_index_in_child_uniform_lists_mappers(self, _, ccc_link_index, assert_equal):
        self._model_mapper.origin_to_destination()
        self._model_mapper['d_link.ccc_link'].index = 1
        self._assert_child_uniform_list_model_values(ccc_link_index=ccc_link_index, assert_equal=assert_equal)

    @parameterized.expand([
        ("values are equal", 1, True),
        ("values are not equal", 0, False)
    ])
    def test_destination_updates_index_in_parent_uniform_lists_mappers(self, _, d_link_index, assert_equal):
        self._model_mapper.origin_to_destination()
        self._model_mapper['d_link'].index = 1
        self._assert_parent_uniform_list_model_values(d_link_index=d_link_index, assert_equal=assert_equal)
        self._assert_child_uniform_list_model_values(d_link_index=d_link_index, assert_equal=assert_equal)

    def test_model_list_updates_with_non_autoresize(self):
        self._model_mapper['list_link'].autoresize = False

        with self.assertRaises(ModelAccessorIndexError):
            self._model_mapper.origin_to_destination()
