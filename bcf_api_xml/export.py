import os
import io
import base64
import zipfile
from os import path
from lxml import etree, builder
from .models import Topic, Comment, VisualizationInfo

SCHEMA_DIR = path.realpath(path.join(path.dirname(__file__), "Schemas"))


def is_valid(schema_name, xml, raise_exception=False):
    schema_path = path.join(SCHEMA_DIR, schema_name)
    with open(schema_path, "r") as file:
        schema = etree.XMLSchema(file=file)

    if not schema.validate(xml):
        if raise_exception:
            raise BcfXmlException(schema.error_log)
        else:
            print(schema.error_log)
        return False
    return True

    schema_path = path.join(SCHEMA_DIR, schema_name)
    with open(schema_path, "r") as file:
        schema = etree.XMLSchema(file=file)

    if not schema.validate(xml):
        print("NOT VALID with", schema_path)
        print(schema.error_log)
        return False
    return True


def export_viewpoint(viewpoint, is_first):
    e = builder.ElementMaker()
    viewpoint_name = "viewpoint.bcfv" if is_first else (viewpoint["guid"] + ".bcfv")
    snapshot_name = "snapshot.png" if is_first else (viewpoint["guid"] + ".png")

    return e.Viewpoints(
        e.Viewpoint(viewpoint_name),
        e.Snapshot(snapshot_name),
        e.Index(str(viewpoint["index"])),
        Guid=str(viewpoint["guid"]),
    )


def export_markup(topic, comments, viewpoints):
    e = builder.ElementMaker()
    children = [Topic(topic).xml]

    for comment in comments:
        children.append(Comment(comment).xml)

    for index, viewpoint in enumerate(viewpoints):
        xml_viewpoint = export_viewpoint(viewpoint, index == 0)
        children.append(xml_viewpoint)
    xml_markup = e.Markup(*children)
    is_valid("markup.xsd", xml_markup, raise_exception=True)
    return xml_markup


def write_xml(zf, path, xml):
    data = etree.tostring(
        xml, encoding="utf-8", pretty_print=True, xml_declaration=True
    )
    zf.writestr(path, data)


def export_bcf_zip(topics, comments, viewpoints):
    """
    topics: list of topics (dict parsed from BCF-API json)
    viewpoints: dict(topics_guid=[viewpoint])
    comments: dict(topics_guid=[comment])
    """
    zip_file = io.BytesIO()
    with zipfile.ZipFile(zip_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        with open(path.join(SCHEMA_DIR, "bcf.version"), "rb") as version_file:
            zf.writestr("bcf.version", version_file.read())

        for topic in topics:
            topic_guid = topic["guid"]
            topic_comments = comments.get(topic_guid, [])
            topic_viewpoints = viewpoints.get(topic_guid, [])
            # 1 dossier par topic
            topic_dir = topic_guid + "/"
            zfi = zipfile.ZipInfo(topic_dir)
            zf.writestr(zfi, "")  # create the directory in the zip

            xml_markup = export_markup(topic, topic_comments, topic_viewpoints)
            write_xml(zf, topic_dir + "markup.bcf", xml_markup)

            for index, viewpoint in enumerate(topic_viewpoints):
                xml_visinfo = VisualizationInfo(viewpoint).xml
                viewpoint_name = (
                    "viewpoint.bcfv" if index == 0 else (viewpoint["guid"] + ".bcfv")
                )
                write_xml(zf, topic_dir + viewpoint_name, xml_visinfo)
                # snapshots
                if viewpoint.get("snapshot"):
                    snapshot_name = (
                        "snapshot.png" if index == 0 else (viewpoint["guid"] + ".png")
                    )
                    snapshot = viewpoint.get("snapshot").get("snapshot_data")
                    # Break out the header from the base64 content
                    header, data = snapshot.split(";base64,")
                    zf.writestr(topic_dir + snapshot_name, base64.b64decode(data))
    return zip_file
