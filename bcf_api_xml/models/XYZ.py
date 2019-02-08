from .models import JsonToXMLModel


class XYZ(JsonToXMLModel):
    @property
    def xml(self):
        point = self.json
        e = self.maker
        return (e.X(str(point["x"])), e.Y(str(point["y"])), e.Z(str(point["z"])))
