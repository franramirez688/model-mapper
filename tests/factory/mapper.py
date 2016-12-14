import unittest

from tests.factory.destination_data import get_destination_model, A
from tests.factory.origin_data import get_origin_model

from modelmapper.core import ModelMapper
from tests.factory.mapper_data import get_model_mapper


class ModelMapperFactoryTest(unittest.TestCase):

    def setUp(self, orig_model=None, dest_model=None, mapper=None):
        self._origin_model = get_origin_model() if orig_model is None else orig_model
        self._destination_model = get_destination_model() if dest_model is None else dest_model
        self._mapper = get_model_mapper() if mapper is None else mapper

        self._model_mapper = ModelMapper(self._origin_model, self._destination_model, self._mapper)
        self._model_mapper.prepare_mapper()

    def update_destination_values(self):
        dest = self._destination_model
        dest.val_d.val_c[0].val_a = "New test val_d.val_c[0].val_a"
        dest.val_d.val_c[1].val_b = "New test val_d.val_c[1].val_b"
        dest.val_d.val_cc = "New test val_d.val_cc"
        dest.val_d.val_ccc.val_a = "New test val_d.val_ccc.val_a"
        dest.val_dd.val_b = "New test val_dd.val_b"
        dest.val_ddd.val_a = "New test val_ddd.val_a"
        dest.val_dddd = "New test val_dddd"
        dest.val_complex.set_val("New test val_complex")
        dest.val_list[0] = A(**{'a': 4, 'aa': [], 'aaa': "1"})
        dest.val_list.append(A(**{'a': 5, 'aa': [1], 'aaa': "2"}))
        dest.val_list.append(A(**{'a': 6, 'aa': [1, 2], 'aaa': "3"}))
        dest.val_list.append(A(**{'a': 7, 'aa': [3, 4], 'aaa': "4"}))

    def assert_all(self):
        self._assert_root_basic_values()

        self._assert_parent_uniform_list_model_values()
        self._assert_child_uniform_list_model_values()
        self._assert_child_uniform_list_model_values(ccc_link_index=1, assert_equal=False)

        self._assert_parent_uniform_list_model_values(d_link_index=1, assert_equal=False)
        self._assert_child_uniform_list_model_values(d_link_index=1, ccc_link_index=0, assert_equal=False)
        self._assert_child_uniform_list_model_values(d_link_index=1, ccc_link_index=1, assert_equal=False)

        self._assert_list_model_values()

    def _assert_list_model_values(self, assert_equal=True):
        assert_ = self._get_assert(assert_equal)

        for i, orig_item in enumerate(self._origin_model['d_list']):
            assert_(orig_item, self._destination_model.val_list[i].get_all())

    def _assert_parent_uniform_list_model_values(self, d_link_index=0, assert_equal=True):
        orig_parent = self._origin_model['d'][d_link_index]
        dest_parent = self._destination_model.val_d
        assert_ = self._get_assert(assert_equal)

        assert_(orig_parent['c'][0]['a'], dest_parent.val_c[0].val_a)
        assert_(orig_parent['c'][1]['b'], dest_parent.val_c[1].val_b)
        assert_(orig_parent['cc'], dest_parent.val_cc)

    def _assert_child_uniform_list_model_values(self, d_link_index=0, ccc_link_index=0, assert_equal=True):
        orig_parent = self._origin_model['d'][d_link_index]
        dest_parent = self._destination_model.val_d
        assert_ = self._get_assert(assert_equal)

        assert_(orig_parent['ccc'][ccc_link_index]['a'], dest_parent.val_ccc.val_a)

    def _assert_root_basic_values(self, assert_equal=True):
        assert_ = self._get_assert(assert_equal)

        assert_(self._origin_model['dd']['b'], self._destination_model.val_dd.val_b)
        assert_(self._origin_model['ddd']['a'], self._destination_model.val_ddd.val_a)
        assert_(self._origin_model['dddd'], self._destination_model.val_dddd)
        assert_(self._origin_model['complex'], self._destination_model.val_complex.get_val())

    def _get_assert(self, equal=True):
        return self.assertEqual if equal else self.assertNotEqual

    def get_dict_data(self, only_origin=False, only_destination=False):
        expected_data = {
            'complex_link': ('fake1', 'New test val_complex'),
            'd_link': ([{'c_0_link': {'a_link': 1},
                         'c_1_link': {'b_link': 2},
                         'cc_link': 'fake 1',
                         'ccc_link': [{'a_link': 1}, {'a_link': 2}]},
                        {'c_0_link': {'a_link': 3},
                         'c_1_link': {'b_link': 4},
                         'cc_link': 'fake 2',
                         'ccc_link': [{'a_link': 3}, {'a_link': 4}]}],
                    {'c_0_link': {'a_link': 'New test val_d.val_c[0].val_a'},
                     'c_1_link': {'b_link': 'New test val_d.val_c[1].val_b'},
                     'cc_link': 'New test val_d.val_cc',
                     'ccc_link': {'a_link': 'New test val_d.val_ccc.val_a'}}),
            'dd_link': ({'new_val_1': 'fake1', 'new_val_2': 'fake2'},
                         'New test val_dd.val_b'),
            'ddd_link': (1, 'New test val_ddd.val_a'),
            'dddd_link': (1, 'New test val_dddd'),
            'list_link': ([{'a_link': 1, 'aa_link': [1, 2], 'aaa_link': 'fake aaa 1'},
                           {'a_link': 2, 'aa_link': [2, 3], 'aaa_link': 'fake aaa 2'}],
                          [{'a_link': 4, 'aa_link': [], 'aaa_link': '1'},
                           {'a_link': 5, 'aa_link': [1], 'aaa_link': '2'},
                           {'a_link': 6, 'aa_link': [1, 2], 'aaa_link': '3'},
                           {'a_link': 7, 'aa_link': [3, 4], 'aaa_link': '4'}])}

        expected_only_origin_data = {
            'complex_link': 'fake1',
            'd_link': [
                {'c_0_link': {'a_link': 1},
                 'c_1_link': {'b_link': 2},
                 'cc_link': 'fake 1',
                 'ccc_link': [{'a_link': 1}, {'a_link': 2}]},
                {'c_0_link': {'a_link': 3},
                 'c_1_link': {'b_link': 4},
                 'cc_link': 'fake 2',
                 'ccc_link': [{'a_link': 3}, {'a_link': 4}]}],
            'dd_link': {'new_val_1': 'fake1', 'new_val_2': 'fake2'},
            'ddd_link': 1,
            'dddd_link': 1,
            'list_link': [{'a_link': 1, 'aa_link': [1, 2], 'aaa_link': 'fake aaa 1'},
                          {'a_link': 2, 'aa_link': [2, 3], 'aaa_link': 'fake aaa 2'}]}

        expected_only_destination_data = {
            'complex_link': 'New test val_complex',
            'd_link': {
                    'c_0_link': {'a_link': 'New test val_d.val_c[0].val_a'},
                    'c_1_link': {'b_link': 'New test val_d.val_c[1].val_b'},
                    'cc_link': 'New test val_d.val_cc',
                    'ccc_link': {'a_link': 'New test val_d.val_ccc.val_a'}
            },
            'dd_link': 'New test val_dd.val_b',
            'ddd_link': 'New test val_ddd.val_a',
            'dddd_link': 'New test val_dddd',
            'list_link': [
                {'a_link': 4, 'aa_link': [], 'aaa_link': '1'},
                {'a_link': 5, 'aa_link': [1], 'aaa_link': '2'},
                {'a_link': 6, 'aa_link': [1, 2], 'aaa_link': '3'},
                {'a_link': 7, 'aa_link': [3, 4], 'aaa_link': '4'}]}

        if only_destination:
            return expected_only_destination_data
        elif only_origin:
            return expected_only_origin_data
        else:
            return expected_data
