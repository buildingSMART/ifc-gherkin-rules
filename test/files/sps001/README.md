File name                              | Expected result | Error | Description |
---------------------------------------------------------|----|----|
pass-0-sites-1-buildings-variant-0.ifc | pass            | | File with 0 sites and 1 buildings, building assigned to project |
pass-0-sites-2-buildings-variant-0.ifc | pass            | | File with 0 sites and 2 buildings, building assigned to project |
pass-1-sites-1-buildings-variant-1.ifc | pass            | | File with 1 sites and 1 buildings, building assigned to site    |
pass-1-sites-2-buildings-variant-1.ifc | pass            | | File with 1 sites and 2 buildings, building assigned to site    |
fail-0-sites-0-buildings-variant-0.ifc | fail            | No instances of type IfcBuilding were encountered | File with 0 sites and 0 buildings, building assigned to project |
fail-1-sites-0-buildings-variant-0.ifc | fail            | No instances of type IfcBuilding were encountered | File with 1 sites and 0 buildings, building assigned to project |
fail-1-sites-1-buildings-variant-0.ifc | fail            | The instance #23=IfcBuilding ... is assigned to #20=IfcProject ... | File with 1 sites and 1 buildings, building assigned to project |
fail-1-sites-2-buildings-variant-0.ifc | fail            | (1) The instance #23=IfcBuilding ... is assigned to #20=IfcProject ... (2) The instance #24=IfcBuilding ... is assigned to #20=IfcProject ... | File with 1 sites and 2 buildings, building assigned to project |
fail-2-sites-0-buildings-variant-0.ifc | fail            | (1) The following 2 instances of type IfcSite were encountered ... (2) No instances of type IfcBuilding were encountered | File with 2 sites and 0 buildings |
fail-2-sites-1-buildings-variant-0.ifc | fail            | (1) The following 2 instances of type IfcSite were encountered ... (2) The instance #24=IfcBuilding ... is assigned to #20=IfcProject ... | File with 2 sites and 1 buildings, building assigned to project |
fail-2-sites-1-buildings-variant-1.ifc | fail            | The following 2 instances of type IfcSite were encountered ... | File with 2 sites and 1 buildings, building assigned to site    |
fail-2-sites-2-buildings-variant-0.ifc | fail            | (1) The following 2 instances of type IfcSite were encountered ... (2) The instance #24=IfcBuilding ... is assigned to #20=IfcProject ... (3) The instance #25=IfcBuilding ... is assigned to #20=IfcProject ... | File with 2 sites and 2 buildings, building assigned to project |
fail-2-sites-2-buildings-variant-1.ifc | fail            | The following 2 instances of type IfcSite were encountered ... (2)  | File with 2 sites and 2 buildings, building assigned to site    |
