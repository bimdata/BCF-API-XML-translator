from .models import JsonToXMLModel
from .XYZ import XYZ


class ClippingPlane(JsonToXMLModel):
    @property
    def xml(self):
        plane = self.json
        e = self.maker
        return e.ClippingPlane(
            e.Location(*XYZ(plane["location"])), e.Direction(*XYZ(plane["direction"]))
        )
