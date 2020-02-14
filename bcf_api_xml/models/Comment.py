from .models import JsonToXMLModel, XMLToJsonModel
from datetime import datetime


class Comment(JsonToXMLModel):
    @property
    def xml(self):
        comment = self.json
        e = self.maker
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


class CommentImport(XMLToJsonModel):
    @property
    def to_python(self):
        comment = {}
        xml = self.xml

        comment["date"] = datetime.fromisoformat(xml.find("Date").text)
        comment["comment"] = xml.find("Comment").text or ""
        comment["author"] = xml.find("Author").text

        if (viewpoint := xml.find("Viewpoint")) is not None:
            comment["viewpoint_guid"] = viewpoint.get("Guid")

        if (modified_date := xml.find("ModifiedDate")) is not None:
            comment["modified_date"] = datetime.fromisoformat(modified_date.text)

        if (modified_author := xml.find("ModifiedAuthor")) is not None:
            comment["modified_author"] = modified_author.text

        return comment
