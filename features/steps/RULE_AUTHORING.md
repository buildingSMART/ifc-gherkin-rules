# Rule Creation and Validation Workflow

This document outlines the workflow for creating and validating rules using `.feature` files from Behave and their implementation in Python.

## 1. Select Givens in .Feature File

The initial step involves determining the applicability of the model for a specific rule using statements like 'Given a model with Schema IFC4.3', selecting the applicable instances along with the attributes that need validation.

### Example .feature File

```gherkin
Feature: EXE001 - Some Example Rule
  The rule verifies that an entity adheres to conditions

Background:
  Given: A model with Schema "IFC4.3"
  Given An IfcEntity
  Given Its attribute some_attribute
```

## 2. Implement Given Statements with Python

In Python, the implementation would be as shown in the image below. In IfcOpenShell, an IFC entity instance possesses an attribute which can be filtered using the standard 'getattr' Python library. If the instance has the required attribute, a 'PASS' is returned for that instance, which will be used to filter the relevant instances. Otherwise, no result is yielded for that instance.
### Example Python Implementation

```python
@gherkin_ifc.step('Its attribute {attribute}')
def step_impl(context, inst, attribute):
    if getattr(inst, attribute, None):
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASS)
```

## 3. Select Then Statements

The actual validation is conducted by adding 'Then' statements, wherein specific conditions are validated. It's important to note that 'Given' and 'Then' statements are quite similar, allowing them to be used both for filtering instances for validation and for performing the validation itself.

### Example .feature Behave File

```gherkin
Feature: EXE001 - Some Example rule
  The rule verifies that an entity adheres to conditions

  Background:
    Given a model with Schema "IFC4.3"
    Given An IfcEntity
    Given Its attribute some_attribute

  Scenario: Entity must adhere to some condition
    Given Some condition X must be met # -> filter
    Then some condition Y must be met # -> check 

  Scenario: Entity must adhere to other condition 
    Given: Some condition Y must be met 
    Then: Some condition X must be met 
```
## 4. Implement 'Then' statements with Python

In Python, the implementation for both 'Given' and 'Then' statements is similar. If a condition is not met during validation, the result is False, and an outcome with Severity=ERROR is yielded. Conversely, when used to filter applicable instances, we look for conditions that are True.

### Example Python Implementation for 'Then'

```python
@gherkin_ifc.step("Some condition {condition} must be met")
def step_impl(context, inst: ifcopenshell.entity_instance, condition: str):
    outcome = execute_some_check(condition)
    if outcome:  # filter instances
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASS)
    else:  # check failed
        yield ValidationOutcome(inst=inst, expected='condition', observed='not condition', severity=OutcomeSeverity.ERROR)
```

## 5. Reverse 'Given' and 'Then' statements

Every statement can be utilized as both a 'Given' and a 'Then'. Thus, the attribute selection process used earlier can also be applied to check instances. Now as a 'Then' statement.

### Example .feature File for Reversed Statements

```gherkin
Feature: ALS005 - Alignment shape representation
  The rule verifies that each IfcAlignment uses correct representation 

  Background: 
    Given a model with Schema "IFC4.3"
    Given an IfcAlignment
    Given Its attribute Representation
    Given its attribute Representations

  Scenario: Agreement on each IfcAlignment using correct representation - Value 

    Then the value of attribute RepresentationIdentifier must be Axis 
    Then the value of attribute RepresentationType must be Curve3D
```

## 6. Implement the reversed statements in Python

The implementation in Python for these reversed statements remains largely the same as described earlier.

### Example Python Implementation for Reversed Statements

```python
@gherkin_ifc.step("Its attribute {attribute}")
def step_impl(context, inst, attribute):
    if getattr(inst, attribute, None):  # GIVEN
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASS)
    else:  # THEN
        yield ValidationOutcome(inst=inst, expected='attribute', observed='not attribute', severity=OutcomeSeverity.ERROR)
```

## 7. A currently implemented example

A concrete example of this methodology applied to a currently implemented rule is added below.

### Example .feature File for a Concrete Example

```gherkin
  Given an IfcEntity
  Then Its attribute some_attribute
```

## 8. Enforce rule-creation protocol

To assist in development and ensure consistency across all rules, a script has been developed to verify implementations. Running this script checks various aspects, such as:
- Whether the rule-code is a valid functional part and consistent with previously used codes
- The uniqueness of the code 
- Whether the descriptions are duplicated and formulated correctly

### Example Python Script to Enforce Protocol

```python
assert protocol.enforce(context, feature), 'failed'
```
