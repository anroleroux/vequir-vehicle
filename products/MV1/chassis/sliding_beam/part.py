"""Sliding beam

A short beam of the MV1 chassis, perpendicular to the longitudinal beam
(lateral, along y), sitting against the longitudinal beam's underside at
its middle. Half the length of the lateral beams.

Assumptions where the description is silent:
- a solid bar of rectangular section, the same 10 x 10 mm section as the
  other beams, half the lateral beams' length (60 mm);
- it slides laterally (along y) against the longitudinal beam's underside;
  nothing yet guides or retains it;
- lateral along y (+y is the left), centred on x = 0 and y = 0, standing on
  z = 0 (the assembly lifts it to the longitudinal beam's underside).
"""
import cadquery as cq

beam = load_part("../beam")  # the longitudinal beam it slides under
lateral = load_part("../lateral_beam")

# parameters, in mm
length = lateral.length / 2  # lateral, along y: half the lateral beams
width = beam.width  # longitudinal, along x
height = beam.height  # vertical, along z

result = cq.Workplane("XY").rect(width, length).extrude(height)

regions = {
    "top": result.faces(">Z"),  # slides against the longitudinal beam's underside
    "left_end": result.faces(">Y"),
    "right_end": result.faces("<Y"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
