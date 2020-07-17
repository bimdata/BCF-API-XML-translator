from lxml import builder

from bcf_api_xml.models import XYZ


def to_xml(plane):
    e = builder.ElementMaker()
    return e.ClippingPlane(
        e.Location(*XYZ.to_xml(plane["location"])),
        e.Direction(*XYZ.to_xml(plane["direction"])),
    )


def to_python(xml):
    return {
        "location": XYZ.to_python(xml.find("Location")),
        "direction": XYZ.to_python(xml.find("Direction")),
    }
