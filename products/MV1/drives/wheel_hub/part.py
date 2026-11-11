"""Wheel hub

The wheel hub on the wheel link: a 4 mm axle running in the wheel link's
bore, driven at its inner end through the hub's coupler, and a flange
outside the bearing boss that the wheel bolts to.

Assumptions where the description is silent:
- the axle reaches from 4.2 mm out from the coupler's joint (in the hub
  yoke's bore) through the strip and the boss to 0.5 mm clear of the boss;
- the flange is 20 mm across and 3 mm thick, with three 2 mm holes on a
  13 mm circle for the wheel's screws, and a 6 mm spigot 3 mm long on its
  outer face to centre the wheel;
- modelled with the axle along +z from its inner end on z = 0.
"""
import cadquery as cq

wheel = load_part("../wheel_link")  # the bore and boss it runs in
yoke = load_part("../motor_yoke")  # the couplers' sizes: where the axle's end sits

# parameters, in mm
axle_diameter = 4.0
flange_diameter = 20.0
flange_thickness = 3.0
flange_clearance = 0.5  # from the boss
bolt_circle = 13.0
bolt_hole = 2.0
spigot_diameter = 6.0
spigot_length = 3.0

inner_end = yoke.bore_start + 0.2  # from the coupler's joint, along the axle
# the axle, from its inner end out past the boss: the joint is drive_joint_y
# in from the wheel link's back face, the boss boss_height out from it
axle_length = wheel.drive_joint_y - inner_end + wheel.boss_height + flange_clearance

axle = cq.Workplane("XY").circle(axle_diameter / 2).extrude(axle_length)
flange = (cq.Workplane("XY", origin=(0, 0, axle_length)).circle(flange_diameter / 2)
          .extrude(flange_thickness)
          .cut(cq.Workplane("XY", origin=(0, 0, axle_length - 1))
               .polarArray(bolt_circle / 2, 90, 360, 3).circle(bolt_hole / 2)
               .extrude(flange_thickness + 2)))
spigot = (cq.Workplane("XY", origin=(0, 0, axle_length + flange_thickness))
          .circle(spigot_diameter / 2).extrude(spigot_length))
result = axle.union(flange).union(spigot)

regions = {
    "axle": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (axle_diameter / 2, 0, axle_length / 2))),
    "wheel_face": result.faces(cq.selectors.NearestToPointSelector(
        (flange_diameter / 2 - 1, 0, axle_length + flange_thickness))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
