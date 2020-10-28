from orm_shacl.rdf_orm_classes import AbstractRDFMetadata, RDFProperty
from rdflib import Namespace


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


class FileMap(AbstractRDFMetadata):
    _target_class = ORE.Aggregation
    
    dc_type = RDFProperty(property_name="dc_type", data_type=XSD.string, path=DCTERMS.type, max_count=1)
    is_documented_by = RDFProperty(property_name="is_documented_by", data_type=XSD.string, path=CITOTERMS.isDocumentedBy, max_count=1)
    files = RDFProperty(property_name="files", data_type=XSD.string, path=ORE.aggregates, max_count=None)
    title = RDFProperty(property_name="title", data_type=XSD.string, path=DC.title, max_count=1)
    is_described_by = RDFProperty(property_name="is_described_by", data_type=XSD.string, path=ORE.isDescribedBy, max_count=1)


class Creator(AbstractRDFMetadata):
    _target_class = DC.creator
    
    email = RDFProperty(property_name="email", data_type=XSD.string, path=HSTERMS.email, max_count=1)
    organization = RDFProperty(property_name="organization", data_type=XSD.string, path=HSTERMS.organization, max_count=1)
    creator_order = RDFProperty(property_name="creator_order", data_type=XSD.integer, path=HSTERMS.creatorOrder, max_count=1)
    name = RDFProperty(property_name="name", data_type=XSD.string, path=HSTERMS.name, max_count=1)


class Contributor(AbstractRDFMetadata):
    _target_class = DC.contributor
    
    google_scholar_id = RDFProperty(property_name="google_scholar_id", data_type=XSD.string, path=HSTERMS.GoogleScholarID, max_count=1)
    research_gate_id = RDFProperty(property_name="research_gate_id", data_type=XSD.string, path=HSTERMS.ResearchGateID, max_count=1)
    phone = RDFProperty(property_name="phone", data_type=XSD.string, path=HSTERMS.phone, max_count=1)
    ORCID = RDFProperty(property_name="ORCID", data_type=XSD.string, path=HSTERMS.ORCID, max_count=1)
    address = RDFProperty(property_name="address", data_type=XSD.string, path=HSTERMS.address, max_count=1)
    organization = RDFProperty(property_name="organization", data_type=XSD.string, path=HSTERMS.organization, max_count=1)
    email = RDFProperty(property_name="email", data_type=XSD.string, path=HSTERMS.email, max_count=1)
    homepage = RDFProperty(property_name="homepage", data_type=XSD.string, path=HSTERMS.homepage, max_count=1)


class Rights(AbstractRDFMetadata):
    _target_class = DC.rights
    
    rights_statement = RDFProperty(property_name="rights_statement", data_type=XSD.string, path=HSTERMS.rightsStatement, max_count=1)
    url = RDFProperty(property_name="url", data_type=XSD.string, path=HSTERMS.URL, max_count=1)


class AwardInfo(AbstractRDFMetadata):
    _target_class = HSTERMS.awardInfo
    
    funding_agency_name = RDFProperty(property_name="funding_agency_name", data_type=XSD.string, path=HSTERMS.fundingAgencyName, max_count=1)
    award_title = RDFProperty(property_name="award_title", data_type=XSD.string, path=HSTERMS.awardTitle, max_count=1)
    award_number = RDFProperty(property_name="award_number", data_type=XSD.string, path=HSTERMS.awardNumber, max_count=1)
    funding_agency_url = RDFProperty(property_name="funding_agency_url", data_type=XSD.string, path=HSTERMS.fundingAgencyURL, max_count=1)


class DCType(AbstractRDFMetadata):
    _target_class = DC.type
    
    is_defined_by = RDFProperty(property_name="is_defined_by", data_type=XSD.string, path=RDFS.isDefinedBy, max_count=1)
    label = RDFProperty(property_name="label", data_type=XSD.string, path=RDFS.label, max_count=1)


class Date(AbstractRDFMetadata):
    _target_class = DC.date
    
    type = RDFProperty(property_name="type", data_type=XSD.string, path=RDF.type, max_count=1)
    value = RDFProperty(property_name="value", data_type=XSD.string, path=RDF.value, max_count=1)


