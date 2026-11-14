"""Belt drive base link

The fixed upright of the belt drive's four-bar linkage: a plate in the x-z
plane (its thickness along y), a Y seen along y. One hinge at the bottom
middle, on a stem that goes up and widens into an upside-down triangle,
its neck closed up to a flat edge under the top link; its two top ends run
straight up from there, either side of the top hinge (its outer knuckles;
the top link's flat bar is the middle one), and on, diagonally out (+y)
and up, to a joint each for a shock absorber. A
bearing seat for the drive shaft sits in the stem, half way between the
hinges. The linkage swings in the y-z plane.

Assumptions where the description is silent:
- the hinges are 40 mm apart (z), their axes along x, 3 mm in front of the
  back face (the knuckles, 3 mm in radius, flush with the flat back face,
  which mounts on a steering beam's upright), with 2.2 mm holes for 2 mm
  pins, as in the drives;
- the plate is 3 mm thick; the stem is 9.6 mm wide (x), the bottom hinge's
  middle knuckle, between the bottom link's two bars;
- the top ends are 8.4 mm apart (0.2 mm clear of the top link's 8 mm bar
  each side) and 26.4 mm overall, as before the top link was halved: 9 mm
  wide each;
- the stem widens from 7 mm above the shaft; the flat edge between the top
  ends, the closed neck, is 4 mm below the top hinge's axis, clear of the
  top link's knuckle, and the top ends run straight up from that height;
- the drive shaft's bearing seat is a 6 mm bore along y (for a 3 x 6 mm
  bearing or bush) in a 12 mm round boss in the plate, on the stem, 20 mm
  above the bottom hinge;
- each shock joint is a 2.2 mm hole along x in the rounded end (4 mm
  radius) of a 6 mm deep bar, 5 mm wide (x), on the top end's outer side,
  rising from the top hinge's knuckle to 11 mm out from the hinge's axis and 15 mm above it;
- no motor mount yet: the motor and its belt come later;
- it stands on z = 0, centred on x = 0, its back face on y = 0.
"""
import math

import cadquery as cq

# parameters, in mm
thickness = 3.0  # the plate, along y
hinge_spacing = 40.0  # between the bottom and top hinge axes, along z
knuckle_radius = 3.0  # the hinge knuckles, about each axis
knuckle_gap = 0.2  # between knuckles, along x
turn_clearance = 0.3  # radial, around the other link's knuckles
hole_diameter = 2.2  # along each hinge axis, for a 2 mm pin
stem_middle = 5.0  # where the bottom link's bars start, each side of x = 0
bar_half = 4.0  # the top link's flat bar, each side of x = 0
prong_outer = 13.2  # the top ends' outer edges, each side of x = 0
shaft_bore = 6.0  # the drive shaft's bearing seat, along y
shaft_boss = 12.0  # the boss around it, in the plate
split_above_shaft = 7.0  # where the stem starts to widen, above the shaft's axis
prong_below_hinge = 4.0  # the flat edge between the top ends (the closed neck), below the top axis
shock_out = 11.0  # each shock joint, out (+y) from the top hinge's axis
shock_up = 15.0  # and above it
shock_bar = 6.0  # the bar up to it, across
shock_width = 5.0  # the bar and its joint, along x
shock_eye_radius = 4.0  # around the joint's pin

stem_half = stem_middle - knuckle_gap  # the stem and its knuckle, each side of x = 0
prong_inner = bar_half + knuckle_gap  # the top ends, from here to prong_outer
prong_width = prong_outer - prong_inner  # each top end, along x
width = 2 * prong_outer  # overall, along x
axis_y = knuckle_radius  # the hinge axes: the knuckles flush with the back face
axes_z = [knuckle_radius, knuckle_radius + hinge_spacing]  # bottom, top
shaft_z = (axes_z[0] + axes_z[1]) / 2  # the drive shaft, half way between the hinges
split_z = shaft_z + split_above_shaft
prong_z = axes_z[1] - prong_below_hinge
height = axes_z[1] + knuckle_radius  # the plate's top edge
shock_x = prong_outer - shock_width / 2  # the shocks' planes, each side of x = 0
shock_mount_y = axis_y + shock_out
shock_mount_z = axes_z[1] + shock_up


