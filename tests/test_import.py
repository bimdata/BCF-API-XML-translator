from os import path

from lxml import etree

from bcf_api_xml.models import Viewpoint
from bcf_api_xml.models import VisualizationInfo

DATA_DIR = path.realpath(path.join(path.dirname(__file__), "./data"))


class TestExportBcfZip:
    def test_export_bcf(self):

        with open(path.join(DATA_DIR, "viewpoint.bcfv"), "rb") as viewpoint_file:
            viewpoint_bcf = etree.fromstring(viewpoint_file.read())

        Viewpoint.to_python(viewpoint_bcf)
        viz_info = VisualizationInfo.to_python(viewpoint_bcf)
        assert len(viz_info["clipping_planes"]) == 2
        assert len(viz_info["components"]["coloring"]) == 5
