import json
from os import path

from bcf_api_xml.export import is_valid
from bcf_api_xml.models import VisualizationInfo

DATA_DIR = path.realpath(path.join(path.dirname(__file__), "../data"))


class TestVisinfo:
    def test_visinfo_validity(self):
        with open(path.join(DATA_DIR, "viewpoints.json"), "r") as viewpoints_file:
            viewpoints = json.load(viewpoints_file)

        assert viewpoints
        for viewpoint in list(viewpoints.values())[0]:
            visinfo = VisualizationInfo.to_xml(viewpoint)
            assert is_valid("visinfo.xsd", visinfo)
