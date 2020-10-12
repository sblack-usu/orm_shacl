from rdflib import Graph

#g = Graph().parse("resourcemetadata.xml", format='xml')
#with open("resourcemetadata.ttl", "wb") as f:
#    f.write(g.serialize(format='turtle'))


g = Graph().parse("shacl/resource.ttl", format='turtle')

with open("shacl/resource.xml", "wb") as f:
    f.write(g.serialize(format='xml'))