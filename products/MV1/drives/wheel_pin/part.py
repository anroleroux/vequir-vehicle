"""Wheel hinge pin

A plain round pin through a wheel-side hinge's knuckles: the arm's two
outer knuckles and the wheel link's middle one. Like the hinge pin, longer
for the wider hinge.

Assumptions where the description is silent:
- the hinge pin's 2 mm diameter, as long as the wheel-side hinge is wide
  (40 mm), flush with the arm's edges; retained by a press fit or glue at
  its ends, not modelled;
- modelled standing up, along z from z = 0 (the assembly lays it along x).
"""
import cadquery as cq

pin = load_part("../pin")
wheel = load_part("../wheel_link")

# parameters, in mm
diameter = pin.diameter
length = wheel.hinge_width  # flush with the arm's edges

result = cq.Workplane("XY").circle(diameter / 2).extrude(length)

regions = {
    "shank": result.faces("%CYLINDER"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
