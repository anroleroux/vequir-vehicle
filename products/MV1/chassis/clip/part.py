"""Beam clip

A clip around the longitudinal beam, at its middle, that holds the sliding
plate up against the beam's bottom: a ring around the beam's section with a
window through its bottom, running laterally (along y), that the plate
passes and slides through.

Assumptions where the description is silent:
- the beam passes through it along x; it hugs the beam's sides and top with
  no clearance (a snug clip), with 2 mm walls;
- the plate's window is 0.2 mm larger than the plate's bar on each side and
  below it (10.4 x 3.2 mm), so the plate slides freely while the window's
  floor, 2 mm thick, holds it up against the beam;
- along x the clip is the window plus 3 mm of wall either side (16.4 mm),
  the walls beside the window carrying the floor;
- its top is split along x with a 6 mm gap, leaving a 2 mm lip over each
  edge of the beam's top, so it snaps over the beam from above (the end
  discs stop it going on from an end); printed in a material that flexes;
- the plate and the clip locate each other along x: the window stops the
  clip sliding along the beam;
- lateral walls on y, centred on x = 0 and y = 0, standing on z = 0 (the
  floor's underside); the beam's bottom is at z = beam_z.
"""
import cadquery as cq

beam = load_part("../beam")  # the longitudinal beam it clips around
plate = load_part("../sliding_plate")  # the plate it holds up

# parameters, in mm
wall = 2.0  # around the beam: its sides and the lips over its top
floor = 2.0  # under the plate's window
plate_clearance = 0.2  # each side of and below the plate, in the window
side_wall = 3.0  # along x, either side of the window
top_gap = 6.0  # the split in the top, along x, for snapping on

window_width = plate.width + 2 * plate_clearance  # along x
window_height = plate.thickness + plate_clearance  # along z
beam_z = floor + window_height  # the beam's bottom
length = window_width + 2 * side_wall  # along x
width = beam.width + 2 * wall  # along y
height = beam_z + beam.height + wall  # along z

body = cq.Workplane("XY").rect(length, width).extrude(height)
beam_passage = (
    cq.Workplane("XY", origin=(0, 0, beam_z))
    .rect(length, beam.width)
    .extrude(beam.height)
)
window = (
    cq.Workplane("XY", origin=(0, 0, floor))
    .rect(window_width, width)
    .extrude(window_height)
)
split = (
    cq.Workplane("XY", origin=(0, 0, beam_z + beam.height))
    .rect(length, top_gap)
    .extrude(wall)
)
result = body.cut(beam_passage).cut(window).cut(split)

regions = {
    "floor": result.faces(cq.selectors.NearestToPointSelector((0, 0, floor))),  # under the plate
    "left_lip": result.faces(
        cq.selectors.NearestToPointSelector((0, beam.width / 2 - wall / 2, beam_z + beam.height))),
    "right_lip": result.faces(
        cq.selectors.NearestToPointSelector((0, -beam.width / 2 + wall / 2, beam_z + beam.height))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
