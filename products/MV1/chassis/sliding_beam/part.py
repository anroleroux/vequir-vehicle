"""Sliding beam

A short beam of the MV1 chassis, perpendicular to the longitudinal beam
(lateral, along y), resting on top of the longitudinal beam at its middle,
in the beam's guide, which is open to the top: it slides sideways there.
Half the length of the lateral beams.

Assumptions where the description is silent:
- a solid bar of rectangular section, 10 mm high like the other beams, half
  the lateral beams' length (60 mm);
- 0.2 mm narrower than the guide on each side (10 mm in the 10.4 mm
  channel), sized from it; it rests on the guide's floor (the longitudinal
  beam's top) and slides laterally (along y) between the cheeks;
- lateral along y (+y is the left), centred on x = 0 and y = 0, standing on
  z = 0 (the assembly lifts it onto the longitudinal beam's top).
"""
import cadquery as cq

beam = load_part("../beam")  # the longitudinal beam whose guide it slides in
lateral = load_part("../lateral_beam")

# parameters, in mm
length = lateral.length / 2  # lateral, along y: half the lateral beams
guide_clearance = 0.2  # each side, between the guide's cheeks
width = beam.guide_width - 2 * guide_clearance  # longitudinal, along x
height = beam.height  # vertical, along z

result = cq.Workplane("XY").rect(width, length).extrude(height)

regions = {
    "bottom": result.faces("<Z"),  # rests and slides on the guide's floor
    "top": result.faces(">Z"),
    "left_end": result.faces(">Y"),
    "right_end": result.faces("<Y"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
