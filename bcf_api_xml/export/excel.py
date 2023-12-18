import base64
import io
from datetime import datetime

import requests
import xlsxwriter
from dateutil import parser
from PIL import Image


HEADER_TRANSLATIONS = {
    "en": {
        "index": "Index",
        "creation_date": "Date",
        "author": "Author",
        "assigned_to": "Assigned to",
        "title": "Title",
        "description": "Description of the problem",
        "due_date": "Due date",
        "status": "Status",
        "priority": "Priority",
        "tags": "Tags",
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
        "assigned_to": "Assigné à",
        "title": "Titre",
        "description": "Description du problème",
        "due_date": "Date d'échéance",
        "status": "Statut",
        "priority": "Priorité",
        "tags": "Tags",
        "comments": "Commentaire du problème",
        "viewpoint": "Image",
        "models": "Nom du modèle",
        "space": "Organisation",
        "project": "Project",
    },
}

INDEX_COL_INDEX = 0
CREATION_DATE_COL_INDEX = 1
AUTHOR_COL_INDEX = 2
ASSIGNED_TO_COL_INDEX = 3
TITLE_COL_INDEX = 4
VIEWPOINT_COL_INDEX = 5
DESCRIPTION_COL_INDEX = 6
DUE_DATE_COL_INDEX = 7
STATUS_COL_INDEX = 8
PRIORITY_COL_INDEX = 9
TAGS_COL_INDEX = 10
COMMENTS_COL_INDEX = 11


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

        # Set default height for tables
        DEFAULT_CELL_HEIGHT = 220
        DEFAULT_NUMBER_OF_ITERATIONS = 1000
        for row in range(DEFAULT_NUMBER_OF_ITERATIONS):
            worksheet.set_row_pixels(row, DEFAULT_CELL_HEIGHT)
            row += 1

        # Set table header row height constant
        TABLE_HEADER_HEIGHT = 45

        # Set model data cell height
        ROW_HEIGHT = 19

        # Set image cell width
        IMAGE_COLUMN_WIDTH = 220
        worksheet.set_column_pixels(VIEWPOINT_COL_INDEX, VIEWPOINT_COL_INDEX, IMAGE_COLUMN_WIDTH)

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

        headers = HEADER_TRANSLATIONS[lang]

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

        # Logo is scaled in a symplistic manner based on BIMData logo, if used with another image with different ratio it may be ugly
        with Image.open(company_logo_data) as img:
            width, height = img.size
        scale = 300 / width

        worksheet.set_row_pixels(
            row, height * scale + 1
        )  # +1 increase height of cell by one pixel to not overlap logo
        worksheet.merge_range("A1:C1", "", merge_format_default)

        worksheet.insert_image(
            row,
            0,
            "company_logo.png",
            {
                "image_data": company_logo_data,
                "x_scale": scale,
                "y_scale": scale,
            },
        )

        worksheet.merge_range("D1:Z1", "", merge_format_gray)
        row += 1
        worksheet.set_row(row, 20)
        worksheet.merge_range("A2:Z2", "", merge_format_default)
        row += 1
        worksheet.set_row_pixels(row, ROW_HEIGHT)
        worksheet.merge_range("A3:B3", "", merge_format_default)
        worksheet.write(row, 0, headers["project"], header_fmt)
        worksheet.merge_range("C3:Z3", "", merge_format_default)
        worksheet.write(row, 2, project["name"], header_fmt2)

        # TODO: add spreadsheet metadata for models

        row += 1
        worksheet.set_row_pixels(row, ROW_HEIGHT)
        worksheet.merge_range("A4:B4", "", merge_format_default)
        worksheet.write(row, 0, headers["space"], header_fmt)
        worksheet.merge_range("C4:Z4", "", merge_format_default)
        worksheet.write(row, 2, space["name"], header_fmt2)

        row += 1
        worksheet.set_row_pixels(row, ROW_HEIGHT)
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

        # Set topic row height
        worksheet.set_row(row, TABLE_HEADER_HEIGHT)

        # Create table header
        worksheet.write(row, INDEX_COL_INDEX, headers["index"], header_fmt)
        worksheet.write(row, CREATION_DATE_COL_INDEX, headers["creation_date"], header_fmt)
        worksheet.write(row, AUTHOR_COL_INDEX, headers["author"], header_fmt)
        worksheet.write(row, ASSIGNED_TO_COL_INDEX, headers["assigned_to"], header_fmt)
        worksheet.write(row, TITLE_COL_INDEX, headers["title"], header_fmt)
        worksheet.write(row, VIEWPOINT_COL_INDEX, headers["viewpoint"], header_fmt)
        worksheet.write(row, DESCRIPTION_COL_INDEX, headers["description"], header_fmt)
        worksheet.write(row, DUE_DATE_COL_INDEX, headers["due_date"], header_fmt)
        worksheet.write(row, STATUS_COL_INDEX, headers["status"], header_fmt)
        worksheet.write(row, PRIORITY_COL_INDEX, headers["priority"], header_fmt)
        worksheet.write(row, TAGS_COL_INDEX, headers["tags"], header_fmt)
        worksheet.write(row, COMMENTS_COL_INDEX, headers["comments"], header_fmt)
        worksheet.set_column_pixels(10, 10, 100)
        worksheet.set_column_pixels(11, 11, 200)
        row += 1

        # Sort topic by index
        topics = sorted(topics, key=lambda k: k.get("index"))
        # Create topic rows
        for topic in topics:
            topic_guid = topic["guid"]
            topic_comments = comments.get(topic_guid, [])
            topic_viewpoints = viewpoints.get(topic_guid, [])

            worksheet.write(row, INDEX_COL_INDEX, topic.get("index"), base_fm_align)
            creation_date = topic.get("creation_date")
            if creation_date:
                creation_date = parser.parse(creation_date)
                worksheet.write_datetime(row, CREATION_DATE_COL_INDEX, creation_date, date_fmt)
            worksheet.write(row, AUTHOR_COL_INDEX, topic.get("creation_author"), base_fmt)
            worksheet.write(row, TITLE_COL_INDEX, topic.get("title"), base_fmt)
            worksheet.write(row, ASSIGNED_TO_COL_INDEX, topic.get("assigned_to"), base_fmt)
            worksheet.write(row, DESCRIPTION_COL_INDEX, topic.get("description"), base_fmt)
            due_date = topic.get("due_date")

            if due_date:
                due_date = parser.parse(due_date)
                worksheet.write_datetime(row, DUE_DATE_COL_INDEX, due_date, date_fmt)
            else:
                worksheet.write(row, DUE_DATE_COL_INDEX, "", base_fmt)
            worksheet.write(row, STATUS_COL_INDEX, topic.get("topic_status"), base_fmt)
            worksheet.write(row, PRIORITY_COL_INDEX, topic.get("priority"), base_fmt)

            concatenated_tags = ", ".join(topic.get("labels", []))

            worksheet.write(row, TAGS_COL_INDEX, concatenated_tags, base_fmt)

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
            worksheet.write(row, COMMENTS_COL_INDEX, concatenated_comments, comments_fmt)

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
                        ratios = (
                            float(IMAGE_COLUMN_WIDTH - 1)
                            / width,  # -1 decrease width by one pixel to not overlap with cell delimiter
                            float(DEFAULT_CELL_HEIGHT - 1)
                            / height,  # -1 decrease height by one pixel to not overlap with cell delimiter
                        )
                        scale = min(ratios)
                        worksheet.insert_image(
                            row,
                            VIEWPOINT_COL_INDEX,
                            "snapshot.png",
                            {
                                "image_data": img_data,
                                "x_scale": scale,
                                "y_scale": scale,
                                "x_offset": 1,  # Offset image to avoid overlap with cell delimtier
                                "y_offset": 1,  # Offset image to avoid overlap with cell delimiter
                            },
                        )
            worksheet.write(row, VIEWPOINT_COL_INDEX, "", base_fmt)

            row += 1
        worksheet.set_column("M:Z", None, None, {"hidden": True})
        worksheet.set_default_row(hide_unused_rows=True)

        worksheet.autofit()

    return xls_file
