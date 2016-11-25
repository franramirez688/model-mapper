
PY2 = str is bytes
PY3 = not PY2


if PY2:  # pragma: no cover
    from itertools import ifilter
    filter = ifilter
else:  # pragma: no cover
    filter = filter
