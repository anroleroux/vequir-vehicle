"""Belt drive bottom link

The bottom link of the belt drive's four-bar linkage: two flat bars along
y, side by side, joined by a crossbar in the middle: an H seen from above.
Each bar ends in a hinge knuckle, the outer knuckles either side of an
upright's stem. A lug stands on each bar, the lower joint of a shock
absorber that comes down from the base link's top extension above it.

Assumptions where the description is silent:
- the top link's 55 mm between its hinge axes (along y), so the linkage is
  a parallelogram; 3 mm thick;
- the bars start 5 mm either side of x = 0 (0.2 mm clear of the stems'
  knuckles) and run out to the uprights' overall width (26.4 mm): 8.2 mm
  wide each, 10 mm apart;
- the crossbar is 10 mm long (y), in the middle of the link;
- a knuckle of 3 mm radius across each bar's ends, with a 2.2 mm hole along
  each axis for a 2 mm pin;
- each shock lug is 5 mm thick (x), in the plane of the base link's top
  end above it, standing on its bar to a rounded end (4 mm radius) about a
  2.2 mm hole along x, 36 mm out from the base end's axis and 7 mm above
  the axes;
- the axes at y = 0 and y = 55 mm, 3 mm up (the knuckles stand on z = 0),
  the bars on their mid-plane, centred on x = 0.
"""
import cadquery as cq

base = load_part("../base_link")  # the upright it hinges on
top = load_part("../top_link")  # the link it runs parallel to

# parameters, in mm
length = top.length  # between the hinge axes, along y
thickness = 3.0  # along z
crossbar = 10.0  # the H's crossbar, along y
shock_joint_y = 36.0  # the shocks' lower joints, out from the base end's axis
shock_joint_up = 7.0  # above the hinge axes
shock_eye_radius = base.shock_eye_radius
knuckle_radius = base.knuckle_radius
hole_diameter = base.hole_diameter

inner = base.stem_middle  # the bars, from here ...
outer = base.prong_outer  # ... to here, each side of x = 0
bar_width = outer - inner
width = 2 * outer
axis_z = knuckle_radius
axes_y = [0.0, length]  # base end, wheel end
shock_joint_z = axis_z + shock_joint_up
lug_x = [base.prong_inner, -base.prong_outer]  # each lug's -x face
lug_width = base.prong_width


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


z0 = axis_z - thickness / 2
result = (cq.Workplane("XY", origin=(0, length / 2, z0)).rect(2 * inner + 1, crossbar)
          .extrude(thickness))
for x0, x1 in ((inner, outer), (-outer, -inner)):
    result = result.union(cq.Workplane("XY", origin=((x0 + x1) / 2, length / 2, z0))
                          .rect(bar_width, length).extrude(thickness))
    for y in axes_y:
        result = result.union(_along_x(x0, x1, y, axis_z, knuckle_radius))
for x0 in lug_x:
    lug = (
        cq.Workplane("YZ", origin=(x0, 0, 0))
        .center(shock_joint_y, (z0 + shock_joint_z) / 2)
        .rect(2 * shock_eye_radius, shock_joint_z - z0).extrude(lug_width)
        .union(cq.Workplane("YZ", origin=(x0, 0, 0)).center(shock_joint_y, shock_joint_z)
               .circle(shock_eye_radius).extrude(lug_width))
    )
    result = result.union(lug)
result = result.cut(_along_x(-width, width, shock_joint_y, shock_joint_z, hole_diameter / 2))
for y in axes_y:
    result = result.cut(_along_x(-width, width, y, axis_z, hole_diameter / 2))

regions = {
    "top": result.faces(cq.selectors.NearestToPointSelector((0, length / 2, z0 + thickness))),
    "bottom": result.faces(cq.selectors.NearestToPointSelector((0, length / 2, z0))),
    "shock_joint_left": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (base.shock_x, shock_joint_y, shock_joint_z + hole_diameter / 2))),
    "shock_joint_right": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (-base.shock_x, shock_joint_y, shock_joint_z + hole_diameter / 2))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
