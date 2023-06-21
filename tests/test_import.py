from os import path

from lxml import etree

from bcf_api_xml.import_zip import to_json
from bcf_api_xml.models import Viewpoint
from bcf_api_xml.models import VisualizationInfo

DATA_DIR = path.realpath(path.join(path.dirname(__file__), "./data"))


class TestImportBcfZip:
    def test_import_file(self):
        to_json(path.join(DATA_DIR, "test.bcf"))
        # Just assert it does not crash for now

    def test_import_viewpoint(self):
        with open(path.join(DATA_DIR, "viewpoint.bcfv"), "rb") as viewpoint_file:
            viewpoint_bcf = etree.fromstring(viewpoint_file.read())

        Viewpoint.to_python(viewpoint_bcf)
        viz_info = VisualizationInfo.to_python(viewpoint_bcf)
        assert len(viz_info["clipping_planes"]) == 2
        assert len(viz_info["components"]["coloring"]) == 5


if __name__ == "__main__":
    print("test import_file")
    TestImportBcfZip().test_import_file()
    print("DONE")
    print("test import_viewpoint")
    TestImportBcfZip().test_import_viewpoint()
    print("DONE")
