"""Longitudinal beam

A straight beam of the MV1 chassis, running in the longitudinal direction
(front to back, along x), with a flat disc at each end, its centre line in
z, and a hole through each disc's middle; a guide across its top, at the
middle, open to the top and closed at the bottom, sunk into the beam, that
the sliding beam rests and slides in.

Assumptions where the description is silent:
- a solid bar of rectangular section, 200 mm long between the disc centres
  (x), 10 mm wide (y) and 10 mm high (z);
- each disc is 20 mm in diameter and as thick as the beam is high (10 mm),
  its centre on the beam's end (x = +-100 mm), flush with the beam's top
  and bottom, so the disc's flat bottom is the beam's seat on a lateral
  beam's disc;
- the hole is 3.4 mm, straight through the disc (an M3 clearance, taking a
  3 mm pin with room to spare);
- the guide is a U-channel running laterally (along y) across the beam at
  x = 0, extended 40 mm along y (15 mm past each side of the beam), so the
  sliding beam is carried beyond the beam: the channel 10.4 mm wide (a
  10 mm sliding beam with 0.2 mm clearance each side) and 5 mm deep,
  closed at the bottom by a 3 mm floor, between two cheeks 3 mm thick; the
  ends are open, for the sliding beam to slide through; the sliding beam
  sizes itself from it;
- the whole guide is sunk into the beam: its top flush with the beam's top,
  the channel cut 5 mm into the beam (leaving 5 mm of beam under the
  floor's top) and the floor's underside 2 mm above the beam's bottom, so
  the sliding beam stands only 5 mm above the beam;
- longitudinal along x (+x is the front), centred on x = 0 and y = 0 (the
  vehicle's centreline), standing on z = 0.
"""
import cadquery as cq

# parameters, in mm
length = 200.0  # longitudinal, between the disc centres, along x
width = 10.0  # lateral, along y
height = 10.0  # vertical, along z
disc_diameter = 20.0  # the end discs, centre line in z
disc_thickness = height  # flush with the beam's top and bottom
hole_diameter = 3.4  # through each disc's middle
guide_width = 10.4  # the channel between the cheeks, along x
guide_wall = 3.0  # each cheek's thickness, along x
guide_depth = 5.0  # the channel, down from the beam's top (the guide's top)
guide_length = 40.0  # lateral, along y: past each side of the beam
guide_floor = 3.0  # the floor under the channel

disc_x = [length / 2, -length / 2]  # front, rear

bar = cq.Workplane("XY").rect(length, width).extrude(height)
discs = (
    cq.Workplane("XY")
    .pushPoints([(x, 0) for x in disc_x])
    .circle(disc_diameter / 2)
    .extrude(disc_thickness)
)
holes = (
    cq.Workplane("XY")
    .pushPoints([(x, 0) for x in disc_x])
    .circle(hole_diameter / 2)
    .extrude(disc_thickness)
)
outer = guide_width / 2 + guide_wall  # the guide's outer faces, either side of x = 0
inner = guide_width / 2
guide_floor_z = height - guide_depth  # the channel's floor: the sliding beam's seat
floor_z = guide_floor_z - guide_floor  # the floor's underside
guide = (
    cq.Workplane("XZ")  # the guide's outline in x-z, run along y
    .rect(2 * outer, height - floor_z, centered=(True, False))
    .extrude(guide_length / 2, both=True)
    .translate((0, 0, floor_z))
)
channel = (
    cq.Workplane("XY", origin=(0, 0, guide_floor_z))
    .rect(guide_width, guide_length)
    .extrude(guide_depth)
)
result = bar.union(discs).cut(holes).union(guide).cut(channel)

regions = {
    "front_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((length / 2, 0, height / 2))),
    "rear_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((-length / 2, 0, height / 2))),
    "guide_floor": result.faces(cq.selectors.NearestToPointSelector((0, 0, guide_floor_z))),
    "guide_underside": result.faces(
        cq.selectors.NearestToPointSelector((0, guide_length / 2 - 1, floor_z))),
    "guide_front_cheek": result.faces(
        cq.selectors.NearestToPointSelector((guide_width / 2, 0, height - guide_depth / 2))),
    "guide_rear_cheek": result.faces(
        cq.selectors.NearestToPointSelector((-guide_width / 2, 0, height - guide_depth / 2))),
    "bottom": result.faces("<Z"),  # its seat on the lateral beams' discs
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
