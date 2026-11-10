"""MV1 linkage

A four-bar linkage moving in the y-z plane: the fixed plate in the x-z
plane, two arms hinged to its top and bottom, and the wheel link (the
plate, extended down for the wheel) hinged to the arms' far ends, turned
half a turn to face the fixed one. The arms are
equal, so the linkage is a parallelogram: the wheel link swings in y-z and
stays parallel to the fixed plate. Shown with the arms level (swing = 0);
a swing turns the arms about the fixed plate's hinges, up for positive.
"""
import math

import cadquery as cq

plate = load_part("plate")
arm = load_part("arm")
pin = load_part("pin")
wheel = load_part("wheel_link")
wheel_pin = load_part("wheel_pin")

swing = 0.0  # degrees, the arms about the fixed plate's hinges, up positive

near_y = plate.axis_y  # the fixed plate's hinge axes
far_y = near_y + arm.length * math.cos(math.radians(swing))  # the wheel link's
rise = arm.length * math.sin(math.radians(swing))  # the wheel link, along z

result = cq.Assembly(name="linkage")
result.add(plate.result, name="fixed_plate", color=cq.Color(0.25, 0.40, 0.55))
# a half turn about z puts its hinge axis at -axis_y; move it out to far_y,
# and down so its hinges meet the arms'
drop = wheel.axes_z[0] - plate.axes_z[0]
result.add(wheel.result, name="wheel_link", color=cq.Color(0.25, 0.40, 0.55),
           loc=cq.Location(cq.Vector(0, far_y + wheel.axis_y, rise - drop),
                           cq.Vector(0, 0, 1), 180))
for name, z in (("bottom_arm", plate.axes_z[0]), ("top_arm", plate.axes_z[1])):
    # turned about x (+y towards +z for a positive swing), about its near axis
    turn = cq.Location(cq.Vector(0, near_y, z), cq.Vector(1, 0, 0), swing)
    result.add(arm.result, name=name, color=cq.Color(0.80, 0.45, 0.20),
               loc=turn * cq.Location(cq.Vector(0, 0, -arm.axis_z)))
# the pins lie along x (+z turned to +x), from the arms' -x edge; the wheel
# side's hinges are wider, with longer pins
for side, part, half, y, dz in (("fixed", pin, plate.hinge_width / 2, near_y, 0.0),
                                ("wheel", wheel_pin, wheel.hinge_width / 2, far_y, rise)):
    for level, z in (("bottom", plate.axes_z[0] + dz), ("top", plate.axes_z[1] + dz)):
        result.add(part.result, name=f"{side}_{level}_pin", color=cq.Color(0.70, 0.70, 0.72),
                   loc=cq.Location(cq.Vector(-half, y, z), cq.Vector(0, 1, 0), 90))

regions = {}
