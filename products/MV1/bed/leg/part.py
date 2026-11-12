"""Bed leg

One of the four legs the rear bed stands on: a post from the chassis's
base plate up to the tray's floor, screwed into from above through the
floor.

Assumptions where the description is silent:
- 6 x 6 mm, standing on the base plate's top (60 mm up) and reaching the
  tray's floor, 2 mm above the rear drives' base links' tops (93 mm up):
  33 mm tall;
- a 1.6 mm pilot hole down its top for the M2 screw through the floor, and
  it is glued or screwed to the plate below (not modelled);
- modelled standing on z = 0, centred on x = 0, y = 0.
"""
import cadquery as cq

chassis_beam = load_part("../../chassis/beam")
steering = load_part("../../chassis/steering_beam")
plate = load_part("../../drives/plate")

# parameters, in mm
size = 6.0
pilot = 1.6
above_drives = 2.0  # the tray's floor, above the rear drives' base links' tops

plate_top = steering.top + chassis_beam.thickness  # the base plate's top
floor_z = steering.upright_bottom + plate.tower_top + above_drives  # the tray's floor
height = floor_z - plate_top

result = (cq.Workplane("XY").rect(size, size).extrude(height)
          .cut(cq.Workplane("XY", origin=(0, 0, height - 8)).circle(pilot / 2).extrude(9)))

regions = {
    "top": result.faces(">Z"),
    "foot": result.faces("<Z"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
