from .models import XMLToJsonModel


class ViewpointImport(XMLToJsonModel):
    @property
    def to_python(self):
        viewpoint = {}
        xml = self.xml

        viewpoint["guid"] = xml.get("Guid")

        if (index := xml.find("Index")) is not None:
            viewpoint["index"] = int(index.text)

        if (snapshot_filename := xml.find("Snapshot")) is not None:
            viewpoint["snapshot_filename"] = snapshot_filename.text

        if (viewpoint_filename := xml.find("Viewpoint")) is not None:
            viewpoint["viewpoint_filename"] = viewpoint_filename.text

        return viewpoint
