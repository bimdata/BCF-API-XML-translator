from lxml import builder


def to_xml(viewpoint, is_first):
    e = builder.ElementMaker()
    viewpoint_name = "viewpoint.bcfv" if is_first else (viewpoint["guid"] + ".bcfv")
    snapshot_name = "snapshot.png" if is_first else (viewpoint["guid"] + ".png")

    return e.Viewpoints(
        e.Viewpoint(viewpoint_name),
        e.Snapshot(snapshot_name),
        e.Index(str(viewpoint["index"])),
        Guid=str(viewpoint["guid"]),
    )


def to_python(xml):
    viewpoint = {"guid": xml.get("Guid")}

    if (index := xml.find("Index")) is not None and index.text is not None:
        viewpoint["index"] = int(index.text)

    if (snapshot_filename := xml.find("Snapshot")) is not None:
        viewpoint["snapshot_filename"] = snapshot_filename.text

    if (viewpoint_filename := xml.find("Viewpoint")) is not None:
        viewpoint["viewpoint_filename"] = viewpoint_filename.text

    return viewpoint
