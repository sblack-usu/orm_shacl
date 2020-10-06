from rdflib import Graph, Namespace
from rdflib.namespace import RDF, SH

from rdf_orm_classes import RDFProperty, AbstractRDFMetadata
from rdf_orm_helpers import root_subject

HSTERMS = Namespace("http://hydroshare.org/terms/")


def root_class(shacl_filename, format='turtle'):
    shacl_graph = Graph().parse(source=shacl_filename, format=format)
    subject = root_subject(shacl_graph)
    target_class = shacl_graph.value(subject=subject, predicate=SH.targetClass)
    return generate_classes(shacl_filename)[target_class]

def generate_classes(shacl_filename, format='turtle'):
    """

    :param shacl_filename:
    :param format: shacl_filename format, defaults to turtle
    :return:
    """
    shacl_graph = Graph().parse(source=shacl_filename, format=format)
    shape_by_targetClass = {}

    def nested_property(subject):
        for prop in shacl_graph.objects(subject=subject, predicate=SH.property):
            if shacl_graph.value(subject=prop, predicate=SH.targetClass):
                return True
        return False

    def parse_class(subject):
        schema_name = shacl_graph.value(subject, SH.name)
        target_class = shacl_graph.value(subject, SH.targetClass)

        attributes = {}
        for prop in shacl_graph.objects(subject, SH.property):
            name = shacl_graph.value(prop, SH.name).value
            path = shacl_graph.value(prop, SH.path)
            max_count = shacl_graph.value(prop, SH.maxCount)
            min_count = shacl_graph.value(prop, SH.minCount)
            data_type = shacl_graph.value(prop, SH.datatype)
            if not data_type:
                # if data type is not provided, then it must be a nested class
                nested_target_class = shacl_graph.value(prop, SH.targetClass)
                if not nested_target_class:
                    raise Exception("Could not find sh:datatype or sh:targetClass on {}".format(name))
                data_type = shape_by_targetClass[nested_target_class]
                if not data_type:
                    raise Exception("Could not find a class definition for {}".format(nested_target_class))

            attributes[name] = RDFProperty(name, path, data_type, max_count, min_count)

        shape_class = type(schema_name, (AbstractRDFMetadata,), {'_target_class': target_class, **attributes})
        shape_by_targetClass[target_class] = shape_class
        return shape_class

    # this will have to be revisisted if we get more complicated than a single nesting
    subjects = []
    with_nested_subjects = []
    for subject in shacl_graph.subjects(RDF.type, SH.NodeShape):
        if nested_property(subject):
            with_nested_subjects.append(subject)
        else:
            subjects.append(subject)

    for subject in subjects:
        parse_class(subject)
    for subject in with_nested_subjects:
        parse_class(subject)

    return shape_by_targetClass
