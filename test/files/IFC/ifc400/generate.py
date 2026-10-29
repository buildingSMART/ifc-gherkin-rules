import os
import ifcopenshell
import ifcopenshell.template

# Test files for IFC400: only FILE_DESCRIPTION and FILE_SCHEMA differ.
TEST_FILES = [
    # pass
    ("pass-ifc400-referenceview_v1_2.ifc", "IFC4",
     ("ViewDefinition [ReferenceView_V1.2]",)),
    ("pass-ifc400-ifc4precast.ifc", "IFC4",
     ("ViewDefinition [IFC4Precast]",)),
    ("pass-ifc400-referenceview_v1_2_with_comment_and_option.ifc", "IFC4",
     ("ViewDefinition [ReferenceView_V1.2]", "Comment [other keywords do not count as a view]", "Option [SplitLevel: On]")),
    # fail
    ("fail-ifc400-scenario01-two_base_mvds.ifc", "IFC4",
     ("ViewDefinition [ReferenceView_V1.2]", "ViewDefinition [IFC4Precast]")),
    ("fail-ifc400-scenario02-coordinationview_v2_0.ifc", "IFC4",
     ("ViewDefinition [CoordinationView_V2.0]",)),
    ("fail-ifc400-scenario03-add_on_view_with_referenceview_v1_2.ifc", "IFC4",
     ("ViewDefinition [ReferenceView_V1.2, SpaceBoundary2ndLevelAddOnView]",)),
    # fail, scenario 1: no MVD declared
    ("fail-ifc400-scenario01-no_view_definition.ifc", "IFC4",
     ("Comment [no ViewDefinition declared]",)),
    ("fail-ifc400-scenario01-empty_description.ifc", "IFC4",
     ("",)),
    # not applicable: another schema
    ("na-ifc400-other_schema_coordinationview_v2_0_ifc2x3.ifc", "IFC2X3",
     ("ViewDefinition [CoordinationView_V2.0]",)),
]

for file_name, schema_identifier, description in TEST_FILES:
    f = ifcopenshell.template.create(filename=file_name, schema_identifier=schema_identifier)
    f.header.file_description.description = description
    f.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name))
