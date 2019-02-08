from .models import JsonToXMLModel
from .XYZ import XYZ


class Line(JsonToXMLModel):
    @property
    def xml(self):
        line = self.json
        e = self.maker
        return e.Line(
            e.StartPoint(*XYZ(line["start_point"])), e.EndPoint(*XYZ(line["end_point"]))
        )
