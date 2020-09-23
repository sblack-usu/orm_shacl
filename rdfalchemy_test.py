from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple
from rdflib import SH, DC, XSD, Graph
from rdflib.namespace import Namespace

from rdfalchemy.orm import mapper

HSTERMS = Namespace("http://hydroshare.org/terms/")
SCHEMA = Namespace("http://schema.org/")


class HSResource(rdfSubject):
    rdf_type = SCHEMA.HSResource
    title = rdfSingle(DC.title, 'title')
    language = rdfSingle(DC.language, 'language')
    subjects = rdfMultiple(DC.subject, 'subject')
    extendedMetadata = rdfMultiple(HSTERMS.extendedMetadata, range_type=SCHEMA.HSExtendedMetadata)

class HSExtendedMetadata(rdfSubject):
    rdf_type = SCHEMA.HSExtendedMetadata
    key = rdfSingle(HSTERMS.key, 'key')
    value = rdfSingle(HSTERMS.value, 'value')

mapper(HSResource, HSExtendedMetadata)

#graph = Graph().parse('resource.ttl', format='turtle')
#with open('resourcesc.xml', 'wb') as f:
#    f.write(graph.serialize(format='application/rdf+xml'))
graph = Graph().parse('test_resource_metadata_files/resourcemetadata.xml', format='application/rdf+xml')
with open('loaded_resourcemetadata.ttl', 'wb') as f:
    f.write(graph.serialize(format='turtle'))

rdfSubject.db = graph

res = next(HSResource.ClassInstances())
for em in res.extendedMetadata:
    print(em.key)
    em.key = em.key + ' changed'

for em in res.extendedMetadata:
    print(em.key)

with open('updated.ttl', 'wb') as f:
    rdfSubject.db.serialize(format='turtle')
