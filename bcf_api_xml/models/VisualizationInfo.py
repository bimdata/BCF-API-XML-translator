from .models import JsonToXMLModel, XMLToJsonModel
from .Component import Component, ComponentImport
from .OrthogonalCamera import OrthogonalCamera, OrthogonalCameraImport
from .PerspectiveCamera import PerspectiveCamera, PerspectiveCameraImport
from .Line import Line, LineImport
from .ClippingPlane import ClippingPlane, ClippingPlaneImport
from .ViewSetupHints import ViewSetupHints
from .Visibility import Visibility, VisibilityImport
from .Color import Color, ColorImport
from .ViewSetupHints import ViewSetupHintsImport


class VisualizationInfo(JsonToXMLModel):
    SCHEMA_NAME = "visinfo.xsd"

    @property
    def xml(self):
        viewpoint = self.json
        e = self.maker

        children = []

        if (components := viewpoint.get("components")) is not None:
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

        if (orthogonal_camera := viewpoint.get("orthogonal_camera")) is not None:
            xml_ortogonal_camera = OrthogonalCamera(orthogonal_camera).xml
            children.append(xml_ortogonal_camera)

        if (perspective_camera := viewpoint.get("perspective_camera")) is not None:
            xml_perspective_camera = PerspectiveCamera(perspective_camera).xml
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


class VisualizationInfoImport(XMLToJsonModel):
    @property
    def to_python(self):
        viewpoint = {}
        xml = self.xml

        if (perspective_camera := xml.find("PerspectiveCamera")) is not None:
            viewpoint["perspective_camera"] = PerspectiveCameraImport(
                perspective_camera
            ).to_python
        if (orthogonal_camera := xml.find("OrthogonalCamera")) is not None:
            viewpoint["orthogonal_camera"] = OrthogonalCameraImport(
                orthogonal_camera
            ).to_python

        viewpoint["lines"] = [
            LineImport(line.find("Line")).to_python for line in xml.findall("Lines")
        ]
        viewpoint["clipping_planes"] = [
            ClippingPlaneImport(plane.find("ClippingPlane")).to_python
            for plane in xml.findall("ClippingPlanes")
        ]
        if (components := xml.find("Components")) is not None:
            viewpoint["components"] = {}
            if (selection := components.find("Selection")) is not None:
                viewpoint["components"]["selection"] = [
                    ComponentImport(component).to_python
                    for component in selection.findall("Component")
                ]
            if (visibility := components.find("Visibility")) is not None:
                viewpoint["components"]["visibility"] = VisibilityImport(visibility).to_python
                if (hints := components.find("ViewSetupHints")) is not None:
                    viewpoint["components"]["visibility"][
                        "view_setup_hints"
                    ] = ViewSetupHintsImport(hints).to_python

            if (colors := components.find("Coloring")) is not None:
                viewpoint["components"]["coloring"] = [
                    ColorImport(color).to_python for color in colors.findall("Color")
                ]

        return viewpoint
