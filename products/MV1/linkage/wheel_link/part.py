"""Wheel link

The wheel-side vertical link of the four-bar linkage: the linkage plate (an
I link, a straight strip with a middle knuckle at its top and bottom
hinges), its strip extended down below the bottom hinge, where the wheel
will come.

Assumptions where the description is silent:
- the extension is the strip's width and thickness (9.6 x 3 mm), 30 mm
  below the plate's bottom edge, straight down, flush with its back face;
- nothing for the wheel yet: its axle and mounting come with the wheel;
- the plate stands on the extension: its hinges are 30 mm higher than the
  linkage plate's (axes_z), on the same back face (y = 0), centred on
  x = 0.
"""
import cadquery as cq

plate = load_part("../plate")  # the linkage plate it extends

# parameters, in mm
extension = 30.0  # below the plate's bottom edge, for the wheel

width = plate.width
thickness = plate.thickness
height = plate.height + extension
axis_y = plate.axis_y
axes_z = [z + extension for z in plate.axes_z]  # bottom, top

below = cq.Workplane("XY").box(width, thickness, extension, centered=(True, False, False))
result = cq.Workplane("XY").add(plate.result.val().translate(cq.Vector(0, 0, extension))).union(below)

regions = {
    "bottom_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[0] + plate.hole_diameter / 2))),
    "top_hinge": result.faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[1] + plate.hole_diameter / 2))),
    "wheel_end": result.faces("<Z"),  # where the wheel will come
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
