from rdflib import Literal, BNode
from rdflib.namespace import SH
from zope import interface
from zope.interface import Attribute

from rdf_orm_helpers import extract_name, from_XSD, to_XSD, root_subject


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

        # I may change the property type setup
        if self._shacl_graph.value(subject, SH.property):
            setattr(self.__class__, property_name,
                    RDFNestedPropertyList(self._root_metadata_subject, term, None))
        else:
            if max_count == Literal(1):
                setattr(self.__class__, property_name,
                        RDFProperty(self._root_metadata_subject, term, data_type))
            else:
                # property is a list
                setattr(self.__class__, property_name,
                        RDFPropertyList(self._root_metadata_subject, term, data_type))

class IRDFProperty(interface.Interface):
    # I haven't decided if I'm going to use zope interfaces yet,
    # but this seems like a good place to do so if I were to use it
    subject = Attribute('subject')
    predicate = Attribute('predicate')
    data_type = Attribute('data_type')

class RDFProperty(object):
    '''
    A property wrapping an rdflib graph that functions as a python property
    '''
    def __init__(self, subject, predicate, data_type):
        """
        :param subject: The property's subject
        :param predicate: The property's predicate (sh:path... maybe all the time?)
        :param data_type: The property's data_type (XSD)
        :return: the property with a getter and setter
        """
        self.subject = subject
        self.predicate = predicate
        self.data_type = data_type

    def __get__(self, instance, owner):
        val = instance._metadata_graph.value(self.subject, self.predicate)
        return from_XSD(val, self.data_type)

    def __set__(self, instance, value):
        instance.metadata_graph().remove((self.subject, self.predicate, None))
        instance.metadata_graph().add((self.subject, self.predicate, to_XSD(value, self.data_type)))


class RDFPropertyList(RDFProperty):
    '''
    A property wrapping an rdflib graph that functions as a python list properties
    '''
    def __get__(self, instance, owner):
        return [from_XSD(obj, self.data_type) for obj in instance.metadata_graph().objects(self.subject, self.predicate)]

    def __set__(self, instance, values):
        instance.metadata_graph().remove((self.subject, self.predicate, None))
        for value in values:
            instance.metadata_graph().add((self.subject, self.predicate, to_XSD(value, self.data_type)))

class RDFNestedPropertyList(RDFProperty):
    # this class is likely not needed once I generalize the other implementations to a new shape as a datatype
    '''
    SETTER IS NOT IMPLEMENTED YET
    A property wrapping an rdflib graph that functions as a python list properties
    '''
    def __get__(self, instance, owner):
        from rdf_orm import schema_class
        classes = []
        print("NESTED READING; subject: {} predicate:{}".format(self.subject, self.predicate))
        for metadata_obj in instance.metadata_graph().objects(self.subject, self.predicate):
            shacl_obj = instance.shacl_graph().value(predicate=SH.path, object=self.predicate)
            clazz = schema_class(instance.shacl_graph(), instance.metadata_graph(), shacl_obj, metadata_obj)
            classes.append(clazz)
        return classes

    def __set__(self, instance, values):
        print("not implemented yet")
        print("NESTED WRITING; subject: {} predicate:{}".format(self.subject, self.predicate))

        # does this delete nested nested?  I don't think so, just makes islands
        for obj in instance.metadata_graph().objects(self.subject, self.predicate):
            instance.metadata_graph().remove((obj, None, None))
        instance.metadata_graph().remove((self.subject, self.predicate, None))

        property_subject = BNode()
        instance.metadata_graph().add((self.subject, self.predicate, property_subject))

        property_mapping = {prop: extract_name(prop) for prop in instance.shacl_graph().objects(obj, SH.property)}
        for key, value in values:
            if key not in property_mapping.values():
                raise Exception("property {} does not match SHACL spec")
            instance.metadata_graph().add((property_subject, property_mapping[key], value))
