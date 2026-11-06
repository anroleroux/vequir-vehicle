"""Longitudinal beam

A straight beam of the MV1 chassis, running in the longitudinal direction
(front to back, along x), with a flat disc at each end, its centre line in
z, and a hole through each disc's middle; a dovetail slot across its
underside, at the middle, for the sliding beam.

Assumptions where the description is silent:
- a solid bar of rectangular section, 200 mm long between the disc centres
  (x), 10 mm wide (y) and 10 mm high (z);
- each disc is 20 mm in diameter and as thick as the beam is high (10 mm),
  its centre on the beam's end (x = +-100 mm), flush with the beam's top
  and bottom, so the disc's flat bottom is the beam's seat on a lateral
  beam's disc;
- the hole is 3.4 mm, straight through the disc (an M3 clearance, taking a
  3 mm pin with room to spare);
- the slot runs laterally (along y) right across the beam's underside at
  x = 0: a dovetail 6.4 mm wide at its mouth, 8.4 mm at its top, 4.2 mm
  deep, so it holds the sliding beam's tongue up against the beam and lets
  it slide only sideways (the sliding beam sizes its tongue from these);
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
slot_mouth = 6.4  # dovetail slot's width at the underside, along x
slot_top = 8.4  # its width at the top of the slot, along x
slot_depth = 4.2  # up from the underside

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
slot = (
    cq.Workplane("XZ")  # the dovetail's profile in x-z, run right across in y
    .polyline([(-slot_mouth / 2, 0), (slot_mouth / 2, 0),
               (slot_top / 2, slot_depth), (-slot_top / 2, slot_depth)])
    .close()
    .extrude(width / 2, both=True)
)
result = bar.union(discs).cut(holes).cut(slot)

regions = {
    "front_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((length / 2, 0, height / 2))),
    "rear_hole": result.faces("%CYLINDER").faces(
        cq.selectors.NearestToPointSelector((-length / 2, 0, height / 2))),
    "slot_top": result.faces(cq.selectors.NearestToPointSelector((0, 0, slot_depth))),
    "top": result.faces(">Z"),
    "bottom": result.faces("<Z"),  # its seat on the lateral beams' discs
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
