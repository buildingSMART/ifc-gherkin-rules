from sqlalchemy import create_engine, Integer, String, Column, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Session, relationship, DeclarativeBase
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.inspection import inspect
from functools import total_ordering
from datetime import datetime
import enum
from sqlalchemy import Enum
import os
import ifcopenshell


DEVELOPMENT = os.environ.get('environment', 'development').lower() == 'development'
NO_POSTGRES = os.environ.get('NO_POSTGRES', '1').lower() in {'1', 'true'}

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

@total_ordering
class OutcomeSeverity(enum.Enum):
    """
    Based on Scotts models.py

    PASS - all validation requirements have been met
    NA - the 'Given' criteria was not met, therefore the validation was not applicable and did not proceed.
    WARNING - validation was performed, with a warning.
    ERROR - a validation requirement is not met
    """
    EXECUTED = 0
    NA = 1
    PASS = 2
    WARNING = 3
    ERROR = 4

    def __ge__(self, other):
        if isinstance(other, OutcomeSeverity):
            return self.value >= other.value

        raise TypeError(f"Unsupported operand type(s) for >=: '{type(self)}' and '{type(other)}'")


if DEVELOPMENT or NO_POSTGRES:
    file_path = os.path.join(os.path.dirname(__file__), "ifc-gherkin.db")
    engine = create_engine(f'sqlite:///{file_path}', connect_args={'check_same_thread': False, 'timeout': 100})
else:
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    password = os.environ['POSTGRES_PASSWORD']
    engine = create_engine(f"postgresql://postgres:{password}@{host}:5432/bimsurfer2")


class Serializable(object):
    def serialize(self, full=False):
        # Transforms data from dataclasses to a dict,
        # storing primary key of references and handling date format
        d = {}
        for attribute in inspect(self).attrs.keys():
            if isinstance(getattr(self, attribute), (list, tuple)):
                if full:
                    d[attribute] = [element.serialize(full) for element in getattr(self, attribute)]
                else:
                    d[attribute] = [element.id for element in getattr(self, attribute)]
            elif isinstance(getattr(self, attribute), datetime.datetime):
                d[attribute] = getattr(self, attribute).strftime("%Y-%m-%d %H:%M:%S")
            else:
                d[attribute] = getattr(self, attribute)
        return d

class Base(DeclarativeBase):
    pass

class IfcInstance(Base, Serializable):
    __tablename__ = 'ifc_instances'

    id = Column(Integer, primary_key=True)

    # @todo there should be the instance numeric id in here as well, in case of
    # non-rooted instances.

    global_id = Column(String)
    # file = Column(Integer, ForeignKey('models.id')) # leave this out for now, not directly related to gherkin
    ifc_type = Column(String)
    # bsdd_results = relationship("bsdd_result")# leave this out for now, not directly related to gherkin
    # syntax_results = relationship("bsdd_result")# leave this out for now, not directly related to gherkin
    # validation_outcomes = relationship("ValidationOutcome")


    def __init__(self, global_id, ifc_type, file):
        self.global_id = global_id
        self.ifc_type = ifc_type
        # self.file = file # leave out for now




class ValidationOutcome(Base):
    __tablename__ = 'gherkin_validation_results'

    id = Column(Integer, primary_key=True)

    outcome_code = Column(Enum(ValidationOutcomeCode), nullable=True)
    observed = Column(JSON, nullable=True)
    expected = Column(JSON, nullable=True)
    feature = Column(String, nullable=True)  # ALS004
    feature_version = Column(Integer)  # 1
    severity = Column(Enum(OutcomeSeverity), nullable=True)  # ERROR = 4

    check_execution_id = Column(Integer)

    ifc_instance_id = Column(Integer) # Reference to IfcInstance, one-to-many
    inst = None

    def __str__(self):
        return(f"Step finished with a/an {self.severity.name} {self.outcome_code.name}. Expected value: {self.expected}. Observed value: {self.observed}. ifc_instance_id: {self.ifc_instance_id}")

    def __hash__(self):
        return hash((self.ifc_instance_id, self.check_execution_id, self.severity, self.feature_version, self.feature, self.observed, self.expected, self.outcome_code))

    def __eq__(self, other):
        if isinstance(other, ValidationOutcome):
            return (self.ifc_instance_id == other.ifc_instance_id and
                    self.check_execution_id == other.check_execution_id and
                    self.severity == other.severity and
                    self.feature_version == other.feature_version and
                    self.feature == other.feature and
                    self.observed == other.observed and
                    self.expected == other.expected and
                    self.outcome_code == other.outcome_code)
        return False



def flush_results_to_db(results):
    with Session(engine) as session:
        for result in results:
            session.add(result)
        session.commit()


def initialize():
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    initialize()
