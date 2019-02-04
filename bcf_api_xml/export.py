import os.path as path
from lxml import etree, builder

SCHEMA_DIR = path.realpath(path.join(path.dirname(__file__), "../BCF-XML/Schemas"))

with open(path.join(SCHEMA_DIR, "markup.xsd"), "r") as file:
    markup_schema = etree.XMLSchema(file=file)
with open(path.join(SCHEMA_DIR, "project.xsd"), "r") as file:
    project_schema = etree.XMLSchema(file=file)
with open(path.join(SCHEMA_DIR, "version.xsd"), "r") as file:
    version_schema = etree.XMLSchema(file=file)
with open(path.join(SCHEMA_DIR, "visinfo.xsd"), "r") as file:
    visinfo_schema = etree.XMLSchema(file=file)


def is_valid_with_schema(schema_name, xml):
    schema_path = path.join(SCHEMA_DIR, schema_name)
    with open(schema_path, "r") as file:
        schema = etree.XMLSchema(file=file)

    if not schema.validate(xml):
        print("NOT VALID with", schema_path)
        print(schema.error_log)
        return False
    return True


def boolean_repr(value):
    return "true" if value else "false"


def format_topic(topic):
    e = builder.ElementMaker()
    xml_topic = e.Topic(
        e.Title(topic["title"]),
        e.Priority(topic["title"]),
        e.Index(topic["title"]),
        e.Labels(topic["title"]),
        e.CreationDate(topic["title"]),
        e.CreationAuthor(topic["title"]),
        e.ModifiedDate(topic["title"]),
        e.ModifiedAuthor(topic["title"]),
        e.DueDate(topic["title"]),
        e.AssignedTo(topic["title"]),
        e.Description(topic["title"]),
        e.Stage(topic["title"]),
        Guid=topic["guid"],
        TopicType=topic["topic_type"],
        TopicStatus=topic["topic_status"],
    )
    return xml_topic


def format_comment(comment):
    e = builder.ElementMaker()
    xml_comment = e.Comment(
        e.Date(comment["date"]),
        e.Author(comment["author"]),
        e.Comment(comment["comment"]),
        e.ModifiedDate(comment["modified_date"]),
        e.ModifiedAuthor(comment["modified_author"]),
        e.Viewpoint(Guid=comment["viewpoint_guid"]),
    )
    return xml_comment


def format_component(component):
    e = builder.ElementMaker()
    return e.Component(IfcGuid=component["ifc_guid"])


def format_viewpoint(viewpoint):
    e = builder.ElementMaker()

    orthogonal_camera = viewpoint["orthogonal_camera"]
    xml_ortogonal_camera = e.OrthogonalCamera(
        e.CameraViewPoint(
            e.X(str(orthogonal_camera["camera_view_point"]["x"])),
            e.Y(str(orthogonal_camera["camera_view_point"]["y"])),
            e.Z(str(orthogonal_camera["camera_view_point"]["z"])),
        ),
        e.CameraDirection(
            e.X(str(orthogonal_camera["camera_direction"]["x"])),
            e.Y(str(orthogonal_camera["camera_direction"]["y"])),
            e.Z(str(orthogonal_camera["camera_direction"]["z"])),
        ),
        e.CameraUpVector(
            e.X(str(orthogonal_camera["camera_up_vector"]["x"])),
            e.Y(str(orthogonal_camera["camera_up_vector"]["y"])),
            e.Z(str(orthogonal_camera["camera_up_vector"]["z"])),
        ),
        e.ViewToWorldScale(str(orthogonal_camera["view_to_world_scale"])),
    )

    perspective_camera = viewpoint["perspective_camera"]
    xml_perspective_camera = e.PerspectiveCamera(
        e.CameraViewPoint(
            e.X(str(perspective_camera["camera_view_point"]["x"])),
            e.Y(str(perspective_camera["camera_view_point"]["y"])),
            e.Z(str(perspective_camera["camera_view_point"]["z"])),
        ),
        e.CameraDirection(
            e.X(str(perspective_camera["camera_direction"]["x"])),
            e.Y(str(perspective_camera["camera_direction"]["y"])),
            e.Z(str(perspective_camera["camera_direction"]["z"])),
        ),
        e.CameraUpVector(
            e.X(str(perspective_camera["camera_up_vector"]["x"])),
            e.Y(str(perspective_camera["camera_up_vector"]["y"])),
            e.Z(str(perspective_camera["camera_up_vector"]["z"])),
        ),
        e.FieldOfView(str(perspective_camera["field_of_view"])),
    )

    lines = viewpoint["lines"]
    xml_lines = []
    for line in lines:
        xml_line = e.Line(
            e.StartPoint(
                e.X(str(line["start_point"]["x"])),
                e.Y(str(line["start_point"]["y"])),
                e.Z(str(line["start_point"]["z"])),
            ),
            e.EndPoint(
                e.X(str(line["end_point"]["x"])),
                e.Y(str(line["end_point"]["y"])),
                e.Z(str(line["end_point"]["z"])),
            ),
        )
        xml_lines.push(xml_line)

    planes = viewpoint["clipping_planes"]
    xml_planes = []
    for plane in planes:
        xml_plane = e.ClippingPlane(
            e.Location(
                e.X(str(plane["location"]["x"])),
                e.Y(str(plane["location"]["y"])),
                e.Z(str(plane["location"]["z"])),
            ),
            e.Direction(
                e.X(str(plane["direction"]["x"])),
                e.Y(str(plane["direction"]["y"])),
                e.Z(str(plane["direction"]["z"])),
            ),
        )
        xml_planes.push(xml_plane)

    components = viewpoint["components"]

    selections = components["selection"]
    xml_selections = [format_component(selection) for selection in selections]

    colorings = components["coloring"]
    xml_colorings = []
    for coloring in colorings:
        xml_color = e.Color(
            *[format_component(component) for component in coloring["components"]],
            Color=coloring["color"],
        )
        xml_colorings.push(xml_color)

    visibility = components["visibility"]
    view_setup_hints = visibility["view_setup_hints"]

    xml_view_setup_hints = e.ViewSetupHints(
        SpacesVisible=boolean_repr(view_setup_hints["spaces_visible"]),
        SpaceBoundariesVisible=boolean_repr(
            view_setup_hints["space_boundaries_visible"]
        ),
        OpeningsVisible=boolean_repr(view_setup_hints["openings_visible"]),
    )

    exceptions = [format_component(component) for component in visibility["exceptions"]]
    xml_visibility = e.Visibility(
        e.Exceptions(*exceptions) if exceptions else "",
        DefaultVisibility=boolean_repr(visibility["default_visibility"]),
    )

    xml_visinfo = e.VisualizationInfo(
        e.Components(
            xml_view_setup_hints,
            e.Selection(*xml_selections),
            xml_visibility,
            e.Coloring(*xml_colorings) if xml_colorings else "",
        ),
        xml_ortogonal_camera,
        xml_perspective_camera,
        e.Lines(*xml_lines) if xml_lines else "",
        e.ClippingPlanes(*xml_planes),
        Guid=viewpoint["guid"],
    )
    is_valid_with_schema("visinfo.xsd", xml_visinfo)

    xml_viewpoint = e.ViewPoint(
        # e.Viewpoint(viewpoint["title"]),  # .bcfv file path
        # e.Snapshot(viewpoint["title"]),  # .png file path
        e.Index(str(viewpoint["index"])),
        Guid=viewpoint["guid"],
    )
    return xml_viewpoint, xml_visinfo


print(markup_schema)
print(project_schema)
print(version_schema)
print(visinfo_schema)
