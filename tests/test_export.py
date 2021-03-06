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
    def test_export_bcf(self):
        with open(path.join(DATA_DIR, "topics.json"), "r") as topics_file:
            topics = json.load(topics_file)
        with open(path.join(DATA_DIR, "comments.json"), "r") as comments_file:
            comments = json.load(comments_file)
        with open(path.join(DATA_DIR, "viewpoints.json"), "r") as viewpoints_file:
            viewpoints = json.load(viewpoints_file)

        export.to_zip(topics, comments, viewpoints)
