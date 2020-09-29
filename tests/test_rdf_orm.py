from rdflib import Graph
from rdflib.namespace import DC
from rdf_orm import RDFMetadata


def test__property_setup():
    metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
    shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
    res = RDFMetadata(shacl_graph, metadata_graph)

    assert res.title == '00_ZemelWoodlandN_SiteModel'

    assert res.language == 'eng'

    assert len(res.subject) == 4
    for subject in res.subject:
        assert subject in ["mmw", "model-my-watershed", "open-space-institute", "osi"]

    assert len(res.creator) == 1
    for creator in res.creator:
        assert creator in ['http://www.hydroshare.org/user/3015/']

    assert res.version == 1

    assert len(res.value) == 3
    for value in res.value:
        assert value in [1, 2, 3]

    assert len(res.extendedMetadata) == 2
    for em in res.extendedMetadata:
        em.key in ['key', 'key2']
        em.value in ['value', 'value2']

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

    assert len(res.extendedMetadata) == 2
    for i, em in enumerate(res.extendedMetadata):
        em.key in ['key', 'key2']
        em.value in ['value', 'value2']
        em.key = "key_{}".format(i)
        em.value = "value_{}".format(i)

    assert len(res.extendedMetadata) == 2
    for em in res.extendedMetadata:
        em.key in ['key_1', 'key_2']
        em.value in ['value_2', 'value_2']

    #res.extendedMetadata = [('key', 'new key')]
