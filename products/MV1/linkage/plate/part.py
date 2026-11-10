"""Linkage plate

A straight upright strip in the x-z plane (its thickness along y), with a
hinge along x at its top and at its bottom, so arms hinged there swing in
the y-z plane. The four-bar linkage uses two: the fixed plate, and the
moving plate facing it. The side plates are the linkage's I links: the
strip is only as wide as its hinges' middle knuckle, which sits between the
outer knuckles of an H-link arm, and runs straight down from the top hinge
to the bottom one.

Assumptions where the description is silent:
- the hinges are 30 mm wide overall (x): the arms' width and the pins'
  length; the strip is the middle knuckle's width, 0.2 mm short of the
  arm's outer knuckles each side (9.6 mm);
- 50 mm high (z) and 3 mm thick (y);
- each hinge is a knuckle about an axis along x, a knuckle's radius (3 mm)
  in front of the plate's back face and in from its top or bottom edge, so
  the knuckle is flush with the back face and the top or bottom edge, and
  stands 3 mm proud of the front face; the back face is flat, to mount the
  plate on (a steering beam's upright);
- a 2.2 mm hole along each axis, for a 2 mm pin;
- the shock absorber's upper joint is a tab on the steering beam's upright
  behind it, 3 mm thick (x), standing 10 mm out from the plate's back face
  at z = 36 mm, between the arms; it passes through a window in the strip,
  0.2 mm larger all round than the tab (3.4 x 8.4 mm), which leaves 3.1 mm
  of strip either side;
- the plate stands on z = 0, centred on x = 0, its back face on y = 0.
"""
import cadquery as cq

# parameters, in mm
hinge_width = 30.0  # the hinges overall, along x: the arms and the pins
height = 50.0  # along z
thickness = 3.0  # along y
knuckle_radius = 3.0  # the hinge knuckles, about each axis
middle = 5.0  # where the arm's outer knuckles start, each side of x = 0
knuckle_gap = 0.2  # between knuckles, along x
knuckle_half = middle - knuckle_gap  # the plate's middle knuckle, each side of x = 0
turn_clearance = 0.3  # radial, around the other leaf's knuckles
hole_diameter = 2.2  # along each hinge axis, for a 2 mm pin

shock_mount_y = 10.0  # the shock's upper joint, out from the back face
shock_mount_z = 36.0  # the shock's upper joint, between the arms
shock_tab_thickness = 3.0  # the steering beam's tab, along x
shock_eye_radius = 4.0  # around the joints' pins
tab_clearance = 0.2  # around the tab, in the window

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
window = cq.Workplane("XZ").center(0, shock_mount_z).rect(
    shock_tab_thickness + 2 * tab_clearance,
    2 * (shock_eye_radius + tab_clearance)).extrude(-thickness * 3).translate((0, -thickness, 0))
result = result.cut(window)

regions = {
    "bottom_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[0] + hole_diameter / 2))),
    "top_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[1] + hole_diameter / 2))),
    "front": result.faces(">Y"),
    "back": result.faces("<Y"),  # flat: mounts on an upright
    "shock_window": result.faces(cq.selectors.BoxSelector(
        (-shock_tab_thickness, -1, shock_mount_z - shock_eye_radius - 1),
        (shock_tab_thickness, thickness + 1, shock_mount_z + shock_eye_radius + 1))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
