import os
import requests
import json

from rdflib import Graph

from hstools.generated_classes import ResourceMap, ResourceMetadata
from zope.interface import Interface, Attribute


class HydroShare:

    def __init__(self, username, password, base_url='https://dev-hs-1.cuahsi.org'):
        self._base_url = base_url
        self._session = requests.Session()
        self._session.auth = (username, password)

    def _get_and_parse(self, path, schema):
        url = "{}/{}".format(self._base_url, path)
        metadata = self._session.request('GET', url, allow_redirects=True)

        try:
            with open("retrieved_metadata.xml", "wb") as f:
                f.write(metadata.content)
            schema.parse("retrieved_metadata.xml", file_format='xml')
        finally:
            pass
            #os.remove("retrieved_metadata.xml")

        return schema

    def my_resources(self):
        url = "{}/hsapi/my-resources/".format(self._base_url)
        resp = self._session.request('GET', url)
        json_data = json.loads(resp.text)
        res_preview = ResourceSummary()
        for res_json in json_data['resources']:
            res_preview.id = res_json['id']
            res_preview.title = res_json['title']
            yield res_preview

    def print_my_resources(self):
        for res in self.my_resources():
            print(res)

    def retrieve(self, url, filename):
        resp = self._session.request('GET', url, allow_redirects=True)
        with open(filename, "wb") as f:
            f.write(resp.content)

    def retrieve_resource(self, map_url):
        map_filename = "resourcemap.xml"
        self.retrieve(map_url, map_filename)

        pass

    def search(self, **kwargs):
        pass


class Aggregation:

    def __init__(self, map):
        self._map = map
        self._metadata = metadata

    @property
    def files(self):
        return self._map.describes.files

    def aggregations(self):
        return self._map.describes.files

    @property
    def metadata(self):
        return self._metadata


map = ResourceMap()
map.parse('shacl/data/resourcemap.ttl')

metadata = ResourceMetadata()
metadata.parse('shacl/data/resourcemetadata.ttl')

resource = Aggregation(map, metadata)
print(resource.metadata.title)

#def convert_uri(uri):
#    import re
#    pattern = re.compile('(.*)/resource/([0-9a-f-]{32})/data/resourcemetadata')
#    match = pattern.match(uri)
#    if match:
#        groups = match.groups()
#        return "{}/resource/{}".format(groups[0], groups[1])
#    pattern = re.compile('(.*)/resource/([0-9a-f-]{32})/(.*)_resmap\.xml')
#    match = pattern.match(uri)
#    if match:
#        groups = match.groups()
#        return "{}/resource/{}/{}_meta.xml".format(groups[0], groups[1], groups[2])
#    raise Exception("Not recognized")

#assert convert_uri("http://www.hydroshare.org/resource/2e127085825b4f7fb9525b10b98270de/data/resourcemetadata.xml")\
#       == "http://www.hydroshare.org/resource/2e127085825b4f7fb9525b10b98270de"
#assert convert_uri("http://www.hydroshare.org/resource/2e127085825b4f7fb9525b10b98270de/data/contents/SWE_time_resmap.xml")\
#       == "http://www.hydroshare.org/resource/2e127085825b4f7fb9525b10b98270de/data/contents/SWE_time_meta.xml"

