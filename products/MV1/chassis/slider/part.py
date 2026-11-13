"""Steering slider

The slider in the slot along the steering beam's leg: a block that runs in
the slot, with a flange on top resting on the leg's top plate, and a hole
for the pin on the steering servo's horn, which turns in it while the
slider runs along the slot.

Assumptions where the description is silent:
- the block is 6 mm long (along the slot) and 0.2 mm narrower than the
  slot each side (3.6 mm), as deep as the leg's top plate is thick (2 mm);
- the flange is 8 mm long, 7 mm wide and 1 mm thick, on the top plate's
  top, keeping the slider from dropping through;
- a 2.2 mm hole on its centre for the 2 mm pin;
- modelled with the pin's axis on x = 0, y = 0, the slot along x, the
  block's bottom (the top plate's underside) on z = 0.
"""
import cadquery as cq

beam = load_part("../steering_beam")  # the slot it runs in

# parameters, in mm
length = 6.0  # along the slot
clearance = 0.2  # each side, in the slot
flange_length = 8.0
flange_width = 7.0
flange_thickness = 1.0
hole_diameter = 2.2

width = beam.slot_width - 2 * clearance
depth = beam.plate_thickness  # the block, in the slot
height = depth + flange_thickness

block = cq.Workplane("XY").rect(length, width).extrude(depth)
flange = (cq.Workplane("XY", origin=(0, 0, depth)).rect(flange_length, flange_width)
          .extrude(flange_thickness))
hole = cq.Workplane("XY", origin=(0, 0, -1)).circle(hole_diameter / 2).extrude(height + 2)
result = block.union(flange).cut(hole)

regions = {
    "hole": result.faces("%CYLINDER"),
    "flange_bottom": result.faces(cq.selectors.NearestToPointSelector(
        (flange_length / 2 - 0.2, 0, depth))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
