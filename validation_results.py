from sqlalchemy import create_engine, Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.orm import Session, mapped_column, sessionmaker, relationship, DeclarativeBase
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
import enum
from sqlalchemy import Enum
import os
import functools
import subprocess

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

class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False) # as in Feature : 'ABC001 - Test Alignment Rule'
    description = Column(String) # 'This rule verifies that alignment is correct'
    filename = Column(String) # ABC001_Test-alignment-rule
    location = Column(String) # location in repository
    github_source_location = Column(String)
    version = Column(Integer)
    _tags = Column('tags', String)

    @property # in case JSON is not supported, e.g. with SQLite, convert to list for use in Python
    def tags(self):
        return self._tags.split(',') if self._tags else []

    @tags.setter
    def tags(self, tags_list):
        self._tags = ','.join(tags_list)

    # Other fields as necessary
    scenarios = relationship("Scenario", back_populates="feature")

    def add_feature(context, name, description=None, filename=None, location=None, github_source_location=None, version=None, tags=None):
        cwd = os.path.dirname(__file__)
        remote = get_remote(cwd)
        shas = get_commits(cwd, context.feature.filename)

        with Session() as session:
            new_feature = Feature(
                name=context,
                description=context.feature.description[0],
                filename=context.feature.filename,
                github_source_location=f"{remote}/blob/{shas[0]}/{context.feature.filename}",
                version=len(shas),
                _tags=','.join(context.tags) if context.tags else None
            )
            session.add(new_feature)
            session.commit()
            return new_feature

class Scenario(Base):
    __tablename__ = 'scenarios'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    feature_id = Column(Integer, ForeignKey('features.id'))
    feature = relationship("Feature", back_populates="scenarios")
    validation_results = relationship("ValidationResult", back_populates="scenario", primaryjoin="Scenario.id == ValidationResult.scenario_id")
    _steps = Column('steps'), String

    @property # in case JSON is not supported, e.g. with SQLite, convert to list for use in Python
    def steps(self):
        return self._steps.split(',') if self._steps else []

    @steps.setter
    def steps(self, steps_list):
        self._steps = ','.join(steps_list)


    def add_scenario(context):
        with Session() as session:
            feature = session.query(Feature).filter_by(name=context.scenario.feature.name).first() #todo make search more explicit
            new_scenario = Scenario(
                name=context.scenario.name,
                feature_id=feature.id,
                _steps=','.join([step.name for step in context.scenario.steps])
            )
            session.add(new_scenario)
            session.commit()
            return new_scenario

class ValidationResult(Base):
    __tablename__ = 'gherkin_validation_results'
    id = mapped_column(Integer, index=True, unique=True, autoincrement=True, primary_key=True)
    check_execution_id = mapped_column(Integer, nullable=True) # id connecting to CheckExecution table
    file = mapped_column(String, nullable=False)  # "tests/als004/fail-als004-segment-rep-item-type.ifc"
    validated_on = mapped_column(DateTime, nullable=False)  # datetime.datetime(2023, 11, 21, 23, 47, 21, 418006)
    reference = mapped_column(String, nullable=True)  # ALS004
    step = mapped_column(String, nullable=True)  # Every edge must be referenced exactly 2 times by the loops of the face # TODO -> scenario based? A bit harder to implement.
    severity = mapped_column(Enum(ValidationOutcome), nullable=True)  # ERROR = 3
    code = mapped_column(Enum(ValidationOutcomeCode), nullable=True)  # E00100 = "Relationship Error"
    feature_version = mapped_column(Integer) # 1
    expected = mapped_column(String, nullable=True)
    observed = mapped_column(String, nullable=True)
    ifc_filepath = Column(String)

    feature_id = Column(Integer, ForeignKey('features.id'))
    feature = relationship("Feature")
    scenario_id = Column(Integer, ForeignKey('scenarios.id'))
    scenario = relationship("Scenario")

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
        validation_keys_set = {code.name for code in ValidationOutcomeCode}
        try:
            return next((tag for tag in context.scenario.tags), next((tag for tag in validation_keys_set if tag in context.tags)))
        except StopIteration:
            raise AssertionError(f'Outcome code not included in tags of .feature file: {context.feature.filename}')
def define_feature_version(context):
    version = next((tag for tag in context.tags if "version" in tag)) # e.g. version1
    return int(version.replace("version",""))

def define_expected_value(context):
    try:
        return str(context.errors[0].expected_value)
    except IndexError: # Passed Rule
        return None

def define_observed_value(context):
    try:
        return str(context.errors[0].observed_value)
    except IndexError: # Passed Rule
        return None

def add_validation_results(context):
    with Session() as session:
        feature = session.query(Feature).filter_by(name=context.feature.name).first()
        scenario = session.query(Scenario).filter_by(name=context.scenario.name).first()

        # if not feature or not scenario: # TODO -> tables are empty for now
        #     raise ValueError("Feature or Scenario not found")

        rule_outcome = define_rule_outcome(context)
        outcome_code = define_outcome_code(context, rule_outcome)
        validation_result = ValidationResult(check_execution_id = None,
                                             file=os.path.basename(context.config.userdata['input']),
                                             validated_on=datetime.now(),
                                             reference=context.feature.name.split(" ")[0],
                                             step=context.step.name,
                                             ifc_filepath = context.config.userdata.get('input'),
                                             severity=rule_outcome,
                                             code=outcome_code,
                                             feature_version=define_feature_version(context),
                                             expected = define_expected_value(context),
                                             observed = define_observed_value(context),
                                             feature_id=getattr(feature, "id", None),
                                             scenario_id=getattr(scenario, "id", None))
        session.add(validation_result)
        session.commit()

def initialize():
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    initialize()