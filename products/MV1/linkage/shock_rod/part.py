"""Shock absorber rod

The upper half of the shock absorber between the steering beam and the
wheel link: a rod that slides in the shock body's bore, its top end a fork
straddling the steering beam's shock tab on a 2 mm pin.

Assumptions where the description is silent:
- the rod is 4 mm across (0.2 mm clearance in the body's 4.4 mm bore),
  reaching 45 mm from the joint's axis;
- its fork matches the body's: two 2 mm cheeks, 3.4 mm apart, rounded
  4 mm about the joint's axis, with a 2.2 mm hole, joined by a 2 mm yoke
  where the rod starts;
- modelled with the joint's axis along x through the origin, the rod along
  +z (the assembly turns it towards the lower joint).
"""
import cadquery as cq

body = load_part("../shock_body")  # the tube it slides in, the fork it matches

# parameters, in mm
diameter = 4.0
reach = 45.0  # the rod's end, from the joint's axis
yoke_start = body.eye_radius  # the yoke across the fork, from the joint's axis
yoke_thickness = 2.0

gap = body.gap
cheek_thickness = body.cheek_thickness
fork_width = body.fork_width

result = (cq.Workplane("XY", origin=(0, 0, yoke_start)).circle(diameter / 2)
          .extrude(reach - yoke_start))
result = result.union(cq.Workplane("XY", origin=(0, 0, yoke_start))
                      .rect(fork_width, 2 * body.eye_radius - 2).extrude(yoke_thickness))
for x0 in (gap / 2, -gap / 2 - cheek_thickness):
    cheek = (
        cq.Workplane("YZ", origin=(x0, 0, 0)).circle(body.eye_radius).extrude(cheek_thickness)
        .union(cq.Workplane("YZ", origin=(x0, 0, 0)).center(0, (yoke_start + yoke_thickness) / 2)
               .rect(2 * body.eye_radius, yoke_start + yoke_thickness).extrude(cheek_thickness))
    )
    result = result.union(cheek)
result = result.cut(cq.Workplane("YZ", origin=(-fork_width, 0, 0))
                    .circle(body.hole_diameter / 2).extrude(2 * fork_width))

regions = {
    "rod": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (diameter / 2, 0, reach - 1))),
    "eye": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (gap / 2 + cheek_thickness / 2, body.hole_diameter / 2, 0))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
