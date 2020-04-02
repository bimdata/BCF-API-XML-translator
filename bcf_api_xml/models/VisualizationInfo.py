from lxml import builder
from bcf_api_xml.models import (
    Component,
    OrthogonalCamera,
    PerspectiveCamera,
    Line,
    ClippingPlane,
    ViewSetupHints,
    Visibility,
    Color,
)


def to_xml(viewpoint):
    e = builder.ElementMaker()

    children = []

    if (components := viewpoint.get("components")) is not None:
        visibility = components.get("visibility")

        components_children = []

        if visibility and (view_setup_hints := visibility.get("view_setup_hints")) is not None:
            components_children.append(ViewSetupHints.to_xml(view_setup_hints))

        xml_selections = [
            Component.to_xml(component)
            for component in components.get("selection", [])
            if component.get("ifc_guid")
        ]
        if xml_selections:
            components_children.append(e.Selection(*xml_selections))

        if visibility:
            components_children.append(Visibility.to_xml(visibility))

        xml_colorings = [Color.to_xml(coloring) for coloring in components.get("coloring", [])]
        if xml_colorings:
            components_children.append(e.Coloring(*xml_colorings))

        children.append(e.Components(*components_children))

    if (orthogonal_camera := viewpoint.get("orthogonal_camera")) is not None:
        xml_ortogonal_camera = OrthogonalCamera.to_xml(orthogonal_camera)
        children.append(xml_ortogonal_camera)

    if (perspective_camera := viewpoint.get("perspective_camera")) is not None:
        xml_perspective_camera = PerspectiveCamera.to_xml(perspective_camera)
        children.append(xml_perspective_camera)

    xml_lines = [Line.to_xml(line) for line in viewpoint.get("lines", [])]
    if xml_lines:
        children.append(e.Lines(*xml_lines))

    xml_planes = [
        ClippingPlane.to_xml(plane) for plane in viewpoint.get("clipping_planes", [])
    ]
    if xml_planes:
        children.append(e.ClippingPlanes(*xml_planes))

    return e.VisualizationInfo(*children, Guid=str(viewpoint["guid"]))


def to_python(xml):
    viewpoint = {}
    if (perspective_camera := xml.find("PerspectiveCamera")) is not None:
        viewpoint["perspective_camera"] = PerspectiveCamera.to_python(perspective_camera)
    if (orthogonal_camera := xml.find("OrthogonalCamera")) is not None:
        viewpoint["orthogonal_camera"] = OrthogonalCamera.to_python(orthogonal_camera)

    viewpoint["lines"] = [
        Line.to_python(line.find("Line"))
        for line in xml.findall("Lines")
        if line.find("Line") is not None
    ]
    viewpoint["clipping_planes"] = [
        ClippingPlane.to_python(plane.find("ClippingPlane"))
        for plane in xml.findall("ClippingPlanes")
        if plane.find("ClippingPlane") is not None
    ]
    if (components := xml.find("Components")) is not None:
        viewpoint["components"] = {}
        if (selection := components.find("Selection")) is not None:
            viewpoint["components"]["selection"] = [
                Component.to_python(component) for component in selection.findall("Component")
            ]
        if (visibility := components.find("Visibility")) is not None:
            viewpoint["components"]["visibility"] = Visibility.to_python(visibility)
            if (hints := components.find("ViewSetupHints")) is not None:
                viewpoint["components"]["visibility"][
                    "view_setup_hints"
                ] = ViewSetupHints.to_python(hints)

        if (colors := components.find("Coloring")) is not None:
            viewpoint["components"]["coloring"] = [
                Color.to_python(color) for color in colors.findall("Color")
            ]

    return viewpoint
