from rdflib import Graph, Namespace, BNode
from rdflib.namespace import RDF, SH, XSD

from orm_shacl.rdf_orm_classes import RDFProperty, AbstractRDFMetadata
from orm_shacl.rdf_orm_helpers import root_subject, extract_name, children_triples

HSTERMS = Namespace("http://hydroshare.org/terms/")


def generate_classes(shacl_filename, format='turtle'):
    """
    Generates classes that represents each NodeShape in a SHACL rdf graph
    :param shacl_filename:
    :param format: shacl_filename format, defaults to turtle
    :return:
    """
    shacl_graph = Graph().parse(source=shacl_filename, format=format)
    classes = {}

    def nested_property(subject):
        """
        Determines whether the subject has a property with a property (nested)
        :param subject: a subject of the shacl_graph
        :return: True if nested
        """
        for prop in shacl_graph.objects(subject=subject, predicate=SH.property):
            if shacl_graph.value(subject=prop, predicate=RDF.type):
                return True
        return False

    def parse_class(subject):
        """
        Generates a class with parent AbstractRDFMetadata for the shacl subject.  The new class
        will have an RDFProperty for each property on the subject
        :param subject: an shacl subject in the shacl rdflib graph
        :return: the class generated from the shacl subject
        """
        schema_name = extract_name(subject)
        target_class = shacl_graph.value(subject, SH.targetClass)

        attributes = {}
        for prop in shacl_graph.objects(subject, SH.property):

            name = shacl_graph.value(prop, SH.name).value
            if name is None:
                raise Exception("sh:name is required, check property {}".format(prop))

            path = shacl_graph.value(prop, SH.path)
            if path is None:
                raise Exception("sh:path is required, check property {}".format(name))

            data_type = shacl_graph.value(prop, SH.datatype)
            node = None
            if not data_type:
                node = shacl_graph.value(prop, SH.node)
                if not node:
                    data_type = XSD.string
            max_count = shacl_graph.value(prop, SH.maxCount)
            if data_type and node:
                raise Exception("I don't know how to handle both sh:node and sh:datatype")
            # TODO implement validation against reserved attribute names of the AbstractRDFMetadata
            if not data_type and node:
                nested_schema_name = extract_name(node)
                if nested_schema_name not in classes:
                    raise Exception("{} is not a known schema".format(nested_schema_name))
                data_type = classes[nested_schema_name]

            # extract all other attributes in the property
            constraints = []
            #for predicate, obj in shacl_graph.predicate_objects(subject=prop):
            #    if predicate not in (SH.name, SH.datatype, SH.path, SH.maxCount):
            #        constraints.append((predicate, obj))
            #        constraints = constraints + children_triples(shacl_graph, obj)

            #constraints = [(predicate, obj)
            #               for predicate, obj in shacl_graph.predicate_objects(subject=prop)
            #               if predicate not in (SH.name, SH.datatype, SH.path, SH.maxCount)]

            attributes[name] = RDFProperty(property_name=name, data_type=data_type, path=path, max_count=max_count,
                                           constraints=constraints)

        shape_class = type(schema_name, (AbstractRDFMetadata,), {'_target_class': target_class, **attributes})
        classes[schema_name] = shape_class
        return shape_class

    for subject in shacl_graph.subjects(RDF.type, SH.Shape):
        parse_class(subject)
    for subject in shacl_graph.subjects(RDF.type, SH.NodeShape):
        parse_class(subject)

    return classes
