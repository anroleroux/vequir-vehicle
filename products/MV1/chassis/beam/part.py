"""Main beam

The MV1 chassis's main beam, a horizontal flat plate running in the
longitudinal direction (front to back, along x): seen from the top it flares
out in the middle and comes together at each end, at the steering rotation
points, where it is rounded about a hole for the steering beam's pin.

On its top: a cylinder at each pivot, and two gussets that run at an angle
away from the pivots and straight through the middle, just far enough apart
for the two SG90 steering servos, one towards each end, which sit upside
down between them, their output shafts down through the plate.

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
- the cylinders at the pivots are the round ends' 20 mm, 6 mm tall on the
  plate's top, the pivot holes running through them;
- the gussets are 2 mm thick and as tall as the cylinders (6 mm); in the
  middle they run straight along x (x = -66 to 66 mm), 12.8 mm apart
  inside (the servo's 12.2 mm case with 0.3 mm each side); from there each
  runs at an angle in towards the pivot, into the side of its cylinder;
- the servos (vequir-standard's actuators/sg90) stand upside down on the
  plate's top between the gussets, symmetrical front and back: their output
  shafts' axes at x = +-55 mm on the centreline, the cases reaching in
  towards the middle; a 12.4 mm hole lets each one's gear housing through
  the plate (0.3 mm round it); each one's tabs rest on two blocks between
  the gussets, 4.3 mm tall (the case's top to the tabs' underside), each
  with a 1.6 mm pilot hole for an M2 screw;
- longitudinal along x (+x is the front), centred on x = 0 and y = 0 (the
  vehicle's centreline), standing on z = 0.
"""
import math

import cadquery as cq

servo = load_library("actuators/sg90")  # the steering servo, upside down on top

# parameters, in mm
length = 200.0  # between the steering rotation points, along x
thickness = 3.0  # vertical, along z
end_diameter = 20.0  # the round ends, about the rotation points
middle_width = 100.0  # the straight section, along y
middle_length = 80.0  # the straight section, along x
corner_radius = 10.0  # where the taper meets the straight section
hole_diameter = 3.4  # at each rotation point
boss_height = 6.0  # the cylinders on top, at the pivots
gusset_thickness = 2.0
gusset_height = boss_height
gusset_straight = 66.0  # the gussets' straight middle, each side of x = 0
servo_clearance = 0.3  # each side of the servo's case, and round its gear housing
servo_x = 55.0  # the servos' output shafts, along x (front +, rear -)
pilot_diameter = 1.6  # in the tab blocks, for M2 screws

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
# on top: the pivots' cylinders, the gussets, the servo's tab blocks
top = thickness
for x in end_x:
    plate = plate.union(cq.Workplane("XY", origin=(x, 0, top)).circle(end_diameter / 2)
                        .extrude(boss_height))
gusset_y = servo.width / 2 + servo_clearance + gusset_thickness / 2  # their centre lines


def _rib(x0, y0, x1, y1):
    """A gusset along the line from (x0, y0) to (x1, y1), rounded at its ends."""
    run = math.hypot(x1 - x0, y1 - y0)
    turn = math.degrees(math.atan2(y1 - y0, x1 - x0))
    rib = (cq.Workplane("XY").rect(run, gusset_thickness).extrude(gusset_height)
           .rotate((0, 0, 0), (0, 0, 1), turn)
           .translate(((x0 + x1) / 2, (y0 + y1) / 2, top)))
    ends = (cq.Workplane("XY", origin=(0, 0, top)).pushPoints([(x0, y0), (x1, y1)])
            .circle(gusset_thickness / 2).extrude(gusset_height))
    return rib.union(ends)


for side in (1, -1):
    y = side * gusset_y
    plate = plate.union(_rib(-gusset_straight, y, gusset_straight, y))
    for x in end_x:
        x0 = math.copysign(gusset_straight, x)
        # towards the pivot, stopping just inside its cylinder's side
        run = math.hypot(x - x0, y)
        reach = (run - (end_diameter / 2 - gusset_thickness)) / run
        plate = plate.union(_rib(x0, y, x0 + (x - x0) * reach, y - y * reach))

tab_overhang = (servo.tab_span - servo.length) / 2
block_height = servo.case_height - servo.tab_bottom - servo.tab_thickness  # case top to tabs
block_width = 2 * (gusset_y - gusset_thickness / 2)  # between the gussets
pilots = cq.Workplane("XY")
housing_holes = cq.Workplane("XY")
for end in (1, -1):  # front, rear: mirror images, the cases reaching in
    centre = end * (servo_x + servo.case_x)  # the servo's case, along x
    for x0 in (centre - servo.length / 2 - tab_overhang, centre + servo.length / 2):
        plate = plate.union(cq.Workplane("XY", origin=(x0 + tab_overhang / 2, 0, top))
                            .rect(tab_overhang, block_width).extrude(block_height))
    pilots = pilots.union(
        cq.Workplane("XY", origin=(0, 0, -1))
        .pushPoints([(centre - servo.hole_spacing / 2, 0), (centre + servo.hole_spacing / 2, 0)])
        .circle(pilot_diameter / 2).extrude(top + block_height + 2))
    housing_holes = housing_holes.union(
        cq.Workplane("XY", origin=(end * servo_x, 0, -1))
        .circle(servo.housing_diameter / 2 + servo_clearance).extrude(top + 2))
pivot_holes = (cq.Workplane("XY", origin=(0, 0, -1)).pushPoints([(x, 0) for x in end_x])
               .circle(hole_diameter / 2).extrude(top + boss_height + 2))
result = plate.cut(holes).cut(pivot_holes).cut(pilots).cut(housing_holes)

regions = {
    "front_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((length / 2, 0, thickness / 2))),
    "rear_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((-length / 2, 0, thickness / 2))),
    "top": result.faces(cq.selectors.NearestToPointSelector((0, 30, thickness))),
    "front_servo_hole": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (servo_x + servo.housing_diameter / 2 + servo_clearance, 0, thickness / 2))),
    "rear_servo_hole": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (-servo_x - servo.housing_diameter / 2 - servo_clearance, 0, thickness / 2))),
    "bottom": result.faces("<Z"),  # its seat on the steering beams' discs
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
