from rdflib import Graph
from rdflib.namespace import DC, Namespace

from shacl_class_generator import root_class, generate_classes

HSTERMS = Namespace("http://hydroshare.org/terms/")

def test__property_setup():
    shacl_filename = 'data/HSResource_SHACL.ttl'
    metadata_filename = 'data/resource.ttl'
    Resource = root_class(shacl_filename)
    res = Resource()
    res.parse(file_name=metadata_filename)

    assert res.title == '00_ZemelWoodlandN_SiteModel'

    assert res.language == 'eng'
    del res.language
    assert not res.language

    assert len(res.subject) == 4
    for subject in res.subject:
        assert subject in ["mmw", "model-my-watershed", "open-space-institute", "osi"]

    assert len(res.creator) == 1
    assert res.creator[0] == 'http://www.hydroshare.org/user/3015'

    assert res.version == 1

    assert len(res.value) == 3
    for value in res.value:
        assert value in [1, 2, 3]

    assert len(res.extended_metadata) == 2
    keys = ['key', 'key2']
    values = ['value', 'value2']
    for em in res.extended_metadata:
        assert em.key in keys
        keys.remove(em.key)
        assert em.value in values
        values.remove(em.value)


def test__property_modification():
    metadata_filename = 'data/resource.ttl'
    shacl_filename = 'data/HSResource_SHACL.ttl'
    Resource = root_class(shacl_filename)
    res = Resource()
    res.parse(file_name=metadata_filename)

    res.title = 'modified'
    assert res.title == 'modified'
    #assert str(next(res._metadata_graph.objects(subject=None, predicate=DC.title))) == 'modified'

    res.language = 'es'
    assert res.language == 'es'
    #assert str(next(res._metadata_graph.objects(subject=None, predicate=DC.language))) == 'es'

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

    assert len(res.extended_metadata) == 2
    keys = ['key', 'key2']
    values = ['value', 'value2']
    new_extended_metadata = []
    for i, em in enumerate(res.extended_metadata):
        assert em.key in keys
        keys.remove(em.key)
        assert em.value in values
        values.remove(em.value)

        em.key = "key_{}".format(i)
        em.value = "value_{}".format(i)
        new_extended_metadata.append(em)

    res.extended_metadata = new_extended_metadata
    assert len(res.extended_metadata) == 2
    keys = ['key_0', 'key_1']
    values = ['value_0', 'value_1']
    for em in res.extended_metadata:
        assert em.key in keys
        keys.remove(em.key)
        assert em.value in values
        values.remove(em.value)


def test_rdf_creation():
    shacl_filename = 'data/HSResource_SHACL.ttl'
    classes_by_targetClass = generate_classes(shacl_filename)

    Resource = classes_by_targetClass[HSTERMS.resource]
    ExtendedMetadata = classes_by_targetClass[HSTERMS.extendedMetadata]
    Coverage = classes_by_targetClass[DC.coverage]

    res = Resource()
    res.subject = ['subject 1', 'subject 2']
    res.title = "a new title"
    res.language = "en"

    em1 = ExtendedMetadata()
    em1.key = "key1"
    em1.value = "value1"

    em2 = ExtendedMetadata()
    em2.key = "key2"
    em2.value = "value2"

    res.extended_metadata = [em1, em2]

    coverage = Coverage()
    coverage.box = "I don't have regex validation running yet so any string will do for box coverage"
    res.coverage = coverage

    print(res.serialize())
