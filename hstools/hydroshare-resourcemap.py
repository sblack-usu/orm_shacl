import os

from rdflib.namespace import Namespace

ORE = Namespace("http://www.openarchives.org/ore/terms/")


def retrieve_and_parse(url, schema):
    import requests

    session = requests.Session()
    session.auth = ('sblack', 'j1u2n3o4')

    metadata = session.request('GET', url, allow_redirects=True)

    try:
        with open("retrieved_metadata.xml", "wb") as f:
            f.write(metadata.content)
        instance = schema.parse_file("retrieved_metadata.xml", file_format='xml')
    finally:
        pass
        #os.remove("retrieved_metadata.xml")

    return instance

from hstools.pydantic_classes import ResourceMap, ResourceMetadata

resourcemap = retrieve_and_parse('https://dev-hs-1.cuahsi.org/hsapi/resource/9560c2b29497470bbc79bd6484db06e1/map/', ResourceMap)

resource = retrieve_and_parse(resourcemap.describes.is_documented_by, ResourceMetadata)
print(resource.title)
