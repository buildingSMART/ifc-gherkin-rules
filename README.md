# IFC Gherkin rules

## Usage as part of buildingSMART validation service

This repository serves as a key element of the buildingSMART [Validation Service](https://technical.buildingsmart.org/services/validation-service/)
by providing the logic for validation of Normative Rules, namely:

- [Implementer Agreements](https://buildingsmart.github.io/validate/user/index.html#implementer-agreements)
- [Informal Propositions](https://buildingsmart.github.io/validate/user/index.html#informal-propositions)

More specifically, the gherkin rules run as workers managed by Celery as shown in the 
[Application Structure](https://buildingsmart.github.io/validate/dev/index.html#application-structure)
of the Validation Service.

Please consult the [IFC Gherkin rules](https://buildingsmart.github.io/validate/dev/index.html#ifc-gherkin-rules) documentation in the Developer Guide for additional information.
