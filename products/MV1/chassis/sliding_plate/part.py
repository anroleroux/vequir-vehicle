"""Sliding plate

A flat plate of the MV1 chassis, perpendicular to the longitudinal beam
(lateral, along y), under the middle of the longitudinal beam: it slides
sideways along the beam's bottom. Seen from the top it is a dog biscuit: a
bar half the length of the lateral beams with a wider end at each end, its
outer corners rounded, and two hinge holes side by side through each end.

Assumptions where the description is silent:
- 3 mm thick, the thickness of the sliding beam's plates;
- the bar is 60 mm long (half the lateral beams) and as wide as the
  longitudinal beam (10 mm, along x);
- each end is 20 mm wide (along x) and 10 mm long (along y), past the bar,
  its two outer corners rounded to 5 mm about the hinge axes;
- the two hinge axes are vertical (z), side by side along x (5 mm either
  side of the centreline), in the middle of each end: a 3.4 mm hole (an M3
  clearance, like the beam's disc holes);
- its top slides against the longitudinal beam's bottom; the clip around
  the beam holds it there;
- lateral along y (+y is the left), centred on x = 0 and y = 0, standing on
  z = 0 (the assembly lifts it to the longitudinal beam's bottom).
"""
import cadquery as cq

beam = load_part("../beam")  # the longitudinal beam it slides under
lateral = load_part("../lateral_beam")

# parameters, in mm
thickness = 3.0  # vertical, along z
length = lateral.length / 2  # the bar, lateral, along y: half the lateral beams
width = beam.width  # the bar, longitudinal, along x
end_length = 10.0  # each end, along y, past the bar
end_width = 20.0  # each end, along x, for two hinges side by side
hinge_spacing = 10.0  # between the two hinge axes, along x
hinge_diameter = 3.4
corner_radius = 5.0  # the ends' outer corners, about the hinge axes

end_y = [length / 2 + end_length / 2, -(length / 2 + end_length / 2)]  # left, right
hinge_x = [hinge_spacing / 2, -hinge_spacing / 2]  # front, rear


def _end(y):
    """One wide end centred on y, its outer corners (away from the bar) rounded."""
    end = cq.Workplane("XY", origin=(0, y, 0)).rect(end_width, end_length).extrude(thickness)
    return end.edges("|Z").edges(">Y" if y > 0 else "<Y").fillet(corner_radius)


bar = cq.Workplane("XY").rect(width, length).extrude(thickness)
for y in end_y:
    bar = bar.union(_end(y))
hinges = (
    cq.Workplane("XY")
    .pushPoints([(x, y) for y in end_y for x in hinge_x])
    .circle(hinge_diameter / 2)
    .extrude(thickness)
)
result = bar.cut(hinges)


def _hinges(y):
    """The hinge holes' faces in the end at y: the cylinders centred on a
    hinge axis (the rounded corners' faces lie off it)."""
    holes = [f for f in result.faces("%CYLINDER").vals()
             if any(abs(f.Center().x - x) < 1e-6 and abs(f.Center().y - y) < 1e-6
                    for x in hinge_x)]
    return result.newObject(holes)


regions = {
    "top": result.faces(">Z"),  # slides along the longitudinal beam's bottom
    "bottom": result.faces("<Z"),
    "left_hinges": _hinges(end_y[0]),
    "right_hinges": _hinges(end_y[1]),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
