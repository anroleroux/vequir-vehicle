"""Linkage plate

A flat plate in the x-z plane (its thickness along y), with a hinge along x
at its top and at its bottom, so arms hinged there swing in the y-z plane.
The four-bar linkage uses two: the fixed plate, and the moving plate facing
it. The side plates are the linkage's I links: each hinge is a single middle
knuckle, between the outer knuckles of an H-link arm.

Assumptions where the description is silent:
- 30 mm wide (x), 50 mm high (z) and 3 mm thick (y);
- each hinge is a set of knuckles about an axis along x, a knuckle's
  radius (3 mm) in front of the plate's back face and in from its top or
  bottom edge, so the knuckles are flush with the back face and the top or
  bottom edge, and stand 3 mm proud of the front face; the back face is
  flat, to mount the plate on (a steering beam's upright);
- the plate carries the middle knuckle (6 mm across, x = +-4.8 mm), the
  arm the two outer ones (from x = +-5 mm to its edges), with 0.2 mm
  between knuckles along x;
- either side of its middle knuckle the plate is cut back to 3.3 mm from
  the axis, so the arm's outer knuckles turn clear of it;
- a 2.2 mm hole along each axis, for a 2 mm pin;
- the plate stands on z = 0, centred on x = 0, its back face on y = 0.
"""
import cadquery as cq

# parameters, in mm
width = 30.0  # along x
height = 50.0  # along z
thickness = 3.0  # along y
knuckle_radius = 3.0  # the hinge knuckles, about each axis
middle = 5.0  # where the arm's outer knuckles start, each side of x = 0
knuckle_gap = 0.2  # between knuckles, along x
knuckle_half = middle - knuckle_gap  # the plate's middle knuckle, each side of x = 0
turn_clearance = 0.3  # radial, around the other leaf's knuckles
hole_diameter = 2.2  # along each hinge axis, for a 2 mm pin

axis_y = knuckle_radius  # the hinge axes: the knuckles flush with the back face
axes_z = [knuckle_radius, height - knuckle_radius]  # bottom, top


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


result = cq.Workplane("XY").box(width, thickness, height, centered=(True, False, False))
for z in axes_z:
    result = result.union(_along_x(-knuckle_half, knuckle_half, axis_y, z, knuckle_radius))
    for x0, x1 in ((knuckle_half, width), (-width, -knuckle_half)):
        result = result.cut(_along_x(x0, x1, axis_y, z, knuckle_radius + turn_clearance))
    result = result.cut(_along_x(-width, width, axis_y, z, hole_diameter / 2))

regions = {
    "bottom_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[0] + hole_diameter / 2))),
    "top_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[1] + hole_diameter / 2))),
    "front": result.faces(">Y"),
    "back": result.faces("<Y"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
