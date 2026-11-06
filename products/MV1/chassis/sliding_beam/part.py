"""Sliding beam

A short beam of the MV1 chassis, perpendicular to the longitudinal beam
(lateral, along y), resting on top of the longitudinal beam at its middle,
in the beam's guide, which is open to the top: it slides sideways there.
Half the length of the lateral beams. Each end is a fork: a top and a
bottom plate, with a hinge hole through both plates.

Assumptions where the description is silent:
- a solid bar of rectangular section, 10 mm high like the other beams, half
  the lateral beams' length (60 mm), the plates within that length;
- 0.2 mm narrower than the guide on each side (10 mm in the 10.4 mm
  channel), sized from it; it rests on the guide's floor (flush with the
  longitudinal beam's top) along the guide's 40 mm and slides laterally
  (along y) between the cheeks;
- the plates are the bar's top and bottom 3 mm over its last 10 mm at each
  end, as wide as the bar, leaving a 4 mm gap between them, open at the end
  and both sides, for the hinged part;
- the hinge axis is vertical (z), through both plates at each end, centred
  on the bar's width, 5 mm in from the end: a 3.4 mm hole (an M3
  clearance, like the beam's disc holes) through each plate;
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
plate_thickness = 3.0  # the top and bottom plates at each end
plate_length = 10.0  # along y, in from each end
hinge_inset = 5.0  # the hinge axis, in from each end
hinge_diameter = 3.4  # through both plates

gap = height - 2 * plate_thickness  # between the plates
ends = [length / 2, -length / 2]  # left (+y), right (-y)
hinge_y = [y - hinge_inset if y > 0 else y + hinge_inset for y in ends]

bar = cq.Workplane("XY").rect(width, length).extrude(height)
gaps = (
    cq.Workplane("XY", origin=(0, 0, plate_thickness))
    .pushPoints([(0, y - plate_length / 2 if y > 0 else y + plate_length / 2) for y in ends])
    .rect(width, plate_length)
    .extrude(gap)
)
hinges = (
    cq.Workplane("XY")
    .pushPoints([(0, y) for y in hinge_y])
    .circle(hinge_diameter / 2)
    .extrude(height)
)
result = bar.cut(gaps).cut(hinges)

regions = {
    "bottom": result.faces("<Z"),  # rests and slides on the guide's floor
    "left_hinge": result.faces("%CYLINDER").faces(
        cq.selectors.BoxSelector((-2, hinge_y[0] - 2, -1), (2, hinge_y[0] + 2, height + 1))),
    "right_hinge": result.faces("%CYLINDER").faces(
        cq.selectors.BoxSelector((-2, hinge_y[1] - 2, -1), (2, hinge_y[1] + 2, height + 1))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
