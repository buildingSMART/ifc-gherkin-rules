import os
from dataclasses import dataclass, asdict
import json

@dataclass
class ExceptionSummary:
    """
    Custom exception for summarizing internal errors during feature validation.
    The exception is forwarded to the JSON output and later evaluated after the Behave run using pytest.
    Errors occurring at any stage of the step implementation or while running the custom decorator are captured by this exception.
    """
    feature: str
    step: str
    error_type: str
    location: str

    @staticmethod
    def extract_traceback_summary(exc_traceback):
        trace = {}
        
        current_tb = exc_traceback
        while current_tb is not None:
            filename = os.path.basename(current_tb.tb_frame.f_code.co_filename)  
            line_number = current_tb.tb_lineno
            
            if filename not in trace:
                trace[filename] = [line_number]
            elif line_number not in trace[filename]:
                trace[filename].append(line_number)
            
            current_tb = current_tb.tb_next
        
        trace_list = []
        for filename in reversed(trace):
            line_numbers = ", ".join(f"#{ln}" for ln in trace[filename])
            trace_list.append(f"{filename}(l{line_numbers})")
        
        
        return ", ".join(trace_list)

    @classmethod
    def from_context(cls, context):
        feature_name = context.feature.name
        step_name = context.step.name
        error_type = str(context.step.exception.__class__.__name__)
        location = cls.extract_traceback_summary(context.step.exc_traceback)
        
        return cls(feature=feature_name, step=step_name, error_type=error_type, location=location)
    
    def to_dict(self):
        return asdict(self)