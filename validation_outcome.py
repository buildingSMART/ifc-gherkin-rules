import ifcopenshell
from typing import Optional, Union, Tuple, Any, List, Literal

from pydantic import ConfigDict, model_validator

from pydantic import BaseModel, ConfigDict

class ConfiguredBaseModel(BaseModel):
    """Base Pydantic model with assignment validation enabled.

    Serves as a base class for Pydantic models, enabling validation when instance values are changed.
    """
    model_config = ConfigDict(validate_assignment=True)

class Scenario(ConfiguredBaseModel):
    name : str = ""
    steps: List[Any] = []
    latest_step: str = ""
    feature: Optional['Feature'] = None
    validation_results : List['ValidationOutcome'] = []

    @model_validator(mode='before')
    def add_to_feature(cls, values):
        """
        Ensure bilaterial relationship between feature and scenario
        """
        feature = values.get('feature')
        if feature:
            scenario = cls.model_construct(_fields_set=values.keys(), **values)
            if scenario not in feature.scenario_list:
                feature.scenario_list.append(scenario)
        return values
    
    def __eq__(self, other):
        """
        Prevent duplicates in the 'scenario_list' of a Feature.
        This ensures accurate retrieval of scenarios associated with a specific feature.
        """
        if not isinstance(other, Scenario):
            return False
        return [step['name'] for step in self.steps] == [step['name'] for step in other.steps]

    def __hash__(self):
        return hash(tuple(step['name'] for step in self.steps))


class Feature(ConfiguredBaseModel):
    name : str = "" # as in Feature : 'ABC001 - Test Alignment Rule'
    description: str = "" # 'This rule verifies that alignment is correct'
    filename : str = "" # ABC001_Test-alignment-rule
    location : str = "" 
    github_source_location : str = ''
    version : int = 1
    tags: List[str] = []
    scenario_list : List['Scenario'] = []


class ValidationOutcome(ConfiguredBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    severity : Literal['failed', 'passed'] = "passed"
    disabled : bool = False
    message : str = ""
    scenario : Optional[Scenario] = None
    feature : Feature
    ifc_filepath : str = ""
    inst: Optional[Union[str, Tuple[Any, Any], ifcopenshell.entity_instance]] = None


    @model_validator(mode='before')
    def add_to_scenario(cls, values):
        """
        Ensure bilaterial relationship between feature and scenario
        """
        scenario = values.get('scenario')
        if scenario:
            result = cls.model_construct(_fields_set=values.keys(), **values)
            if result not in scenario.validation_results:
                scenario.validation_results.append(result)
        return values
    