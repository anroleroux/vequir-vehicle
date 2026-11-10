"""Lateral steering beam

A straight beam of the MV1 chassis, running in the lateral direction
(sideways, along y), shorter than the longitudinal beam, with a disc on top
and a pin sticking up from the disc's middle. The longitudinal beam's end
disc sits on this disc, the pin in its hole, so the beam turns about the
pin to steer. A T leg runs from its middle in the longitudinal direction
(along x), towards the middle of the longitudinal beam, to steer it by.
Its ends extend downward and are widened, into uprights.

Assumptions where the description is silent:
- a solid bar of rectangular section, 120 mm long (y), 10 mm wide (x) and
  10 mm high (z);
- the disc is the longitudinal beam's disc diameter (20 mm) and 3 mm thick,
  centred on the beam's middle, on its top;
- the pin is 0.2 mm smaller than the main beam's hole (3.2 mm in a
  3.4 mm hole) and as tall as the main beam plate is thick (3 mm), so it
  locates the plate through its whole hole and ends flush with its top;
- the leg has the bar's 10 x 10 mm section and stands out 40 mm from the
  bar's side, along -x: with the beam under the front of the longitudinal
  beam it points rearwards, under the longitudinal beam, and the rear copy
  is turned half a turn so its leg points forwards; it stands on z = 0 like
  the bar, its top 3 mm below the longitudinal beam's bottom (the disc's
  thickness), so it swings clear under it;
- each end is an upright, extended 40 mm down below the bar, the bar's
  width (10 mm) along x and 10 mm thick along y, the end face flush with
  the bar's end: the linkage plate's height (50 mm overall), so each end
  face is an x-z face to mount the linkage's 9.6 mm plate on;
- lateral along y (+y is the left), centred on x = 0 and y = 0 (the
  vehicle's centreline), standing on z = 0 on its uprights; the bar and
  the leg are 40 mm up.
"""
import cadquery as cq

beam = load_part("../beam")  # the longitudinal beam this one supports
linkage_plate = load_part("../../linkage/plate")  # the ends' height, to mount it on

# parameters, in mm
length = 120.0  # lateral, along y; shorter than the longitudinal beam
width = 10.0  # longitudinal, along x
height = 10.0  # vertical, along z
disc_diameter = beam.disc_diameter  # matches the longitudinal beam's end disc
disc_thickness = 3.0
pin_clearance = 0.2  # diametral, in the longitudinal beam's hole
pin_diameter = beam.hole_diameter - pin_clearance
pin_height = beam.disc_thickness  # flush with the main beam's top
leg_length = 40.0  # the T leg, along -x from the bar's side
end_width = width  # the uprights, along x: the bar's width
end_thickness = 10.0  # the uprights, along y, in from each end
drop = linkage_plate.height - height  # the uprights below the bar

bar_z = drop  # the bar's bottom
top = bar_z + height + disc_thickness  # the disc's top face: the longitudinal beam's seat
end_y = [length / 2 - end_thickness / 2, -(length / 2 - end_thickness / 2)]  # left, right

bar = cq.Workplane("XY", origin=(0, 0, bar_z)).rect(width, length).extrude(height)
disc = cq.Workplane("XY", origin=(0, 0, bar_z + height)).circle(disc_diameter / 2).extrude(
    disc_thickness)
pin = cq.Workplane("XY", origin=(0, 0, top)).circle(pin_diameter / 2).extrude(pin_height)
leg = (
    cq.Workplane("XY", origin=(-(width / 2 + leg_length / 2), 0, bar_z))
    .rect(leg_length, width)
    .extrude(height)
)
ends = (
    cq.Workplane("XY")
    .pushPoints([(0, y) for y in end_y])
    .rect(end_width, end_thickness)
    .extrude(drop + height)
)
result = bar.union(leg).union(ends).union(disc).union(pin)

regions = {
    "seat": result.faces(cq.selectors.NearestToPointSelector((disc_diameter / 2 - 1, 0, top))),
    "pin": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((0, 0, top + pin_height / 2))),
    "feet": result.faces("<Z"),  # the uprights' bottoms
    "leg_end": result.faces(cq.selectors.NearestToPointSelector(
        (-(width / 2 + leg_length), 0, bar_z + height / 2))),  # where the steering takes hold
    "left_end": result.faces(">Y"),  # x-z faces the linkage plate's size
    "right_end": result.faces("<Y"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
