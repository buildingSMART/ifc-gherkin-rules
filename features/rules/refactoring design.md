# Design document for steps refactoring

(Q1 2025)

Goals:

- Remove redundant implementations
- Refactor so we re-use as much as we can
- Provide clear instructions and a set for selecting instance in a file

This will be accomplished primarily by adding control structures
to maximize re-use of implementation statements.

Additionally, step implementations will be re-grouped by domain, rather than
`Given` and `Then` statements.
This will aid greatly in reducing the overall number of code lines currently being managed
for similar logic.

## Background

`Given its attribute X must start with Y or Z`

Is almost the same as

`Given its attribute X`
`Its value must start with Y or Z`

However, when navigating the context stack and there is a subsequent step,
it is sometimes preferable to include the statement within a single step.

For example:

(1) `Given an entity IfcBuildingStorey`
(2) `Given its attribute X must start with Y or Z`
(3) `Given its relating Wall`
(4) `Then Some condiion`

In this case, it is challenging to split step (2) into two separate steps and then return to the
relating Wall (step 3) of the entity in step (1). This is because the instances in the context will be
the content of the attribute X of IfcBuildingStorey rather than the storey itself."

## Basics

Double quotes must always be used at the start and end of gherkin matching statements.
(`black` will reformat single quotes to double quotes)

Single quotes should only be used in any matching or control sub-parts.

## Preferred statements

``` gherkin
The value of attribute .RepresentationIdentifier. must be 'Axis'
The type of attribute .Items. must be .IfcCurveSegment.
```

## Control characters

## Angle brackets `<>`

Not used.
They are used by gherkin for Example tables

## Single quotes `'`

Used only for string values in IFC.
This goes for labels, text, enum values, etc.

Example:

`.RepresentationType.` is 'ANNOTATION'`

## Double quotes `"`

See above - only used at beginning and end of an implementation step

## Schema constructs `.`

Use for any reserved keyword in the schema, including types.

### Modifiers (Custom Enums) - Caret `^`

Prior to this refactor, there were enums registered in multiple places and with varying implementation.

They have been centralized and are now defined in `registered_type_definitions.json`.
They are registered in `steps/__init__.py` so that they are universally available and not tied to
any particular step implementation module.

## Square brackets '[]'

Prose used for matching

This can be used when a step implementation uses schema constructs
as well as other matching text in the same statements.

For example, the following two lines use the same step implementation:

```gherkin
Given .Closed. ^is^ True

Given [Its entity type] ^is^ 'IfcAlignmentVerticalSegment'
```
