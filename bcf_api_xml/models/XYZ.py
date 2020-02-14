from lxml import builder


def to_xml(point):
    e = builder.ElementMaker()
    return (e.X(str(point["x"])), e.Y(str(point["y"])), e.Z(str(point["z"])))


def to_python(xml):
    return {
        "x": float(xml.find("X").text),
        "y": float(xml.find("Y").text),
        "z": float(xml.find("Z").text),
    }
