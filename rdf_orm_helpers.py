from rdflib import URIRef, Literal, XSD


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

def root_subject(graph):
    '''
    Determines and returns the root subject of an rdflib graph. Currently
    assumes a graph only has one root subject, this may change later.
    :param graph: an rdflib Graph
    :return: a single root subject of the graph
    '''
    root_nodes = set()
    for s in graph.subjects():
        try:
            next(graph.triples((None, None, s)))
        except StopIteration:
            root_nodes.add(s)
    if len(root_nodes) == 0:
        raise Exception("no root subject found... is shacl_graph empty?")
    if len(root_nodes) > 1:
        raise Exception("Currently only supporting one root node in shacl spec")
    return root_nodes.pop()

def from_datatype(val, data_type):
    '''
    Determines the python type from the XSD data type.  If the property has a property
    then a schema_class is setup to handle the nested properties as a schema class object
    :param
    :param val: an rdflib value
    :param data_type: an XSD data type
    :return: val as a python type
    '''
    if not val:
        return None
    if data_type == XSD.string:
        return str(val)
    if data_type == XSD.integer:
        return int(val)
    raise Exception("Unknown data type {}".format(data_type))

def to_datatype(val, data_type):
    '''
    Determines the XSD data type from the python type
    :param val: an rdflib value
    :param data_type: an XSD data type
    :return: val as a XSD data type
    '''
    if not val:
        return None
    if data_type == XSD.string:
        return URIRef_or_Literal(val)
    if data_type == XSD.integer:
        return Literal(val)
    else:
        raise Exception("Encountered unsupported XSD data type {}".format(data_type))