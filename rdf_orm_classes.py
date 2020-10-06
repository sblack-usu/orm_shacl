from rdflib import XSD, Literal, RDF, Graph

from rdf_orm_helpers import from_datatype


class RDFProperty:
    '''
    A property to allow us to do validation at assignment
    '''
    def __init__(self, property_name, path, data_type, max_count=None, min_count=None):
        '''
        :param property_name: The name of the property
        '''
        self.property_name = property_name
        self.private_property = "_" + property_name
        self.path = path
        self.data_type = data_type
        self.max_count = max_count
        self.min_count = min_count

    def __get__(self, instance, owner):
        if instance is None:
            # returning self allows us to store property parsing data and logic on the descriptor
            return self
        return getattr(instance, self.private_property)

    def __set__(self, instance, value):
        return setattr(instance, self.private_property, value)

    def __delete__(self, instance):
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
        else:
            return values


class AbstractRDFMetadata:
    _target_class = None

    def __init__(self, file_name=None, format='turtle', metadata_graph=None, root_subject=None):
        if file_name and metadata_graph:
            raise Exception("give me either the rdflib graph or the filename, not both")
        if not file_name and not metadata_graph:
            raise Exception("I need either the file_name or the rdflib graph")
        if file_name:
            metadata_graph = Graph().parse(source=file_name, format=format)

        if not root_subject:
            root_subject = metadata_graph.value(predicate=RDF.type, object=self._target_class)
        props = self._public_properties()
        for property_name in props:
            # we can grab the descriptor because __get__ returns itself when accessed from the class
            prop_descriptor = getattr(type(self), property_name)
            if not prop_descriptor:
                raise Exception("{} is not a RDFProperty or RDFProperty got screwed up")
            property_value = prop_descriptor.parse(metadata_graph, root_subject)
            setattr(self, property_name, property_value)

    def _public_properties(self):
        names = []
        for name in dir(self):
            if not name.startswith('_'):
                names.append(name)
        return names
