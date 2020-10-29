import uuid
from datetime import datetime
from typing import List

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


class RDFBaseModel(BaseModel):

    rdf_subject: Literal = Field(default_factory=BNode)
    rdf_type: URIRef = None

    @classmethod
    def _rdf_fields(cls):
        for f in cls.__fields__.values():
            if f.alias not in ['rdf_subject', 'rdf_type']:
                yield f

    def rdf(self, graph):
        for f in self._rdf_fields():
            predicate = f.field_info.extra['rdf_predicate']
            values = getattr(self, f.name, Undefined)
            if values is not Undefined:
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    if isinstance(value, RDFBaseModel):
                        graph.add((self.rdf_subject, predicate, value.rdf_subject))
                        graph = value.rdf(graph)
                    else:
                        value = Literal(value)
                        graph.add((self.rdf_subject, predicate, value))
        if self.rdf_type:
            graph.add((self.rdf_subject, RDF.type, self.rdf_type))
        return graph

    def rdf_string(self, rdf_format='ttl'):
        g = Graph()
        return self.rdf(g).serialize(format=rdf_format).decode()

    @classmethod
    def parse(cls, metadata_graph, subject):
        kwargs = {'rdf_subject': subject}
        for f in cls._rdf_fields():
            predicate = f.field_info.extra['rdf_predicate']
            parsed = []
            for value in metadata_graph.objects(subject=subject, predicate=predicate):
                if metadata_graph.value(subject=value):
                    if f.sub_fields:
                        clazz = f.sub_fields[0].outer_type_
                    else:
                        clazz = f.outer_type_
                    parsed.append(clazz.parse(metadata_graph, value))
                else:
                    parsed.append(value.value)
            if len(parsed) > 0:
                if f.sub_fields:
                    kwargs[f.name] = parsed
                else:
                    kwargs[f.name] = parsed[0]
        return cls(**kwargs)


class Date(RDFBaseModel):
    type: str = Field(rdf_predicate=RDF.type)
    value: datetime = Field(rdf_predicate=RDF.value)


def hs_uid():
    return getattr(HSRESOURCE, uuid.uuid4().hex)

class ResourceMetadata(RDFBaseModel):
    rdf_subject: URIRef = Field(default_factory=hs_uid)
    rdf_type: URIRef = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.resource)

    title: str = Field(rdf_predicate=DC.title)
    description: str = Field(rdf_predicate=DC.description)
    dates: List[Date] = Field(rdf_predicate=DC.date)
    subjects: List[str] = Field(rdf_predicate=DC.subject)

created = Date(type='created', value=datetime.now())
modified = Date(type='modified', value=datetime.now())
res = ResourceMetadata(title="default",
                       description="default description",
                       dates=[created, modified],
                       subjects=['s1', 's2', 's3'])
res.description = "a description"
res.title = "a title"
res.dates[0].value = datetime.now()
print(res.rdf_string('turtle'))

g = res.rdf(Graph())
for t in g.triples((None, None, None)):
    print(t)

new_res = ResourceMetadata.parse(g, res.rdf_subject)
print(new_res.title)
print(new_res.rdf_string('turtle'))



