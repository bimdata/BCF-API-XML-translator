from .models import JsonToXMLModel, XMLToJsonModel
from .XYZ import XYZ, XYZImport


class Line(JsonToXMLModel):
    @property
    def xml(self):
        line = self.json
        e = self.maker
        return e.Line(
            e.StartPoint(*XYZ(line["start_point"])), e.EndPoint(*XYZ(line["end_point"]))
        )


class LineImport(XMLToJsonModel):
    @property
    def to_python(self):
        xml = self.xml
        return {
            "start_point": XYZImport(xml.find("StartPoint")).to_python,
            "end_point": XYZImport(xml.find("EndPoint")).to_python,
        }
