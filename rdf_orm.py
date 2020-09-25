from rdflib import Literal
from rdflib.namespace import SH, XSD
from rdf_metadata_properties import property_string, property_list_string


class RDFMetadata(object):
    '''
    A python class object wrapper around an rdflib graph.  Given a SHACL schema as an rdflib graph,
    this class will build a python class which will allow you to create/edit an rdflib graph in a
    familiar python class object way.
    '''

    def __init__(self, shacl_graph, metadata_graph):
        '''
        Given a SHACL spec, sets up class properties outlined by the SHACL spec
        :param shacl_graph: an rdflib Graph with a SHACL spec
        :param metadata_graph: an rdflib Graph to read/update metadata complian with the SHACL spec
        '''
        self._shacl_graph = shacl_graph
        self._metadata_graph = metadata_graph

        self._root_shacl_subject = root_subject(self._shacl_graph)
        self._root_instance_subject = root_subject(self._metadata_graph)

        for property_object in self._shacl_graph.objects(subject=self._root_shacl_subject, predicate=SH.property):
            self._setup_property(property_object)

    def _setup_property(self, subject):
        '''
        Given a sh:property subject, determine the property type outlined by the SHACL spec and setup
        an appropriate class property for the SHACL spec

        Currently only supports strings and lists of strings
        :param subject: A sh:property subject
        :return: N/A
        '''
        data_type = self._shacl_graph.value(subject, SH.datatype)
        term = self._shacl_graph.value(subject, SH.path)
        max_count = self._shacl_graph.value(subject, SH.maxCount)
        # minCount = self._shacl_graph.value(subject, SH.minCount)
        property_name = extract_name(term)

        if data_type == XSD.string:
            if max_count == Literal(1):
                setattr(self.__class__, property_name,
                        property_string(self._root_instance_subject, term))
            else:
                setattr(self.__class__, property_name,
                        property_list_string(self._root_instance_subject, term))

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
