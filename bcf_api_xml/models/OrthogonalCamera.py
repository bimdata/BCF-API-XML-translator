from .models import JsonToXMLModel
from .XYZ import XYZ


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
