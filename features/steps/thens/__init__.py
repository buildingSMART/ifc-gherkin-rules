import sys
import os
from pathlib import Path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(str(Path(current_script_dir).parent.parent))
from validation_results import IfcValidationOutcome

OutcomeSeverity = IfcValidationOutcome.OutcomeSeverity