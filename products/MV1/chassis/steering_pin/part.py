"""Steering pin

The pin pressed into the steering servo's horn, reaching down into the
slider in the steering beam's slot, where it turns.

Assumptions where the description is silent:
- 2 mm across (a press fit in the horn's 2 mm hole, a running fit in the
  slider's 2.2 mm hole), from the horn's top face down to 0.2 mm above the
  slider's bottom: 8.3 mm long;
- modelled standing up, along z from z = 0.
"""
import cadquery as cq

# parameters, in mm
diameter = 2.0
length = 8.3

result = cq.Workplane("XY").circle(diameter / 2).extrude(length)

regions = {
    "shank": result.faces("%CYLINDER"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
