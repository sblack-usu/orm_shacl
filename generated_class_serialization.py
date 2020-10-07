from jinja2 import Template


property_metadata_str = '''\
from rdf_orm_classes import RDFProperty

class {{ name }}(RDFProperty):
    
'''




metadata_template_str = '''\
from rdf_orm_classes import AbstractRDFMetadata

class {{ name }}(AbstractRDFMetadata):
    _target_class = {{ target_class }}
    {% for key, value in attributes.items() %}
    {{key}} = {{value}}
    {% endfor %}\
'''
metadata_template = Template(metadata_template_str)

print(metadata_template.render(name="Resource", target_class='hsterms:resource', attributes={'hello': 'goodbye'}))