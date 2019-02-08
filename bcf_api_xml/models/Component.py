from .models import JsonToXMLModel


class Component(JsonToXMLModel):
    @property
    def xml(self):
        component = self.json
        e = self.maker
        children = []
        if component.get("originating_system"):
            children.append(e.OriginatingSystem(component.get("originating_system")))
        if component.get("authoring_tool_id"):
            children.append(e.AuthoringToolId(component.get("authoring_tool_id")))

        return e.Component(*children, IfcGuid=component["ifc_guid"])