class Source(AbstractRDFMetadata):
    _target_class = DC.source
    
    is_derived_from = RDFProperty(property_name="is_derived_from", data_type=XSD.string, path=HSTERMS.isDerivedFrom, max_count=1)


class Relation(AbstractRDFMetadata):
    _target_class = DC.relation
    
    is_copied_from = RDFProperty(property_name="is_copied_from", data_type=XSD.string, path=HSTERMS.isCopiedFrom, max_count=1)
    is_part_of = RDFProperty(property_name="is_part_of", data_type=XSD.string, path=HSTERMS.isPartOf, max_count=1)


class Description(AbstractRDFMetadata):
    _target_class = DC.description
    
    abstract = RDFProperty(property_name="abstract", data_type=XSD.string, path=DCTERMS.abstract, max_count=1)


class Coverage(AbstractRDFMetadata):
    _target_class = DC.coverage
    
    value = RDFProperty(property_name="value", data_type=XSD.string, path=RDF.value, max_count=1)
    type = RDFProperty(property_name="type", data_type=XSD.string, path=RDF.type, max_count=1)


class Identifier(AbstractRDFMetadata):
    _target_class = DC.identifier
    
    hydroshare_identifier = RDFProperty(property_name="hydroshare_identifier", data_type=XSD.string, path=HSTERMS.hydroShareIdentifier, max_count=1)


class ExtendedMetadata(AbstractRDFMetadata):
    _target_class = HSTERMS.extendedMetadata
    
    value = RDFProperty(property_name="value", data_type=XSD.string, path=HSTERMS.value, max_count=1)
    key = RDFProperty(property_name="key", data_type=XSD.string, path=HSTERMS.key, max_count=1)


class CellInformation(AbstractRDFMetadata):
    _target_class = HSTERMS.CellInformation
    
    columns = RDFProperty(property_name="columns", data_type=XSD.string, path=HSTERMS.columns, max_count=1)
    rows = RDFProperty(property_name="rows", data_type=XSD.string, path=HSTERMS.rows, max_count=1)
    name = RDFProperty(property_name="name", data_type=XSD.string, path=HSTERMS.name, max_count=1)
    cell_size_x_value = RDFProperty(property_name="cell_size_x_value", data_type=XSD.string, path=HSTERMS.cellSizeXValue, max_count=1)
    cell_data_type = RDFProperty(property_name="cell_data_type", data_type=XSD.string, path=HSTERMS.cellDataType, max_count=1)
    cell_size_y_value = RDFProperty(property_name="cell_size_y_value", data_type=XSD.string, path=HSTERMS.cellSizeYValue, max_count=1)


class BandInformation(AbstractRDFMetadata):
    _target_class = HSTERMS.BandInformation
    
    no_data_value = RDFProperty(property_name="no_data_value", data_type=XSD.string, path=HSTERMS.noDataValue, max_count=1)
    variable_unit = RDFProperty(property_name="variable_unit", data_type=XSD.string, path=HSTERMS.variableUnit, max_count=1)
    maximum_value = RDFProperty(property_name="maximum_value", data_type=XSD.string, path=HSTERMS.maximumValue, max_count=None)
    comment = RDFProperty(property_name="comment", data_type=XSD.string, path=HSTERMS.comment, max_count=1)
    method = RDFProperty(property_name="method", data_type=XSD.string, path=HSTERMS.method, max_count=1)
    minimum_value = RDFProperty(property_name="minimum_value", data_type=XSD.string, path=HSTERMS.minimumValue, max_count=None)
    variable_name = RDFProperty(property_name="variable_name", data_type=XSD.string, path=HSTERMS.variableName, max_count=1)
    name = RDFProperty(property_name="name", data_type=XSD.string, path=HSTERMS.name, max_count=1)


