"""Longitudinal beam

A straight beam of the MV1 chassis, running in the longitudinal direction
(front to back, along x).

Assumptions where the description is silent:
- a solid bar of rectangular section, 200 mm long (x), 10 mm wide (y) and
  10 mm high (z), with plain square ends;
- longitudinal along x (+x is the front), centred on x = 0 and y = 0 (the
  vehicle's centreline), standing on z = 0;
- no holes or other features yet.
"""
import cadquery as cq

# parameters, in mm
length = 200.0  # longitudinal, along x
width = 10.0  # lateral, along y
height = 10.0  # vertical, along z

result = (
    cq.Workplane("XY")
    .rect(length, width)  # centred on x = 0, y = 0
    .extrude(height)  # from z = 0 up
)

regions = {
    "front_end": result.faces(">X"),
    "rear_end": result.faces("<X"),
    "top": result.faces(">Z"),
    "bottom": result.faces("<Z"),
    "left_side": result.faces(">Y"),
    "right_side": result.faces("<Y"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
