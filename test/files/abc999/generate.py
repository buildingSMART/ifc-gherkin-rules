import ifcopenshell

base = "UT_AWC_1_no_geometry_ifc4x3tc1.ifc"
rel_labels = 'EndsAt', 'StartsAt'

cases = 'valid main points', 'no referents', 'no main point referents', 'double referent', 'missing relation', 'double relationship', 'label reversed', 'all labels reversed', 'no labels', 'wrong labels'

for ci, case in enumerate(cases):
        
    f = ifcopenshell.open(base)
    # parts = sorted(set(f.by_type('IfcLinearElement')) - set(f.by_type('IfcAlignmentSegment')), key=lambda inst: inst.id())
    parts = f.by_type('IfcAlignmentHorizontal')

    for p in parts:
        for x in p.IsNestedBy[0].RelatedObjects[5:]:
            f.remove(x.DesignParameters)
            f.remove(x)

    if case == 'no referents':
        parts[:] = []

    for li, lin in enumerate(parts):
        obs = list(enumerate((None,) + lin.IsNestedBy[0].RelatedObjects + (None,)))
        all_refs = []

        station = 0.

        for (i, a), (j, b) in zip(obs[:-1], obs[1:]):
            idxs = ' '.join(map(str, (idx for idx, seg in ((i, a), (j, b)) if seg)))
            num_refs = 1
            if case == 'double referent' and li == 0 and i == 2:
                num_refs = 2

            if case == 'no main point referents':
                ob_type = 'NotAMainPoint'
            else:
                ob_type = 'MainPoint'

            refs = [f.createIfcReferent(ifcopenshell.guid.new(), None, f'Referent {lin.is_a()[12:]} {idxs}', ObjectType=ob_type, PredefinedType='USERDEFINED') for i in range(num_refs)]
            all_refs.extend(refs)

            for ref in refs:
                ref.ObjectPlacement = f.createIfcLocalPlacement(
                    PlacementRelTo = lin.ObjectPlacement,
                    # RelativePlacement = f.createIfcAxis2PlacementLinear(
                    #     f.createIfcPointByDistanceExpression(
                    #         f.createIfcNonNegativeLengthMeasure(station),
                    #         BasisCurve=
                    #     )
                    # )
                    RelativePlacement = f.createIfcAxis2Placement3D(
                        f.createIfcCartesianPoint((0., 0., 0.))
                    )
                )

            if a is not None:
                station += a.DesignParameters.SegmentLength

            if not (case == 'missing relation' and li == 0 and i == 2):
                for ref in refs:
                    fn = lambda x: x
                    if case == 'all labels reversed' or (case == 'label reversed' and li == 0 and i == 2):
                        fn = reversed
                    elif case == 'no labels':
                        fn = lambda _: (None, None)
                    for lbl, seg in zip(fn(rel_labels), (a, b)):
                        if seg:
                            f.createIfcRelPositions(ifcopenshell.guid.new(), None, lbl, RelatingPositioningElement=ref, RelatedProducts=[seg])
                            if case == 'double relationship' and li == 0 and i == 2:
                                f.createIfcRelPositions(ifcopenshell.guid.new(), None, lbl, RelatingPositioningElement=ref, RelatedProducts=[seg])
        f.createIfcRelNests(ifcopenshell.guid.new(), RelatingObject=lin, RelatedObjects=all_refs)

    valid = ci in (0,1,2)
    postfix = '_' + case.replace(' ', '_')

    f.write(f"{'pass' if valid else 'fail'}-UT_AWC_1_no_geometry_ifc4x3tc1{postfix}.ifc")
