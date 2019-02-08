from .models import JsonToXMLModel


class Topic(JsonToXMLModel):
    @property
    def xml(self):
        topic = self.json
        e = self.maker
        children = []
        for ref in topic.get("reference_links", []):
            children.append(e.ReferenceLink(ref))
        children.append(e.Title(topic["title"]))
        if topic.get("priority"):
            children.append(e.Priority(topic.get("priority")))
        if topic.get("index"):
            children.append(e.Index(str(topic.get("index"))))
        for label in topic.get("labels"):
            children.append(e.Labels(label))

        children.append(e.CreationDate(topic["creation_date"]))
        children.append(e.CreationAuthor(topic["creation_author"]))
        if topic.get("modified_date"):
            children.append(e.ModifiedDate(topic.get("modified_date")))
        if topic.get("modified_author"):
            children.append(e.ModifiedAuthor(topic.get("modified_author")))
        if topic.get("due_date"):
            children.append(e.DueDate(topic.get("due_date")))
        if topic.get("assigned_to"):
            children.append(e.AssignedTo(topic.get("assigned_to")))
        if topic.get("stage"):
            children.append(e.Stage(topic.get("stage")))
        if topic.get("description"):
            children.append(e.Description(topic.get("description")))

        attributes = {"Guid": topic["guid"]}
        if topic.get("topic_type"):
            attributes["TopicType"] = topic.get("topic_type")

        if topic.get("topic_status"):
            attributes["TopicStatus"] = topic.get("topic_status")
        return e.Topic(*children, **attributes)
