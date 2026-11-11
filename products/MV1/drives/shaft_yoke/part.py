"""Shaft yoke

The drive shaft's half of each coupler, one at each end of the drive shaft:
a sleeve the drive shaft slides in, so it can lengthen and shorten as the
suspension moves, keyed to turn with it (the key not modelled), the other
half of the universal joint on the motor's or the hub's yoke.

Assumptions where the description is silent:
- the motor yoke's 7 mm sleeve, but longer: 2.5 to 14 mm from the joint,
  bored 3.1 mm (a sliding fit on the 3 mm drive shaft) from 4 mm out,
  leaving the shaft 10 mm to slide in each yoke;
- modelled with the joint on the origin, the sleeve along +z (the assembly
  turns it along the drive shaft).
"""
import cadquery as cq

yoke = load_part("../motor_yoke")  # the coupler's sizes

# parameters, in mm
end = 14.0  # longer than the others, for the shaft to slide
bore = 3.1  # a sliding fit on the 3 mm drive shaft

result = (cq.Workplane("XY", origin=(0, 0, yoke.start)).circle(yoke.diameter / 2)
          .extrude(end - yoke.start)
          .cut(cq.Workplane("XY", origin=(0, 0, yoke.bore_start)).circle(bore / 2)
               .extrude(end - yoke.bore_start + 1)))

regions = {
    "bore": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (bore / 2, 0, (yoke.bore_start + end) / 2))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
