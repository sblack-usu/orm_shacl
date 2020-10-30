import uuid
from datetime import datetime
from typing import List

from pydantic.fields import Undefined
from rdflib import Namespace, Graph, BNode, URIRef, Literal
from rdflib.term import Identifier as RDFIdentifier
from pydantic import BaseModel, Field, AnyUrl, HttpUrl

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

    rdf_subject: RDFIdentifier = Field(default_factory=BNode)
    rdf_type: URIRef = None

    @classmethod
    def _rdf_fields(cls):
        for f in cls.__fields__.values():
            if f.alias not in ['rdf_subject', 'rdf_type']:
                yield f

    @classmethod
    def class_rdf_type(cls):
        return cls.__fields__['rdf_type'].default

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
                        if value:
                            value = Literal(value)
                            graph.add((self.rdf_subject, predicate, value))
        if self.rdf_type:
            graph.add((self.rdf_subject, RDF.type, self.rdf_type))
        return graph

    def rdf_string(self, rdf_format='ttl'):
        g = Graph()
        return self.rdf(g).serialize(format=rdf_format).decode()

    @classmethod
    def parse_file(cls, file, file_format='ttl', subject=None):
        metadata_graph = Graph().parse(file, format=file_format)
        return cls.parse(metadata_graph, subject)

    @classmethod
    def parse(cls, metadata_graph, subject=None):
        if not subject:
            target_class = cls.class_rdf_type()
            subject = metadata_graph.value(predicate=RDF.type, object=target_class)
            if not subject:
                raise Exception("Could not find subject for predicate=RDF.type, object={}".format(target_class))
        if not isinstance(subject, RDFIdentifier):
            subject = URIRef(subject)
        kwargs = {'rdf_subject': subject}
        for f in cls._rdf_fields():
            predicate = f.field_info.extra['rdf_predicate']
            parsed = []
            for value in metadata_graph.objects(subject=subject, predicate=predicate):
                if isinstance(value, BNode):
                    if f.sub_fields:
                        clazz = f.sub_fields[0].outer_type_
                    else:
                        clazz = f.outer_type_
                    parsed.append(clazz.parse(metadata_graph, value))
                else:
                    parsed.append(str(value))
            if len(parsed) > 0:
                if f.sub_fields:
                    kwargs[f.name] = parsed
                else:
                    kwargs[f.name] = parsed[0]
        return cls(**kwargs)


class DCType(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.type)

    is_defined_by: AnyUrl = Field(rdf_predicate=RDFS.isDefinedBy)
    label: str = Field(rdf_predicate=RDFS.label)


class Source(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.source)

    is_derived_from: AnyUrl = Field(rdf_predicate=HSTERMS.isDerivedFrom)


class Relation(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.relation)

    is_copied_from: AnyUrl = Field(rdf_predicate=HSTERMS.isCopiedFrom, default=None)
    is_part_of: AnyUrl = Field(rdf_predicate=HSTERMS.isPartOf, default=None)


class Description(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.Description)

    abstract: str = Field(rdf_predicate=DCTERMS.abstract)


class Coverage(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.coverage)

    value: str = Field(rdf_predicate=RDF.value)
    type: str = Field(rdf_predicate=RDF.type)


class Identifier(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.identifier)

    hydroshare_identifier: AnyUrl = Field(rdf_predicate=HSTERMS.hydroShareIdentifier)


class ExtendedMetadata(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.extendedMetadata)

    value: str = Field(rdf_predicate=HSTERMS.value)
    key: str = Field(rdf_predicate=HSTERMS.key)


class CellInformation(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.CellInformation)

    columns: str = Field(rdf_predicate=HSTERMS.columns)
    rows: str = Field(rdf_predicate=HSTERMS.rows)
    name: str = Field(rdf_predicate=HSTERMS.name)
    cell_size_x_value: str = Field(rdf_predicate=HSTERMS.cellSizeXValue)
    cell_data_type: str = Field(rdf_predicate=HSTERMS.cellDataType)
    cell_size_y_value: str = Field(rdf_predicate=HSTERMS.cellSizeYValue)


class Date(RDFBaseModel):
    type: AnyUrl = Field(rdf_predicate=RDF.type)
    value: datetime = Field(rdf_predicate=RDF.value)


class Rights(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.rights)

    rights_statement: str = Field(rdf_predicate=HSTERMS.rightsStatement)
    url: AnyUrl = Field(rdf_predicate=HSTERMS.URL)


