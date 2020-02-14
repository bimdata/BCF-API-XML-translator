from .models import JsonToXMLModel, XMLToJsonModel
from .Component import Component, ComponentImport


def boolean_repr(value):
    return "true" if value else "false"


def to_boolean(value):
    return value == "true"


class Visibility(JsonToXMLModel):
    @property
    def xml(self):
        visibility = self.json
        e = self.maker
        children = []
        if exceptions := visibility.get("exceptions"):
            components = [
                Component(component).xml
                for component in exceptions
                if component.get("ifc_guid")
            ]
            children.append(e.Exceptions(*components))
        return e.Visibility(
            *children, DefaultVisibility=boolean_repr(visibility["default_visibility"])
        )


class VisibilityImport(XMLToJsonModel):
    @property
    def to_python(self):
        xml = self.xml
        visibility = {
            "default_visibility": xml.get("DefaultVisibility"),
        }
        if (exceptions := xml.find("Exceptions")) is not None:
            visibility["exceptions"] = [
                ComponentImport(component).to_python
                for component in exceptions.findall("Component")
            ]

        return visibility
