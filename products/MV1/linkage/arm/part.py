"""Linkage arm

A flat plate in the x-y plane (its thickness along z), the plates' width,
with a hinge along x at each end: two outer knuckles either side of a
linkage plate's middle one. The arms are the linkage's H links, at the top
and bottom; the side plates are its I links. A slot cut in from each hinge
between its outer knuckles gives the arm its H shape. Two arms of equal length make the four-bar linkage
a parallelogram, so the moving plate stays parallel to the fixed one.

Assumptions where the description is silent:
- 40 mm between its hinge axes (along y), 3 mm thick, as wide as the
  hinges (30 mm);
- its outer knuckles, 6 mm across like the plate's, run from 0.2 mm beyond
  the plate's middle knuckle (x = +-5 mm) to its edges; between them,
  around each axis, it is cut back to 3.3 mm from the axis so it turns
  clear of the plate's middle knuckle;
- the slot is as wide as the gap between the outer knuckles (10 mm) and
  runs 12 mm in from each hinge axis, leaving a 16 mm crossbar in the
  middle and two 10 mm wide legs either side, so the plate's middle
  knuckle and strip swing freely in it;
- a 2.2 mm hole along each axis, for a 2 mm pin;
- the axes at y = 0 and y = 40 mm, 3 mm up (so the knuckles stand on
  z = 0), the plate on their mid-plane, centred on x = 0.
"""
import cadquery as cq

plate = load_part("../plate")  # the plates it is hinged to

# parameters, in mm
length = 40.0  # between the hinge axes, along y
thickness = 3.0  # along z
width = plate.hinge_width  # along x
knuckle_radius = plate.knuckle_radius
middle = plate.middle  # the outer knuckles start here, each side of x = 0
cut_radius = plate.knuckle_radius + plate.turn_clearance  # around the plate's knuckles
hole_diameter = plate.hole_diameter
slot_depth = 12.0  # the H's slot, in from each hinge axis, along y

axis_z = knuckle_radius
axes_y = [0.0, length]


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


result = cq.Workplane("XY", origin=(0, 0, axis_z - thickness / 2)).box(
    width, length, thickness, centered=(True, False, False))
for y in axes_y:
    for x0, x1 in ((middle, width / 2), (-width / 2, -middle)):
        result = result.union(_along_x(x0, x1, y, axis_z, knuckle_radius))
    result = result.cut(_along_x(-middle, middle, y, axis_z, cut_radius))
    inward = 1 if y == axes_y[0] else -1  # towards the crossbar
    slot = (
        cq.Workplane("XY", origin=(0, y + inward * slot_depth / 2, -1))
        .rect(2 * middle, slot_depth)
        .extrude(2 * knuckle_radius + 2)
    )
    result = result.cut(slot)
    result = result.cut(_along_x(-width, width, y, axis_z, hole_diameter / 2))

regions = {
    "top": result.faces(cq.selectors.NearestToPointSelector((width / 2 - 1, length / 2, axis_z + thickness / 2))),
    "bottom": result.faces(cq.selectors.NearestToPointSelector((width / 2 - 1, length / 2, axis_z - thickness / 2))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
