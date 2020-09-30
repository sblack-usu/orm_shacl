from rdflib.namespace import SH
from rdf_metadata_properties import RDFMetadata
from rdf_orm_helpers import extract_name, root_subject


def schema_class(shacl_graph, metadata_graph, shacl_obj=None, metadata_obj=None):
    """
    Creates a new class with a name that maps to the sh:targetClass (schema) or sh:path (property).
    The class derives from RDFMetadata which dynamically builds the properties of the class
    by reading the shacl schema for the shacl_obj provided
    :param shacl_graph: An rdflib graph with a SHACL schema
    :param metadata_graph: An rdflib graph with metadata in the structure of the provided shacl schema
    :param shacl_obj: The shacl shape to map the schema properties to the python class attributes
    :param metadata_obj: The corresponding metadata object the schema is applied to
    :return: a RDFMetadata derived class with class attributes which map to the shacl schema
    """
    if not shacl_obj:
        shacl_obj = root_subject(shacl_graph)
    term = shacl_graph.value(shacl_obj, SH.targetClass)
    if not term:
        term = shacl_graph.value(shacl_obj, SH.path)
    if not term:
        raise Exception("shacl_obj {} must have a predicate sh:targetClass or sh:path")
    term = extract_name(term)
    schema_class = type(term, (RDFMetadata, ), {})
    return schema_class(shacl_graph, metadata_graph, shacl_obj, metadata_obj)
