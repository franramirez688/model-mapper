from sys import version_info as py_version_info


PY2 = py_version_info[0] == 2
PY3 = py_version_info[0] == 3


if PY2:
    from itertools import ifilter
    filter = ifilter
else:
    pass
