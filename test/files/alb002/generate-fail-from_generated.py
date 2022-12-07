import ifcopenshell
import random


#Scenario 5 -> Attribute designparameter of wrong segment type (directions are husled and placed back wrong)
directions = ('IfcAlignmentHorizontal', 'IfcAlignmentVertical', 'IfcAlignmentCant') #global variable used both local and global, but better for readability
def create_fail_scenario04(direction):
    f = ifcopenshell.open('pass-alb002-generated_file.ifc')
    segments = list(map(lambda x: f.by_type(x)[0].IsNestedBy[0].RelatedObjects[1].DesignParameters, list(directions)))
    direction_segment_pairs = {'IfcAlignmentHorizontal': segments[0], 'IfcAlignmentVertical': segments[1], 'IfcAlignmentCant': segments[2]}

    def hustle(direction):
        while True:
            random_segment = random.choice(list(direction_segment_pairs.items()))
            if not random_segment[0] == direction:
                return random_segment[1]

    for alignment_direction in f.by_type("IfcAlignment")[0].IsNestedBy[0].RelatedObjects:
        if alignment_direction.is_a(direction):
            alignment_direction.IsNestedBy[0].RelatedObjects[0].DesignParameters = hustle(alignment_direction.is_a())
            f.write(f"fail-alb002-scenario04-wrong_alignment_direction_{alignment_direction.is_a()}.ifc")

for direction in directions:
    create_fail_scenario04(direction)


# Scenario 4 -> Each direction nest a list with IfcWall in it, not only IfcAlignmentSegment

def create_fail_scenario03(direction):
    f = ifcopenshell.open('pass-alb002-generated_file.ifc')
    owner = f.by_type("IfcOwnerHistory")[0]
    relationships = f.by_type(direction)[0].IsNestedBy[0]
    new_segments = list(relationships.RelatedObjects)
    new_segments.append(f.createIfcWall(ifcopenshell.guid.new(), owner))
    relationships.RelatedObjects = new_segments
    f.write(f"fail-alb002-scenario03-wrong_element_in_list_{direction}.ifc")

for direction in directions:
    create_fail_scenario03(direction)