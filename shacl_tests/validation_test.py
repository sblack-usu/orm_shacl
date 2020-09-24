from subject import hydro_document

hd = hydro_document("ea93a49284204912be7fab054a9d41df")

# with open('resource.ttl', 'w') as f:
#     f.write(hd.document.get_turtle())

from rdflib import Graph
shacl_graph = Graph().parse("shacl_tests/HSResource_SHACL.ttl", format='turtle')
#resource_graph = hd.document.graph
resource_graph = Graph().parse("shacl_tests/resource.ttl", format='turtle')

from pyshacl import validate


r = validate(resource_graph, shacl_graph=shacl_graph, abort_on_error=False, debug=True)
conforms, results_graph, results_text = r

assert conforms

resource_graph = Graph().parse("shacl_tests/resource-bad.ttl", format='turtle')
r = validate(resource_graph, shacl_graph=shacl_graph, abort_on_error=False, debug=True)
conforms, results_graph, results_text = r

assert not conforms
#assert 'More than 1 values on [ hsterms:key Literal("another key"), Literal("key2") ; hsterms:value Literal("value2") ]->hsterms:key' in results_text
assert 'Less than 1 values on <http://www.hydroshare.org/resource/ea93a49284204912be7fab054a9d41df>->dc:title' in results_text
#assert 'Value Literal("fr") not in list [\'Literal("es")\', \'Literal("eng")\']' in results_text
#assert 'Less than 1 values on [ hsterms:key Literal("key") ]->hsterms:value' in results_text
