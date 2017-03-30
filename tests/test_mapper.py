from nose_parameterized import parameterized

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

    def test_to_dict_data(self):
        self.update_destination_values()
        self.assertEqual(self.get_dict_data(), self._model_mapper.to_dict())

    def test_to_dict_only_origin_data(self):
        self.assertEqual(self.get_dict_data(only_origin=True), self._model_mapper.to_dict(only_origin=True))

    def test_to_dict_only_destination_data(self):
        self.update_destination_values()
        self.assertEqual(self.get_dict_data(only_destination=True), self._model_mapper.to_dict(only_destination=True))

    @parameterized.expand([
        ("in children", 'd', 'd_link'),
        ("in fields", 'dddd', 'dddd_link')
    ])
    def test_filter_origin_access(self, _, access, link_name):
        filtered_values = list(self._model_mapper.filter_origin_access(access))
        expected_values = [(link_name, self._model_mapper[link_name])]
        self.assertEqual(expected_values, filtered_values)

    @parameterized.expand([
        ("in children", 'val_d', 'd_link'),
        ("in fields", 'val_dddd', 'dddd_link')
    ])
    def test_filter_destination_access(self, _, access, link_name):
        filtered_values = list(self._model_mapper.filter_destination_access(access))
        expected_values = [(link_name, self._model_mapper[link_name])]
        self.assertEqual(expected_values, filtered_values)
