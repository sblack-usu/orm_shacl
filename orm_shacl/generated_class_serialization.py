import collections

from jinja2 import Template


metadata_template_str = '''\
from orm_shacl.rdf_orm_classes import AbstractRDFMetadata, RDFProperty
from rdflib import Namespace

{% for abbreviation, url in namespaces %}
{{ abbreviation }} = Namespace("{{ url }}"){% endfor %}

{% for schema in schemas %}
class {{ schema.name }}(AbstractRDFMetadata):
    _target_class = {{ schema.target_class }}
    {% for prop_name, data_type, path, max_count in schema.prop_parameters %}
    {{prop_name}} = RDFProperty(property_name="{{prop_name}}", data_type={{data_type}}, path={{path}}, max_count={{max_count}}){% endfor %}

{% endfor %}\
'''

Schema = collections.namedtuple('Schema', 'name target_class prop_parameters')


def generate_classes_from_schemas(namespaces, schemas):
    metadata_template = Template(metadata_template_str)
    with open("generated_classes.py", "w") as f:
        f.write(metadata_template.render(namespaces=namespaces, schemas=schemas))