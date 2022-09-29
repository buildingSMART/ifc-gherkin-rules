@informal-proposition
Feature: SweptDiskSolidPolygonal

  Scenario: IfcSweptDiskSolidPolygonal

      Given An IfcSweptDiskSolidPolygonal
        And FilletRadius = not null
        And Directrix forms an open curve
        
       Then FilletRadius has to be smaller than or equal to the length of the start and end segments of the Directrix
        And FilletRadius has to be smaller than or equal to the length / 2 of the inner segments of the Directrix

      Given An IfcSweptDiskSolidPolygonal
        And FilletRadius = not null
        And Directrix forms a closed curve
        
       Then FilletRadius has to be smaller than or equal to the length of all segments of the Directrix
  