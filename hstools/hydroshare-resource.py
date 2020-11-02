import os
import requests

from hstools.pydantic_classes import load_rdf


class HydroShare:

    def __init__(self, username=None, password=None, host='dev-hs-1.cuahsi.org'):
        self._username = username
        self._session = requests.Session()
        if username and password:
            self._session.auth = (username, password)
        self._host = host

    def sign_in(self):
        import getpass
        self._username = input("Username: ").strip()
        password = getpass.getpass("Password for {}: ".format(self._username))
        self._session.auth = (self._username, password)

    def search(self):
        pass

    def resource(self, resource_id):
        return Aggregation("https://{}/resource/{}/data/resourcemap.xml".format(self._host, resource_id), self)

    def retrieve(self, url, save_path):
        file = self._session.request('GET', url, allow_redirects=True)

        with open(save_path, "wb") as f:
            f.write(file.content)


class File:

    def __init__(self, file_url, hs):
        self._url = file_url
        self._hs = hs

    @property
    def url(self):
        return str(self._url)

    @property
    def name(self):
        return os.path.basename(self._url.path)

    @property
    def full_path(self):
        return self._url.path

    @property
    def relative_path(self):
        return self._url.path.split('/data/contents/', 1)[1]

    @property
    def relative_folder(self):
        return self.relative_path.rsplit(self.name, 1)[0]

    def download(self, save_path):
        self._hs.retrieve(self.url, save_path)


def is_aggregation(path):
    return path.endswith('#aggregation')

class Aggregation:

    def __init__(self, map_url, hs):
        self._map_url = map_url
        self._hs = hs
        self._retrieved_map = None
        self._retrieved_metadata = None
        self._parsed_files = None
        self._parsed_aggregations = None

    @property
    def _map(self):
        if not self._retrieved_map:
            self._retrieved_map = self._retrieve_and_parse(self._map_url)
        return self._retrieved_map

    @property
    def _metadata(self):
        if not self._retrieved_metadata:
            self._retrieved_metadata = self._retrieve_and_parse(self.metadata_url)
        return self._retrieved_metadata

    @property
    def _files(self):
        if not self._parsed_files:
            self._parsed_files = []
            for file_url in self._map.describes.files:
                if not is_aggregation(str(file_url.path)):
                    if not file_url == self.metadata_url:
                        if not str(file_url.path).endswith('/'): # checking for folders, shouldn't have to do this
                            self._parsed_files.append(File(file_url, self._hs))
        return self._parsed_files

    @property
    def _aggregations(self):
        if not self._parsed_aggregations:
            self._parsed_aggregations = []
            for file_url in self._map.describes.files:
                if is_aggregation(str(file_url.path)):
                    self._parsed_aggregations.append(Aggregation(str(file_url), self._hs))
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

    @property
    def metadata_url(self):
        return self._map.describes.is_documented_by

    def download(self, save_path):
        pass
        #TODO can we save a resource and aggregation in the same way?

    def delete(self):
        pass

    def upload(self, *files, dest_relative_path):
        pass

    def __str__(self):
        return self._map_url

    def _retrieve_and_parse(self, url):
        filename = 'retrieve_metadata.xml'
        try:
            self._hs.retrieve(url, filename)
            instance = load_rdf(filename, file_format='xml')
        finally:
            pass
            os.remove(filename)

        return instance


hs = HydroShare()
hs.sign_in()
resource = hs.resource('09041bbe8015485db414a4d41b3575db')
print(resource.metadata.title)

from pathlib import Path
for f in resource.files:
    Path("temp/" + f.relative_folder).mkdir(parents=True, exist_ok=True)
    f.download("temp/" + f.relative_path)

for agg in resource.aggregations:
    print(agg.metadata.title)
    for f in agg.files:
        Path("temp/" + f.relative_folder).mkdir(parents=True, exist_ok=True)
        f.download("temp/" + f.relative_path)


