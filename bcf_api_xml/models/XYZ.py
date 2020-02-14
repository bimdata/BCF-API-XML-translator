from .models import JsonToXMLModel, XMLToJsonModel


class XYZ(JsonToXMLModel):
    @property
    def xml(self):
        point = self.json
        e = self.maker
        return (e.X(str(point["x"])), e.Y(str(point["y"])), e.Z(str(point["z"])))


class XYZImport(XMLToJsonModel):
    @property
    def to_python(self):
        xml = self.xml
        return {
            "x": float(xml.find("X").text),
            "y": float(xml.find("Y").text),
            "z": float(xml.find("Z").text),
        }
