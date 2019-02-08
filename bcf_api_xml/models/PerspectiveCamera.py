from .models import JsonToXMLModel
from .XYZ import XYZ


class PerspectiveCamera(JsonToXMLModel):
    @property
    def xml(self):
        camera = self.json
        e = self.maker
        return e.PerspectiveCamera(
            e.CameraViewPoint(*XYZ(camera["camera_view_point"]).xml),
            e.CameraDirection(*XYZ(camera["camera_direction"]).xml),
            e.CameraUpVector(*XYZ(camera["camera_up_vector"]).xml),
            e.FieldOfView(str(camera["field_of_view"])),
        )
