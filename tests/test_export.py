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

        data = export.to_zip(topics, comments, viewpoints)
        with open("test_bcf_export.zip", "wb") as f:
            f.write(data.getvalue())


class TestExportBcfXls:
    def test_export_bcf_xls(self):
        with open(path.join(DATA_DIR, "space.json"), "r") as space_file:
            space = json.load(space_file)
        with open(path.join(DATA_DIR, "project.json"), "r") as project_file:
            project = json.load(project_file)
        with open(path.join(DATA_DIR, "models.json"), "r") as models_file:
            models = json.load(models_file)
        with open(path.join(DATA_DIR, "topics.json"), "r") as topics_file:
            topics = json.load(topics_file)
        with open(path.join(DATA_DIR, "comments.json"), "r") as comments_file:
            comments = json.load(comments_file)
        with open(path.join(DATA_DIR, "viewpoints.json"), "r") as viewpoints_file:
            viewpoints = json.load(viewpoints_file)

        with open("tests/BIMData.png", "rb") as company_logo_content:
            data = export.to_xlsx(
                space,
                project,
                models,
                topics,
                comments,
                viewpoints,
                company_logo_content.read(),
            )
            with open("test_bcf_export.xlsx", "wb") as f:
                f.write(data.getvalue())


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
