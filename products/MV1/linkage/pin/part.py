"""Hinge pin

A plain round pin through a hinge's knuckles: the arm's two outer knuckles
and the linkage plate's middle one.

Assumptions where the description is silent:
- 2 mm in diameter, a running fit in the knuckles' 2.2 mm holes, as long
  as the plate is wide (30 mm), flush with its edges; retained by a press
  fit or glue at its ends, not modelled;
- modelled standing up, along z from z = 0 (the assembly lays it along x).
"""
import cadquery as cq

plate = load_part("../plate")

# parameters, in mm
diameter = 2.0
length = plate.width  # flush with the plate's edges

result = cq.Workplane("XY").circle(diameter / 2).extrude(length)

regions = {
    "shank": result.faces("%CYLINDER"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