def _along_x(x0, x1, y, z, radius):
    """A cylinder about the line (y, z), along x from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(x1 - x0)


def _along_y(x, z, radius, y0, y1):
    """A cylinder about the line (x, z), along y from y0 to y1."""
    return cq.Workplane("XZ", origin=(0, y1, 0)).center(x, z).circle(radius).extrude(y1 - y0)


def upright(below=0.0):
    """The Y plate with its hinges and the shaft's bearing seat, shared with
    the wheel link: the stem carried on ``below`` under the bottom hinge's
    knuckle (down to z = -below)."""
    outline = [(-stem_half, -below), (stem_half, -below), (stem_half, split_z),
               (prong_outer, prong_z), (prong_outer, height), (prong_inner, height),
               (prong_inner, prong_z), (-prong_inner, prong_z),
               (-prong_inner, height), (-prong_outer, height), (-prong_outer, prong_z),
               (-stem_half, split_z)]
    body = (cq.Workplane("XZ", origin=(0, thickness, 0)).polyline(outline).close()
            .extrude(thickness))  # XZ extrudes along -y: back to y = 0
    body = body.union(_along_y(0, shaft_z, shaft_boss / 2, 0, thickness))
    body = body.union(_along_x(-stem_half, stem_half, axis_y, axes_z[0], knuckle_radius))
    for x0, x1 in ((prong_inner, prong_outer), (-prong_outer, -prong_inner)):
        body = body.union(_along_x(x0, x1, axis_y, axes_z[1], knuckle_radius))
    body = body.cut(_along_y(0, shaft_z, shaft_bore / 2, -1, thickness + 1))
    for z in axes_z:
        body = body.cut(_along_x(-width, width, axis_y, z, hole_diameter / 2))
    return body


result = upright()

# the shock joints: a bar from each top end's knuckle, diagonally out and up
run = math.hypot(shock_out, shock_up)
lean = math.degrees(math.atan2(shock_out, shock_up))  # from +z towards +y
for x0 in (prong_outer - shock_width, -prong_outer):
    bar = (
        cq.Workplane("YZ", origin=(x0, 0, 0))
        .center(0, run / 2).rect(shock_bar, run).extrude(shock_width)
        .union(cq.Workplane("YZ", origin=(x0, 0, 0)).center(0, run)
               .circle(shock_eye_radius).extrude(shock_width))
        .rotate((0, 0, 0), (1, 0, 0), -lean)
        .translate((0, axis_y, axes_z[1]))
    )
    # nothing behind the flat back face
    keep = cq.Workplane("XY").box(shock_width, 2 * run, 2 * run, centered=False).translate(
        (x0, 0, axes_z[1]))
    result = result.union(bar.intersect(keep))
result = result.cut(_along_x(-width, width, shock_mount_y, shock_mount_z, hole_diameter / 2))
result = result.cut(_along_x(-width, width, axis_y, axes_z[1], hole_diameter / 2))

regions = {
    "bottom_hinge": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, axis_y, axes_z[0] + hole_diameter / 2))),
    "top_hinge_left": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (shock_x, axis_y, axes_z[1] + hole_diameter / 2))),
    "top_hinge_right": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (-shock_x, axis_y, axes_z[1] + hole_diameter / 2))),
    "shaft_bearing": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (0, thickness / 2, shaft_z + shaft_bore / 2))),
    "shock_joint_left": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (shock_x, shock_mount_y, shock_mount_z + hole_diameter / 2))),
    "shock_joint_right": result.faces("%CYLINDER").faces(cq.selectors.NearestToPointSelector(
        (-shock_x, shock_mount_y, shock_mount_z + hole_diameter / 2))),
    "back": result.faces(cq.selectors.NearestToPointSelector(
        (0, 0, axes_z[0] + 8))),  # flat: mounts on an upright
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
