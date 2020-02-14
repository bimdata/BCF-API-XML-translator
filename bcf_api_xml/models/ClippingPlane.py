from .models import JsonToXMLModel, XMLToJsonModel
from .XYZ import XYZ, XYZImport


class ClippingPlane(JsonToXMLModel):
    @property
    def xml(self):
        plane = self.json
        e = self.maker
        return e.ClippingPlane(
            e.Location(*XYZ(plane["location"])), e.Direction(*XYZ(plane["direction"]))
        )


class ClippingPlaneImport(XMLToJsonModel):
    @property
    def to_python(self):
        xml = self.xml
        return {
            "location": XYZImport(xml.find("Location")).to_python,
            "direction": XYZImport(xml.find("Direction")).to_python,
        }
