from rdflib import Literal, URIRef
from rdflib.namespace import XSD

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

def from_XSD(val, data_type):
    '''
    Determines the python type from the XSD data type
    :param val: an rdflib value
    :param data_type: an XSD data type
    :return: val as a python type
    '''
    if data_type == XSD.string:
        return str(val)
    if data_type == XSD.integer:
        return int(val)
    else:
        raise Exception("Encountered unsupported XSD data type {}".format(data_type))

def to_XSD(val, data_type):
    '''
    Determines the XSD data type from the python type
    :param val: an rdflib value
    :param data_type: an XSD data type
    :return: val as a XSD data type
    '''
    if data_type == XSD.string:
        return URIRef_or_Literal(val)
    elif data_type == XSD.integer:
        return Literal(val)
    else:
        raise Exception("Encountered unsupported XSD data type {}".format(data_type))

def rdf_property(subject, predicate, data_type):
    '''
    A property wrapping an rdflib graph that functions as a python property
    :param subject: The property's subject
    :param predicate: The property's predicate
    :return: the property with a getter and setter
    '''
    @property
    def rdf_property(self):
        val = self._metadata_graph.value(subject, predicate)
        return from_XSD(val, data_type)

    @rdf_property.setter
    def rdf_property(self, value):
        self._metadata_graph.remove((subject, predicate, None))
        self._metadata_graph.add((subject, predicate, to_XSD(value, data_type)))

    return rdf_property

def rdf_property_list(subject, predicate, data_type):
    '''
    A property wrapping an rdflib graph that functions as a python list properties
    :param subject: The property's subject
    :param predicate: The property's predicate
    :return: the property_list_string with a getter and setter
    '''
    @property
    def rdf_property_list(self):
        return [from_XSD(obj, data_type) for obj in self._metadata_graph.objects(subject, predicate)]

    @rdf_property_list.setter
    def rdf_property_list(self, values):
        self._metadata_graph.remove((subject, predicate, None))
        for value in values:
            self._metadata_graph.add((subject, predicate, to_XSD(value, data_type)))

    return rdf_property_list
