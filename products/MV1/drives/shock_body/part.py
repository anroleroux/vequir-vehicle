"""Shock absorber body

The lower half of the shock absorber between the steering beam and the
wheel link: a tube, closed at its bottom end, which is a fork straddling
the wheel link's shock tab on a 2 mm pin. The shock rod slides in it.

Assumptions where the description is silent:
- the tube is 10 mm across with a 4.4 mm bore for the 4 mm rod, 41 mm
  long, starting 5 mm from the joint's axis, closed for its first 2 mm;
- the fork's two cheeks are 2 mm thick, either side of the 3 mm tab with
  0.2 mm clearance (3.4 mm between them, 7.4 mm overall), each rounded
  4 mm about the joint's axis, with a 2.2 mm hole;
- the travel it allows: 56 to 84 mm between the joints' axes, the rod's
  end at least 5 mm off the bore's bottom and 8 mm inside the tube;
- modelled with the joint's axis along x through the origin, the tube
  along +z (the assembly turns it towards the upper joint).
"""
import cadquery as cq

plate = load_part("../plate")  # the joints' tab and eye

# parameters, in mm
tube_diameter = 10.0
bore_diameter = 4.4  # for the 4 mm rod
tube_length = 41.0
tube_start = 5.0  # from the joint's axis
tube_floor = 2.0  # closed at its bottom
cheek_thickness = 2.0
tab_clearance = 0.2  # each side of the tab, between the cheeks
eye_radius = plate.shock_eye_radius
hole_diameter = plate.hole_diameter

gap = plate.shock_tab_thickness + 2 * tab_clearance  # between the cheeks
fork_width = gap + 2 * cheek_thickness  # along x
tube_top = tube_start + tube_length  # from the joint's axis

tube = (cq.Workplane("XY", origin=(0, 0, tube_start)).circle(tube_diameter / 2)
        .extrude(tube_length))
bore = (cq.Workplane("XY", origin=(0, 0, tube_start + tube_floor)).circle(bore_diameter / 2)
        .extrude(tube_length))
result = tube.cut(bore)
for x0 in (gap / 2, -gap / 2 - cheek_thickness):
    cheek = (
        cq.Workplane("YZ", origin=(x0, 0, 0)).circle(eye_radius).extrude(cheek_thickness)
        .union(cq.Workplane("YZ", origin=(x0, 0, 0)).center(0, tube_start / 2 + 0.5)
               .rect(2 * eye_radius, tube_start + 1).extrude(cheek_thickness))
    )
    result = result.union(cheek)
result = result.cut(cq.Workplane("YZ", origin=(-fork_width, 0, 0)).circle(hole_diameter / 2)
                    .extrude(2 * fork_width))

regions = {
    "bore": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (bore_diameter / 2, 0, tube_top - 1))),
    "eye": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (gap / 2 + cheek_thickness / 2, hole_diameter / 2, 0))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
