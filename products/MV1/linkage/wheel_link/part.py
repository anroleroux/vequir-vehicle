"""Wheel link

The wheel-side vertical link of the four-bar linkage: an I link like the
linkage plate, a straight upright strip only as wide as its hinges' middle
knuckle, but wider, for the H-link arms' legs that angle out towards the
wheel. Its strip extends down below the bottom hinge, where the wheel will
come. A tab on its inner face there is the lower joint of the shock
absorber, below the bottom arm.

Assumptions where the description is silent:
- its hinges are 40 mm wide overall (x), 10 mm wider than at the linkage
  plate: the arms' legs angle out 5 mm each side over their length; the
  strip is the middle knuckle's width, 0.2 mm short of the arm's outer
  knuckles each side (19.6 mm);
- the linkage plate's 50 mm between its top and bottom edges, its 3 mm
  thickness, 3 mm knuckle radius and 2.2 mm holes, its knuckles flush with
  its back face;
- the extension is the strip's width and thickness, 30 mm below the bottom
  edge, straight down, flush with its back face; nothing for the wheel
  yet: its axle and mounting come with the wheel;
- the shock tab is 3 mm thick (x), centred, standing out from the front
  face (the inner face, towards the chassis) to a rounded end (4 mm
  radius) about a 2.2 mm hole, 13 mm from the back face and 12 mm up from
  the extension's bottom: 18 mm below the bottom arm's hinge axis;
- it stands on the extension: its hinges are 30 mm higher than the linkage
  plate's (axes_z), its back face on y = 0, centred on x = 0.
"""
import cadquery as cq

plate = load_part("../plate")  # the linkage plate it matches

# parameters, in mm
hinge_width = 40.0  # the hinges overall, along x: the arms' wheel ends, the wheel pins
middle = 10.0  # where the arm's outer knuckles start, each side of x = 0
extension = 30.0  # below the bottom edge, for the wheel

knuckle_gap = plate.knuckle_gap
knuckle_half = middle - knuckle_gap  # the middle knuckle, each side of x = 0
knuckle_radius = plate.knuckle_radius
hole_diameter = plate.hole_diameter
thickness = plate.thickness
width = 2 * knuckle_half  # the strip, along x
height = plate.height + extension
axis_y = plate.axis_y
axes_z = [z + extension for z in plate.axes_z]  # bottom, top
shock_joint_y = 13.0  # the shock's lower joint, out from the back face
shock_joint_z = 12.0  # the shock's lower joint, up from the bottom
shock_tab_thickness = plate.shock_tab_thickness
shock_eye_radius = plate.shock_eye_radius


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


result = cq.Workplane("XY").box(width, thickness, height, centered=(True, False, False))
for z in axes_z:
    result = result.union(_along_x(-knuckle_half, knuckle_half, axis_y, z, knuckle_radius))
    result = result.cut(_along_x(-width, width, axis_y, z, hole_diameter / 2))
tab_x = -shock_tab_thickness / 2
tab = (
    cq.Workplane("YZ", origin=(tab_x, 0, 0))
    .center((thickness + shock_joint_y) / 2 - 0.5, shock_joint_z)
    .rect(shock_joint_y - thickness + 1, 2 * shock_eye_radius)
    .extrude(shock_tab_thickness)
    .union(cq.Workplane("YZ", origin=(tab_x, 0, 0)).center(shock_joint_y, shock_joint_z)
           .circle(shock_eye_radius).extrude(shock_tab_thickness))
)
result = result.union(tab).cut(_along_x(-width, width, shock_joint_y, shock_joint_z,
                                        hole_diameter / 2))

regions = {
    "bottom_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[0] + hole_diameter / 2))),
    "top_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[1] + hole_diameter / 2))),
    "wheel_end": result.faces("<Z"),  # where the wheel will come
    "shock_tab": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, shock_joint_y, shock_joint_z + 1))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
