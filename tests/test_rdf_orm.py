from rdflib import Graph
from rdflib.namespace import DC
from rdf_orm import schema_class


def test__property_setup():
    metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
    shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
    res = schema_class(shacl_graph, metadata_graph)

    assert str(res.metadata_subject) == 'http://www.hydroshare.org/resource/ea93a49284204912be7fab054a9d41df'

    assert res.title == '00_ZemelWoodlandN_SiteModel'

    assert res.language == 'eng'
    del res.language
    assert not res.language

    assert len(res.subject) == 4
    for subject in res.subject:
        assert subject in ["mmw", "model-my-watershed", "open-space-institute", "osi"]

    del res.subject
    assert len(res.subject) == 0

    assert len(res.creator) == 1
    assert res.creator[0] == 'http://www.hydroshare.org/user/3015'

    assert res.version == 1

    assert len(res.value) == 3
    for value in res.value:
        assert value in [1, 2, 3]

    '''
    assert len(res.extendedMetadata) == 2
    keys = ['key', 'key2']
    values = ['value', 'value2']
    for em in res.extendedMetadata:
        assert em.key in keys
        keys.remove(em.key)
        assert em.value in values
        values.remove(em.value)

    del res.extendedMetadata
    assert len(res.extendedMetadata) == 0
    '''


def test__property_modification():
    metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
    shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
    res = schema_class(shacl_graph, metadata_graph)

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

    new_creators = ['http://www.hydroshare.org/user/3015', 'http://www.hydroshare.org/user/3014']
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
    '''
    assert len(res.extendedMetadata) == 2
    keys = ['key', 'key2']
    values = ['value', 'value2']
    new_extendedMetadata = []
    for i, em in enumerate(res.extendedMetadata):
        assert em.key in keys
        keys.remove(em.key)
        assert em.value in values
        values.remove(em.value)

        em.key = "key_{}".format(i)
        em.value = "value_{}".format(i)
        new_extendedMetadata.append(em)

    res.extendedMetadata = new_extendedMetadata
    assert len(res.extendedMetadata) == 2
    keys = ['key_0', 'key_1']
    values = ['value_0', 'value_1']
    for em in res.extendedMetadata:
        assert em.key in keys
        keys.remove(em.key)
        assert em.value in values
        values.remove(em.value)
    '''

