
PY2 = str is bytes


if PY2:  # pragma: no cover
    from itertools import ifilter
    filter = ifilter
    basestring = basestring
else:  # pragma: no cover
    filter = filter
    basestring = str
