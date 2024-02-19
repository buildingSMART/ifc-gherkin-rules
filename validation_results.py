import os
import sys
from pathlib import Path

import django
from django.core.management import call_command

# @todo importing from random directories is a security hazard, this should be properly passed as a configuration param
current_script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(current_script_dir.parent.parent.parent.parent))

try:
    import apps.ifc_validation_models as ifc_validation_models
except:
    import ifc_validation_models

if Path(ifc_validation_models.__file__).parent == current_script_dir / 'ifc_validation_models':
    # we are using our own submodule
    ifc_validation_models.apps.IfcValidationModelsConfig.name = 'ifc_validation_models'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ifc_validation_models.independent_worker_settings'
else:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.ifc_validation_models.dependent_worker_settings'

django.setup()

try:
    from apps.ifc_validation_models.models import ValidationOutcome, ModelInstance, ValidationTask
except:
    from ifc_validation_models.models import ValidationOutcome, ModelInstance, ValidationTask

OutcomeSeverity = ValidationOutcome.OutcomeSeverity
ValidationOutcomeCode = ValidationOutcome.ValidationOutcomeCode

if __name__ == "__main__":

    call_command(
        'migrate', interactive=False,
    )

    import ifc_validation_models.models as database
    from django.contrib.auth.models import User

    user = User.objects.filter(username='system').first()

    if not user:
        user = User.objects.create(username='system',
                                   email='system',
                                   password='system')

    database.set_user_context(user)

    model = database.Model.objects.create(
        size=1,
        uploaded_by = user
    )

    validation_request = database.ValidationRequest.objects.create(size=1, model_id = 1)
    validation_task = database.ValidationTask.objects.create(request_id=1)