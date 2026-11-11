"""Linkage plate

A straight upright strip in the x-z plane (its thickness along y), with a
hinge along x at its top and at its bottom, so arms hinged there swing in
the y-z plane. The four-bar linkage uses two: the fixed plate, and the
moving plate facing it. The side plates are the linkage's I links: the
strip is only as wide as its hinges' middle knuckle, which sits between the
outer knuckles of an H-link arm, and runs straight down from the top hinge
to the bottom one, and on up over the top arm to carry the shock absorber's
upper joint. Below its bottom hinge it carries the bracket of the wheel's
drive motor, tilted down towards the hub.

Assumptions where the description is silent:
- the hinges are 30 mm wide overall (x): the arms' width and the pins'
  length; the strip is the middle knuckle's width, 0.2 mm short of the
  arm's outer knuckles each side (9.6 mm);
- 42 mm high (z) and 3 mm thick (y): its hinges 36 mm apart, the top arm
  4 mm lower and the bottom arm 4 mm higher than they were (44 mm apart), to
  bring the suspension down;
- each hinge is a knuckle about an axis along x, a knuckle's radius (3 mm)
  in front of the plate's back face and in from its top or bottom edge, so
  the knuckle is flush with the back face and the top or bottom edge, and
  stands 3 mm proud of the front face; the back face is flat, to mount the
  plate on (a steering beam's upright);
- a 2.2 mm hole along each axis, for a 2 mm pin;
- above its top hinge the strip carries on straight up to 27 mm above
  the hinge (66 mm), then turns out (+y) as a 6 mm bar (z = 60 to 66 mm),
  the strip's width,
  reaching 38 mm out from the back face, over the top arm's wheel-end
  opening; a 3 mm tab (x) hangs from the bar's end to a rounded end (4 mm
  radius) about a 2.2 mm hole, 34 mm out, 15 mm above the top hinge
  (z = 54 mm): the shock
  absorber's upper joint. The bar clears the top arm and the wheel link
  over the linkage's travel;
- the drive motor (vequir-standard's actuators/motor_130) hangs below the
  bottom hinge, its body behind the plate (under the steering beam), its
  shaft tilted down at the hub: its front face's centre 1 mm behind the
  back face and 12 mm below the plate's bottom, its axis aimed at the
  drive's joint by the hub (47 mm out, 32 mm below the plate's bottom,
  with the arms level), about 22.6 degrees down;
- the motor's bracket is a 2 mm plate across its front face, 22 x 24 mm,
  with a 6.6 mm hole for its bearing boss and two 2.2 mm holes for M2
  screws, hung from a block under the strip (3.5 mm deep, 6 mm out from
  the back face) clear of the motor, its shaft and the coupler;
- the plate stands on z = 0, centred on x = 0, its back face on y = 0.
"""
import math

import cadquery as cq

motor = load_library("actuators/motor_130")  # the wheel's drive motor, under the plate

# parameters, in mm
hinge_width = 30.0  # the hinges overall, along x: the arms and the pins
height = 42.0  # along z: its hinges 36 mm apart (the bottom one 4 mm up, the top one 4 mm down from 44)
thickness = 3.0  # along y
knuckle_radius = 3.0  # the hinge knuckles, about each axis
middle = 5.0  # where the arm's outer knuckles start, each side of x = 0
knuckle_gap = 0.2  # between knuckles, along x
knuckle_half = middle - knuckle_gap  # the plate's middle knuckle, each side of x = 0
turn_clearance = 0.3  # radial, around the other leaf's knuckles
hole_diameter = 2.2  # along each hinge axis, for a 2 mm pin

