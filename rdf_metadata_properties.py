from rdflib import Literal, URIRef, BNode
from rdflib.namespace import XSD, SH


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

def extract_name(term):
    '''
    Strips the namespace from the term and returns the identifer
    :param term: An rdflib term
    :return: the identifier of the term as a string
    '''
    if not term:
        return None
    delimiter = '/'
    if '#' in term:
        delimiter = '#'
    return term.split(delimiter)[-1]

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
        print("READING; subject: {} predicate:{}".format(subject, predicate))
        return from_XSD(val, data_type)

    @rdf_property.setter
    def rdf_property(self, value):
        print("WRITING; subject: {} predicate:{}".format(subject, predicate))
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
        print("LIST READING; subject: {} predicate:{}".format(subject, predicate))
        return [from_XSD(obj, data_type) for obj in self._metadata_graph.objects(subject, predicate)]

    @rdf_property_list.setter
    def rdf_property_list(self, values):
        print("LIST WRITING; subject: {} predicate:{}".format(subject, predicate))
        self._metadata_graph.remove((subject, predicate, None))
        for value in values:
            self._metadata_graph.add((subject, predicate, to_XSD(value, data_type)))

    return rdf_property_list

def rdf_nested_property_list(subject, predicate):
    '''
    SETTER IS NOT IMPLEMENTED YET
    A property wrapping an rdflib graph that functions as a python list properties
    :param subject: The property's subject
    :param predicate: The property's predicate
    :return: the property_list_string with a getter and setter
    '''
    @property
    def rdf_nested_property_list(self):
        from rdf_orm import RDFMetadata
        classes = []
        print("NESTED READING; subject: {} predicate:{}".format(subject, predicate))
        for metadata_obj in self._metadata_graph.objects(subject, predicate):
            shacl_obj = self._shacl_graph.value(predicate=SH.path, object=predicate)
            prop = RDFMetadata(self._shacl_graph, self._metadata_graph, shacl_obj, metadata_obj)
            classes.append(prop)
        return classes

    @rdf_nested_property_list.setter
    def rdf_nested_property_list(self, values):
        print("not implemented yet")
        print("NESTED WRITING; subject: {} predicate:{}".format(subject, predicate))

        # does this delete nested nested?  I don't think so, just makes islands
        for obj in self._metadata_graph.objects(subject, predicate):
            self._metadata_graph.remove((obj, None, None))
        self._metadata_graph.remove((subject, predicate, None))

        property_subject = BNode()
        self._metadata_graph.add((subject, predicate, property_subject))

        property_mapping = {prop: extract_name(prop) for prop in self._shacl_graph.objects(obj, SH.property)}
        for key, value in values:
            if key not in property_mapping.values():
                raise Exception("property {} does not match SHACL spec")
            self._metadata_graph.add((property_subject, property_mapping[key], value))

    return rdf_nested_property_list
