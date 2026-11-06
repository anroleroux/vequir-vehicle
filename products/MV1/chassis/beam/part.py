"""Longitudinal beam

A straight beam of the MV1 chassis, running in the longitudinal direction
(front to back, along x), with a flat disc at each end, its centre line in
z, and a hole through each disc's middle; a guide across its top, at the
middle, open to the top and closed at the bottom, that the sliding beam
rests and slides in.

Assumptions where the description is silent:
- a solid bar of rectangular section, 200 mm long between the disc centres
  (x), 10 mm wide (y) and 10 mm high (z);
- each disc is 20 mm in diameter and as thick as the beam is high (10 mm),
  its centre on the beam's end (x = +-100 mm), flush with the beam's top
  and bottom, so the disc's flat bottom is the beam's seat on a lateral
  beam's disc;
- the hole is 3.4 mm, straight through the disc (an M3 clearance, taking a
  3 mm pin with room to spare);
- the guide is a U-channel running laterally (along y) across the beam's
  top at x = 0, extended 40 mm along y (15 mm past each side of the beam),
  so the sliding beam is carried beyond the beam: the channel 10.4 mm wide
  (a 10 mm sliding beam with 0.2 mm clearance each side), closed at the
  bottom by a 3 mm floor flush with the beam's top (the beam's top is the
  floor where they meet), between two cheeks 3 mm thick standing 5 mm
  above the floor; the ends are open, for the sliding beam to slide
  through; the sliding beam sizes itself from it;
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
guide_height = 5.0  # the cheeks, up from the floor (the beam's top)
guide_length = 40.0  # lateral, along y: past each side of the beam
guide_floor = 3.0  # the floor under the channel, down from the beam's top

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
floor_z = height - guide_floor  # the floor's underside
top_z = height + guide_height  # the cheeks' tops
guide = (
    cq.Workplane("XZ")  # the U's profile in x-z, run along y
    .polyline([(-outer, floor_z), (outer, floor_z), (outer, top_z), (inner, top_z),
               (inner, height), (-inner, height), (-inner, top_z), (-outer, top_z)])
    .close()
    .extrude(guide_length / 2, both=True)
)
result = bar.union(discs).cut(holes).union(guide)

regions = {
    "front_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((length / 2, 0, height / 2))),
    "rear_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((-length / 2, 0, height / 2))),
    "guide_floor": result.faces(cq.selectors.NearestToPointSelector((0, 0, height))),
    "guide_underside": result.faces(
        cq.selectors.NearestToPointSelector((0, guide_length / 2 - 1, floor_z))),
    "guide_front_cheek": result.faces(
        cq.selectors.NearestToPointSelector((guide_width / 2, 0, height + guide_height / 2))),
    "guide_rear_cheek": result.faces(
        cq.selectors.NearestToPointSelector((-guide_width / 2, 0, height + guide_height / 2))),
    "bottom": result.faces("<Z"),  # its seat on the lateral beams' discs
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
