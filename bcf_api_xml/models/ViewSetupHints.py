from lxml import builder


def boolean_repr(value):
    return "true" if value else "false"


def to_boolean(value):
    return value == "true"


def to_xml(hints):
    e = builder.ElementMaker()
    return e.ViewSetupHints(
        SpacesVisible=boolean_repr(hints["spaces_visible"]),
        SpaceBoundariesVisible=boolean_repr(hints["space_boundaries_visible"]),
        OpeningsVisible=boolean_repr(hints["openings_visible"]),
    )


def to_python(xml):
    return {
        "spaces_visible": to_boolean(xml.get("SpacesVisible")),
        "space_boundaries_visible": to_boolean(xml.get("SpaceBoundariesVisible")),
        "openings_visible": to_boolean(xml.get("OpeningsVisible")),
    }
