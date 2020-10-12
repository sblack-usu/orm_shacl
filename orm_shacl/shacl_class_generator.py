from rdflib import Graph, Namespace
from rdflib.namespace import RDF, SH, XSD

from orm_shacl.rdf_orm_classes import RDFProperty, AbstractRDFMetadata
from orm_shacl.rdf_orm_helpers import root_subject, extract_name

HSTERMS = Namespace("http://hydroshare.org/terms/")


def root_class(shacl_filename, format='turtle'):
    """
    Generates all the classes in the shacl file.  Returns only the generated root class described in the shacl file.
    :param shacl_filename:
    :param format:
    :return:
    """
    shacl_graph = Graph().parse(source=shacl_filename, format=format)
    subject = root_subject(shacl_graph)
    schema_name = shacl_graph.value(subject=subject, predicate=SH.name)
    return generate_classes(shacl_filename)[schema_name.value]

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
            nested_schema = shacl_graph.value(prop, RDF.type)
            if nested_schema:
                nested_schema_name = extract_name(shacl_graph.value(prop, RDF.type))
                if nested_schema_name not in classes:
                    raise Exception("{} is not a known schema".format(nested_schema_name))
                name = extract_name(shacl_graph.value(prop, SH.name))
                if not name:
                    raise Exception("Could not find sh:name on {}".format(nested_schema_name))
                term = shacl_graph.value(nested_schema, SH.targetClass)
                data_type = classes[nested_schema_name]
                if not data_type:
                    raise Exception("Could not find a class definition for {}".format(nested_schema_name))
                max_count = shacl_graph.value(prop, SH.maxCount)
            else:
                name = shacl_graph.value(prop, SH.name).value
                # TODO implement validation against reserved attribute names of the AbstractRDFMetadata
                term = shacl_graph.value(prop, SH.path)

                max_count = shacl_graph.value(prop, SH.maxCount)
                data_type = shacl_graph.value(prop, SH.datatype)
                if not data_type:
                    # TODO - should account for rdf:type rdf:value better than this
                    if shacl_graph.value(prop, getattr(SH, "in")):
                        data_type = XSD.string
            if term is None:
                raise Exception("term is required")
            attributes[name] = RDFProperty(property_name=name, data_type=data_type, term=term, max_count=max_count)

        shape_class = type(schema_name, (AbstractRDFMetadata,), {'_target_class': target_class, **attributes})
        classes[schema_name] = shape_class
        return shape_class

    # this will have to be revisited if we get more complicated than a single nesting
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

    return classes
