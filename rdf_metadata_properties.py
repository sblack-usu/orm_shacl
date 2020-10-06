from rdflib import Literal
from rdflib.namespace import SH, XSD, Namespace, RDF
from collections import defaultdict
from rdf_orm_helpers import extract_name, root_subject, URIRef_or_Literal

HSRESOURCE = Namespace('http://www.hydroshare.org/resource/')


class MetadataCard(defaultdict):
    def __init__(self):
        super(MetadataCard, self).__init__(MetadataCard)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


class RDFMetadata:
    '''
    A python class object wrapper around an rdflib graph.  Given a SHACL schema as an rdflib graph,
    this class will build a python class which will allow you to create/edit an rdflib graph in a
    familiar python class object way.
    '''

    @property
    def shacl_subject(self):
        return self._root_shacl_subject

    @property
    def metadata_subject(self):
        return self._root_metadata_subject

    @property
    def term(self):
        term = self._shacl_graph.value(self._shacl_subject, SH.targetClass)
        if not term:
            term = self._shacl_graph.value(self._shacl_subject, SH.path)
        if not term:
            raise Exception("shacl_obj {} must have a predicate sh:targetClass or sh:path")
        return term

    def __init__(self, shacl_graph, metadata_graph, shacl_subject=None, metadata_subject=None):
        '''
        Given a SHACL spec, sets up class properties outlined by the SHACL spec and maps the
        values found in the metadata graph to the class
        :param shacl_graph: an rdflib Graph with a SHACL spec
        :param metadata_graph: an rdflib Graph to read/update metadata complian with the SHACL spec
        '''
        self._shacl_graph = shacl_graph
        self._metadata_graph = metadata_graph

        if shacl_subject:
            self._root_shacl_subject = shacl_subject
        else:
            self._root_shacl_subject = root_subject(self._shacl_graph)

        if metadata_subject:
            self._root_metadata_subject = metadata_subject
        else:
            self._root_metadata_subject = root_subject(self._metadata_graph)

        for property_object in self._shacl_graph.objects(subject=self._root_shacl_subject, predicate=SH.property):
            if self._shacl_graph.value(subject=property_object, predicate=SH.property):
                self._setup_nested_property(property_object)
            else:
                self._setup_property(property_object)

    def _setup_nested_property(self, subject):
        term = self._shacl_graph.value(subject, SH.path)
        max_count = self._shacl_graph.value(subject, SH.maxCount)
        property_name = extract_name(term)
        cards = []
        for obj in self.metadata_objects(subject, term):
            card = MetadataCard()
            for prop in self._shacl_graph.objects(subject, SH.property):
                data_type = self._shacl_graph.value(prop, SH.datatype)
                if not data_type:
                    raise Exception("dc:datatype is required for all nested properties")
                term = self._shacl_graph.value(prop, SH.path)
                max_count = self._shacl_graph.value(subject, SH.maxCount)
                property_name = extract_name(term)
                if max_count == Literal(1):
                    val = self.metadata_value(subject, term)
                    setattr(card, property_name, from_datatype(val, data_type))
                else:
                    raise Exception("Not supporting nested property lists right now, this could change?")
            cards.append(card)
        if max_count == Literal(1):
            setattr(self, property_name)
        else:
            setattr(self, property_name, )


    def _setup_property(self, subject):
        '''
        Given a sh:property subject, determine the property type outlined by the SHACL spec and setup
        an appropriate class property
        :param subject: A sh:property subject
        :return: N/A
        '''
        data_type = self._shacl_graph.value(subject, SH.datatype)
        if not data_type:
            raise Exception("subject {} must include predicate of sh:datatype")
        term = self._shacl_graph.value(subject, SH.path)
        max_count = self._shacl_graph.value(subject, SH.maxCount)
        # minCount = self._shacl_graph.value(subject, SH.minCount)
        property_name = extract_name(term)

        if max_count == Literal(1):
            # single item
            setattr(self.__class__, property_name,
                    RDFProperty(self.metadata_subject, term, data_type, subject))
        else:
            # list of items
            setattr(self.__class__, property_name,
                    RDFPropertyList(self.metadata_subject, term, data_type, subject))

    def metadata_value(self, subject=None, predicate=RDF.value,
                       object=None, default=None, any=True):
        return self._metadata_graph.value(subject, predicate, object, default, any)

    def shacl_value(self, subject=None, predicate=RDF.value,
                       object=None, default=None, any=True):
        return self._shacl_graph.value(subject, predicate, object, default, any)

    def metadata_objects(self, subject=None, predicate=None):
        return self._metadata_graph.objects(subject, predicate)

    def metadata_triples(self, triple):
        return self._metadata_graph.triples(triple)

    def metadata_replace_object(self, subject, predicate, object):
        self.metadata_remove_objects(subject, predicate)
        self.metadata_add(subject, predicate, object)

    def metadata_add(self, subject, predicate, object):
        self._metadata_graph.add((subject, predicate, object))

    def metadata_remove_objects(self, subject, predicate):
        # todo, update this to remove children
        self._metadata_graph.remove((subject, predicate, None))


class RDFProperty(object):
    '''
    A property wrapping an rdflib graph that functions as a python property
    '''
    def __init__(self, subject, predicate, data_type, **kwargs):
        """
        :param subject: The property's subject
        :param predicate: The property's predicate (sh:path... maybe all the time?)
        :param data_type: The property's data_type (XSD or sh:property)
        :return: the property with a getter and setter
        """
        self.subject = subject
        self.predicate = predicate
        self.data_type = data_type
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        val = instance.metadata_value(self.subject, self.predicate)
        return from_datatype(val, self.data_type)

    def __set__(self, instance, value):
        instance.metadata_replace_object(self.subject, self.predicate, to_datatype(value, self.data_type))

    def __delete__(self, instance):
        instance.metadata_remove_objects(self.subject, self.predicate)


class RDFPropertyList(RDFProperty):
    '''
    A property wrapping an rdflib graph that functions as a python list properties
    '''

    def __get__(self, instance, owner):
        return [from_datatype(obj, self.data_type)
                for obj in instance.metadata_objects(self.subject, self.predicate)]

    def __set__(self, instance, values):
        self.__delete__(instance)
        instance.metadata_remove_objects(self.subject, self.predicate)
        if values:
            for value in values:
                instance.shacl_value(subject=self.data_type, predicate=SH.property)
                instance.metadata_add(self.subject, self.predicate, to_datatype(value, self.data_type))

    def __delete__(self, instance):
        instance.metadata_remove_objects(self.subject, self.predicate)


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
    return None