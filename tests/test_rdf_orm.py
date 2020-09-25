from rdflib import Graph
from rdf_orm import RDFMetadata


def test__property_setup():
    metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
    shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
    res = RDFMetadata(shacl_graph, metadata_graph)
    assert res.title == '00_ZemelWoodlandN_SiteModel'
    assert res.language == 'eng'
    for subject in res.subject:
        assert subject in ["mmw", "model-my-watershed", "open-space-institute", "osi"]

def test__property_modification():
    metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
    shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
    res = RDFMetadata(shacl_graph, metadata_graph)

    res.title = 'modified'
    assert res.title == 'modified'

    res.language = 'es'
    assert res.language == 'es'

    new_subjects = ['one', 'two', 'three']
    res.subject = new_subjects
    for subject in res.subject:
        assert subject in ['one', 'two', 'three']
