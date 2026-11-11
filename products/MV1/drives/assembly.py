"""MV1 drive

One of the MV1's four drives: a four-bar linkage moving in the y-z plane: the fixed plate in the x-z
plane, two arms hinged to its top and bottom, and the wheel link (the
plate, extended down for the wheel) hinged to the arms' far ends, turned
half a turn to face the fixed one. The arms are
equal, so the linkage is a parallelogram: the wheel link swings in y-z and
stays parallel to the fixed plate. A shock absorber runs from the
fixed plate's joint, carried up and out over the top arm, down through the
top and bottom arms' wheel-end openings to the tab on the wheel link below
the bottom arm: its body at the bottom, its rod at the top,
sliding in it as the linkage moves. A drive motor hangs on the fixed
plate's bracket below the bottom hinge, tilted down at the wheel hub on the
wheel link: its shaft, a coupler, the drive shaft, a second coupler and the
hub's axle; the couplers are universal joints and the drive shaft slides in
their yokes, so the drive follows the suspension. The wheel is bolted to
the hub's flange. Shown with the arms level (swing = 0);
a swing turns the arms about the fixed plate's hinges, up for positive; the
shock's travel allows +-15 degrees.
"""
import math

import cadquery as cq

plate = load_part("plate")
arm = load_part("arm")
pin = load_part("pin")
wheel = load_part("wheel_link")
wheel_pin = load_part("wheel_pin")
shock_body = load_part("shock_body")
shock_rod = load_part("shock_rod")
shock_pin = load_part("shock_pin")
motor = load_library("actuators/motor_130")
motor_yoke = load_part("motor_yoke")
shaft_yoke = load_part("shaft_yoke")
hub_yoke = load_part("hub_yoke")
drive_shaft = load_part("drive_shaft")
hub = load_part("wheel_hub")
wheel_part = load_part("wheel")

swing = 0.0  # degrees, the arms about the fixed plate's hinges, up positive

near_y = plate.axis_y  # the fixed plate's hinge axes
far_y = near_y + arm.length * math.cos(math.radians(swing))  # the wheel link's
rise = arm.length * math.sin(math.radians(swing))  # the wheel link, along z

result = cq.Assembly(name="drive")
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

# the shock absorber, between its joints, in this frame (the fixed plate's
# back face on y = 0): the fixed plate's, over the top arm, and the wheel link's
upper = cq.Vector(0, plate.shock_mount_y, plate.shock_mount_z)
lower = cq.Vector(0, far_y + wheel.axis_y - wheel.shock_joint_y,
                  wheel.shock_joint_z + rise - drop)
span = upper - lower
shock_length = span.Length  # between the joints' axes
up = math.degrees(math.atan2(-span.y, span.z))  # turns +z towards the upper joint
down = math.degrees(math.atan2(span.y, -span.z))  # turns +z towards the lower joint
result.add(shock_body.result, name="shock_body", color=cq.Color(0.85, 0.20, 0.15),
           loc=cq.Location(lower, cq.Vector(1, 0, 0), up))
result.add(shock_rod.result, name="shock_rod", color=cq.Color(0.80, 0.80, 0.82),
           loc=cq.Location(upper, cq.Vector(1, 0, 0), down))
for name, at in (("upper_shock_pin", upper), ("lower_shock_pin", lower)):
    result.add(shock_pin.result, name=name, color=cq.Color(0.70, 0.70, 0.72),
               loc=cq.Location(at - cq.Vector(shock_pin.length / 2, 0, 0),
                               cq.Vector(0, 1, 0), 90))


def _along(at, axis):
    """A location at ``at`` turning a part's +z to ``axis`` (in the y-z plane)."""
    return cq.Location(at, cq.Vector(1, 0, 0), math.degrees(math.atan2(-axis.y, axis.z)))


# the drive: the motor on the fixed plate's bracket, its coupler's joint along
# its shaft; the hub's coupler's joint on the hub's axis, which runs along +y
# (out of the wheel link), moving with it
result.add(motor.result, name="motor", color=cq.Color(0.75, 0.75, 0.70), loc=plate.motor_location)
motor_joint = plate.motor_face + plate.motor_axis * (
    motor.shaft_length + motor_yoke.bore_start + 0.2)
hub_joint = cq.Vector(0, far_y + wheel.axis_y - wheel.drive_joint_y, wheel.hub_z + rise - drop)
drive = (hub_joint - motor_joint).normalized()
outward = cq.Vector(0, 1, 0)
result.add(motor_yoke.result, name="motor_yoke", color=cq.Color(0.55, 0.55, 0.60),
           loc=_along(motor_joint, -plate.motor_axis))
result.add(shaft_yoke.result, name="motor_shaft_yoke", color=cq.Color(0.55, 0.55, 0.60),
           loc=_along(motor_joint, drive))
result.add(shaft_yoke.result, name="hub_shaft_yoke", color=cq.Color(0.55, 0.55, 0.60),
           loc=_along(hub_joint, -drive))
result.add(hub_yoke.result, name="hub_yoke", color=cq.Color(0.55, 0.55, 0.60),
           loc=_along(hub_joint, outward))
# the drive shaft centred between the joints, sliding in the shaft yokes
span_middle = (motor_joint + hub_joint) * 0.5
result.add(drive_shaft.result, name="drive_shaft", color=cq.Color(0.70, 0.70, 0.72),
           loc=_along(span_middle - drive * (drive_shaft.length / 2), drive))
hub_at = hub_joint + outward * hub.inner_end  # the hub's axle's inner end
result.add(hub.result, name="wheel_hub", color=cq.Color(0.20, 0.20, 0.22),
           loc=_along(hub_at, outward))
# the wheel against the hub's flange, on its spigot
result.add(wheel_part.result, name="wheel", color=cq.Color(0.10, 0.10, 0.10),
           loc=_along(hub_at + outward * (hub.axle_length + hub.flange_thickness), outward))

regions = {}
