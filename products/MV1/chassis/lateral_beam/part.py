"""Lateral steering beam

The MV1 chassis's steering beam, running in the lateral direction
(sideways, along y), built from plates rather than solid bars: a top plate
along the beam that turns down at each end into an outer end plate, the
upright a linkage mounts on, with a curved gusset along each side edge
that runs the entire beam and down both uprights. A disc on top, with a pin
sticking up from its middle, carries the main beam's round end, its pin in
the end's hole, so the beam turns about the pin to steer. A T leg, built
the same way, runs from its middle in the longitudinal direction (along x),
towards the middle of the chassis, to steer it by.

Assumptions where the description is silent:
- 60 mm long (y) and 10 mm wide (x), 50 mm tall at its ends (the linkage
  plate's height), so each end plate's outer face is an x-z face to mount
  the linkage's 9.6 mm plate on;
- the top plate and the end plates are 2 mm thick;
- the gussets are 1.5 mm plates flush with the beam's side edges (x =
  +-5 mm), 8 mm deep: under the top plate along the beam and in from the
  end plates down the uprights, their inner edge curved to 15 mm where
  the beam turns down into the uprights;
- the leg stands out 40 mm from the beam's side, along -x: a 10 mm wide
  top plate with an 8 mm deep gusset along each edge and an end plate;
  with the beam under the front of the main beam it points rearwards, and
  the rear copy is turned half a turn so its leg points forwards; its top
  is the beam's, 3 mm below the main beam's bottom (the disc's thickness),
  so it swings clear under it;
- the disc is the main beam's round end (20 mm) and 3 mm thick, centred on
  the beam's middle, on its top plate;
- the pin is 0.2 mm smaller than the main beam's hole (3.2 mm in a
  3.4 mm hole) and as tall as the main beam plate is thick (3 mm), so it
  locates the plate through its whole hole and ends flush with its top;
- lateral along y (+y is the left), centred on x = 0 and y = 0 (the
  vehicle's centreline), standing on z = 0 on its uprights.
"""
import cadquery as cq

beam = load_part("../beam")  # the main beam this one carries
linkage_plate = load_part("../../linkage/plate")  # the uprights' height, to mount it on

# parameters, in mm
length = 60.0  # lateral, along y
width = 10.0  # longitudinal, along x
height = linkage_plate.height  # to the top plate's top, along z
plate_thickness = 2.0  # the top plate and the end plates
gusset_thickness = 1.5  # along x (along y on the leg)
gusset_depth = 8.0  # under the top plate, and in from the end plates
gusset_radius = 15.0  # the gussets' inner edge, where the beam turns down
leg_length = 40.0  # the T leg, along -x from the beam's side
disc_diameter = beam.disc_diameter  # matches the main beam's round end
disc_thickness = 3.0
pin_clearance = 0.2  # diametral, in the main beam's hole
pin_diameter = beam.hole_diameter - pin_clearance
pin_height = beam.disc_thickness  # flush with the main beam's top

top = height + disc_thickness  # the disc's top face: the main beam's seat
leg_end = width / 2 + leg_length  # the leg's end, along -x


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate(
        (x0, y0, z0))


# the top plate and the outer end plates
result = _box(-width / 2, width / 2, -length / 2, length / 2, height - plate_thickness, height)
for y0 in (length / 2 - plate_thickness, -length / 2):
    result = result.union(_box(-width / 2, width / 2, y0, y0 + plate_thickness, 0, height))

# a gusset along each side edge: the beam's outline less a band 8 mm in, its
# inner corners curved where the beam turns down into the uprights
outline = cq.Workplane("YZ").center(0, height / 2).rect(length, height).extrude(gusset_thickness)
inside = (
    cq.Workplane("YZ")
    .center(0, (height - gusset_depth - 1) / 2 - 1)
    .rect(length - 2 * gusset_depth, height - gusset_depth + 1)
    .extrude(gusset_thickness)
    .edges("|X").edges(">Z")
    .fillet(gusset_radius)
)
gusset = outline.cut(inside)
for x0 in (width / 2 - gusset_thickness, -width / 2):
    result = result.union(gusset.translate((x0, 0, 0)))

# the T leg: a top plate, a gusset along each edge, an end plate
result = result.union(_box(-leg_end, -width / 2, -width / 2, width / 2,
                           height - plate_thickness, height))
for y0 in (width / 2 - gusset_thickness, -width / 2):
    result = result.union(_box(-leg_end, -width / 2, y0, y0 + gusset_thickness,
                               height - gusset_depth, height))
result = result.union(_box(-leg_end, -leg_end + plate_thickness, -width / 2, width / 2,
                           height - gusset_depth, height))

# the disc and the pin the main beam turns on
disc = cq.Workplane("XY", origin=(0, 0, height)).circle(disc_diameter / 2).extrude(
    disc_thickness)
pin = cq.Workplane("XY", origin=(0, 0, top)).circle(pin_diameter / 2).extrude(pin_height)
result = result.union(disc).union(pin)

regions = {
    "seat": result.faces(cq.selectors.NearestToPointSelector((disc_diameter / 2 - 1, 0, top))),
    "pin": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((0, 0, top + pin_height / 2))),
    "feet": result.faces("<Z"),  # the uprights' bottoms
    "leg_end": result.faces("<X"),  # where the steering takes hold
    "left_end": result.faces(">Y"),  # x-z faces to mount the linkage on
    "right_end": result.faces("<Y"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
