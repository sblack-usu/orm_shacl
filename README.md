# orm-shacl
a python class object mapper with SHACL and rdflib

## Example:
```python
metadata_graph = Graph().parse('data/resource.ttl', format='turtle')
shacl_graph = Graph().parse('data/HSResource_SHACL.ttl', format='turtle')
res = RDFMetadata(shacl_graph, metadata_graph)

print(res.title) # '00_ZemelWoodlandN_SiteModel'
print(str(next(res._metadata_graph.objects(subject=None, predicate=DC.title)))) # '00_ZemelWoodlandN_SiteModel'

res.title = "modified title"

print(res.title) # 'modified title'
print(str(next(res._metadata_graph.objects(subject=None, predicate=DC.title)))) # 'modified title'
```
#### data/HSResource_SHACL.ttl
```
@prefix schema: <http://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix hsterms: <http://hydroshare.org/terms/> .

schema:HSResourceShape
    a sh:NodeShape ;
    sh:targetClass hsterms:resource ;
    sh:property [
        sh:path dc:title ;
        sh:datatype xsd:string ;
        sh:maxCount 1 ;
        sh:minCount 1 ;
    ] .
```
#### data/resource.ttl
```
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix hsterms: <http://hydroshare.org/terms/> .

<http://www.hydroshare.org/resource/ea93a49284204912be7fab054a9d41df>
    a hsterms:resource ;
    dc:title "00_ZemelWoodlandN_SiteModel" .
```
