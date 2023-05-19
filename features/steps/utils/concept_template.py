from functools import reduce
import itertools
import operator
import re

import networkx

import ifcopenshell


class namespace_object:
    def __init__(
        self,
        namespace,
        identifier,
        constraint=None,
        binding=None,
        optional=False,
        parent=None,
    ):
        self.namespace = namespace
        self.identifier = identifier
        self.constraint = constraint
        self.binding = binding
        self.optional = optional
        self.parent = parent

    def __repr__(self):
        return f"{self.namespace.namespace}.{self.identifier}{f'({repr(self.constraint)})' if self.constraint is not None else ''}{f'[{repr(self.binding)}]' if self.binding is not None else ''}{'?' if self.optional else ''}"

    def __call__(self, v):
        return namespace_object(self.namespace, self.identifier, v)

    def __getitem__(self, k):
        return namespace_object(self.namespace, self.identifier, self.constraint, k)

    def __neg__(self):
        return namespace_object(
            self.namespace,
            self.identifier,
            self.constraint,
            self.binding,
            optional=True,
        )


class namespace:
    def __init__(self, namespace):
        self.namespace = namespace

    def __getattr__(self, k):
        return namespace_object(self, k)

    v = __getattr__


ENTITY = namespace("ENTITY")
ATTRIBUTE = namespace("ATTRIBUTE")


def merge_dictionaries(dicts):
    d = {}
    for e in dicts:
        d.update(e)
    return d


def _query(data, query, children, depth=0, debug=False):
    if debug:
        print(
            " " * depth,
            query,
            (40 - len(str(query))) * " ",
            query.parent,
            " ",
            data,
            sep="",
        )

    if isinstance(children, namespace_object):
        children = {children: {}}

    if query.namespace == ATTRIBUTE:
        vs = getattr(data, query.identifier)
        # if vs is None:
        #     if query.optional:
        #         return [{query: data}]
        #     else:
        #         print(' ' * depth, 'X')
        #         return []
        if not isinstance(vs, (list, tuple)):
            vs = [vs]

        if children:
            return_value = []
            for child, v in itertools.product(children.items(), vs):
                child_values = _query(v, *child, depth=depth + 1)
                if not isinstance(child_values, (list, tuple)):
                    child_values = [child_values]
                if query.constraint:
                    unpack = (
                        lambda v: v[0]
                        if isinstance(v, ifcopenshell.entity_instance)
                        else v
                    )
                    child_values = [
                        c for c in child_values if unpack(c) == query.constraint
                    ]
                return_value.extend(child_values)
            return return_value
        else:
            return [{query: data}]

    elif query.namespace == ENTITY:

        if isinstance(data, ifcopenshell.entity_instance) and not data.is_a(
            query.identifier
        ):
            if query.optional:
                return [{query: data}]
            else:
                if debug:
                    print(" " * depth, "X")
                return []

        to_combine = [[{query: data}]]
        for child in children.items():
            to_combine.append(_query(data, *child, depth=depth + 1))
        return list(map(merge_dictionaries, itertools.product(*to_combine)))


def iden(x):
    return x


def filter_bindings(di):
    def inner(d):
        for k, v in d.items():
            if k.binding is not None:
                yield k.binding, v
            elif k.parent and k.parent.binding is not None:
                yield k.parent.binding, v
            elif k.parent is None:
                yield "_root", v

    return dict(inner(di))


def apply_parents(x, parent=None):
    if isinstance(x, namespace_object):
        x.parent = parent
    elif isinstance(x, dict):
        for k, v in x.items():
            apply_parents(k, parent)
            apply_parents(v, k)
    else:
        breakpoint()


def query(f: ifcopenshell.file, concept: dict, projection_only: bool = True):
    apply_parents(concept)
    elems = f.by_type(next(iter(concept.keys())).identifier)
    if projection_only:
        post = filter_bindings
    else:
        post = iden
    return list(
        map(
            post,
            sum((_query(elem, *next(iter(concept.items()))) for elem in elems), []),
        )
    )


def from_graphviz(*, filename=None, filecontent=None, debug=False):
    if filename:
        assert not filecontent
        filecontent = open(filename).read()
    concept_blocks = re.findall(r"concept\s*\{.+?\}", filecontent, flags=re.S)
    root = None

    if not concept_blocks:
        return

    block = concept_blocks[0]

    edges = re.findall("([\:\w]+)\s*\->\s*([\-\:\w]+)", block)
    rule_bindings = dict(re.findall(r'(\w+:\w+)\[binding="(.+?)"\]', block))
    # constraint_expressions = dict(re.findall(r'(constraint_[\d+])\[label="=(.+?)"\]', block))

    G = networkx.DiGraph()

    for a, b in edges:
        rb = rule_bindings.get(a)
        attr = a.split(":")[1] if ":" in a else None
        a, b = map(lambda x: x.split(":")[0], (a, b))
        if attr:
            G.add_edge(a, f"{attr}_{a}")
            G.add_edge(f"{attr}_{a}", b)
            G.nodes[f"{attr}_{a}"]["type"] = "AttributeRule"
            G.nodes[f"{attr}_{a}"]["binding"] = rb
        else:
            G.add_edge(a, b)
            if not b.startswith("Ifc"):
                if b.startswith("constraint"):
                    G.nodes[b]["type"] = "Constraint"
                else:
                    G.nodes[b]["type"] = "Reference"

    if len(G):
        root = min(G.in_degree(), key=operator.itemgetter(1))[0]

        Gadj = networkx.to_dict_of_lists(G)

        def build(x):
            ty = G.nodes[x].get("type", "EntityRule")

            if ty in ("Reference", "Constraint"):
                raise NotImplementedError("Constraints and references not supported")

            name = x.split("_")[0]

            ns = {"EntityRule": ENTITY, "AttributeRule": ATTRIBUTE}[ty]
            nd = ns.v(name)

            ruleid = G.nodes[x].get("binding")

            if ruleid:
                nd = nd[ruleid]

            if debug:
                nd = str(nd)

            if adj := Gadj[x]:
                return {nd: reduce(lambda a, b: {**a, **b}, map(build, adj))}
            else:
                return nd

        if debug:
            import sys, json

            json.dump(build(root), sys.stdout, indent=2)
            exit(0)
        else:
            return build(root)


if __name__ == "__main__":
    import sys
    import pprint

    template = {
        ENTITY.IfcProduct["Product"]: {
            ATTRIBUTE.Representation: {
                ENTITY.IfcProductDefinitionShape: {
                    ATTRIBUTE.Representations: {
                        ENTITY.IfcShapeRepresentation: {
                            ATTRIBUTE.ContextOfItems: ENTITY.IfcGeometricRepresentationContext,
                            ATTRIBUTE.RepresentationIdentifier: ENTITY.IfcLabel("Axis"),
                            ATTRIBUTE.RepresentationType: ENTITY.IfcLabel("Curve2D"),
                            ATTRIBUTE.Items: ENTITY.IfcBoundedCurve["Curve"],
                        }
                    }
                }
            }
        }
    }

    f = ifcopenshell.open(sys.argv[1])
    if len(sys.argv) == 3:
        template = from_graphviz(sys.argv[2])

    for x in query(f, template):
        pprint.pprint(x, sort_dicts=False)
        print()
