"""Belt drive top link

The top link of the belt drive's four-bar linkage: a single flat bar in the
x-y plane (its thickness along z), with a hinge knuckle along x across each
end: the middle knuckle between an upright's two top ends.

Assumptions where the description is silent:
- 55 mm between its hinge axes (along y), as the drives' arms; 3 mm thick;
- 16 mm wide (x), 0.2 mm clear of the uprights' top ends each side;
- a knuckle of 3 mm radius across each end, with a 2.2 mm hole along its
  axis for a 2 mm pin;
- the axes at y = 0 and y = 55 mm, 3 mm up (the knuckles stand on z = 0),
  the bar on their mid-plane, centred on x = 0.
"""
import cadquery as cq

base = load_part("../base_link")  # the upright it hinges on

# parameters, in mm
length = 55.0  # between the hinge axes, along y
thickness = 3.0  # along z
width = 2 * base.bar_half  # along x, between the uprights' top ends
knuckle_radius = base.knuckle_radius
hole_diameter = base.hole_diameter

axis_z = knuckle_radius
axes_y = [0.0, length]  # base end, wheel end


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


z0 = axis_z - thickness / 2
result = cq.Workplane("XY", origin=(0, length / 2, z0)).rect(width, length).extrude(thickness)
for y in axes_y:
    result = result.union(_along_x(-width / 2, width / 2, y, axis_z, knuckle_radius))
    result = result.cut(_along_x(-width, width, y, axis_z, hole_diameter / 2))

regions = {
    "base_hinge": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, axes_y[0], axis_z + hole_diameter / 2))),
    "wheel_hinge": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, axes_y[1], axis_z + hole_diameter / 2))),
    "top": result.faces(cq.selectors.NearestToPointSelector((0, length / 2, z0 + thickness))),
    "bottom": result.faces(cq.selectors.NearestToPointSelector((0, length / 2, z0))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
