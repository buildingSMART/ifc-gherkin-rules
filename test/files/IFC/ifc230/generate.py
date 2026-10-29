import os
import ifcopenshell
import ifcopenshell.template

# Test files for IFC230: only FILE_DESCRIPTION and FILE_SCHEMA differ.
TEST_FILES = [
    # pass
    ("pass-ifc230-coordinationview_v2_0.ifc", "IFC2X3",
     ("ViewDefinition [CoordinationView_V2.0]",)),
    ("pass-ifc230-structuralanalysisview.ifc", "IFC2X3",
     ("ViewDefinition [StructuralAnalysisView]",)),
    ("pass-ifc230-coordinationview_with_add_on_views_in_separate_strings.ifc", "IFC2X3",
     ("ViewDefinition [CoordinationView_V2.0]", "ViewDefinition [QuantityTakeOffAddOnView]", "ViewDefinition [SpaceBoundary2ndLevelAddOnView]")),
    ("pass-ifc230-coordinationview_with_add_on_view_in_one_string.ifc", "IFC2X3",
     ("ViewDefinition [CoordinationView_V2.0, QuantityTakeOffAddOnView]",)),
    # fail
    ("fail-ifc230-scenario01-two_base_mvds.ifc", "IFC2X3",
     ("ViewDefinition [CoordinationView_V2.0]", "ViewDefinition [StructuralAnalysisView]")),
    ("fail-ifc230-scenario02-coordinationview_without_version.ifc", "IFC2X3",
     ("ViewDefinition [CoordinationView]",)),
    ("fail-ifc230-scenario03-add_on_view_without_coordinationview.ifc", "IFC2X3",
     ("ViewDefinition [StructuralAnalysisView]", "ViewDefinition [SpaceBoundaryAddonView]")),  # lowercase 'on' occurs in practice
    # fail, scenario 1: no MVD declared
    ("fail-ifc230-scenario01-no_view_definition.ifc", "IFC2X3",
     ("Comment [no ViewDefinition declared]",)),
    ("fail-ifc230-scenario01-empty_description.ifc", "IFC2X3",
     ("",)),
    # not applicable: another schema
    ("na-ifc230-other_schema_referenceview_ifc4x3_add2.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [ReferenceView]",)),
]

for file_name, schema_identifier, description in TEST_FILES:
    f = ifcopenshell.template.create(filename=file_name, schema_identifier=schema_identifier)
    f.header.file_description.description = description
    f.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name))
