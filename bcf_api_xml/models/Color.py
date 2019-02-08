from .models import JsonToXMLModel
from .Component import Component


class Color(JsonToXMLModel):
    @property
    def xml(self):
        coloring = self.json
        e = self.maker
        return e.Color(
            *[Component(component) for component in coloring["components"]],
            Color=coloring["color"],
        )
