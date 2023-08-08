import base64
import io
import os
import requests
import xlsxwriter
import zipfile
from datetime import datetime
from PIL import Image
from os import path

from lxml import builder
from lxml import etree

from bcf_api_xml.errors import InvalidBCF
from bcf_api_xml.models import Comment
from bcf_api_xml.models import Topic
from bcf_api_xml.models import Viewpoint
from bcf_api_xml.models import VisualizationInfo

SCHEMA_DIR = path.realpath(path.join(path.dirname(__file__), "Schemas"))


def is_valid(schema_name, xml, raise_exception=False):
    schema_path = path.join(SCHEMA_DIR, schema_name)
    with open(schema_path, "r") as file:
        schema = etree.XMLSchema(file=file)

    if not schema.validate(xml):
        if raise_exception:
            raise InvalidBCF(schema.error_log)
        else:
            print(schema.error_log)
        return False
    return True


def export_markup(topic, comments, viewpoints):
    e = builder.ElementMaker()
    children = [Topic.to_xml(topic)]

    for comment in comments:
        children.append(Comment.to_xml(comment))

    for index, viewpoint in enumerate(viewpoints):
        xml_viewpoint = Viewpoint.to_xml(viewpoint, index == 0)
        children.append(xml_viewpoint)
    xml_markup = e.Markup(*children)
    is_valid("markup.xsd", xml_markup, raise_exception=True)
    return xml_markup


def write_xml(zf, path, xml):
    data = etree.tostring(xml, encoding="utf-8", pretty_print=True, xml_declaration=True)
    zf.writestr(path, data)


def to_zip(topics, comments, viewpoints):
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
            # 1 directory per topic
            topic_dir = topic_guid + "/"
            zfi = zipfile.ZipInfo(topic_dir)
            zf.writestr(zfi, "")  # create the directory in the zip

            xml_markup = export_markup(topic, topic_comments, topic_viewpoints)
            write_xml(zf, topic_dir + "markup.bcf", xml_markup)

            for index, viewpoint in enumerate(topic_viewpoints):
                xml_visinfo = VisualizationInfo.to_xml(viewpoint)
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
                    if ";base64," in snapshot:
                        # Break out the header from the base64 content
                        _, data = snapshot.split(";base64,")
                        zf.writestr(topic_dir + snapshot_name, base64.b64decode(data))
    return zip_file


def to_xls(topics, comments, viewpoints):
    """
    topics: list of topics (dict parsed from BCF-API json)
    comments: dict(topics_guid=[comment])
    viewpoints: dict(topics_guid=[viewpoint])
    """
    workbook = xlsxwriter.Workbook("bcf-export.xlsx")
    worksheet = workbook.add_worksheet()

    headerFmt = workbook.add_format({ "align": "center", "bold": True, "bg_color": "#C0C0C0" })
    baseFmt = workbook.add_format({ "valign": "top" })
    dateFmt = workbook.add_format({ "valign": "top", "num_format": "yyyy-mm-dd" })

    row = 0

    # TODO: add spreadsheet metadata

    # Create table header
    worksheet.write(row, 0, "N°",              headerFmt)
    worksheet.write(row, 1, "Index",           headerFmt)
    worksheet.write(row, 2, "Date",            headerFmt)
    worksheet.write(row, 3, "Auteur",          headerFmt)
    worksheet.write(row, 4, "Titre",           headerFmt)
    worksheet.write(row, 5, "Description",     headerFmt)
    worksheet.write(row, 6, "Date d'échéance", headerFmt)
    worksheet.write(row, 7, "Statut",          headerFmt)
    worksheet.write(row, 8, "Priorité",        headerFmt)
    worksheet.write(row, 9, "Image",           headerFmt)
    row += 1

    # Create topic rows
    for topic in topics:
        topic_guid = topic["guid"]
        topic_comments = comments.get(topic_guid, [])
        topic_viewpoints = viewpoints.get(topic_guid, [])

        worksheet.write(row, 0, row, baseFmt)
        worksheet.write(row, 1, topic.get("index"), baseFmt)

        creation_date = topic.get("creation_date")
        if creation_date:
            creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            worksheet.write_datetime(row, 2, creation_date, dateFmt)

        worksheet.write(row, 3, topic.get("creation_author"), baseFmt)
        worksheet.write(row, 4, topic.get("title"), baseFmt)
        worksheet.write(row, 5, topic.get("description"), baseFmt)

        due_date = topic.get("due_date")
        if due_date:
            due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ")
            worksheet.write_datetime(row, 6, due_date, dateFmt)

        worksheet.write(row, 7, topic.get("topic_status"), baseFmt)
        worksheet.write(row, 8, topic.get("priority"), baseFmt)

        for viewpoint in topic_viewpoints:
            if viewpoint.get("snapshot"):
                snapshot = viewpoint.get("snapshot").get("snapshot_data")
                img_file = "snapshot-"+viewpoint["guid"]+".png"
                if ";base64," in snapshot:
                    _, img_data = snapshot.split(";base64,")
                    img_data = base64.b64decode(img_data)
                else:
                    img_data = requests.get(snapshot).content

                with open(img_file, "wb") as f:
                    f.write(img_data)
                with Image.open(img_file) as img:
                    width, height = img.size
                scale = 300 / width

                worksheet.set_column_pixels(9, 9, 300)
                worksheet.set_row_pixels(row, height * scale)
                worksheet.insert_image(row, 9, img_file, { "x_scale": scale, "y_scale": scale })

                row += 1

        row += 1

    worksheet.autofit()

    workbook.close()