class ResourceMap(AbstractRDFMetadata):
    _target_class = ORE.ResourceMap
    
    describes = RDFProperty(property_name="describes", data_type=FileMap, path=ORE.describes, max_count=1)
    identifier = RDFProperty(property_name="identifier", data_type=XSD.string, path=DC.identifier, max_count=1)
    modified = RDFProperty(property_name="modified", data_type=XSD.string, path=DCTERMS.modified, max_count=1)
    creator = RDFProperty(property_name="creator", data_type=XSD.string, path=DC.creator, max_count=1)
    format = RDFProperty(property_name="format", data_type=XSD.string, path=DC.format, max_count=1)
    created = RDFProperty(property_name="created", data_type=XSD.string, path=DCTERMS.created, max_count=1)


class GeographicRaster(AbstractRDFMetadata):
    _target_class = HSTERMS.geographicRaster
    
    band_information = RDFProperty(property_name="band_information", data_type=XSD.string, path=HSTERMS.BandInformation, max_count=None)
    title = RDFProperty(property_name="title", data_type=XSD.string, path=DC.title, max_count=1)
    spatial_reference = RDFProperty(property_name="spatial_reference", data_type=XSD.string, path=HSTERMS.spatialReference, max_count=None)
    coverage = RDFProperty(property_name="coverage", data_type=Coverage, path=DC.coverage, max_count=None)
    subject = RDFProperty(property_name="subject", data_type=XSD.string, path=DC.subject, max_count=None)
    extended_metadata = RDFProperty(property_name="extended_metadata", data_type=ExtendedMetadata, path=HSTERMS.extendedMetadata, max_count=None)
    rights = RDFProperty(property_name="rights", data_type=Rights, path=DC.rights, max_count=None)
    cell_information = RDFProperty(property_name="cell_information", data_type=XSD.string, path=HSTERMS.CellInformation, max_count=None)


class ResourceMetadata(AbstractRDFMetadata):
    _target_class = HSTERMS.resource
    
    identifier = RDFProperty(property_name="identifier", data_type=Identifier, path=DC.identifier, max_count=1)
    language = RDFProperty(property_name="language", data_type=XSD.string, path=DC.language, max_count=1)
    source = RDFProperty(property_name="source", data_type=Source, path=DC.source, max_count=None)
    subject = RDFProperty(property_name="subject", data_type=XSD.string, path=DC.subject, max_count=None)
    description = RDFProperty(property_name="description", data_type=Description, path=DC.description, max_count=1)
    relation = RDFProperty(property_name="relation", data_type=Relation, path=DC.relation, max_count=None)
    date = RDFProperty(property_name="date", data_type=Date, path=DC.date, max_count=None)
    title = RDFProperty(property_name="title", data_type=XSD.string, path=DC.title, max_count=1)
    extended_metadata = RDFProperty(property_name="extended_metadata", data_type=ExtendedMetadata, path=HSTERMS.extendedMetadata, max_count=None)
    rights = RDFProperty(property_name="rights", data_type=Rights, path=DC.rights, max_count=None)
    award_info = RDFProperty(property_name="award_info", data_type=AwardInfo, path=HSTERMS.awardInfo, max_count=None)
    creator = RDFProperty(property_name="creator", data_type=Creator, path=DC.creator, max_count=None)
    dc_type = RDFProperty(property_name="dc_type", data_type=DCType, path=DC.type, max_count=1)
    coverage = RDFProperty(property_name="coverage", data_type=Coverage, path=DC.coverage, max_count=None)
    contributor = RDFProperty(property_name="contributor", data_type=Contributor, path=DC.contributor, max_count=None)



schemas_by_target_class = {

ORE.Aggregation: FileMap,
DC.creator: Creator,
DC.contributor: Contributor,
DC.rights: Rights,
HSTERMS.awardInfo: AwardInfo,
DC.type: DCType,
DC.date: Date,
DC.source: Source,
DC.relation: Relation,
DC.description: Description,
DC.coverage: Coverage,
DC.identifier: Identifier,
HSTERMS.extendedMetadata: ExtendedMetadata,
HSTERMS.CellInformation: CellInformation,
HSTERMS.BandInformation: BandInformation,
ORE.ResourceMap: ResourceMap,
HSTERMS.geographicRaster: GeographicRaster,
HSTERMS.resource: ResourceMetadata,
}