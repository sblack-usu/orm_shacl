from rdflib import Literal, URIRef

def URIRef_or_Literal(value):
    '''
    Determines whether the value is a url. Not sure if we can assume all urls should be URIRef.
    :param value:
    :return: URIRef(value) for urls, else Literal(value)
    '''
    if value.startswith('http'):
        return URIRef(value)
    else:
        return Literal(value)

def property_string(subject, predicate):
    '''
    A property wrapping an rdflib graph that functions as a python string property
    :param subject: The property's subject
    :param predicate: The property's predicate
    :return: the property_string with a getter and setter
    '''
    @property
    def property_string(self):
        return str(self._metadata_graph.value(subject, predicate))

    @property_string.setter
    def property_string(self, value):
        self._metadata_graph.remove((subject, predicate, None))
        self._metadata_graph.add((subject, predicate, URIRef_or_Literal(value)))

    return property_string

def property_list_string(subject, predicate):
    '''
        A property wrapping an rdflib graph that functions as a python list of strings property
        :param subject: The property's subject
        :param predicate: The property's predicate
        :return: the property_list_string with a getter and setter
        '''
    @property
    def property_list_string(self):
        return [str(obj) for obj in self._metadata_graph.objects(subject, predicate)]

    @property_list_string.setter
    def property_list_string(self, values):
        self._metadata_graph.remove((subject, predicate, None))
        for value in values:
            self._metadata_graph.add((subject, predicate, URIRef_or_Literal(value)))

    return property_list_string
