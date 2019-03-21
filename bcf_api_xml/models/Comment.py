from .models import JsonToXMLModel


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
        if comment.get("viewpoint_guid"):
            children.append(e.Viewpoint(Guid=str(comment.get("viewpoint_guid"))))
        if comment.get("modified_date"):
            children.append(e.ModifiedDate(comment.get("modified_date")))
        if comment.get("modified_author"):
            children.append(e.ModifiedAuthor(comment.get("modified_author")))

        return e.Comment(*children, Guid=str(comment["guid"]))
