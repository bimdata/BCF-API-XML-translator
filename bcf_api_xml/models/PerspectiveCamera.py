from lxml import builder

from bcf_api_xml.models import XYZ


def to_xml(camera):
    e = builder.ElementMaker()
    return e.PerspectiveCamera(
        e.CameraViewPoint(*XYZ.to_xml(camera["camera_view_point"])),
        e.CameraDirection(*XYZ.to_xml(camera["camera_direction"])),
        e.CameraUpVector(*XYZ.to_xml(camera["camera_up_vector"])),
        e.FieldOfView(str(camera["field_of_view"])),
    )


def to_python(xml):
    perspective_camera = {
        "camera_view_point": XYZ.to_python(xml.find("CameraViewPoint")),
        "camera_direction": XYZ.to_python(xml.find("CameraDirection")),
        "camera_up_vector": XYZ.to_python(xml.find("CameraUpVector")),
    }
    if (
        field_of_view := xml.find("FieldOfView")
    ) is not None and field_of_view.text is not None:
        perspective_camera["field_of_view"] = float(field_of_view.text)

    return perspective_camera
