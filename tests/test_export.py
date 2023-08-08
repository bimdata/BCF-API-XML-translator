import json
from os import path

from bcf_api_xml import export

DATA_DIR = path.realpath(path.join(path.dirname(__file__), "./data"))


class TestMarkup:
    def test_markup_validity(self):
        with open(path.join(DATA_DIR, "topics.json"), "r") as topics_file:
            topics = json.load(topics_file)
        with open(path.join(DATA_DIR, "comments.json"), "r") as comments_file:
            comments = json.load(comments_file)
        with open(path.join(DATA_DIR, "viewpoints.json"), "r") as viewpoints_file:
            viewpoints = json.load(viewpoints_file)

        topic = topics[0]
        export.export_markup(topic, comments[topic["guid"]], viewpoints[topic["guid"]])


class TestExportBcfZip:
    def test_export_bcf_zip(self):
        with open(path.join(DATA_DIR, "topics.json"), "r") as topics_file:
            topics = json.load(topics_file)
        with open(path.join(DATA_DIR, "comments.json"), "r") as comments_file:
            comments = json.load(comments_file)
        with open(path.join(DATA_DIR, "viewpoints.json"), "r") as viewpoints_file:
            viewpoints = json.load(viewpoints_file)

        export.to_zip(topics, comments, viewpoints)


class TestExportBcfXls:
    def test_export_bcf_xls(self):
        with open(path.join(DATA_DIR, "topics.json"), "r") as topics_file:
            topics = json.load(topics_file)
        with open(path.join(DATA_DIR, "comments.json"), "r") as comments_file:
            comments = json.load(comments_file)
        with open(path.join(DATA_DIR, "viewpoints.json"), "r") as viewpoints_file:
            viewpoints = json.load(viewpoints_file)

        export.to_xls(topics, comments, viewpoints)


if __name__ == "__main__":
    print("test test_markup_validity")
    TestMarkup().test_markup_validity()
    print("DONE")
    print("test export bcf to_zip")
    TestExportBcfZip().test_export_bcf_zip()
    print("DONE")
    print("test export bcf to_xls")
    TestExportBcfXls().test_export_bcf_xls()
    print("DONE")
