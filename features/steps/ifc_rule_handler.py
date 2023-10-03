from utils import misc
import errors as err

from functools import wraps

def handle(fn):
    @wraps(fn)
    def inner(context, *args, **kwargs):
        if context.step.step_type.lower() == 'given':
            context.instances = list(fn, context, *args, **kwargs)
            #@todo solution for 'applicable'

        elif context.step.step_type.lower() == 'then':
            if not getattr(context, 'applicable', True):
                return

            errors = []
            insts = getattr(context, 'instances', None) or context.model.by_type(kwargs.get('entity', None))
            for inst in getattr(context, 'instances', None) or context.model.by_type(kwargs.get('entity', None)):
                try:
                    error = next(fn(context, inst, *args, **kwargs))
                    errors.append(error)
                except StopIteration:
                    if getattr(context, 'error_on_passed_rule', False):
                        errors.append(err.RuleSuccessInst(True, inst))
            
            generate_error_message(context, errors)

    return inner


def generate_error_message(context, errors):
    import json
    error_formatter = (lambda dc: json.dumps(misc.asdict(dc), default=tuple)) if context.config.format == ["json"] else str
    assert not errors, "Errors occured:\n{}".format(
        "\n".join(map(error_formatter, errors))
    )

def handle_context_instances(fn):
    @wraps(fn)
    def inner(context, entity, *args, **kwargs):
        if not getattr(context, 'applicable', True):
            return

        errors = []
        for inst in context.model.by_type(entity):
            error_or_none = fn(context, inst, *args, **kwargs)
            if error_or_none is not None:
                errors.append(error_or_none)
            elif context.error_on_passed_rule:
                errors.append(err.RuleSuccessInst(True, inst))
                
        generate_error_message(context, errors)

    return inner