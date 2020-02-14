from .models import JsonToXMLModel, XMLToJsonModel
from .Component import Component, ComponentImport


class Color(JsonToXMLModel):
    @property
    def xml(self):
        coloring = self.json
        e = self.maker
        return e.Color(
            *[Component(component) for component in coloring["components"]],
            Color=coloring["color"],
        )


class ColorImport(XMLToJsonModel):
    @property
    def to_python(self):
        xml = self.xml
        return {
            "color": xml.get("Color"),
            "components": [
                ComponentImport(component).to_python for component in xml.findall("Component")
            ],
        }
