"""Motor yoke

The drive motor's half of the coupler between its shaft and the drive
shaft: a sleeve pressed onto the motor's 2 mm shaft. The two halves of each
coupler meet at its joint, a universal joint, so the drive shaft can run at
an angle to the shafts it joins as the suspension moves.

Assumptions where the description is silent:
- a 7 mm sleeve from 2.5 to 10 mm from the joint, closed at its joint end,
  bored 2.0 mm (a press fit on the motor's shaft) from 4 mm out; the
  joint's cross and its pins, inside the 5 mm between the two halves, are
  not modelled;
- modelled with the joint on the origin, the sleeve along +z (the assembly
  turns it along the motor's shaft).
"""
import cadquery as cq

motor = load_library("actuators/motor_130")  # the shaft it is pressed onto

# parameters, in mm
diameter = 7.0
start = 2.5  # the sleeve's end at the joint, out from the joint
end = 10.0
bore_start = 4.0  # where the shaft's end sits, out from the joint
bore = motor.shaft_diameter

result = (cq.Workplane("XY", origin=(0, 0, start)).circle(diameter / 2).extrude(end - start)
          .cut(cq.Workplane("XY", origin=(0, 0, bore_start)).circle(bore / 2)
               .extrude(end - bore_start + 1)))

regions = {
    "bore": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (bore / 2, 0, (bore_start + end) / 2))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
