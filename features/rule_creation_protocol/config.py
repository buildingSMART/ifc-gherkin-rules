from pydantic import BaseModel

class ConfiguredBaseModel(BaseModel):
    """Base Pydantic model with assignment validation enabled.

    Serves as a base class for Pydantic models, enabling validation when instance values are changed.
    """
    class Config:
        validate_assignment = True