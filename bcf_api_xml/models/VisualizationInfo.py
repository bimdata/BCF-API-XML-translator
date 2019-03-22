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

        children = []

        components = viewpoint.get("components")
        if components:
            visibility = components["visibility"]

            components_children = [ViewSetupHints(visibility["view_setup_hints"]).xml]

            xml_selections = [
                Component(component).xml
                for component in components.get("selection", [])
                if component.get("ifc_guid")
            ]
            if xml_selections:
                components_children.append(e.Selection(*xml_selections))

            components_children.append(Visibility(visibility).xml)

            xml_colorings = [
                Color(coloring).xml for coloring in components.get("coloring", [])
            ]
            if xml_colorings:
                components_children.append(e.Coloring(*xml_colorings))

            children.append(e.Components(*components_children))

        if viewpoint.get("orthogonal_camera"):
            xml_ortogonal_camera = OrthogonalCamera(viewpoint["orthogonal_camera"]).xml
            children.append(xml_ortogonal_camera)

        if viewpoint.get("perspective_camera"):
            xml_perspective_camera = PerspectiveCamera(
                viewpoint["perspective_camera"]
            ).xml
            children.append(xml_perspective_camera)

        xml_lines = [Line(line).xml for line in viewpoint.get("lines", [])]
        if xml_lines:
            children.append(e.Lines(*xml_lines))

        xml_planes = [
            ClippingPlane(plane).xml for plane in viewpoint.get("clipping_planes", [])
        ]
        if xml_planes:
            children.append(e.ClippingPlanes(*xml_planes))

        return e.VisualizationInfo(*children, Guid=str(viewpoint["guid"]))
