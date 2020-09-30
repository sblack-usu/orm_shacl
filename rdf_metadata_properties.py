from rdflib import Literal
from rdflib.namespace import SH, XSD
from rdflib.term import Identifier, BNode

from rdf_orm_helpers import extract_name, root_subject, URIRef_or_Literal


class RDFMetadata:
    '''
    A python class object wrapper around an rdflib graph.  Given a SHACL schema as an rdflib graph,
    this class will build a python class which will allow you to create/edit an rdflib graph in a
    familiar python class object way.
    '''

    def shacl_graph(self):
        return self._shacl_graph

    def metadata_graph(self):
        return self._metadata_graph

    def shacl_subject(self):
        return self._root_shacl_subject

    def metadata_subject(self):
        return self._root_metadata_subject

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
            self._setup_property(property_object)

    def _setup_property(self, subject):
        '''
        Given a sh:property subject, determine the property type outlined by the SHACL spec and setup
        an appropriate class property
        :param subject: A sh:property subject
        :return: N/A
        '''
        data_type = self._shacl_graph.value(subject, SH.datatype)
        if not data_type:
            data_type = self._shacl_graph.value(subject, SH.property)
        if not data_type:
            raise Exception("subject {} must include predicate of sh:datatype or sh:property")
        term = self._shacl_graph.value(subject, SH.path)
        max_count = self._shacl_graph.value(subject, SH.maxCount)
        # minCount = self._shacl_graph.value(subject, SH.minCount)
        property_name = extract_name(term)

        if max_count == Literal(1):
            # single item
            setattr(self.__class__, property_name,
                    RDFProperty(self._root_metadata_subject, term, data_type))
        else:
            # list of items
            setattr(self.__class__, property_name,
                    RDFPropertyList(self._root_metadata_subject, term, data_type))


class RDFProperty(object):
    '''
    A property wrapping an rdflib graph that functions as a python property
    '''
    def __init__(self, subject, predicate, data_type):
        """
        :param subject: The property's subject
        :param predicate: The property's predicate (sh:path... maybe all the time?)
        :param data_type: The property's data_type (XSD or sh:property)
        :return: the property with a getter and setter
        """
        self.subject = subject
        self.predicate = predicate
        self.data_type = data_type

    def __get__(self, instance, owner):
        val = instance.metadata_graph().value(self.subject, self.predicate)
        return self.from_datatype(instance, val, self.data_type)

    def __set__(self, instance, value):
        instance.metadata_graph().remove((self.subject, self.predicate, None))
        instance.metadata_graph().add((self.subject, self.predicate, self.to_datatype(value, self.data_type)))

    def __delete__(self, instance):
        instance.metadata_graph().remove((self.subject, self.predicate, None))

    def from_datatype(self, instance, val, data_type):
        '''
        Determines the python type from the XSD data type.  If the property has a property
        then a schema_class is setup to handle the nested properties as a schema class object
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
        if isinstance(data_type, Identifier):
            from rdf_orm import schema_class
            # data_type is a property of the shape, the subject of data_type is the schema
            prop = instance.shacl_graph().value(predicate=SH.property, object=data_type)
            clazz = schema_class(instance.shacl_graph(), instance.metadata_graph(), prop, val)
            return clazz
        raise Exception("Encountered unsupported XSD data type {}".format(data_type))

    def to_datatype(self, val, data_type):
        '''
        Determines the XSD data type from the python type
        :param val: an rdflib value
        :param data_type: an XSD data type
        :return: val as a XSD data type
        '''
        if data_type == XSD.string:
            return URIRef_or_Literal(val)
        if data_type == XSD.integer:
            return Literal(val)
        if isinstance(data_type, Identifier):
            return data_type
        else:
            raise Exception("Encountered unsupported XSD data type {}".format(data_type))


class RDFPropertyList(RDFProperty):
    '''
    A property wrapping an rdflib graph that functions as a python list properties
    '''
    def __get__(self, instance, owner):
        return [self.from_datatype(instance, obj, self.data_type) for obj in instance.metadata_graph().objects(self.subject, self.predicate)]

    def __set__(self, instance, values):
        instance.metadata_graph().remove((self.subject, self.predicate, None))
        if values:
            if self.to_datatype(values[0], self.data_type) != self.data_type:
                # add each value
                for value in values:
                    instance.shacl_graph().value(subject=self.data_type, predicate=SH.property)
                    instance.metadata_graph().add((self.subject, self.predicate, self.to_datatype(value, self.data_type)))
            else:
                # it's a nested property... this should be revisited
                for value in values:
                    schema = BNode()
                    instance.metadata_graph().add((self.subject, self.predicate, schema))
                    for prop in instance.shacl_graph().objects(subject=value.shacl_subject(), predicate=SH.property):
                        data_type = instance.shacl_graph().value(prop, SH.datatype)
                        term = instance.shacl_graph().value(prop, SH.path)
                        property_name = extract_name(term)
                        prop_value = getattr(value, property_name)
                        instance.metadata_graph().add(
                            (schema, term, self.to_datatype(prop_value, data_type)))

    def __delete__(self, instance):
        instance.metadata_graph().remove((self.subject, self.predicate, None))
