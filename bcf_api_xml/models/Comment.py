from dateutil.parser import parse
from lxml import builder


def to_xml(comment):
    e = builder.ElementMaker()
    children = [
        e.Date(comment["date"]),
        e.Author(comment.get("author", "")),
        e.Comment(comment["comment"]),
    ]
    if (viewpoint_guid := comment.get("viewpoint_guid")) is not None:
        children.append(e.Viewpoint(Guid=str(viewpoint_guid)))
    if (modified_date := comment.get("modified_date")) is not None:
        children.append(e.ModifiedDate(modified_date))
    if (modified_author := comment.get("modified_author")) is not None:
        children.append(e.ModifiedAuthor(modified_author))

    return e.Comment(*children, Guid=str(comment["guid"]))


def to_python(xml):
    comment = {}

    if (viewpoint := xml.find("Viewpoint")) is not None:
        comment["viewpoint_guid"] = viewpoint.get("Guid")

    if (author := xml.find("Author")) is not None:
        comment["author"] = author.text

    if (comment_field := xml.find("Comment")) is not None:
        comment["comment"] = comment_field.text or ""
    else:
        comment["comment"] = ""

    if (date := xml.find("Date")) is not None and date.text is not None:
        comment["date"] = parse(date.text)

    if (
        modified_date := xml.find("ModifiedDate")
    ) is not None and modified_date.text is not None:
        comment["modified_date"] = parse(modified_date.text)

    if (
        modified_author := xml.find("ModifiedAuthor")
    ) is not None and modified_author.text is not None:
        comment["modified_author"] = modified_author.text

    return comment
