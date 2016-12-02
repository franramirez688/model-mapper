

def get_origin_model():
    return {
        'd': [
            {
                'c': [
                    {'a': 1},
                    {'b': 2}
                ],
                'cc': 'fake 1',
                'ccc': [
                    {'a': 1},
                    {'a': 2}
                ]
            },
            {
                'c': [
                    {'a': 3},
                    {'b': 4}
                ],
                'cc': 'fake 2',
                'ccc': [
                    {'a': 3},
                    {'a': 4}
                ]
            },
        ],
        'dd': {
            'b': {
                'new_val_1': 'fake1',
                'new_val_2': 'fake2'
            }
        },
        'ddd': {
            'a': 1
        },
        'dddd': 1,
        'complex': "fake1",
        'd_list': [
            {'a': 1, 'aa': [1, 2], 'aaa': "fake aaa 1"},
            {'a': 2, 'aa': [2, 3], 'aaa': "fake aaa 2"},
            {'a': 3, 'aa': [4, 5], 'aaa': "fake aaa 3"}
        ]
    }
