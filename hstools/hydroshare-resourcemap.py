import os

from rdflib import URIRef

from rdflib.namespace import Namespace
from orm_shacl.shacl_class_generator import generate_classes

ORE = Namespace("http://www.openarchives.org/ore/terms/")


def retrieve_and_parse(url, schema):
    import requests

    session = requests.Session()
    session.auth = ('sblack', 'j1u2n3o4')

    metadata = session.request('GET', url, allow_redirects=True)

    try:
        with open("retrieved_metadata.xml", "wb") as f:
            f.write(metadata.content)
        schema.parse("retrieved_metadata.xml", file_format='xml')
    finally:
        pass
        os.remove("retrieved_metadata.xml")

    return schema

generate_classes('shacl/resourcemap.ttl', 'shacl/resource.ttl')

from hstools.generated_classes import ResourceMap, ResourceMetadata

resourcemap = retrieve_and_parse('https://dev-hs-1.cuahsi.org/hsapi/resource/9560c2b29497470bbc79bd6484db06e1/map/', ResourceMap())

resource = retrieve_and_parse(resourcemap.describes.is_documented_by, ResourceMetadata())
print(resource.title)
