"""Steering pin

The pin pressed into the steering servo's horn, reaching down into the
slider in the steering beam's slot, where it turns.

Assumptions where the description is silent:
- 2 mm across (a press fit in the horn's 2 mm hole, a running fit in the
  slider's 2.2 mm hole), from the horn arm's top face down to 0.2 mm above
  the slider's bottom: its length follows from the servo upside down on the
  main beam, the horn on its shaft and the slider in the leg's slot;
- modelled standing up, along z from z = 0.
"""
import cadquery as cq

beam = load_part("../beam")
steering = load_part("../steering_beam")
servo = load_library("actuators/sg90")
horn = load_library("actuators/sg90_horn")

# parameters, in mm
diameter = 2.0
above_bottom = 0.2  # the pin's end, above the slider's bottom

plate_top = steering.top + beam.thickness
housing_bottom = plate_top + servo.case_height - servo.housing_top  # the horn's servo face
arm_top = housing_bottom - horn.arm_z  # the horn upside down: its arm's face towards the servo
slot_bottom = steering.height - steering.plate_thickness
length = arm_top - (slot_bottom + above_bottom)

result = cq.Workplane("XY").circle(diameter / 2).extrude(length)

regions = {
    "shank": result.faces("%CYLINDER"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
