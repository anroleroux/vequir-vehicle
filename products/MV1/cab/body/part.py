"""Cab body

The MV1's cab: a shell with a floor, four walls and a roof, with a
windscreen, side windows and a back window. It rests on the tops of the
front drives' base links (their towers' bars) and the front steering
beam's two posts, all at one height, and is screwed to the posts, so it
turns with the front steering about the front pivot.

Assumptions where the description is silent:
- in plan 57 mm long (x, from 12 mm behind the front pivot to 45 mm in
  front of it) and 140 mm wide (y), covering both drives' bars (out to
  y = +-68 mm), its corners rounded to 12 mm so its back sweeps as little
  as it can when it turns;
- 45 mm tall overall: a 3 mm floor, 2 mm walls and roof;
- a windscreen 120 x 22 mm in the front wall, 15 mm up; a side window
  35 x 20 mm in each side wall, 18 mm up; a back window 80 x 16 mm, 22 mm
  up;
- a 2.2 mm hole through the floor over each post, for an M2 screw into it;
- modelled with the front pivot's axis on x = 0, y = 0, the floor's bottom
  (the posts' and bars' tops) on z = 0.
"""
import cadquery as cq

front_beam = load_part("../../chassis/front_steering_beam")  # the posts it rests on

# parameters, in mm
back = -12.0  # behind the front pivot, along x
front = 45.0
width = 140.0  # along y
corner = 12.0  # the plan's corners
height = 45.0
floor = 3.0
wall = 2.0
roof = 2.0
screw_hole = 2.2
windscreen = (120.0, 22.0, 15.0)  # width, height, up from the floor's bottom
side_window = (35.0, 20.0, 18.0)  # length, height, up
back_window = (80.0, 16.0, 22.0)  # width, height, up

length = front - back
centre_x = (front + back) / 2

outer = (cq.Workplane("XY").center(centre_x, 0).rect(length, width).extrude(height)
         .edges("|Z").fillet(corner))
inner = (cq.Workplane("XY", origin=(0, 0, floor)).center(centre_x, 0)
         .rect(length - 2 * wall, width - 2 * wall).extrude(height - floor - roof)
         .edges("|Z").fillet(corner - wall))
result = outer.cut(inner)


def _window(x, y, z, sx, sy, sz):
    return cq.Workplane("XY").box(sx, sy, sz).translate((x, y, z))


ws_w, ws_h, ws_z = windscreen
result = result.cut(_window(front - wall / 2, 0, ws_z + ws_h / 2, wall * 3, ws_w, ws_h))
sw_l, sw_h, sw_z = side_window
for side in (1, -1):
    result = result.cut(_window(centre_x, side * (width / 2 - wall / 2), sw_z + sw_h / 2,
                                sw_l, wall * 3, sw_h))
bw_w, bw_h, bw_z = back_window
result = result.cut(_window(back + wall / 2, 0, bw_z + bw_h / 2, wall * 3, bw_w, bw_h))
result = result.cut(cq.Workplane("XY", origin=(0, 0, -1))
                    .pushPoints([(front_beam.post_x, front_beam.post_y),
                                 (front_beam.post_x, -front_beam.post_y)])
                    .circle(screw_hole / 2).extrude(floor + 2))

regions = {
    "floor_bottom": result.faces("<Z"),  # on the posts and the bars
    "roof": result.faces(">Z"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
