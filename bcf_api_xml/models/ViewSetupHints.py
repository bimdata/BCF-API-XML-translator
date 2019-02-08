from .models import JsonToXMLModel


def boolean_repr(value):
    return "true" if value else "false"


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
