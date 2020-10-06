from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, SH, XSD

from rdf_metadata_properties import to_datatype, from_datatype

HSTERMS = Namespace("http://hydroshare.org/terms/")


class RDFProperty:
    '''
    A property to allow us to do validation at assignment
    '''
    def __init__(self, property_name, path, data_type, max_count=None, min_count=None):
        '''
        :param property_name: The name of the property
        '''
        self.property_name = property_name
        self.private_property = "_" + property_name
        self.path = path
        self.data_type = data_type
        self.max_count = max_count
        self.min_count = min_count

    def __get__(self, instance, owner):
        if instance is None:
            # returning self allows us to store property parsing data and logic on the descriptor
            return self
        return getattr(instance, self.private_property)

    def __set__(self, instance, value):
        return setattr(instance, self.private_property, value)

    def __delete__(self, instance):
        setattr(instance, self.private_property, None)

    def parse(self, metadata_graph, subject):
        """
        Using property information stored within this class descriptor,
        parse this property's value from the metadata graph
        :param metadata_graph: an rdflib Graph
        :param subject: the subject in the metadata graph to parse
        :return: the value of this property in the metadata_graph
        """
        values = []
        if str(self.data_type).startswith(str(XSD)):
            values = [from_datatype(prop_value, self.data_type)
                      for prop_value in
                      metadata_graph.objects(subject=subject, predicate=self.path)]
        else:
            for nested_subject in metadata_graph.objects(subject=subject, predicate=self.path):
                val = self.data_type(metadata_graph, nested_subject)
                values.append(val)

        if self.max_count == Literal(1):
            return values[0]
        else:
            return values


class AbstractRDFMetadata:
    _target_class = None

    def __init__(self, metadata_graph, root_subject=None):
        if not root_subject:
            root_subject = metadata_graph.value(predicate=RDF.type, object=self._target_class)
        props = self._public_properties()
        for property_name in props:
            # we can grab the descriptor because __get__ returns itself when accessed from the class
            prop_descriptor = getattr(type(self), property_name)
            if not prop_descriptor:
                raise Exception("{} is not a RDFProperty or RDFProperty got screwed up")
            property_value = prop_descriptor.parse(metadata_graph, root_subject)
            setattr(self, property_name, property_value)

    def _public_properties(self):
        names = []
        for name in dir(self):
            if not name.startswith('_'):
                names.append(name)
        return names


shacl_graph = Graph().parse('tests/data/HSResource_SHACL.ttl', format='turtle')

shape_by_targetClass = {}
property_by_path = {}

def nested_property(subject):
    for prop in shacl_graph.objects(subject=subject, predicate=SH.property):
        if shacl_graph.value(subject=prop, predicate=SH.targetClass):
            return True
    return False

def parse_class(subject):
    schema_name = shacl_graph.value(subject, SH.name)
    target_class = shacl_graph.value(subject, SH.targetClass)

    attributes = {}
    for prop in shacl_graph.objects(subject, SH.property):
        name = shacl_graph.value(prop, SH.name).value
        path = shacl_graph.value(prop, SH.path)
        max_count = shacl_graph.value(prop, SH.maxCount)
        min_count = shacl_graph.value(prop, SH.minCount)
        data_type = shacl_graph.value(prop, SH.datatype)
        if not data_type:
            # if data type is not provided, then it must be a nested class
            nested_target_class = shacl_graph.value(prop, SH.targetClass)
            if not nested_target_class:
                raise Exception("Could not find sh:datatype or sh:targetClass on {}".format(name))
            data_type = shape_by_targetClass[nested_target_class]
            if not data_type:
                raise Exception("Could not find a class definition for {}".format(nested_target_class))

        attributes[name] = RDFProperty(name, path, data_type, max_count, min_count)

    shape_class = type(schema_name, (AbstractRDFMetadata,), {'_target_class': target_class, **attributes})
    shape_by_targetClass[target_class] = shape_class

# this will have to be revisisted if we get more complicated than a single nesting
subjects = []
with_nested_subjects = []
for subject in shacl_graph.subjects(RDF.type, SH.NodeShape):
    if nested_property(subject):
        with_nested_subjects.append(subject)
    else:
        subjects.append(subject)

for subject in subjects:
    parse_class(subject)
for subject in with_nested_subjects:
    parse_class(subject)


metadata_graph = Graph().parse('tests/data/resource.ttl', format='turtle')

res_class = shape_by_targetClass[HSTERMS.resource]
res = res_class(metadata_graph)
print(dir(res))
print(res.title)
print(res.subject)
res.title = "changed"
print(res.title)
for em in res.extended_metadata:
    print(em.key)

print(res.coverage.box)
