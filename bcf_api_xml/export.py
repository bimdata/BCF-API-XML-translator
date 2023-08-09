import base64
import io
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

XLS_HEADER_TRANSLATIONS = {
    "en": {
        "index": "Index",
        "creation_date": "Date",
        "author": "Author",
        "title": "Title",
        "description": "Description",
        "due_date": "Due date",
        "status": "Status",
        "priority": "Priority",
        "comments": "Comments",
        "viewpoint": "Image"
    },
    "fr": {
        "index": "N°",
        "creation_date": "Date",
        "author": "Auteur",
        "title": "Titre",
        "description": "Description",
        "due_date": "Date d'échéance",
        "status": "Statut",
        "priority": "Priorité",
        "comments": "Commentaires",
        "viewpoint": "Image"
    }
}



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


def to_xls(topics, comments, viewpoints, lang = "en"):
    """
    topics: list of topics (dict parsed from BCF-API json)
    comments: dict(topics_guid=[comment])
    viewpoints: dict(topics_guid=[viewpoint])
    """
    xls_file = io.BytesIO()
    with xlsxwriter.Workbook(xls_file) as workbook:
        worksheet = workbook.add_worksheet()

        header_fmt = workbook.add_format({ "align": "center", "bold": True, "bg_color": "#C0C0C0" })
        base_fmt = workbook.add_format({ "valign": "top" })
        date_fmt = workbook.add_format({ "valign": "top", "num_format": "yyyy-mm-dd" })
        comments_fmt = workbook.add_format({ "valign": "top", "text_wrap": True })

        headers = XLS_HEADER_TRANSLATIONS[lang]
        row = 0

        # TODO: add spreadsheet metadata (e.g. project, models, user, ...)

        # Create table header
        worksheet.write(row, 0, headers["index"],         header_fmt)
        worksheet.write(row, 1, headers["creation_date"], header_fmt)
        worksheet.write(row, 2, headers["author"],        header_fmt)
        worksheet.write(row, 3, headers["title"],         header_fmt)
        worksheet.write(row, 4, headers["description"],   header_fmt)
        worksheet.write(row, 5, headers["due_date"],      header_fmt)
        worksheet.write(row, 6, headers["status"],        header_fmt)
        worksheet.write(row, 7, headers["priority"],      header_fmt)
        worksheet.write(row, 8, headers["comments"],      header_fmt)
        worksheet.write(row, 9, headers["viewpoint"],     header_fmt)
        worksheet.set_column_pixels(8, 8, 300)
        worksheet.set_column_pixels(9, 9, 300)
        row += 1

        # Create topic rows
        for topic in topics:
            topic_guid = topic["guid"]
            topic_comments = comments.get(topic_guid, [])
            topic_viewpoints = viewpoints.get(topic_guid, [])

            worksheet.write(row, 0, topic.get("index"), base_fmt)
            creation_date = topic.get("creation_date")
            if creation_date:
                if isinstance(creation_date, str):
                    creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                worksheet.write_datetime(row, 1, creation_date, date_fmt)
            worksheet.write(row, 2, topic.get("creation_author"), base_fmt)
            worksheet.write(row, 3, topic.get("title"), base_fmt)
            worksheet.write(row, 4, topic.get("description"), base_fmt)
            due_date = topic.get("due_date")
            if due_date:
                if isinstance(due_date, str):
                    due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ")
                worksheet.write_datetime(row, 5, due_date, date_fmt)
            worksheet.write(row, 6, topic.get("topic_status"), base_fmt)
            worksheet.write(row, 7, topic.get("priority"), base_fmt)

            concatenated_comments = ""
            for comment in topic_comments:
                concatenated_comments += f"[{comment['date']}] {comment['author']}: {comment['comment']}\n"
            worksheet.write(row, 8, concatenated_comments, comments_fmt)

            if len(topic_viewpoints):
                viewpoint = topic_viewpoints[0]
                if viewpoint.get("snapshot"):
                    snapshot = viewpoint.get("snapshot").get("snapshot_data")
                    if ";base64," in snapshot:
                        _, img_data = snapshot.split(";base64,")
                        img_data = base64.b64decode(img_data)
                    else:
                        img_data = requests.get(snapshot).content
                    img_data = io.BytesIO(img_data)

                    with Image.open(img_data) as img:
                        width, height = img.size
                    scale = 300 / width

                    worksheet.set_row_pixels(row, height * scale)
                    worksheet.insert_image(row, 9, "snapshot.png", { "image_data": img_data, "x_scale": scale, "y_scale": scale })

            row += 1

        worksheet.autofit()

    workbook.close()
    return xls_file
