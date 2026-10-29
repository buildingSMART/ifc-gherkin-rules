import os
import ifcopenshell
import ifcopenshell.template

# Test files for IFC432: only FILE_DESCRIPTION and FILE_SCHEMA differ.
TEST_FILES = [
    # pass
    ("pass-ifc432-referenceview.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [ReferenceView]",)),
    ("pass-ifc432-alignment_basedview.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [Alignment-basedView]",)),
    ("pass-ifc432-referenceview_with_comment_and_option.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [ReferenceView]", "Comment [other keywords do not count as a view]", "Option [SplitLevel: On]")),
    ("pass-ifc432-referenceview_declared_twice.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [ReferenceView]", "ViewDefinition [ReferenceView]")),
    # fail
    ("fail-ifc432-scenario01-two_base_mvds_in_separate_strings.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [Alignment-basedView]", "ViewDefinition [ReferenceView]")),  # as seen in a vendor export on PROD
    ("fail-ifc432-scenario01-two_base_mvds_in_one_string.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [Alignment-basedView, ReferenceView]",)),
    ("fail-ifc432-scenario02-coordinationview_without_version.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [CoordinationView]",)),
    ("fail-ifc432-scenario02-referenceview_v1_2.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [ReferenceView_V1.2]",)),
    ("fail-ifc432-scenario02-notdefined.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [NotDefined]",)),
    ("fail-ifc432-scenario03-add_on_view_with_referenceview.ifc", "IFC4X3_ADD2",
     ("ViewDefinition [ReferenceView]", "ViewDefinition [QuantityTakeOffAddOnView]")),
    # fail, scenario 1: no MVD declared
    ("fail-ifc432-scenario01-no_view_definition.ifc", "IFC4X3_ADD2",
     ("Comment [no ViewDefinition declared]",)),
    ("fail-ifc432-scenario01-empty_description.ifc", "IFC4X3_ADD2",
     ("",)),
    # not applicable: another schema
    ("na-ifc432-other_schema_coordinationview_v2_0_ifc2x3.ifc", "IFC2X3",
     ("ViewDefinition [CoordinationView_V2.0]",)),
]

for file_name, schema_identifier, description in TEST_FILES:
    f = ifcopenshell.template.create(filename=file_name, schema_identifier=schema_identifier)
    f.header.file_description.description = description
    f.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name))
