from sqlalchemy import create_engine, Integer, String, Sequence, DateTime, Identity
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session, mapped_column, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
import enum
from sqlalchemy import Enum
import os

DEVELOPMENT = os.environ.get('environment', 'production').lower() == 'development'
NO_POSTGRES = os.environ.get('NO_POSTGRES', '0').lower() in {'1', 'true'}

class ValidationOutcomeCode(enum.Enum):
    """
    Based on Scotts models.py
    """
    P00010 = "Passed"
    N00010 = "Not applicable"
    E00001 = "Syntax Error"
    E00010 = "Type Error"
    E00020 = "Value Error"
    E00030 = "Geometry Error"
    E00040 = "Cardinality Error"
    E00050 = "Duplicate Error"
    E00060 = "Placement Error"
    E00070 = "Units Error"
    E00080 = "Quantity Error"
    E00090 = "Enumerated Value Error"
    E00100 = "Relationship Error"
    E00110 = "Naming Error"
    E00120 = "Reference Error"
    E00130 = "Resource Error"
    E00140 = "Deprecation Error"
    W00010 = "Alignment contains business logic only"
    W00020 = "Alignment contains geometry only"
    W00030 = "Warning"


class ValidationOutcome(enum.Enum):
    """
    Based on Scotts models.py

    PASS - all validation requirements have been met
    NA - the 'Given' criteria was not met, therefore the validation was not applicable and did not proceed.
    WARNING - validation was performed, with a warning.
    ERROR - a validation requirement is not met
    """
    PASS = 0
    NA = 1
    WARNING = 2
    ERROR = 3


if DEVELOPMENT or NO_POSTGRES:
    file_path = os.path.join(os.path.dirname(__file__), "ifc-gherkin.db") 
    engine = create_engine(f'sqlite:///{file_path}', connect_args={'check_same_thread': False, 'timeout': 100})
else:
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    password = os.environ['POSTGRES_PASSWORD']
    engine = create_engine(f"postgresql://postgres:{password}@{host}:5432/bimsurfer2")

Session = sessionmaker(bind=engine)
class Base(DeclarativeBase):
    pass

class ValidationResult(Base):
    __tablename__ = 'gherkin_validation_results'
    id = mapped_column(Integer, index=True, unique=True, autoincrement=True, primary_key=True)
    file = mapped_column(String, nullable=False)  # "tests/als004/fail-als004-segment-rep-item-type.ifc"
    validated_on = mapped_column(DateTime, nullable=False)  # datetime.datetime(2023, 11, 21, 23, 47, 21, 418006)
    reference = mapped_column(String, nullable=True)  # ALS004
    step = mapped_column(String, nullable=True)  # Every edge must be referenced exactly 2 times by the loops of the face # TODO -> scenario based? A bit harder to implement.
    severity = mapped_column(Enum(ValidationOutcome), nullable=True)  # ERROR = 3
    code = mapped_column(Enum(ValidationOutcomeCode), nullable=True)  # E00100 = "Relationship Error"
    expected = mapped_column(String(6), nullable=True)  # 3
    observed = mapped_column(String(6), nullable=True)  # 2

    def __repr__(self) -> str:
        return f"ValidationResult(id={self.file!r}, validated_on={self.validated_on!r}, " \
               f"reference={self.reference!r}, scenario={self.scenario!r}, " \
               f"severity={self.severity!r}, code={self.code!r}, " \
               f"expected={self.expected!r}, observed={self.observed!r})"

def define_rule_outcome(context):
    if not context.applicable:
        return ValidationOutcome(1)
    elif context.errors: # TODO -> this will be more complex
        return ValidationOutcome(3)
    else:
        return ValidationOutcome(0)

def define_outcome_code(context, rule_outcome):
    if rule_outcome == ValidationOutcome(0):
        return ValidationOutcomeCode("Passed")
    elif rule_outcome == ValidationOutcome(1):
        return ValidationOutcomeCode("Not applicable")
    elif rule_outcome == ValidationOutcome(2):
        return ValidationOutcomeCode("Warning")
    elif rule_outcome == ValidationOutcome(3):
        return context.errors[0].code # TODO -> not sure if always 0 index

# def define_outcome_code(context, rule_outcome)

def add_validation_results(context):
    with Session() as session:
        rule_outcome = define_rule_outcome(context)
        outcome_code = define_outcome_code(context, rule_outcome)
        validation_result = ValidationResult(file=os.path.basename(context.config.userdata['input']),
                                             validated_on=datetime.now(),
                                             reference=context.feature.name.split(" ")[0],
                                             step=context.step.name,
                                             severity=rule_outcome,
                                             code=outcome_code,)
        session.add(validation_result)
        session.commit()

def initialize():
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    initialize()