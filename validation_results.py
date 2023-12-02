from sqlalchemy import create_engine, Integer, String, Column, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Session, mapped_column, sessionmaker, relationship, DeclarativeBase
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
import enum
from sqlalchemy import Enum
import os
import functools
import subprocess

from utils import *


@functools.lru_cache(maxsize=16)
def get_remote(cwd):
    return subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd=cwd).decode('ascii').split('\n')[0]


@functools.lru_cache(maxsize=16)
def get_commits(cwd, feature_file):
    return subprocess.check_output(['git', 'log', '--pretty=format:%h', feature_file], cwd=cwd).decode('ascii').split('\n')


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
    E00150 = "Shape Representation Error"
    E00160 = "Instance Structure Error"
    W00010 = "Alignment contains business logic only"
    W00020 = "Alignment contains geometry only"
    W00030 = "Warning"


class OutcomeSeverity(enum.Enum):
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

class CheckExecution(Base):
    __tablename__ = 'check_executions'
    id = Column(Integer, index=True, unique=True, autoincrement=True, primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    success = Column(Boolean)

    validation_outcomes = relationship("ValidationOutcome", backref="check_execution")

class ValidationOutcome(Base):
    __tablename__ = 'gherkin_validation_results'
    id = mapped_column(Integer, index=True, unique=True, autoincrement=True, primary_key=True)
    code = mapped_column(Enum(ValidationOutcomeCode), nullable=True)  # E00100 = "Relationship Error"
    data = mapped_column(JSON, nullable=True)
    feature = mapped_column(String, nullable=True)  # ALS004
    feature_version = mapped_column(Integer)  # 1
    severity = Column(Enum(OutcomeSeverity), nullable=True)  # ERROR = 3

    check_execution_id = Column(Integer, ForeignKey('check_executions.id'))

    # def __repr__(self) -> str:
    #     return f"ValidationResult(id={self.file!r}, validated_on={self.validated_on!r}, " \
    #            f"reference={self.reference!r}, scenario={self.scenario!r}, " \
    #            f"severity={self.severity!r}, code={self.code!r}, " \
    #            f"expected={self.expected!r}, observed={self.observed!r})"


def define_rule_outcome(context):
    if not context.applicable:
        return OutcomeSeverity.NA
    elif context.errors:  # TODO -> this will be more complex
        return OutcomeSeverity.ERROR
    else:
        return OutcomeSeverity.PASS


def define_outcome_code(context, rule_outcome):
    if rule_outcome == OutcomeSeverity.PASS:
        return ValidationOutcomeCode.P00010
    elif rule_outcome == OutcomeSeverity.NA:
        return ValidationOutcomeCode.N00010
    elif rule_outcome == OutcomeSeverity.WARNING:
        return ValidationOutcomeCode.W00030
    elif rule_outcome == OutcomeSeverity.ERROR:
        validation_keys_set = {code.name for code in ValidationOutcomeCode}
        try:
            return next((tag for tag in context.scenario.tags), next((tag for tag in validation_keys_set if tag in context.tags)))
        except StopIteration:
            raise AssertionError(f'Outcome code not included in tags of .feature file: {context.feature.filename}')


def define_data(context):
    data = {"file": os.path.basename(context.config.userdata['input']),
            "ifc_filepath": context.config.userdata.get('input'),
            "validated_on": str(datetime.now()),
            "expected_value": define_expected_value(context),
            "observed_value": define_observed_value(context), }

    return data


def add_validation_results(context):
    with Session() as session:

        rule_outcome = define_rule_outcome(context)
        outcome_code = define_outcome_code(context, rule_outcome)
        validation_result = ValidationOutcome(code=outcome_code,
                                             data=define_data(context),
                                             feature=context.feature.name.split(" ")[0],
                                             feature_version=define_feature_version(context),
                                             severity=rule_outcome,

                                             check_execution_id=None,
                                             step=context.step.name)
        session.add(validation_result)
        session.commit()


def initialize():
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    initialize()
