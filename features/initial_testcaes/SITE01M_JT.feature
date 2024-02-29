@SITE01M
@version1
@N00010
Feature: SITE01M

  Scenario: Project

    Given An IfcProject
    Given Name = 'IFC4RV_Site_01M'

    Then Its global positioning is CRSName='EPSG:25832', Eastings=473853.49470582, Northings=5190250.24160506, OrthogonalHeight=466


