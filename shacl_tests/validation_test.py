from rdflib import Graph

shacl_graph = Graph().parse("../hstools/shacl/resource.ttl", format='turtle')
for triple in shacl_graph.triples((None, None, None)):
    print(triple)
resource_graph = Graph().parse("resource.ttl", format='turtle')

from pyshacl import validate


r = validate(resource_graph, shacl_graph=shacl_graph, abort_on_error=False, debug=True)
conforms, results_graph, results_text = r

assert conforms

resource_graph = Graph().parse("resource-bad.ttl", format='turtle')
r = validate(resource_graph, shacl_graph=shacl_graph, abort_on_error=False, debug=True)
conforms, results_graph, results_text = r

assert not conforms
#assert 'More than 1 values on [ hsterms:key Literal("another key"), Literal("key2") ; hsterms:value Literal("value2") ]->hsterms:key' in results_text
assert 'Less than 1 values on <http://www.hydroshare.org/resource/ea93a49284204912be7fab054a9d41df>->dc:title' in results_text
#assert 'Value Literal("fr") not in list [\'Literal("es")\', \'Literal("eng")\']' in results_text
#assert 'Less than 1 values on [ hsterms:key Literal("key") ]->hsterms:value' in results_text
