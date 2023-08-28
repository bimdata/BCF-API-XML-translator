from dateutil.parser import parse
from lxml import builder


def to_xml(topic):
    e = builder.ElementMaker()
    children = []
    for ref in topic.get("reference_links", []):
        children.append(e.ReferenceLink(ref))
    children.append(e.Title(topic["title"]))
    if (priority := topic.get("priority")) is not None:
        children.append(e.Priority(priority))
    if (index := topic.get("index")) is not None:
        children.append(e.Index(str(index)))
    for label in topic.get("labels"):
        children.append(e.Labels(label))

    children.append(e.CreationDate(topic["creation_date"]))
    children.append(e.CreationAuthor(topic.get("creation_author", "")))
    if (modified_date := topic.get("modified_date")) is not None:
        children.append(e.ModifiedDate(modified_date))
    if (modified_author := topic.get("modified_author")) is not None:
        children.append(e.ModifiedAuthor(modified_author))
    if (due_date := topic.get("due_date")) is not None:
        children.append(e.DueDate(due_date))
    if (assigned_to := topic.get("assigned_to")) is not None:
        children.append(e.AssignedTo(assigned_to))
    if (stage := topic.get("stage")) is not None:
        children.append(e.Stage(stage))
    if (description := topic.get("description")) is not None:
        children.append(e.Description(description))

    attributes = {"Guid": topic["guid"]}
    if (topic_type := topic.get("topic_type")) is not None:
        attributes["TopicType"] = topic_type

    if (topic_status := topic.get("topic_status")) is not None:
        attributes["TopicStatus"] = topic_status
    return e.Topic(*children, **attributes)


def to_python(xml):
    topic = {
        "guid": xml.get("Guid"),
        "title": xml.find("Title").text,
        "topic_type": xml.get("TopicType"),
        "topic_status": xml.get("TopicStatus"),
    }

    if (
        creation_author := xml.find("CreationAuthor")
    ) is not None and creation_author.text is not None:
        topic["creation_author"] = creation_author.text

    if (
        creation_date := xml.find("CreationDate")
    ) is not None and creation_date.text is not None:
        topic["creation_date"] = parse(creation_date.text)

    if (priority := xml.find("Priority")) is not None and priority.text is not None:
        topic["priority"] = priority.text

    if (index := xml.find("Index")) is not None and index.text is not None:
        topic["index"] = index.text

    if (due_date := xml.find("DueDate")) is not None and due_date.text is not None:
        topic["due_date"] = parse(due_date.text)

    if (
        modified_date := xml.find("ModifiedDate")
    ) is not None and modified_date.text is not None:
        topic["modified_date"] = parse(modified_date.text)

    if (
        modified_author := xml.find("ModifiedAuthor")
    ) is not None and modified_author.text is not None:
        topic["modified_author"] = modified_author.text

    if (assigned_to := xml.find("AssignedTo")) is not None and assigned_to.text is not None:
        topic["assigned_to"] = assigned_to.text

    if (description := xml.find("Description")) is not None and description.text is not None:
        topic["description"] = description.text

    return topic
