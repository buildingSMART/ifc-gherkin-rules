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
django.setup()

from ifc_validation_models.models import ValidationOutcome

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

    instance = database.ModelInstance.objects.create(
        stepfile_id=1,
        model = model
    )

    validation_request = database.ValidationRequest.objects.create(size=1)
    validation_task = database.ValidationTask.objects.create(request_id=1)