class Creator(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.creator)

    email: str = Field(rdf_predicate=HSTERMS.email, default=None)
    organization: str = Field(rdf_predicate=HSTERMS.organization, default=None)
    creator_order: int = Field(rdf_predicate=HSTERMS.creatorOrder, default=None)
    name: str = Field(rdf_predicate=HSTERMS.name, default=None)


class Contributor(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=DC.contributor)

    google_scholar_id: str = Field(rdf_predicate=HSTERMS.GoogleScholarID, default=None)
    research_gate_id: str = Field(rdf_predicate=HSTERMS.ResearchGateID, default=None)
    phone: str = Field(rdf_predicate=HSTERMS.phone, default=None)
    ORCID: str = Field(rdf_predicate=HSTERMS.ORCID, default=None)
    address: str = Field(rdf_predicate=HSTERMS.address, default=None)
    organization: str = Field(rdf_predicate=HSTERMS.organization, default=None)
    email: str = Field(rdf_predicate=HSTERMS.email, default=None)
    homepage: HttpUrl = Field(rdf_predicate=HSTERMS.homepage, default=None)


class AwardInfo(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.awardInfo)

    funding_agency_name: str = Field(rdf_predicate=HSTERMS.fundingAgencyName)
    award_title: str = Field(rdf_predicate=HSTERMS.awardTitle)
    award_number: str = Field(rdf_predicate=HSTERMS.awardNumber)
    funding_agency_url: HttpUrl = Field(rdf_predicate=HSTERMS.fundingAgencyURL)


class BandInformation(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.BandInformation)

    no_data_value: str = Field(rdf_predicate=HSTERMS.noDataValue)
    variable_unit: str = Field(rdf_predicate=HSTERMS.variableUnit)
    maximum_value: List[str] = Field(rdf_predicate=HSTERMS.maximumValue)
    comment: str = Field(rdf_predicate=HSTERMS.comment)
    method: str = Field(rdf_predicate=HSTERMS.method)
    minimum_value: List[str] = Field(rdf_predicate=HSTERMS.minimumValue)
    variable_name: str = Field(rdf_predicate=HSTERMS.variableName)
    name: str = Field(rdf_predicate=HSTERMS.name)


def hs_uid():
    return getattr(HSRESOURCE, uuid.uuid4().hex)

class ResourceMetadata(RDFBaseModel):
    rdf_subject: RDFIdentifier = Field(default_factory=hs_uid)
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.resource)

    identifier: Identifier = Field(rdf_predicate=DC.identifier)
    language: str = Field(rdf_predicate=DC.language)
    source: List[Source] = Field(rdf_predicate=DC.source)
    relation: List[Relation] = Field(rdf_predicate=DC.relation)
    extended_metadata: List[ExtendedMetadata] = Field(rdf_predicate=HSTERMS.extendedMetadata)
    rights: List[Rights] = Field(rdf_predicate=DC.rights)
    title: str = Field(rdf_predicate=DC.title)
    description: Description = Field(rdf_predicate=DC.description)
    dates: List[Date] = Field(rdf_predicate=DC.date)
    subjects: List[str] = Field(rdf_predicate=DC.subject)
    award_info: List[AwardInfo] = Field(rdf_predicate=HSTERMS.awardInfo)
    creator: List[Creator] = Field(rdf_predicate=DC.creator)
    dc_type: DCType = Field(rdf_predicate=DC.type)
    coverage: List[Coverage] = Field(rdf_predicate=DC.coverage)
    contributor: List[Contributor] = Field(rdf_predicate=DC.contributor)


class FileMap(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=ORE.Aggregation)

    dc_type: str = Field(rdf_predicate=DCTERMS.type)
    is_documented_by: AnyUrl = Field(rdf_predicate=CITOTERMS.isDocumentedBy)
    files: List[AnyUrl] = Field(rdf_predicate=ORE.aggregates)
    title: str = Field(rdf_predicate=DC.title)
    is_described_by: AnyUrl = Field(rdf_predicate=ORE.isDescribedBy)


class ResourceMap(RDFBaseModel):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=ORE.ResourceMap)

    describes: str = Field(rdf_predicate=ORE.describes)
    identifier: str = Field(rdf_predicate=DC.identifier)
    modified: datetime = Field(rdf_predicate=DCTERMS.modified)
    creator: str = Field(rdf_predicate=DC.creator)




