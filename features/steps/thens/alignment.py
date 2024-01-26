import operator

from utils import ifc
from utils import misc
from utils import system
from utils import geometry
from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step('The business logic must contain a {layout} layout')
def step_impl(context, inst, layout):
    if layout in ["cant", "vertical"]:
        align_ent = context.instances[0].inst[0]


        print("foo to tha bah")