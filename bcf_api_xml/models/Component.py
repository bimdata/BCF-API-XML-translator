from lxml import builder


def to_xml(component):
    e = builder.ElementMaker()
    children = []
    if (originating_system := component.get("originating_system")) is not None:
        children.append(e.OriginatingSystem(originating_system))
    if (authoring_tool_id := component.get("authoring_tool_id")) is not None:
        children.append(e.AuthoringToolId(authoring_tool_id))

    return e.Component(*children, IfcGuid=component["ifc_guid"])


def to_python(xml):
    component = {"ifc_guid": xml.get("IfcGuid")}
    if (originating_system := xml.find("OriginatingSystem")) is not None:
        component["originating_system"] = originating_system.text

    if (authoring_tool_id := xml.find("AuthoringToolId")) is not None:
        component["authoring_tool_id"] = authoring_tool_id.text
    return component
