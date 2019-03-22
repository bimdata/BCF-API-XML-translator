from .models import JsonToXMLModel
from .Component import Component


def boolean_repr(value):
    return "true" if value else "false"


class Visibility(JsonToXMLModel):
    @property
    def xml(self):
        visibility = self.json
        e = self.maker
        children = []
        if visibility["exceptions"]:
            components = [
                Component(component).xml
                for component in visibility["exceptions"]
                if component.get("ifc_guid")
            ]
            children.append(e.Exceptions(*components))
        return e.Visibility(
            *children, DefaultVisibility=boolean_repr(visibility["default_visibility"])
        )
