from rdflib import Graph

g = Graph().parse("shacl/data/resourcemap.xml", format='xml')
with open("shacl/data/resourcemap.ttl", "wb") as f:
    f.write(g.serialize(format='turtle'))


#g = Graph().parse("shacl/resource.ttl", format='turtle')
#with open("shacl/resource.xml", "wb") as f:
#    f.write(g.serialize(format='pretty-xml'))