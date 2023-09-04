import base64
import io
import zipfile
from datetime import datetime
from os import path

import requests
import xlsxwriter
from dateutil import parser
from lxml import builder
from lxml import etree
from PIL import Image

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
        "description": "Description of the problem",
        "due_date": "Due date",
        "status": "Status",
        "priority": "Priority",
        "comments": "Comments",
        "viewpoint": "Image",
        "models": "Name of model",
        "space": "Organisation",
        "project": "Project",
    },
    "fr": {
        "index": "N°",
        "creation_date": "Date",
        "author": "Auteur",
        "title": "Titre",
        "description": "Description du problème",
        "due_date": "Date d'échéance",
        "status": "Statut",
        "priority": "Priorité",
        "comments": "Commentaire du problème",
        "viewpoint": "Image",
        "models": "Nom du modèle",
        "space": "Organisation",
        "project": "Project",
    },
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


def to_xlsx(
    space, project, models, topics, comments, viewpoints, company_logo_content, lang="en"
):
    """
    topics: list of topics (dict parsed from BCF-API json)
    comments: dict(topics_guid=[comment])
    viewpoints: dict(topics_guid=[viewpoint])
    """
    xls_file = io.BytesIO()
    with xlsxwriter.Workbook(xls_file, options={"remove_timezone": True}) as workbook:
        worksheet = workbook.add_worksheet()

        header_fmt = workbook.add_format(
            {"align": "center", "bold": True, "bg_color": "#C0C0C0", "border": 1}
        )
        base_fmt = workbook.add_format({"valign": "top", "border": 1})
        if lang == "fr":
            date_fmt = workbook.add_format(
                {"valign": "top", "num_format": "dd/mm/yyyy", "border": 1}
            )
        else:
            date_fmt = workbook.add_format(
                {"valign": "top", "num_format": "yyyy-mm-dd", "border": 1}
            )

        comments_fmt = workbook.add_format({"valign": "top", "text_wrap": True, "border": 1})
        header_fmt2 = workbook.add_format({"border": 1})
        base_fm_align = workbook.add_format({"align": "center", "valign": "top"})

        headers = XLS_HEADER_TRANSLATIONS[lang]

        worksheet.set_default_row(120)
        # Company Logo followed by date, espace, space, models
        row = 0

        merge_format_gray = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "#C0C0C0",
            }
        )

        merge_format_default = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "white",
            }
        )
        company_logo_data = io.BytesIO(company_logo_content)

        with Image.open(company_logo_data) as img:
            width, height = img.size
        scale = 300 / width

        worksheet.set_row_pixels(row, height * scale)
        worksheet.merge_range("A1:C1", "", merge_format_default)

        worksheet.insert_image(
            row,
            0,
            "company_logo.png",
            {"image_data": company_logo_data, "x_scale": scale, "y_scale": scale},
        )

        worksheet.merge_range("D1:Z1", "", merge_format_gray)
        row += 1
        worksheet.set_row(row, 20)
        worksheet.merge_range("A2:Z2", "", merge_format_default)
        row += 1
        worksheet.set_row(row, 15)
        worksheet.merge_range("A3:B3", "", merge_format_default)
        worksheet.write(row, 0, headers["project"], header_fmt)
        worksheet.merge_range("C3:Z3", "", merge_format_default)
        worksheet.write(row, 2, project["name"], header_fmt2)

        # TODO: add spreadsheet metadata for models

        row += 1
        worksheet.set_row(row, 15)
        worksheet.merge_range("A4:B4", "", merge_format_default)
        worksheet.write(row, 0, headers["space"], header_fmt)
        worksheet.merge_range("C4:Z4", "", merge_format_default)
        worksheet.write(row, 2, space["name"], header_fmt2)

        row += 1
        worksheet.set_row(row, 15)
        worksheet.merge_range("A5:B5", "", merge_format_default)
        worksheet.write(row, 0, "Date", header_fmt)
        worksheet.merge_range("C5:Z5", "", merge_format_default)
        if lang == "fr":
            current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        worksheet.write(row, 2, current_time, header_fmt2)

        row += 1
        worksheet.set_row(row, 20)
        worksheet.merge_range("A6:Z6", "", merge_format_default)
        row += 1

        # Create table header
        worksheet.set_row(row, 45)
        worksheet.write(row, 0, headers["index"], header_fmt)
        worksheet.write(row, 1, headers["creation_date"], header_fmt)
        worksheet.write(row, 2, headers["author"], header_fmt)
        worksheet.write(row, 3, headers["title"], header_fmt)
        worksheet.write(row, 4, headers["viewpoint"], header_fmt)
        worksheet.write(row, 5, headers["description"], header_fmt)
        worksheet.write(row, 6, headers["due_date"], header_fmt)
        worksheet.write(row, 7, headers["status"], header_fmt)
        worksheet.write(row, 8, headers["priority"], header_fmt)
        worksheet.write(row, 9, headers["comments"], header_fmt)
        worksheet.set_column_pixels(8, 8, 100)
        worksheet.set_column_pixels(9, 9, 200)
        row += 1

        worksheet.set_column(4, 4, 30)
        # Create topic rows
        for topic in topics:
            topic_guid = topic["guid"]
            topic_comments = comments.get(topic_guid, [])
            topic_viewpoints = viewpoints.get(topic_guid, [])

            worksheet.write(row, 0, topic.get("index"), base_fm_align)
            creation_date = topic.get("creation_date")
            if creation_date:
                creation_date = parser.parse(creation_date)
                worksheet.write_datetime(row, 1, creation_date, date_fmt)
            worksheet.write(row, 2, topic.get("creation_author"), base_fmt)
            worksheet.write(row, 3, topic.get("title"), base_fmt)
            worksheet.write(row, 5, topic.get("description"), base_fmt)
            due_date = topic.get("due_date")

            if due_date:
                due_date = parser.parse(due_date)
                worksheet.write_datetime(row, 6, due_date, date_fmt)
            else:
                worksheet.write(row, 6, "", base_fmt)
            worksheet.write(row, 7, topic.get("topic_status"), base_fmt)
            worksheet.write(row, 8, topic.get("priority"), base_fmt)

            concatenated_comments = ""

            for comment in topic_comments:
                comment_date = parser.parse(comment["date"])
                if lang == "fr":
                    comment_date = comment_date.strftime("%d/%m/%Y, %H:%M:%S")
                else:
                    comment_date = comment_date.strftime("%Y-%m-%d, %H:%M:%S")
                concatenated_comments += (
                    f"[{comment_date}] {comment['author']}: {comment['comment']}\n"
                )
            worksheet.write(row, 9, concatenated_comments, comments_fmt)

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
                        if width > height:
                            scale = 215 / width
                        else:
                            scale = 215 / height

                    worksheet.insert_image(
                        row,
                        4,
                        "snapshot.png",
                        {"image_data": img_data, "x_scale": scale, "y_scale": scale},
                    )
            worksheet.write(row, 4, "", base_fmt)

            row += 1
        worksheet.set_column("K:Z", None, None, {"hidden": True})
        worksheet.set_default_row(hide_unused_rows=True)

        worksheet.autofit()

    return xls_file
