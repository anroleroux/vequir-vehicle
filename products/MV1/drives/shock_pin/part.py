"""Shock pin

A plain round pin through a shock absorber fork's cheeks and the tab
between them, at the upper and the lower joint.

Assumptions where the description is silent:
- the hinge pin's 2 mm diameter, as long as the fork is wide (7.4 mm),
  flush with its cheeks; retained by a press fit, not modelled;
- modelled standing up, along z from z = 0 (the assembly lays it along x).
"""
import cadquery as cq

pin = load_part("../pin")
body = load_part("../shock_body")

# parameters, in mm
diameter = pin.diameter
length = body.fork_width  # flush with the cheeks

result = cq.Workplane("XY").circle(diameter / 2).extrude(length)

regions = {
    "shank": result.faces("%CYLINDER"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
