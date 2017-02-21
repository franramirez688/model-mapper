
PY2 = str is bytes


if PY2:  # pragma: no cover
    from itertools import ifilter

    filter = ifilter
    basestring = basestring
    unicode = unicode

    def iteritems(d, **kw):
        return d.iteritems(**kw)

else:  # pragma: no cover
    filter = filter
    basestring = str
    unicode = str

    def iteritems(d, **kw):
        return iter(d.items(**kw))
