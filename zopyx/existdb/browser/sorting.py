# *-* encoding: iso-8859-15 *-*

################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################


def normalize(s, encoding):
    """ German normalization """

    if not isinstance(s, unicode):
        s = unicode(s, encoding, 'ignore')
    s = s.lower()
    s = s.replace(u'ä', 'ae')
    s = s.replace(u'ö', 'oe')
    s = s.replace(u'ü', 'ue')
    s = s.replace(u'ß', 'ss')
    return s

def germanCmp(o1, o2, encoding='utf-8'):
    return cmp(normalize(o1.Title(), encoding),
               normalize(o2.Title(), encoding))

def default_sort_method(o1, o2, encoding='utf-8'):
    return cmp(o1.Title().lower(),
               o2.Title().lower())


sort_methods = {
    'de' : germanCmp,
}

