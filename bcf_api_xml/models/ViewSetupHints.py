from .models import JsonToXMLModel, XMLToJsonModel


def boolean_repr(value):
    return "true" if value else "false"


def to_boolean(value):
    return value == "true"


class ViewSetupHints(JsonToXMLModel):
    @property
    def xml(self):
        hints = self.json
        e = self.maker
        return e.ViewSetupHints(
            SpacesVisible=boolean_repr(hints["spaces_visible"]),
            SpaceBoundariesVisible=boolean_repr(hints["space_boundaries_visible"]),
            OpeningsVisible=boolean_repr(hints["openings_visible"]),
        )


class ViewSetupHintsImport(XMLToJsonModel):
    @property
    def to_python(self):
        xml = self.xml
        return {
            "spaces_visible": to_boolean(xml.get("SpacesVisible")),
            "space_boundaries_visible": to_boolean(xml.get("SpaceBoundariesVisible")),
            "openings_visible": to_boolean(xml.get("OpeningsVisible")),
        }
