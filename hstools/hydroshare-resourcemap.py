import os

from rdflib import URIRef
from rdflib.namespace import Namespace

from orm_shacl.shacl_class_generator import generate_classes

ORE = Namespace("http://www.openarchives.org/ore/terms/")

shacl_filename = 'shacl/resourcemap.ttl'
classes = generate_classes(shacl_filename)
filemap = classes['ResourceMap']()

filemap.parse('shacl/data/resourcemap.ttl', file_format='turtle')

filemap.title

subject = URIRef("http://www.hydroshare.org/resource/0da9f76234844c2094a2f598ecdf261d")
updated_graph = filemap.serialize(subject=subject)


