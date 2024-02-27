## Example Scenario

The scenario involves processing a list of `IfcBuildingStorey` entities, applying a function to extract specific attributes, and handling nested structures.

### Initial Setup

Given a list of instances (`insts`), which are `IfcBuildingStorey` entities, the goal is to apply a function `fn` to these instances based on their attributes.

```python
insts = [
    # Example instances of IfcBuildingStorey
]
=
[#157=IfcBuildingStor...17387E-14), #163=IfcBuildingStor...EMENT.,4.)]

# Function to apply
def apply_fn_to_item(fn, context, inst, **kwargs):
    if isinstance(inst, tuple):
        return tuple(apply_fn_to_item(fn, context, i, **kwargs) for i in inst)
    else:
        return tuple(map(attrgetter('instance_id'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, fn(context, inst, **kwargs))))
```

### Iteration and Attribute Application

Using the function to iterate and apply based on attributes:

1. **Layer 1 - ContainsElements**:
   - Modify `kwargs` and `context.instances` manually to focus on the `ContainsElements` attribute of `IfcBuildingStorey`.
   - Resulting in tuples of `IfcRelContainsInSpatialStructure`.

```python
layer_2 = list(itertools.chain.from_iterable(apply_fn_to_item(fn, context, inst=tuple(insts), attribute='ContainsElements')))
[(#90999=IfcRelContain...793),#157),), (#91036=IfcRelContain...889),#163),)]
```

2. **Layer 2 - GlobalId**:
   - Focusing on `GlobalId` results in a list of Global IDs.

```python
layer_3 = list(itertools.chain.from_iterable(apply_fn_to_item(fn, context, inst=tuple(layer_2), attribute='GlobalId')))
[('1S6CXignL4rQnOml7DlvNd',), ('1Dac7DKhbEyQEYUQYibzv4',)] # still the same structure
```

3. **Layer 3 - RelatedElements**:
   - Extracting `RelatedElements` results in a deeper nested structure, indicating relationships such as columns related to the storey.

```python
layer_3 = list(itertools.chain.from_iterable(apply_fn_to_item(fn, context, inst=tuple(layer_2), attribute='RelatedElements')))
[((...),), ((...),)] # <((Column, Column, Column, ...),(Slab))
```

4. **Layer 4 - Name**:
   - Finally, extracting the `Name` attribute from the related elements.

```python
names = list(itertools.chain.from_iterable(apply_fn_to_item(fn, context, inst=tuple(layer_3), attribute='Name')))
[(..),),(..),)] # <(('Column_1-01', 'Column_1-02', 'Column_1-03', ...),('Floor:3cm Clipping Plane:491137'))
```

### Summary

The stack of behavior statements now becomes:

- Given an `IfcBuildingStorey`
- Given Its attribute `ContainsElements`
- Given Its attribute `RelatedElements`
- Given Its attribute `Name`

### Verification with Stack Tree

To verify the process, `get_stack_tree(context)` can be used to inspect the relationships and attributes at each layer, confirming the expected outcomes at each step of the application.

```python
# Example stack tree inspection
stack_tree[3][1]  # IfcBuildingStorey details
stack_tree[2][1]  # IfcRelContainsInSpatialStructure details
stack_tree[1][1]  # Related elements details
stack_tree[0][1]  # Names of related elements
```

This method ensures a structured approach to navigating and extracting information from IFC entities, leveraging the capabilities of IfcOpenShell and Python's iterative and functional programming features.
