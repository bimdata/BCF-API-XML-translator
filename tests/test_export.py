from bcf_api_xml import export


TEST_VIEWPOINT = {
    "index": 1,
    "guid": "386fd073-e917-4d5b-95cb-889f03b855c2",
    "orthogonal_camera": {
        "view_to_world_scale": 41.7600572814024,
        "camera_direction": {
            "x": 25.0320091247559,
            "y": -4.7735333442688,
            "z": 12.3861236572266,
        },
        "camera_up_vector": {
            "x": 0.247033074498177,
            "y": 0.913663029670715,
            "z": 0.32279160618782,
        },
        "camera_view_point": {
            "x": -5.91817426681519,
            "y": 17.8825130462646,
            "z": -28.0556755065918,
        },
    },
    "perspective_camera": {
        "field_of_view": 60.0,
        "camera_direction": {
            "x": 25.0320091247559,
            "y": -4.7735333442688,
            "z": 12.3861236572266,
        },
        "camera_up_vector": {
            "x": 0.247033074498177,
            "y": 0.913663029670715,
            "z": 0.32279160618782,
        },
        "camera_view_point": {
            "x": -5.91817426681519,
            "y": 17.8825130462646,
            "z": -28.0556755065918,
        },
    },
    "lines": [],
    "clipping_planes": [],
    "snapshot": {
        "snapshot_type": "png",
        "snapshot_data": "data:image/png;base64,iVBORw0KGgoAAAA5CYII=",
    },
    "components": {
        "coloring": [],
        "visibility": {
            "default_visibility": True,
            "exceptions": [],
            "view_setup_hints": {
                "spaces_visible": False,
                "space_boundaries_visible": False,
                "openings_visible": False,
            },
        },
        "selection": [
            {
                "ifc_guid": "1NGqMK$rr6deAkvyvBfweO",
                "originating_system": "BIMData.io",
                "authoring_tool_id": "BIMViewer/v1.0",
            },
            {
                "ifc_guid": "2WdxFq7sf6hwiNbwPomafz",
                "originating_system": "BIMData.io",
                "authoring_tool_id": "BIMViewer/v1.0",
            },
            {
                "ifc_guid": "0dWoULYUH3zPg8qJpTnRGv",
                "originating_system": "BIMData.io",
                "authoring_tool_id": "BIMViewer/v1.0",
            },
            {
                "ifc_guid": "1RoAsT5gfDsesFmCMQyIlY",
                "originating_system": "BIMData.io",
                "authoring_tool_id": "BIMViewer/v1.0",
            },
            {
                "ifc_guid": "3Yy1v4SdfCqR4wq4R8kMar",
                "originating_system": "BIMData.io",
                "authoring_tool_id": "BIMViewer/v1.0",
            },
            {
                "ifc_guid": "3Yy1v4SdfCqR4wq4R8kMbN",
                "originating_system": "BIMData.io",
                "authoring_tool_id": "BIMViewer/v1.0",
            },
        ],
    },
}


class TestExportViewpoint:
    def test_viewpoint_validity(self):
        xml_viewpoint, xml_visinfo = export.format_viewpoint(TEST_VIEWPOINT)
        assert export.is_valid_with_schema("visinfo.xsd", xml_visinfo)
