from rdflib import Graph
from rdflib.namespace import DC
from rdf_orm import RDFMetadata


def test__property_setup():
    metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
    shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
    res = RDFMetadata(shacl_graph, metadata_graph)

    assert res.title == '00_ZemelWoodlandN_SiteModel'

    assert res.language == 'eng'

    for subject in res.subject:
        assert subject in ["mmw", "model-my-watershed", "open-space-institute", "osi"]

    for creator in res.creator:
        assert creator in ['http://www.hydroshare.org/user/3015/']

    assert res.version == 1

    for value in res.value:
        assert value in [1, 2, 3]

def test__property_modification():
    metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
    shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
    res = RDFMetadata(shacl_graph, metadata_graph)

    res.title = 'modified'
    assert res.title == 'modified'
    assert str(next(res._metadata_graph.objects(subject=None, predicate=DC.title))) == 'modified'

    res.language = 'es'
    assert res.language == 'es'
    assert str(next(res._metadata_graph.objects(subject=None, predicate=DC.language))) == 'es'

    new_subjects = ['one', 'two', 'three']
    res.subject = new_subjects
    assert len(res.subject) == 3
    for subject in res.subject:
        assert subject in new_subjects

    new_creators = ['http://www.hydroshare.org/user/3015/', 'http://www.hydroshare.org/user/3014/']
    res.creator = new_creators
    assert len(res.creator) == 2
    for creator in res.creator:
        assert creator in new_creators

    res.version = 2
    assert res.version == 2

    new_values = [4, 5, 6]
    res.value = new_values
    for value in res.value:
        assert value in [4, 5, 6]
