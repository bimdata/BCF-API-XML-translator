from .models import JsonToXMLModel
from .Component import Component
from .OrthogonalCamera import OrthogonalCamera
from .PerspectiveCamera import PerspectiveCamera
from .Line import Line
from .ClippingPlane import ClippingPlane
from .ViewSetupHints import ViewSetupHints
from .Visibility import Visibility


class VisualizationInfo(JsonToXMLModel):
    SCHEMA_NAME = "visinfo.xsd"

    @property
    def xml(self):
        viewpoint = self.json
        e = self.maker

        xml_ortogonal_camera = OrthogonalCamera(viewpoint["orthogonal_camera"]).xml
        xml_perspective_camera = PerspectiveCamera(viewpoint["perspective_camera"]).xml

        xml_lines = [Line(line).xml for line in viewpoint.get("lines", [])]
        xml_planes = [
            ClippingPlane(plane).xml for plane in viewpoint.get("clipping_planes", [])
        ]

        components = viewpoint["components"]
        selections = components["selection"]
        xml_selections = [Component(selection).xml for selection in selections]

        colorings = components["coloring"]
        xml_colorings = [Color(coloring).xml for coloring in colorings]

        visibility = components["visibility"]
        xml_view_setup_hints = ViewSetupHints(visibility["view_setup_hints"]).xml

        xml_visibility = Visibility(visibility).xml

        components_children = [xml_view_setup_hints]
        if xml_selections:
            components_children.append(e.Selection(*xml_selections))
        components_children.append(xml_visibility)
        if xml_colorings:
            components_children.append(e.Coloring(*xml_colorings))
        xml_components = e.Components(*components_children)

        children = [xml_components, xml_ortogonal_camera, xml_perspective_camera]
        if xml_lines:
            children.append(e.Lines(*xml_lines))
        if xml_planes:
            children.append(e.ClippingPlanes(*xml_planes))

        return e.VisualizationInfo(*children, Guid=viewpoint["guid"])
