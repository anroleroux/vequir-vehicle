"""Bed tray

The MV1's rear bed: an open tray on four legs on the chassis's base plate,
above the rear drives' base links, fixed while the cab in front of it turns
with the front steering. Its front is set back from the farthest the cab's
back reaches as it turns, so the two never meet.

Assumptions where the description is silent:
- the cab turns with the front steering beam, at most as far as the
  steering servo's horn turned 90 degrees turns it (about 17.3 degrees);
  the tray's front is 5 mm behind the farthest back its rounded back
  corners then reach;
- it runs back to 125 mm behind the middle (x = -125 mm), over the rear
  drives, and is the cab's 140 mm wide, its corners rounded to 6 mm;
- a 3 mm floor and 2 mm walls, 22 mm tall overall, open on top;
- a 2.2 mm hole through the floor over each leg, for an M2 screw into it;
- modelled in the MV1's x and y, its floor's bottom on z = 0 (2 mm above
  the rear drives' base links' tops).
"""
import math

import cadquery as cq

cab = load_part("../../cab/body")
beam = load_part("../../chassis/beam")  # the front pivot, the servos
horn = load_library("actuators/sg90_horn")

# parameters, in mm
clearance = 5.0  # behind the cab's back's farthest reach
rear = -125.0  # the tray's back, along x
width = cab.width
corner = 6.0
floor = 3.0
wall = 2.0
height = 22.0
screw_hole = 2.2
leg_spots = [(40.0, 40.0), (40.0, -40.0), (-60.0, 30.0), (-60.0, -30.0)]  # on the base plate

# how far back the cab's back reaches: its back corners' arcs, turned as far
# as the steering goes (the servo's horn at 90 degrees, its pin 14 mm out)
pivot_x = beam.length / 2
max_turn = math.atan2(horn.arm_length, pivot_x - beam.servo_x)
reach = pivot_x
for side in (1, -1):
    cx, cy = cab.back + cab.corner, side * (cab.width / 2 - cab.corner)  # the corner arc's centre
    for turn in (-max_turn, 0.0, max_turn):
        x = cx * math.cos(turn) - cy * math.sin(turn)
        reach = min(reach, pivot_x + x - cab.corner)
front = reach - clearance

length = front - rear
outer = (cq.Workplane("XY").center((front + rear) / 2, 0).rect(length, width).extrude(height)
         .edges("|Z").fillet(corner))
inner = (cq.Workplane("XY", origin=(0, 0, floor)).center((front + rear) / 2, 0)
         .rect(length - 2 * wall, width - 2 * wall).extrude(height)
         .edges("|Z").fillet(corner - wall))
result = outer.cut(inner).cut(
    cq.Workplane("XY", origin=(0, 0, -1)).pushPoints(leg_spots).circle(screw_hole / 2)
    .extrude(floor + 2))

regions = {
    "floor_bottom": result.faces("<Z"),
    "front_wall": result.faces(cq.selectors.NearestToPointSelector((front, 0, height / 2))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
