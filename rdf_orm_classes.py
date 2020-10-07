from rdflib import XSD, Literal, RDF, Graph, BNode, Namespace, DC

from rdf_orm_helpers import from_datatype, to_datatype


HSTERMS = Namespace("http://hydroshare.org/terms/")


class RDFProperty:
    '''
    A property that can read/write to a metadata graph for a given sh:property.

    Someday, we can add validation at assignment within __get__
    '''
    def __init__(self, property_name, path, data_type, max_count=None, min_count=None):
        """

        :param property_name:
        :param path:
        :param data_type:
        :param max_count:
        :param min_count:
        """
        self.property_name = property_name
        self.private_property = "_" + property_name
        self.path = path
        self.data_type = data_type
        self.max_count = max_count
        self.min_count = min_count

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
        if str(self.data_type).startswith(str(XSD)):
            values = [from_datatype(prop_value, self.data_type)
                      for prop_value in
                      metadata_graph.objects(subject=subject, predicate=self.path)]
        else:
            for nested_subject in metadata_graph.objects(subject=subject, predicate=self.path):
                val = self.data_type(metadata_graph=metadata_graph, root_subject=nested_subject)
                values.append(val)

        if self.max_count == Literal(1):
            return values[0]
            if len(values) == 1:
                return values[0]
            if len(values) > 1:
                raise Exception("Invalid data, max count of 1, "
                                "found {} for path {} and {}".format(len(values), self.path, subject))
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
        if self.max_count == Literal(1):
            values = [values]

        for val in values:
            if str(self.data_type).startswith(str(XSD)):
                metadata_graph.add((subject, self.path, to_datatype(val, self.data_type)))
            else:
                property_subject = BNode()
                metadata_graph.add((subject, self.path, property_subject))
                val.serialize(metadata_graph, property_subject)


class AbstractRDFMetadata:
    """
    A base abstract class for generating a SHACL schema with an RDFProperty for each sh:property in the schema
    """
    _target_class = None

    def __init__(self, file_name=None, format='turtle', metadata_graph=None, root_subject=None):
        """
        Requires either the file_name or the metadata_graph.
        Extracts all metadata information from the metadata for the given root_subject.  If root_subject is
        not supplied, the root of the graph is used.
        :param file_name:
        :param format:
        :param metadata_graph:
        :param root_subject:
        """
        if file_name and metadata_graph:
            raise Exception("give me either the rdflib graph or the filename, not both")
        if not file_name and not metadata_graph:
            raise Exception("I need either the file_name or the rdflib graph")
        if file_name:
            metadata_graph = Graph().parse(source=file_name, format=format)

        if not root_subject:
            root_subject = metadata_graph.value(predicate=RDF.type, object=self._target_class)
            if not root_subject:
                raise Exception("Coult not find subject for predicate=RDF.type, object={}".format())
        self._root_subject = root_subject

        properties = self._rdf_properties()
        for property_name in properties:
            # we can grab the descriptor because __get__ returns itself when accessed from the class
            prop_descriptor = getattr(type(self), property_name)
            if not prop_descriptor:
                raise Exception("{} is not a RDFProperty or RDFProperty got screwed up")
            property_value = prop_descriptor.parse(metadata_graph, self._root_subject)
            setattr(self, property_name, property_value)

    def serialize(self, metadata_graph, subject=None):
        """
        Serializes all data contained within this class to an rdflib Graph with the given subject
        :param metadata_graph: The rdflib Graph to serialize the class data to
        :param subject: The subject of the class data
        :return:
        """
        if not subject:
            subject = self._root_subject
        props = self._rdf_properties()
        metadata_graph.add((subject, RDF.type, self._target_class))
        for property_name in props:
            prop_descriptor = getattr(type(self), property_name)
            prop_descriptor.serialize(self, metadata_graph, subject)
        metadata_graph.bind('dc', DC)
        metadata_graph.bind('hsterms', HSTERMS)


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
