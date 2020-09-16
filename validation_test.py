from subject import hydro_document

hd = hydro_document("ea93a49284204912be7fab054a9d41df")

# with open('resource.ttl', 'w') as f:
#     f.write(hd.document.get_turtle())

from rdflib import Graph
shacl_graph = Graph().parse("HSResource_SHACL.ttl", format='turtle')
#resource_graph = hd.document.graph
resource_graph = Graph().parse("resource.ttl", format='turtle')

from pyshacl import validate


r = validate(resource_graph, shacl_graph=shacl_graph, abort_on_error=True, debug=True)
conforms, results_graph, results_text = r
print(conforms)