shock_mount_y = 34.0  # the shock's upper joint, out from the back face
shock_mount_z = height - 3.0 + 15.0  # the shock's upper joint, 15 mm above the top hinge
shock_tab_thickness = 3.0  # the joints' tabs, along x
shock_eye_radius = 4.0  # around the joints' pins
tower_top = height - 3.0 + 27.0  # the strip, carried on up 27 mm above the top hinge
motor_face_y = -1.0  # the drive motor's front face's centre, behind the back face
motor_face_z = -12.0  # below the plate's bottom
drive_target_y = 47.0  # the drive's joint by the hub, with the arms level
drive_target_z = -32.0
bracket_width = 22.0  # across the motor's front face, along x
bracket_height = 24.0  # across it, in the y-z plane
bracket_thickness = 2.0
bracket_hole = 6.6  # for the motor's bearing boss
screw_hole = 2.2  # for M2 screws into the motor's front face
hanger_depth = 3.5  # the block under the strip the bracket hangs from
hanger_reach = 6.0  # out from the back face
overhang_thickness = 6.0  # the bar out over the top arm, along z
overhang_reach = shock_mount_y + shock_eye_radius  # the bar, out from the back face

width = 2 * knuckle_half  # the strip, along x: straight down from knuckle to knuckle
axis_y = knuckle_radius  # the hinge axes: the knuckles flush with the back face
axes_z = [knuckle_radius, height - knuckle_radius]  # bottom, top


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


result = cq.Workplane("XY").box(width, thickness, height, centered=(True, False, False))
for z in axes_z:
    result = result.union(_along_x(-knuckle_half, knuckle_half, axis_y, z, knuckle_radius))
    result = result.cut(_along_x(-width, width, axis_y, z, hole_diameter / 2))


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate(
        (x0, y0, z0))


# up over the top arm: the tower, the bar out, the tab hanging from its end
bar_bottom = tower_top - overhang_thickness
result = result.union(_box(-width / 2, width / 2, 0, thickness, height, tower_top))
result = result.union(_box(-width / 2, width / 2, thickness, overhang_reach, bar_bottom, tower_top))
tab = (
    _box(-shock_tab_thickness / 2, shock_tab_thickness / 2, shock_mount_y - shock_eye_radius,
         shock_mount_y + shock_eye_radius, shock_mount_z, bar_bottom)
    .union(cq.Workplane("YZ", origin=(-shock_tab_thickness / 2, 0, 0))
           .center(shock_mount_y, shock_mount_z).circle(shock_eye_radius)
           .extrude(shock_tab_thickness))
)
result = result.union(tab).cut(_along_x(-width, width, shock_mount_y, shock_mount_z,
                                        hole_diameter / 2))

# the drive motor's place: its front face's centre, its axis tilted down at
# the drive's joint by the hub; motor_location turns the motor's +z (its
# shaft) to that axis
motor_tilt = math.degrees(math.atan2(motor_face_z - drive_target_z,
                                     drive_target_y - motor_face_y))  # down from +y
motor_axis = cq.Vector(0, math.cos(math.radians(motor_tilt)), -math.sin(math.radians(motor_tilt)))
motor_face = cq.Vector(0, motor_face_y, motor_face_z)
motor_location = cq.Location(motor_face, cq.Vector(1, 0, 0),
                             math.degrees(math.atan2(-motor_axis.y, motor_axis.z)))

# the bracket across the motor's front face (built in the motor's frame),
# hung from a block under the strip
bracket = (
    cq.Workplane("XY").rect(bracket_width, bracket_height).extrude(bracket_thickness)
    .cut(cq.Workplane("XY", origin=(0, 0, -1)).circle(bracket_hole / 2)
         .extrude(bracket_thickness + 2))
    .cut(cq.Workplane("XY", origin=(0, 0, -1))
         .pushPoints([(-motor.mount_hole_spacing / 2, 0), (motor.mount_hole_spacing / 2, 0)])
         .circle(screw_hole / 2).extrude(bracket_thickness + 2))
)
hanger = _box(-width / 2, width / 2, 0, hanger_reach, -hanger_depth, 0)
result = result.union(hanger).union(
    cq.Workplane("XY").add(bracket.val().moved(motor_location)))

regions = {
    "bottom_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[0] + hole_diameter / 2))),
    "top_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[1] + hole_diameter / 2))),
    "front": result.faces(">Y"),
    "back": result.faces(cq.selectors.NearestToPointSelector(
        (0, 0, height / 2))),  # flat: mounts on an upright
    "motor_bracket": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        motor_face + motor_axis * (bracket_thickness / 2) + cq.Vector(0, 0, bracket_hole / 2))),
    "shock_joint": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, shock_mount_y, shock_mount_z + 1))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
