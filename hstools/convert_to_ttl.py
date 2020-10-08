from rdflib import Graph

g = Graph().parse("resourcemetadata.xml", format='xml')

with open("resourcemetadata.ttl", "wb") as f:
    f.write(g.serialize(format='turtle'))