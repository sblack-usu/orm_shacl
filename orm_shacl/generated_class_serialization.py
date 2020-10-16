from jinja2 import Template

'''
from rdf_orm_classes import AbstractRDFMetadata, RDFProperty
from rdflib import Namespace, DC, XSD

HSTERMS = Namespace("http://www.hydroshare.org/terms/")

class HSResource(AbstractRDFMetadata):
    _target_class = HSTERMS.resource
    title = RDFProperty(property_name="title", 
                        data_type=XSD.string, 
                        path=DC.title, 
                        max_count=1)
    ...
'''

metadata_template_str = '''\
from rdf_orm_classes import AbstractRDFMetadata, RDFProperty
from rdflib import Namespace

{% for abbreviation, url in namespaces %}
{{ abbreviation }} = Namespace("{{ url }}"){% endfor %}

{% for schema in schemas %}
class {{ schema.name }}(AbstractRDFMetadata):
    _target_class = {{ schema.target_class }}
    {% for prop_name, data_type, path, max_count in schema.prop_parameters %}
    {{prop_name}} = RDFProperty(property_name={{prop_name}}, data_type={{data_type}}, path={{path}}, max_count={{max_count}}){% endfor %}

{% endfor %}\
'''
metadata_template = Template(metadata_template_str)

import collections

Schema = collections.namedtuple('Schema', 'name target_class prop_parameters')
schema1 = Schema(name="HSResource", target_class='hsterms:resource',
                 prop_parameters=(('title', 'XSD.string', 'DC.title', '1'),
                                  ('subject', 'XSD.string', 'DC.subject', 'None')))
schema2 = Schema(name="ExtendedMetadata", target_class='hsterms:extendedMetadata',
                 prop_parameters=(('key', 'XSD.string', 'HSTERMS.key', '1'),
                                  ('value', 'XSD.string', 'HSTERMS.value', '1')))
# name - schema identifier
# target_class - sh:targetClass
# prop_name - sh:name
# data_type - sh:datatype
# path - sh:path
# max_count - sh:maxCount
print(metadata_template.render(namespaces=(('DC', 'http://dcblar.com'),
                                           ('XSD', 'http://XSD.com')
                                           ),
                               schemas=(schema1, schema2)
                               )
      )