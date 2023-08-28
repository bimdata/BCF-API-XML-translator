from lxml import builder

from bcf_api_xml.models import XYZ


def to_xml(camera):
    e = builder.ElementMaker()
    return e.OrthogonalCamera(
        e.CameraViewPoint(*XYZ.to_xml(camera["camera_view_point"])),
        e.CameraDirection(*XYZ.to_xml(camera["camera_direction"])),
        e.CameraUpVector(*XYZ.to_xml(camera["camera_up_vector"])),
        e.ViewToWorldScale(str(camera["view_to_world_scale"])),
    )


def to_python(xml):
    orthogonal_camera = {
        "camera_view_point": XYZ.to_python(xml.find("CameraViewPoint")),
        "camera_direction": XYZ.to_python(xml.find("CameraDirection")),
        "camera_up_vector": XYZ.to_python(xml.find("CameraUpVector")),
    }
    if (
        view_to_world_scale := xml.find("ViewToWorldScale")
    ) is not None and view_to_world_scale.text is not None:
        orthogonal_camera["view_to_world_scale"] = float(view_to_world_scale.text)

    return orthogonal_camera
