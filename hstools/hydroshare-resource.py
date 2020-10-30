import os

from hstools.pydantic_classes import load_rdf

def retrieve_and_parse(url):
    import requests

    session = requests.Session()
    session.auth = ('sblack', 'password')

    metadata = session.request('GET', url, allow_redirects=True)

    try:
        with open("retrieved_metadata.xml", "wb") as f:
            f.write(metadata.content)
        instance = load_rdf("retrieved_metadata.xml", file_format='xml')
    finally:
        pass
        os.remove("retrieved_metadata.xml")

    return instance


class Aggregation:

    def __init__(self, map_url):
        self._map_url = map_url
        self._retrieved_map = None
        self._retrieved_metadata = None
        self._parsed_files = None
        self._parsed_aggregations = None

    @property
    def _map(self):
        if not self._retrieved_map:
            self._retrieved_map = retrieve_and_parse(self._map_url)
        return self._retrieved_map

    @property
    def _metadata(self):
        if not self._retrieved_metadata:
            self._retrieved_metadata = retrieve_and_parse(self._map.describes.is_documented_by)
        return self._retrieved_metadata

    @property
    def _files(self):
        if not self._parsed_files:
            self._parsed_files = []
            for file in self._map.describes.files:
                if not str(file.path).endswith('#aggregation'):
                    self._parsed_files.append(str(file))
        return self._parsed_files

    @property
    def _aggregations(self):
        if not self._parsed_aggregations:
            self._parsed_aggregations = []
            for file in self._map.describes.files:
                if str(file.path).endswith('#aggregation'):
                    self._parsed_aggregations.append(Aggregation(str(file)))
        return self._parsed_aggregations

    @property
    def files(self):
        return self._files

    @property
    def aggregations(self):
        return self._aggregations

    @property
    def metadata(self):
        return self._metadata

    def __str__(self):
        return self._map_url


resource = Aggregation('https://dev-hs-1.cuahsi.org/resource/09041bbe8015485db414a4d41b3575db/data/resourcemap.xml')
print(resource.metadata.title)
print([f for f in resource.files])

for agg in resource.aggregations:
    print(agg.metadata.title)
    for f in agg.files:
        print(f)


