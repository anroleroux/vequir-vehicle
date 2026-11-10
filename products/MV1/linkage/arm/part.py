"""Linkage arm

A flat plate in the x-y plane (its thickness along z), with a hinge along x
at each end: two outer knuckles either side of an I link's middle one. The
arms are the linkage's H links, at the top and bottom; the linkage plate and
the wheel link are its I links. Its legs angle out towards the wheel, so the
H is wider at the wheel end, and the slot between the legs there runs
deeper than at the chassis end, leaving room for a shock absorber to pass
through. The crossbar's corners are filleted. Two arms of equal length make
the four-bar linkage a parallelogram, so the wheel link stays parallel to
the linkage plate.

Assumptions where the description is silent:
- 40 mm between its hinge axes (along y), 3 mm thick;
- at the chassis end (y = 0) it is the linkage plate's hinge width (30 mm),
  at the wheel end (y = 40 mm) the wheel link's (40 mm); its outer edges
  and its legs (10 mm wide) run straight between them;
- its outer knuckles, 6 mm across like the I links', run from 0.2 mm beyond
  the I link's middle knuckle to its edges: x = +-5 to +-15 mm at the
  chassis end, +-10 to +-20 mm at the wheel end;
- the slot at the chassis end is the knuckle gap's width (10 mm) and runs
  10 mm in; the slot at the wheel end runs 20 mm in, between the legs'
  inner edges (20 mm wide at the hinge, 15 mm where it ends), leaving a
  10 mm crossbar; around each axis it is cut back to 3.3 mm from the axis
  so it turns clear of the I link's middle knuckle;
- the crossbar's four corners, where the slots meet the legs, are filleted
  to 3 mm;
- a 2.2 mm hole along each axis, for a 2 mm pin;
- the axes at y = 0 and y = 40 mm, 3 mm up (so the knuckles stand on
  z = 0), the plate on their mid-plane, centred on x = 0.
"""
import cadquery as cq

plate = load_part("../plate")  # the I link at the chassis end
wheel = load_part("../wheel_link")  # the I link at the wheel end

# parameters, in mm
length = 40.0  # between the hinge axes, along y
thickness = 3.0  # along z
chassis_slot = 10.0  # the slot at the chassis end, in from its axis
wheel_slot = 20.0  # the slot at the wheel end, in from its axis: room for a shock absorber
crossbar_fillet = 3.0  # the crossbar's corners
knuckle_radius = plate.knuckle_radius
cut_radius = plate.knuckle_radius + plate.turn_clearance  # around the I links' knuckles
hole_diameter = plate.hole_diameter

axis_z = knuckle_radius
axes_y = [0.0, length]  # chassis end, wheel end
# half widths at each end: overall, and where the outer knuckles start
outer = [plate.hinge_width / 2, wheel.hinge_width / 2]
inner = [plate.middle, wheel.middle]


def _at(y, ends):
    """A half width at y, straight between its values at the two ends."""
    return ends[0] + (ends[1] - ends[0]) * y / length


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


z0 = axis_z - thickness / 2
result = (
    cq.Workplane("XY", origin=(0, 0, z0))
    .polyline([(-outer[0], 0), (outer[0], 0), (outer[1], length), (-outer[1], length)])
    .close()
    .extrude(thickness)
)
# the slots: square at the chassis end, between the legs at the wheel end
reach = cut_radius + 1  # past the axis, clear of the knuckles
chassis = cq.Workplane("XY", origin=(0, 0, z0 - 1)).polyline([
    (-inner[0], -reach), (inner[0], -reach), (inner[0], chassis_slot), (-inner[0], chassis_slot),
]).close().extrude(thickness + 2)
y1 = length - wheel_slot
wheel_cut = cq.Workplane("XY", origin=(0, 0, z0 - 1)).polyline([
    (-_at(y1, inner), y1), (_at(y1, inner), y1),
    (_at(length + reach, inner), length + reach), (-_at(length + reach, inner), length + reach),
]).close().extrude(thickness + 2)
result = result.cut(chassis).cut(wheel_cut)
for x, y in [(inner[0], chassis_slot), (-inner[0], chassis_slot),
             (_at(y1, inner), y1), (-_at(y1, inner), y1)]:
    result = result.edges("|Z").edges(cq.selectors.BoxSelector(
        (x - 0.5, y - 0.5, z0 - 1), (x + 0.5, y + 0.5, z0 + thickness + 1))).fillet(crossbar_fillet)
# the knuckles, the cut-backs around the I links' knuckles, the holes
for y, half_outer, half_inner in zip(axes_y, outer, inner):
    for x0, x1 in ((half_inner, half_outer), (-half_outer, -half_inner)):
        result = result.union(_along_x(x0, x1, y, axis_z, knuckle_radius))
    result = result.cut(_along_x(-half_inner, half_inner, y, axis_z, cut_radius))
    result = result.cut(_along_x(-half_outer - 1, half_outer + 1, y, axis_z, hole_diameter / 2))

regions = {
    "top": result.faces(cq.selectors.NearestToPointSelector((0, length / 2, z0 + thickness))),
    "bottom": result.faces(cq.selectors.NearestToPointSelector((0, length / 2, z0))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
