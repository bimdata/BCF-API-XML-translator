from os import path
import json
from bcf_api_xml.models import VisualizationInfo

DATA_DIR = path.realpath(path.join(path.dirname(__file__), "../data"))


class TestVisinfo:
    def test_visinfo_validity(self):
        with open(path.join(DATA_DIR, "viewpoints.json"), "r") as viewpoints_file:
            viewpoints = json.load(viewpoints_file)

        assert viewpoints
        for viewpoint in list(viewpoints.values())[0]:
            visinfo = VisualizationInfo(viewpoint)
            assert visinfo.is_valid()
