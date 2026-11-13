"""Belt drive wheel link

The moving upright of the belt drive's four-bar linkage: the base link's Y
plate (one hinge at the bottom middle, two top ends either side of the top
hinge, the drive shaft's bearing seat half way between), without the shock
joints, its stem carried on down past the bottom link to the wheel hub's
bearing. A belt will run from the drive shaft's end down to the hub.

Assumptions where the description is silent:
- the base link's hinges, widths, thickness and shaft bearing seat, so the
  two uprights face each other and the links between them are parallel;
- the stem runs 22 mm below the bottom hinge's knuckle, as in the drives,
  straight down, flush with the back face;
- the hub's axis runs along y through the stem, 8 mm up from its bottom,
  17 mm below the bottom hinge's axis: a 4.2 mm bore for a 4 mm axle,
  through the plate and a 12 mm boss standing 4 mm proud of the back face
  (the outer face, towards the wheel);
- it stands on the stem's bottom: its hinges are 22 mm higher than the base
  link's (axes_z), its back face on y = 0, centred on x = 0.
"""
import cadquery as cq

base = load_part("../base_link")  # the upright it matches

# parameters, in mm
extension = 22.0  # the stem, below the bottom hinge's knuckle, for the wheel
hub_z = 8.0  # the hub's axis, up from the bottom
hub_bore = 4.2  # for the hub's 4 mm axle
boss_diameter = 12.0  # the hub's bearing boss, on the back (outer) face
boss_height = 4.0  # proud of the back face

thickness = base.thickness
width = base.width
axis_y = base.axis_y
axes_z = [z + extension for z in base.axes_z]  # bottom, top
shaft_z = base.shaft_z + extension  # the drive shaft's bearing seat
height = base.height + extension
prong_x = base.shock_x  # the top ends' centres, each side of x = 0

result = base.upright(below=extension).translate((0, 0, extension))
# the hub's bearing: a boss through the plate, proud of the back face
boss = (cq.Workplane("XZ", origin=(0, thickness, 0)).center(0, hub_z)
        .circle(boss_diameter / 2).extrude(thickness + boss_height))  # along -y
bore = (cq.Workplane("XZ", origin=(0, thickness + 1, 0)).center(0, hub_z)
        .circle(hub_bore / 2).extrude(thickness + boss_height + 2))
result = result.union(boss).cut(bore)

regions = {
    "bottom_hinge": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[0] + base.hole_diameter / 2))),
    "top_hinge_left": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (prong_x, axis_y, axes_z[1] + base.hole_diameter / 2))),
    "top_hinge_right": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (-prong_x, axis_y, axes_z[1] + base.hole_diameter / 2))),
    "shaft_bearing": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, thickness / 2, shaft_z + base.shaft_bore / 2))),
    "hub_bore": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, -boss_height / 2, hub_z + hub_bore / 2))),
    "hub_boss": result.faces("<Y"),  # the hub runs against it
    "wheel_end": result.faces("<Z"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
