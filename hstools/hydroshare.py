import os

from rdflib import URIRef

from orm_shacl.shacl_class_generator import generate_classes

shacl_filename = 'shacl/resource.ttl'
classes = generate_classes(shacl_filename)
res = classes['HSResource']()

import requests

session = requests.Session()
session.auth = ('sblack', 'password')

scimeta = session.request('GET', 'https://dev-hs-1.cuahsi.org/hsapi/scimeta/0da9f76234844c2094a2f598ecdf261d')

try:
    with open("retrieved_xml.xml", "wb") as f:
        f.write(scimeta.content)
    res.parse("retrieved_xml.xml", file_format='xml')
finally:
    os.remove("retrieved_xml.xml")

res.title = "hello"
res.description.abstract = "updated abstract with DescriptionShape"
res.subject = ['it', 'works', 'dude']
extended_metadata = classes['ExtendedMetadata']()
extended_metadata.key = "key1"
extended_metadata.value = 'value1'
extended_metadata2 = classes['ExtendedMetadata']()
extended_metadata2.key = "hello"
extended_metadata2.value = 'goodbye'
res.extended_metadata = [extended_metadata, extended_metadata2]
subject = URIRef("http://www.hydroshare.org/resource/0da9f76234844c2094a2f598ecdf261d")
updated_graph = res.serialize(subject=subject)

print(updated_graph.serialize(format="pretty-xml").decode())
session.request("POST",
                'https://dev-hs-1.cuahsi.org/hsapi/resource/0da9f76234844c2094a2f598ecdf261d/files/',
                files={'file': ('resourcemetadata.xml', updated_graph.serialize(format="xml"))})

