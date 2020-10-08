
from orm_shacl.shacl_class_generator import root_class

shacl_filename = 'shacl/resource.ttl'
Resource = root_class(shacl_filename)
res = Resource()

import requests

session = requests.Session()
session.auth = ('sblack', 'password')

scimeta = session.request('GET', 'https://dev-hs-1.cuahsi.org/hsapi/scimeta/8b38ae4d89894c1987504f5beb9b49b8')

with open("resourcemetadata.xml", "wb") as f:
    f.write(scimeta.content)

res.parse("resourcemetadata.xml", file_format='xml')

print(res.title)