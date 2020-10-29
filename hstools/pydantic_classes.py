from datetime import datetime

from marshmallow import Schema, fields
from pydantic.fields import Undefined
from rdflib import Namespace, Graph, BNode, URIRef, Literal
from pydantic import BaseModel, Field

HSRESOURCE = Namespace("http://www.hydroshare.org/resource/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
RDFS1 = Namespace("http://www.w3.org/2001/01/rdf-schema#")
SCHEMA = Namespace("http://schema.org/")
HSTERMS = Namespace("http://hydroshare.org/terms/")
XML = Namespace("http://www.w3.org/XML/1998/namespace")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
CITOTERMS = Namespace("http://purl.org/spar/cito/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
SH = Namespace("http://www.w3.org/ns/shacl#")
ORE = Namespace("http://www.openarchives.org/ore/terms/")
HSUSER = Namespace("http://www.hydroshare.org/user/")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DASH = Namespace("http://datashapes.org/dash#")


#class Date(Schema):
#    value = fields.DateTime(predicate=RDF.value)
#    type = fields.

class RDFBaseModel(BaseModel):
    def rdf(self, graph, subject=BNode()):
        for f in self.__fields__.values():
            predicate = f.field_info.extra['rdf_predicate']
            predicate = URIRef(predicate)
            val = getattr(self, f.name, Undefined)
            if val is not Undefined:
                if isinstance(val, RDFBaseModel):
                    sub = BNode()
                    graph.add((subject, predicate, sub))
                    graph = val.rdf(graph, sub)
                else:
                    val = Literal(val)
                    graph.add((subject, predicate, val))
        return graph

    def rdf_string(self, subject=BNode(), rdf_format='ttl'):
        g = Graph()
        return self.rdf(g, subject).serialize(format=rdf_format).decode()

    @classmethod
    def parse(cls, metadata_graph, subject):
        kwargs = {}
        for f in cls.__fields__.values():
            predicate = f.field_info.extra['rdf_predicate']
            val = metadata_graph.value(subject=subject, predicate=predicate)
            if metadata_graph.value(subject=val):
                kwargs[f.name] = f.outer_type_.parse(metadata_graph, val)
            else:
                kwargs[f.name] = val.value
        return cls(**kwargs)


class Date(RDFBaseModel):
    type: str = Field(rdf_predicate=RDF.type)
    value: datetime = Field(rdf_predicate=RDF.value)

class HydroShareResource(RDFBaseModel):
    title: str = Field(rdf_predicate=DC.title)
    description: str = Field(rdf_predicate=DC.description)
    date: Date = Field(rdf_predicate=DC.date)

date = Date(type='created', value=datetime.now())
res = HydroShareResource(title="default", description="default description", date=date)
res.description = "a description"
res.title = "a title"
res.date.value = datetime.now()


g = res.rdf(Graph(), HSRESOURCE.ab3234)

new_res = HydroShareResource.parse(g, HSRESOURCE.ab3234)
print(new_res.title)
print(new_res.date.value)

print(res.rdf_string(HSRESOURCE.ab3234, 'turtle'))

#res.parse(g, subject)
#print(res.description)
#print(res.title)


