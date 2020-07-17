from lxml import builder

from bcf_api_xml.models import Component


def to_xml(coloring):
    e = builder.ElementMaker()
    return e.Color(
        *[Component.to_xml(component) for component in coloring["components"]],
        Color=coloring["color"],
    )


def to_python(xml):
    return {
        "color": xml.get("Color"),
        "components": [
            Component.to_python(component) for component in xml.findall("Component")
        ],
    }
