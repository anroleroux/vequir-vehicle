"""Main beam

The MV1 chassis's main beam, a horizontal flat plate running in the
longitudinal direction (front to back, along x): seen from the top it flares
out in the middle and comes together at each end, at the steering rotation
points, where it is rounded about a hole for the steering beam's pin.

Assumptions where the description is silent:
- 200 mm between the steering rotation points (x = +-100 mm), 3 mm thick;
- at each rotation point the plate is a 20 mm round end (the steering
  beam's disc diameter), about a 3.4 mm hole (an M3 clearance, taking the
  steering beam's 3.2 mm pin);
- in the middle a straight section, 100 mm wide (y) and 80 mm long (x =
  -40 to 40 mm), its sides parallel to x;
- from each end of the straight section the sides taper sharply in, in
  straight lines tangent to the round ends; the corners where the taper
  meets the straight section are rounded to 10 mm;
- its flat bottom is its seat on the steering beams' discs;
- longitudinal along x (+x is the front), centred on x = 0 and y = 0 (the
  vehicle's centreline), standing on z = 0.
"""
import math

import cadquery as cq

# parameters, in mm
length = 200.0  # between the steering rotation points, along x
thickness = 3.0  # vertical, along z
end_diameter = 20.0  # the round ends, about the rotation points
middle_width = 100.0  # the straight section, along y
middle_length = 80.0  # the straight section, along x
corner_radius = 10.0  # where the taper meets the straight section
hole_diameter = 3.4  # at each rotation point

disc_diameter = end_diameter  # the seat the steering beam's disc matches
disc_thickness = thickness  # the depth of the holes the pins go in
end_x = [length / 2, -length / 2]  # front, rear


def _tangent(cx, side):
    """Where the taper on that side (+1 left, -1 right), from the straight
    section's nearer corner, touches the round end at (cx, 0)."""
    r = end_diameter / 2
    px = math.copysign(middle_length / 2, cx)
    py = side * middle_width / 2
    d = math.hypot(px - cx, py)
    towards = math.atan2(py, px - cx)  # from the end's centre to the corner
    spread = math.acos(r / d)  # between that and the radius to the tangent point
    angle = towards - side * spread if cx > 0 else towards + side * spread
    return cx + r * math.cos(angle), r * math.sin(angle)


corners = [(x, y) for x in (middle_length / 2, -middle_length / 2)
           for y in (middle_width / 2, -middle_width / 2)]
outline = [
    (middle_length / 2, middle_width / 2), (-middle_length / 2, middle_width / 2),
    _tangent(end_x[1], 1), _tangent(end_x[1], -1),
    (-middle_length / 2, -middle_width / 2), (middle_length / 2, -middle_width / 2),
    _tangent(end_x[0], -1), _tangent(end_x[0], 1),
]
body = cq.Workplane("XY").polyline(outline).close().extrude(thickness)
ends = (
    cq.Workplane("XY")
    .pushPoints([(x, 0) for x in end_x])
    .circle(end_diameter / 2)
    .extrude(thickness)
)
holes = (
    cq.Workplane("XY")
    .pushPoints([(x, 0) for x in end_x])
    .circle(hole_diameter / 2)
    .extrude(thickness)
)
plate = body.union(ends)
for x, y in corners:
    plate = plate.edges("|Z").edges(cq.selectors.BoxSelector(
        (x - 1, y - 1, -1), (x + 1, y + 1, thickness + 1))).fillet(corner_radius)
result = plate.cut(holes)

regions = {
    "front_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((length / 2, 0, thickness / 2))),
    "rear_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((-length / 2, 0, thickness / 2))),
    "top": result.faces(">Z"),
    "bottom": result.faces("<Z"),  # its seat on the steering beams' discs
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
