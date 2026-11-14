"""MV1 belt drive

The links of the belt drive, the MV1's second suspension concept: a
four-bar linkage moving in the y-z plane. The base link's flat back face is
on y = 0; the top link (a single flat bar) and the bottom link (an H of two
bars) are hinged to it and, at their far ends, to the wheel link, turned
half a turn to face the base link, its stem reaching down past the bottom
link to the wheel hub's bearing. The links are equal, so the linkage is a
parallelogram and the drive shaft's bearing seats in the two uprights, half
way between the links, stay a link's length apart. Shown with the links
level (swing = 0); a swing turns them about the base link's hinges, up for
positive. Only the links for now: the pins, the two shock absorbers, the
drive shaft, the belts, the motor and the hub come later.
"""
import math

import cadquery as cq

base = load_part("base_link")
top = load_part("top_link")
bottom = load_part("bottom_link")
wheel = load_part("wheel_link")

swing = 0.0  # degrees, the links about the base link's hinges, up positive

near_y = base.axis_y  # the base link's hinge axes
far_y = near_y + top.length * math.cos(math.radians(swing))  # the wheel link's
rise = top.length * math.sin(math.radians(swing))  # the wheel link, along z

result = cq.Assembly(name="belt_drive")
result.add(base.result, name="base_link", color=cq.Color(0.25, 0.40, 0.55))
# a half turn about z puts its hinge axis at -axis_y; move it out to far_y,
# and down so its hinges meet the links'
drop = wheel.axes_z[0] - base.axes_z[0]
result.add(wheel.result, name="wheel_link", color=cq.Color(0.25, 0.40, 0.55),
           loc=cq.Location(cq.Vector(0, far_y + wheel.axis_y, rise - drop),
                           cq.Vector(0, 0, 1), 180))
for name, link, z in (("bottom_link", bottom, base.axes_z[0]), ("top_link", top, base.axes_z[1])):
    # turned about x (+y towards +z for a positive swing), about its near axis
    turn = cq.Location(cq.Vector(0, near_y, z), cq.Vector(1, 0, 0), swing)
    result.add(link.result, name=name, color=cq.Color(0.80, 0.45, 0.20),
               loc=turn * cq.Location(cq.Vector(0, 0, -link.axis_z)))

# the shocks' joints, for the shock absorbers to come: on the base link's
# top extensions and on the bottom link's lugs, in the same planes
shock_upper = cq.Vector(base.shock_x, base.shock_mount_y, base.shock_mount_z)
_out = bottom.shock_joint_y
_up = bottom.shock_joint_up
_c, _s = math.cos(math.radians(swing)), math.sin(math.radians(swing))
shock_lower = cq.Vector(base.shock_x, near_y + _out * _c - _up * _s,
                        base.axes_z[0] + _out * _s + _up * _c)
shock_length = (shock_upper - shock_lower).Length  # between the joints' axes

regions = {}
