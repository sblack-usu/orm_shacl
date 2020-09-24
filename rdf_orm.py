from rdflib import BNode, Literal, Graph
from rdflib.namespace import SH, XSD, DC


def extract_name(term):
    delimiter = '/'
    if '#' in term:
        delimiter = '#'
    return term.split(delimiter)[-1]

def root_subject(graph):
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

def property_maker(subject, predicate):
    @property
    def prop(self):
        # need to account for nested properties, just testing title now
        return str(self._metadata_graph.value(subject, predicate))

    @prop.setter
    def prop(self, value):
        # need to account for nested properties and type enforcement, etc
        self._metadata_graph.remove((subject, predicate, None))
        self._metadata_graph.add((subject, predicate, Literal(value)))

    return prop


class RDFMetadata(object):

    def __init__(self, shacl_graph, metadata_graph):
        self._shacl_graph = shacl_graph
        self._metadata_graph = metadata_graph

        self.root_shacl_subject = root_subject(self._shacl_graph)
        self.root_instance_subject = root_subject(self._metadata_graph)

        # this should loop through all properties (hardcoding to title for initial design)
        title_subject = self._shacl_graph.value(predicate=SH.path, object=DC.title)
        self._setup_property(title_subject)

    def _setup_property(self, subject):
        data_type = self._shacl_graph.value(subject, SH.datatype)
        term = self._shacl_graph.value(subject, SH.path)

        if not data_type or not term:
            raise Exception("sh:path and sh:datatype are required within a sh:property")

        if data_type != XSD.string:
            raise Exception("only supporting strings at the moment, got {}".format(data_type))

        # property name is the term without the namespace
        property_name = extract_name(term)
        #save the full term for interacting with rdflib
        #setattr(self, "_{}_term".format(property_name), term)
        setattr(self.__class__, property_name, property_maker(self.root_instance_subject, term))#property_name)))
