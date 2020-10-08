# orm-shacl
a python class object mapper with SHACL and rdflib.  Given a SHACL spec, create and modify an rdflib graph through python class properties which comply with the SHACL specification.

## Example:
#### HSResource_SHACL.ttl
```
@prefix schema: <http://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix hsterms: <http://hydroshare.org/terms/> .

schema:HSResourceShape
    a sh:NodeShape ;
    sh:targetClass hsterms:resource ;
    sh:name 'resource'
    sh:property [
        sh:path dc:title ;
        sh:datatype xsd:string ;
        sh:maxCount 1 ;
        sh:minCount 1 ;
    ] .
```
#### resource.ttl
```
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix hsterms: <http://hydroshare.org/terms/> .

<http://www.hydroshare.org/resource/ea93a49284204912be7fab054a9d41df>
    a hsterms:resource ;
    dc:title "00_ZemelWoodlandN_SiteModel" .
```
```python
from rdflib import Graph
from rdflib.namespace import DC
from orm_shacl.shacl_class_generator import generate_classes

# given the SHACL specification, generate python classes with the same structure
shacl_filename = 'HSResource_SHACL.ttl'
classes = generate_classes(shacl_filename)

# retrieve generated class by sh:name (in SHACL spec) and create instance
res = classes['resource']()

# set a property for the python class (correlates with sh:property on SHACL spec)
res.title = "new resource title"

# serialize resource to an rdflib Graph
g = res.serialize()

# print string serialization of graph
print(g.serialize().decode())

# create new python class for resource
res2 = classes['resource']()

# parse metadata from file
res2.parse('resource.ttl')

# access the data using the python class
print(res.title) # '00_ZemelWoodlandN_SiteModel'
```

