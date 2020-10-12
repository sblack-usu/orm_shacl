from rdflib import XSD, Literal, RDF, Graph, BNode, Namespace, DC

from orm_shacl.rdf_orm_helpers import from_datatype, to_datatype


HSTERMS = Namespace("http://hydroshare.org/terms/")


class RDFProperty:
    '''
    A property that can read/write to a metadata graph for a given sh:property.

    Someday, we can add validation at assignment within __get__/__delete__
    '''
    def __init__(self, property_name, data_type, path, max_count=None, constraints={}):
        """
        :param property_name:
        :param data_type:
        :param path:
        :param max_count:
        :param min_count:
        """
        self.property_name = property_name
        self.private_property = "_" + property_name
        self.data_type = data_type
        self.term = path
        self.max_count = max_count
        self.constraints = constraints

    def __get__(self, instance, owner):
        """
        If instance is None, return self for this property. If instance is provided,
        return the private property on the instance
        :param instance:
        :param owner:
        :return:
        """
        if instance is None:
            # returning self allows us to store property parsing data and logic on the descriptor
            return self
        return getattr(instance, self.private_property)

    def __set__(self, instance, value):
        """
        validation could happen here in the future
        :param instance:
        :param value:
        :return:
        """
        return setattr(instance, self.private_property, value)

    def __delete__(self, instance):
        """
        We could eventually add validation here, currently just sets the property to None
        :param instance:
        :return:
        """
        setattr(instance, self.private_property, None)

    def parse(self, metadata_graph, subject):
        """
        Using property information stored within this class descriptor,
        parse this property's value from the metadata graph
        :param metadata_graph: an rdflib Graph
        :param subject: the subject in the metadata graph to parse
        :return: the value of this property in the metadata_graph
        """
        values = []
        predicate = self.term

        if str(self.data_type).startswith(str(XSD)):
            values = [from_datatype(prop_value, self.data_type)
                      for prop_value in
                      metadata_graph.objects(subject=subject, predicate=predicate)]
        else:
            for nested_subject in metadata_graph.objects(subject=subject, predicate=predicate):
                rdf_metadata_class = self.data_type
                val = rdf_metadata_class()
                val.parse_from_graph(metadata_graph=metadata_graph, root_subject=nested_subject)
                values.append(val)

        if self.max_count == Literal(1):
            if len(values) == 1:
                return values[0]
            if len(values) > 1:
                raise Exception("Invalid data, max count of 1, "
                                "found {} for term {} and {}".format(len(values), predicate, subject))
            return None
        else:
            return values

    def serialize(self, instance, metadata_graph, subject):
        """
        Serializes the data on the instance to the metadata_graph with the provided subject
        :param instance: The instance of the class that has this property
        :param metadata_graph: an rdflib Graph to serialize data into
        :param subject: The subject of the property's data
        :return:
        """
        values = getattr(instance, self.private_property)
        if values:
            if self.max_count == Literal(1):
                values = [values]

            for val in values:
                if str(self.data_type).startswith(str(XSD)):
                    metadata_graph.add((subject, self.term, to_datatype(val, self.data_type)))
                else:
                    property_subject = BNode()
                    metadata_graph.add((subject, self.term, property_subject))
                    val.serialize(metadata_graph, property_subject, False)


class AbstractRDFMetadata:
    """
    A base abstract class for generating a SHACL schema with an RDFProperty for each sh:property in the schema
    """
    _target_class = None

    def __init__(self):
        """
        Initiallizes all properties to None
        """

        properties = self._rdf_properties()
        for property_name in properties:
            setattr(self, property_name, None)

    def parse(self, file, file_format='turtle', root_subject=None):
        """
        Requires the file path of an rdf serialization.  The default file format is turtle.
        Extracts all metadata for each RDFPropertynon the class for the given root_subject.
        If root_subject is not supplied, the root of the graph is used.
        :param file:
        :param file_format:
        :param root_subject:
        """
        metadata_graph = Graph().parse(file, format=file_format)
        self.parse_from_graph(metadata_graph, root_subject)

    def parse_from_graph(self, metadata_graph, root_subject=None):
        """
        Requires an rdflib graph. Extracts all metadata for each RDFProperty within
        the class for the given root_subject.
        If root_subject is not supplied, a root_subject will be extracted from the graph using
        the _target_class term associated with the class implementation
        :param metadata_graph: an rdflib Graph
        :param root_subject:
        """
        if not root_subject:
            root_subject = metadata_graph.value(predicate=RDF.type, object=self._target_class)
            if not root_subject:
                raise Exception("Could not find subject for predicate=RDF.type, object={}".format(self._target_class))

        properties = self._rdf_properties()
        for property_name in properties:
            # we can grab the descriptor because __get__ returns itself when accessed from the class
            prop_descriptor = getattr(type(self), property_name)
            if not prop_descriptor:
                raise Exception("{} is not a RDFProperty or RDFProperty got screwed up")
            property_value = prop_descriptor.parse(metadata_graph, root_subject)
            setattr(self, property_name, property_value)

    def serialize(self, metadata_graph=Graph(), subject=BNode(), root=True):
        """
        Serializes all data contained within this class to an rdflib Graph with the given subject
        :param metadata_graph: The rdflib Graph to serialize the class data to
        :param subject: The subject of the class data
        :param root:
        :return:
        """
        props = self._rdf_properties()
        if root:
            metadata_graph.add((subject, RDF.type, self._target_class))
        for property_name in props:
            prop_descriptor = getattr(type(self), property_name)
            prop_descriptor.serialize(self, metadata_graph, subject)

        # TODO these bindings should happen elsewhere
        metadata_graph.bind('dc', DC)
        metadata_graph.bind('hsterms', HSTERMS)

        return metadata_graph

    def _rdf_properties(self):
        """
        Determines all the properties on self that are an instance of RDFProperty
        :return: list of property names as strings
        """
        names = []
        for name in dir(self):
            if not name.startswith('_') and isinstance(getattr(type(self), name), RDFProperty):
                names.append(name)
        return names
