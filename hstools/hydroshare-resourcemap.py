import os

from rdflib import URIRef

from rdflib.namespace import Namespace
from orm_shacl.shacl_class_generator import generate_classes

ORE = Namespace("http://www.openarchives.org/ore/terms/")

#generate_classes('shacl/resourcemap.ttl', 'shacl/resource.ttl')

from hstools.generated_classes import ResourceMap
resourcemap = ResourceMap()

resourcemap.parse('shacl/data/mapandmetadata.ttl', file_format='turtle')

resourcemap.title



