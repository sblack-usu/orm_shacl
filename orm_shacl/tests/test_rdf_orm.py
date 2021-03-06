from rdflib import Graph
from rdflib.namespace import Namespace

from orm_shacl.shacl_class_generator import generate_classes

HSTERMS = Namespace("http://hydroshare.org/terms/")

def test__property_setup():
    shacl_filename = 'data/HSResource_SHACL.ttl'
    metadata_filename = 'data/resource.ttl'
    classes = generate_classes(shacl_filename)
    res = classes['HSResource']()
    res.parse(file=metadata_filename, file_format='turtle')

    assert res.title == 'hello'

    assert res.language == 'eng'
    del res.language
    assert not res.language

    assert len(res.subject) == 3
    for subject in res.subject:
        assert subject in ["dude", "it", "works"]

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
    classes = generate_classes(shacl_filename)
    res = classes['HSResource']()
    res.parse(file=metadata_filename)

    res.title = 'modified'
    assert res.title == 'modified'

    res.language = 'es'
    assert res.language == 'es'

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
    classes = generate_classes(shacl_filename)

    res = classes['HSResource']()
    res.subject = ['subject 1', 'subject 2']
    res.title = "a new title"
    res.language = "en"

    em1 = classes['ExtendedMetadata']()
    em1.key = "key1"
    em1.value = "value1"

    em2 = classes['ExtendedMetadata']()
    em2.key = "key2"
    em2.value = "value2"

    res.extended_metadata = [em1, em2]

    coverage = classes['Coverage']()
    coverage.box = "I don't have regex validation running yet so any string will do for box coverage"
    res.coverage = [coverage]

    g = Graph()
    res.serialize(g)

    res2 = classes['HSResource']()
    res2.parse_from_graph(g)

    assert res2.title == 'a new title'
    assert res2.language == 'en'

    keys = ['key1', 'key2']
    values = ['value1', 'value2']
    assert len(res2.extended_metadata) == 2
    for em in res2.extended_metadata:
        assert em.key in keys
        keys.remove(em.key)
        assert em.value in values
        values.remove(em.value)

    subjects = ['subject 1', 'subject 2']
    assert len(res2.subject) == 2
    for subject in res2.subject:
        assert subject in subjects
        subjects.remove(subject)

    assert res.coverage[0].box == "I don't have regex validation running yet so any string will do for box coverage"


