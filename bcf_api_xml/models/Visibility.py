from lxml import builder

from bcf_api_xml.models import Component


def boolean_repr(value):
    return "true" if value else "false"


def to_boolean(value):
    return value == "true"


def to_xml(visibility):
    e = builder.ElementMaker()
    children = []
    if exceptions := visibility.get("exceptions"):
        components = [
            Component.to_xml(component)
            for component in exceptions
            if component.get("ifc_guid")
        ]
        children.append(e.Exceptions(*components))
    return e.Visibility(
        *children, DefaultVisibility=boolean_repr(visibility["default_visibility"])
    )


def to_python(xml):
    visibility = {
        "default_visibility": xml.get("DefaultVisibility"),
    }
    if (exceptions := xml.find("Exceptions")) is not None:
        visibility["exceptions"] = [
            Component.to_python(component) for component in exceptions.findall("Component")
        ]

    return visibility
