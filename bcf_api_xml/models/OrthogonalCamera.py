from .models import JsonToXMLModel, XMLToJsonModel
from .XYZ import XYZ, XYZImport


class OrthogonalCamera(JsonToXMLModel):
    @property
    def xml(self):
        camera = self.json
        e = self.maker
        return e.OrthogonalCamera(
            e.CameraViewPoint(*XYZ(camera["camera_view_point"]).xml),
            e.CameraDirection(*XYZ(camera["camera_direction"]).xml),
            e.CameraUpVector(*XYZ(camera["camera_up_vector"]).xml),
            e.ViewToWorldScale(str(camera["view_to_world_scale"])),
        )


class OrthogonalCameraImport(XMLToJsonModel):
    @property
    def to_python(self):
        xml = self.xml
        return {
            "camera_view_point": XYZImport(xml.find("CameraViewPoint")).to_python,
            "camera_direction": XYZImport(xml.find("CameraDirection")).to_python,
            "camera_up_vector": XYZImport(xml.find("CameraUpVector")).to_python,
            "view_to_world_scale": float(xml.find("ViewToWorldScale").text),
        }
