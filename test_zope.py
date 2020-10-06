class AbstractRDFMetadata:
    _paths = None
    _datatypes = None
    _maxCounts = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in RDFMetadata._paths:
                raise Exception()
            else:
                setattr(self, key, value)

    @staticmethod
    def rdf_path(name):
        return RDFMetadata._paths[name]

    @staticmethod
    def rdf_datatype(name):
        return RDFMetadata._datatypes[name]

    @staticmethod
    def rdf_maxCount(name):
        return RDFMetadata._maxCounts[name]

class RDFMetadata(AbstractRDFMetadata):
    _paths = {'a': 'a_path'}
    _datatypes = {'a': 'a_datatype'}
    _maxCounts = {'a': 'a_maxCount'}

    @property
    def a(self):
        if hasattr(self, '_a'):
            return self._a
        return None

    @a.setter
    def a(self, value):
        # using property for adding validation
        self._a = value

t = RDFMetadata()
print(t.a)
t.a = 'updated'
print(t.a)
print(t.rdf_datatype('a'))

