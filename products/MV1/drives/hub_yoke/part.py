"""Hub yoke

The wheel hub's half of the coupler between the drive shaft and the hub: a
sleeve pressed onto the hub's 4 mm axle, the other half of the universal
joint on the drive shaft.

Assumptions where the description is silent:
- the motor yoke's 7 mm sleeve, 2.5 to 10 mm from the joint, bored 4.0 mm
  (a press fit on the hub's axle) from 4 mm out;
- modelled with the joint on the origin, the sleeve along +z (the assembly
  turns it along the hub's axle).
"""
import cadquery as cq

yoke = load_part("../motor_yoke")  # the coupler's sizes

# parameters, in mm
bore = 4.0  # the hub's axle

result = (cq.Workplane("XY", origin=(0, 0, yoke.start)).circle(yoke.diameter / 2)
          .extrude(yoke.end - yoke.start)
          .cut(cq.Workplane("XY", origin=(0, 0, yoke.bore_start)).circle(bore / 2)
               .extrude(yoke.end - yoke.bore_start + 1)))

regions = {
    "bore": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (bore / 2, 0, (yoke.bore_start + yoke.end) / 2))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
