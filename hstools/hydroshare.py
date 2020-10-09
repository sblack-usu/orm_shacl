import os

from rdflib import URIRef

from orm_shacl.shacl_class_generator import root_class

shacl_filename = 'shacl/resource.ttl'
Resource = root_class(shacl_filename)
res = Resource()

import requests

session = requests.Session()
session.auth = ('sblack', 'password')

scimeta = session.request('GET', 'https://dev-hs-1.cuahsi.org/hsapi/scimeta/8b38ae4d89894c1987504f5beb9b49b8')

try:
    with open("retrieved_xml.xml", "wb") as f:
        f.write(scimeta.content)
    res.parse("retrieved_xml.xml", file_format='xml')
finally:
    os.remove("retrieved_xml.xml")

res.title = "a boring title"
res.description.abstract = "updated abstract"
res.subject = ['it', 'works', 'dude']
subject = URIRef("http://www.hydroshare.org/resource/8b38ae4d89894c1987504f5beb9b49b8")
updated_graph = res.serialize(subject=subject)

session.request("POST",
                'https://dev-hs-1.cuahsi.org/hsapi/resource/8b38ae4d89894c1987504f5beb9b49b8/files/',
                files={'resourcemetadata.xml': updated_graph.serialize(format="xml")})

