import enum
import os
import sys
from pathlib import Path


import django
from django.core.management import call_command

current_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(str(Path(current_script_dir).parent.parent))

import ifc_validation_models.apps

ifc_validation_models.apps.IfcValidationModelsConfig.name = 'ifc_validation_models'

os.environ['DJANGO_SETTINGS_MODULE'] = 'ifc_validation_models.independent_worker_settings'

# Setup, initialize db and perform migration
django.setup()
call_command(
    'migrate', interactive=False,
)

import ifc_validation_models.models as database
from django.contrib.auth.models import User

# Create a mandatory user and assign to context
user = User.objects.filter(username='JT').first()

if not user:
    user = User.objects.create(username='JT',
                                     email='JT',
                                     password='something funky')
database.set_user_context(user)

from ifc_validation_models.models import ValidationOutcome

# # Interact with the datamodel
# model = database.IfcModel.objects.create(
#     size=1,
#     uploaded_by = user
# )
#
# instance = database.IfcModelInstance.objects.create(
#     stepfile_id=1,
#     model = model
# )
#
#
# validation_request = database.IfcValidationRequest.objects.create(created=datetime.datetime.now())
# validation_task = database.IfcValidationTask.objects.create(request_id=1)

OutcomeSeverity = ValidationOutcome.OutcomeSeverity

OutcomeCode = ValidationOutcome.ValidationOutcomeCode
class ValidationOutcomeCode(enum.Enum):
    """
    Based on Scotts models.py
    """
    P00010 = "PASSED"
    N00010 = "NOT_APPLICABLE"
    E00001 = "SYNTAX_ERROR"
    E00010 = "TYPE_ERROR"
    E00020 = "VALUE_ERROR"
    E00030 = "GEOMETRY_ERROR"
    E00040 = "CARDINALITY_ERROR"
    E00050 = "DUPLICATE_ERROR"
    E00060 = "PLACEMENT_ERROR"
    E00070 = "UNITS_ERROR"
    E00080 = "QUANTITY_ERROR"
    E00090 = "ENUMERATED_VALUE_ERROR"
    E00100 = "RELATIONSHIP_ERROR"
    E00110 = "NAMING_ERROR"
    E00120 = "REFERENCE_ERROR"
    E00130 = "RESOURCE_ERROR"
    E00140 = "DEPRECATION_ERROR"
    E00150 = "SHAPE_REPRESENTATION_ERROR"
    E00160 = "INSTANCE_STRUCTURE_ERROR"
    W00010 = "ALIGNMENT_CONTAINS_BUSINESS_LOGIC_ONLY"
    W00020 = "ALIGNMENT_CONTAINS_GEOMETRY_ONLY"
    W00030 = "WARNING" # @todo q : couple this to Error? e.g. E00010 = VALUE_ERROR with Severity = ERROR, W00030 = VALUE_ERROR with Severity = WARNING?
    X00040 = "EXECUTED"

    def determine_severity(self):
        match self.name[0]:
            case 'X':
                return OutcomeSeverity.EXECUTED
            case 'P':
                return OutcomeSeverity.PASS
            case 'N':
                return OutcomeSeverity.NA
            case 'W':
                return OutcomeSeverity.WARNING
            case 'E':
                return OutcomeSeverity.ERROR
            case _:
                raise ValueError(f"Outcome code {self.name} not recognized")