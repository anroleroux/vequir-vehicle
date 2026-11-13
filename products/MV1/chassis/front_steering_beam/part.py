"""Front steering beam

The front steering beam: the steering beam, with an extrusion forward on
each end of its lateral beam, on the opposite side to the steering lever
(its T leg). Each extrusion is an arm forward from the beam's top and a
post up to the height of the front drives' base links' tops, so the cab
rests on the posts and those tops and turns with the steering.

Assumptions where the description is silent:
- each arm runs forward (+x) from the beam's front face, 25 mm, 8 mm deep
  under the beam's top and 6 mm wide (y), its outer face flush with the
  end plate's (y = +-30 mm), clear of the drive mounted outside it;
- each post is the arm's 6 x 8 mm, at the arm's front end, standing up to
  the drives' base links' tops (91 mm: the linkage plate's 62 mm tower
  over the uprights' 29 mm), with a 2.2 mm hole down its top for an M2
  screw into the cab's floor; the corner between arm and post filled with
  a curved gusset, 10 mm radius;
- otherwise the steering beam, in its frame.
"""
import cadquery as cq

beam = load_part("../steering_beam")
plate = load_part("../../drives/plate")  # the base links' tops, the cab's other seats

# parameters, in mm
arm_reach = 25.0  # forward of the beam's front face
arm_depth = 8.0  # under the beam's top
arm_width = 6.0  # along y, in from the end plate's outer face
post_length = 6.0  # along x
gusset_radius = 10.0
screw_hole = 2.2

post_top = beam.upright_bottom + plate.tower_top  # the base links' tops: where the cab sits
arm_front = beam.width / 2 + arm_reach
post_x = arm_front - post_length / 2  # the posts' centres, along x
post_y = beam.length / 2 - arm_width / 2  # each side


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate(
        (x0, y0, z0))


result = beam.result
for side in (1, -1):
    y0 = side * beam.length / 2 - (arm_width if side > 0 else 0)
    extrusion = (_box(beam.width / 2 - 1, arm_front, y0, y0 + arm_width,
                      beam.height - arm_depth, beam.height)
                 .union(_box(arm_front - post_length, arm_front, y0, y0 + arm_width,
                             beam.height - arm_depth, post_top)))
    # the curved gusset in the corner between the arm's top and the post
    extrusion = extrusion.edges("|Y").edges(cq.selectors.NearestToPointSelector(
        (arm_front - post_length, side * post_y, beam.height))).fillet(gusset_radius)
    result = result.union(extrusion)
    result = result.cut(cq.Workplane("XY", origin=(post_x, side * post_y, post_top - 10))
                        .circle(screw_hole / 2).extrude(11))

regions = {
    "left_post_top": result.faces(cq.selectors.NearestToPointSelector(
        (post_x + 2, post_y, post_top))),
    "right_post_top": result.faces(cq.selectors.NearestToPointSelector(
        (post_x + 2, -post_y, post_top))),
    "slot": result.faces(cq.selectors.BoxSelector(
        (-beam.slot_to - 0.1, -beam.slot_width, beam.height - beam.plate_thickness - 0.1),
        (-beam.slot_from + 0.1, beam.slot_width, beam.height + 0.1))).faces("not(|Z)"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
