from rdflib.namespace import SH
from rdf_metadata_properties import RDFMetadata
from rdf_orm_helpers import extract_name, root_subject


def schema_class(shacl_graph, metadata_graph, shacl_obj=None, metadata_obj=None):
    if not shacl_obj:
        shacl_obj = root_subject(shacl_graph)
    term = shacl_graph.value(shacl_obj, SH.targetClass)
    if not term:
        term = shacl_graph.value(shacl_obj, SH.path)
    if not term:
        raise("shacl_obj {} must have a predicate sh:targetClass or sh:path")
    term = extract_name(term)
    schema_class = type(term, (RDFMetadata, ), {})
    return schema_class(shacl_graph, metadata_graph, shacl_obj, metadata_obj)
