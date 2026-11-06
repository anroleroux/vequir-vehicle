"""Sliding beam

A short beam of the MV1 chassis, perpendicular to the longitudinal beam
(lateral, along y), resting on top of the longitudinal beam at its middle,
in the beam's guide, which is open to the top: it slides sideways there.
Half the length of the lateral beams. At each end, a top and a bottom
plate, with two hinge holes side by side through both plates, its outer
corners rounded about the hinges.

Assumptions where the description is silent:
- a solid bar of rectangular section, 10 mm high like the other beams, half
  the lateral beams' length (60 mm);
- 0.2 mm narrower than the guide on each side (10 mm in the 10.4 mm
  channel), sized from it; it rests on the guide's floor (sunk 5 mm into
  the longitudinal beam) along the guide's 40 mm and slides laterally
  (along y) between the cheeks;
- the plates stand out 10 mm past each end of the bar, flush with its top
  and bottom, 3 mm thick, leaving a 4 mm gap between them, open at the end
  and both sides, for the hinged part; they are 20 mm wide (along x), twice
  the bar, to take the two holes side by side;
- the plates start at the bar's ends, outside the 40 mm guide, so the bar
  can still slide 10 mm either way before a plate meets the guide;
- the two hinge axes are vertical (z), through both plates, side by side
  along x (5 mm either side of the centreline), in the plates' middle (5 mm
  from the plate's end): a 3.4 mm hole (an M3 clearance, like the beam's
  disc holes) through each plate;
- the plates' two outer corners at each end are rounded to 5 mm, about the
  hinge axes, so a part swinging on a hinge clears the plate;
- lateral along y (+y is the left), centred on x = 0 and y = 0, standing on
  z = 0 (the assembly lifts it onto the longitudinal beam's top).
"""
import cadquery as cq

beam = load_part("../beam")  # the longitudinal beam whose guide it slides in
lateral = load_part("../lateral_beam")

# parameters, in mm
length = lateral.length / 2  # the bar, lateral, along y: half the lateral beams
guide_clearance = 0.2  # each side, between the guide's cheeks
width = beam.guide_width - 2 * guide_clearance  # longitudinal, along x
height = beam.height  # vertical, along z
plate_thickness = 3.0  # the top and bottom plates at each end
plate_length = 10.0  # along y, past each end of the bar
plate_width = 20.0  # along x, for two hinges side by side
hinge_spacing = 10.0  # between the two hinge axes, along x
hinge_diameter = 3.4  # through both plates
corner_radius = 5.0  # the plates' outer corners, about the hinge axes

plate_y = [length / 2 + plate_length / 2, -(length / 2 + plate_length / 2)]  # left, right
hinge_x = [hinge_spacing / 2, -hinge_spacing / 2]  # front, rear

bar = cq.Workplane("XY").rect(width, length).extrude(height)


def _plate(y, z):
    """One plate centred on y, from z up, its outer corners (away from the bar) rounded."""
    plate = cq.Workplane("XY", origin=(0, y, z)).rect(plate_width, plate_length).extrude(
        plate_thickness)
    return plate.edges("|Z").edges(">Y" if y > 0 else "<Y").fillet(corner_radius)


plates = cq.Workplane("XY")
for y in plate_y:
    for z in (0, height - plate_thickness):
        plates = plates.union(_plate(y, z))
hinges = (
    cq.Workplane("XY")
    .pushPoints([(x, y) for y in plate_y for x in hinge_x])
    .circle(hinge_diameter / 2)
    .extrude(height)
)
result = bar.union(plates).cut(hinges)


def _hinges(y):
    """The hinge holes' faces in the plates at y: the cylinders centred on a
    hinge axis (the rounded corners' faces lie off it)."""
    holes = [f for f in result.faces("%CYLINDER").vals()
             if any(abs(f.Center().x - x) < 1e-6 and abs(f.Center().y - y) < 1e-6
                    for x in hinge_x)]
    return result.newObject(holes)


regions = {
    "bottom": result.faces(cq.selectors.NearestToPointSelector((0, 0, 0))),  # on the guide's floor
    "left_hinges": _hinges(plate_y[0]),
    "right_hinges": _hinges(plate_y[1]),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
