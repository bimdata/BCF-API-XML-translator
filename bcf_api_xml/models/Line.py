from lxml import builder

from bcf_api_xml.models import XYZ


def to_xml(line):
    e = builder.ElementMaker()
    return e.Line(
        e.StartPoint(*XYZ.to_xml(line["start_point"])),
        e.EndPoint(*XYZ.to_xml(line["end_point"])),
    )


def to_python(xml):
    return {
        "start_point": XYZ.to_python(xml.find("StartPoint")),
        "end_point": XYZ.to_python(xml.find("EndPoint")),
    }
