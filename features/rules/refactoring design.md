# Design document for steps refactoring

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

## Basics

Doubles quotes must always be used at the start and end of gherkin matching statements.
(`black` will reformat single quotes to double quotes)

Single quotes should only be used in any matching or control sub-parts.

## Preferred statements

``` gherkin
The value of attribute .RepresentationIdentifier. must be 'Axis'
The type of attribute .Items. must be .IfcCurveSegment.
```

## Swappable statements

These are groups of terms that are interchanged based on whether they will be used for a Given or Then.

| Construct | Given  | Then       |
|-----------|--------|------------|
| Equality  | is     | must be    |
| Existence | exists | must exist |

## Control characters

## Angle brackets `<>`

Not used.
They are used by gherkin for Example tables

## Square brackets '[]'

Prose used for matching

```
Then [its type] is not .IfcWall.
```

## Single quotes `'`

Used only for string values in IFC.
This goes for labels, text, enum values, etc.

Example:

`.RepresentationType.` is 'ANNOTATION'`

## Double quotes `"`

See above - only used at beginning and end of an implementation step

## Schema constructs `.`

Use for any reserved keyword in the schema, including types.

## Binary and unary operators - Asterisk `*`

- binary and unary operators
  - see `comparisons` implemented by Fernando
    - 

- equal to

### Modifiers (Custom Enums) - Ampersand `&`

definite TODO: gater all of the custom registered types in one spot! we have a lot of duplication

possible TODO: rewrite as string enums with the literal values, or decorate with @register_enum_type

| class              | defined in        | opt1    | opt 2          | Notes |
|--------------------|-------------------|---------|----------------|-------|
| FirstOrFinal       | givens/attributes | FIRST   | FINAL          |       | 
| ComparisonOperator | givens/attributes | EQUAL   | NOT_EQUAL      |       | 
| SubtypeHandling    | givens/attributes | INCLUDE | EXCLUDE        |       | 
| PrefixCondition    | givens/attributes | STARTS  | DOES_NOT_START |       | 

#### FirstOrFinal

- &first&
- &final&

#### Comparison Operator

- &equal to&
- &not equal to&

#### Subtype handling

- &including subtypes&
- &excluding subtypes&

#### Prefix Conditions

- &starts&
- &does not start&
