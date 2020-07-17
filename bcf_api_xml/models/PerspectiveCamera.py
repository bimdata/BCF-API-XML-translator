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
    return {
        "camera_view_point": XYZ.to_python(xml.find("CameraViewPoint")),
        "camera_direction": XYZ.to_python(xml.find("CameraDirection")),
        "camera_up_vector": XYZ.to_python(xml.find("CameraUpVector")),
        "field_of_view": float(xml.find("FieldOfView").text),
    }
