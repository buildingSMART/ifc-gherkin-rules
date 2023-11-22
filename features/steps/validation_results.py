from sqlalchemy import create_engine, Integer, String, Sequence, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column
from datetime import datetime
import enum
from sqlalchemy import Enum
import os


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


engine = create_engine('sqlite:///poc.db', echo=True)  # TODO -> adapt to production solution


class Base(DeclarativeBase):
    pass


class ValidationResult(Base):
    __tablename__ = 'gherkin_validation_results'

    file = mapped_column(String, nullable=False, primary_key=True)  # "tests/als004/fail-als004-segment-rep-item-type.ifc"
    validated_on = mapped_column(DateTime, nullable=False, primary_key=True)  # datetime.datetime(2023, 11, 21, 23, 47, 21, 418006)
    reference = mapped_column(String, nullable=True)  # ALS004
    scenario = mapped_column(String, nullable=True)  # Agreement on nested elements of IfcAlignment
    severity = mapped_column(Enum(ValidationOutcome), nullable=True)  # ERROR = 3
    code = mapped_column(Enum(ValidationOutcomeCode), nullable=True)  # E00100 = "Relationship Error"
    expected = mapped_column(String(6), nullable=True)  # 3
    observed = mapped_column(String(6), nullable=True)  # 2

    def __repr__(self) -> str:
        return f"ValidationResult(id={self.file!r}, validated_on={self.validated_on!r}, " \
               f"reference={self.reference!r}, scenario={self.scenario!r}, " \
               f"severity={self.severity!r}, code={self.code!r}, " \
               f"expected={self.expected!r}, observed={self.observed!r})"

def define_rule_outcome(error_list):
    if error_list: # TODO -> this will be more complex
        return ValidationOutcome(3)
    else:
        ValidationOutcome(0)

def add_validation_results(context):
    with Session(engine) as session:
        validation_result = ValidationResult(file=os.path.basename(context.config.userdata['input']),
                                             validated_on=datetime.now(),
                                             reference=context.feature.name.split(" ")[0],
                                             scenario=context.scenario.name,
                                             severity=define_rule_outcome(context.errors))
        session.add(validation_result)
        session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
