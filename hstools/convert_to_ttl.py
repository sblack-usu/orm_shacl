from rdflib import Graph

#g = Graph().parse("retrieved_xml.xml", format='xml')
#with open("retrieved_xml.ttl", "wb") as f:
#    f.write(g.serialize(format='turtle'))


#g = Graph().parse("shacl/resource.ttl", format='turtle')
#with open("shacl/resource.xml", "wb") as f:
#    f.write(g.serialize(format='pretty-xml'))

g = Graph().parse("shacl/data/resourcemetadata.ttl", format='turtle')
with open("shacl/data/resourcemetadata.json", "wb") as f:
    f.write(g.serialize(format='json-ld', context=dict(g.namespaces())))