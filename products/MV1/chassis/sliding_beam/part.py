"""Sliding beam

A short beam of the MV1 chassis, perpendicular to the longitudinal beam
(lateral, along y), sitting against the longitudinal beam's underside at
its middle. Half the length of the lateral beams. A dovetail tongue along
its top runs in the longitudinal beam's slot, holding it up against the beam
and letting it slide only sideways.

Assumptions where the description is silent:
- a solid bar of rectangular section, the same 10 x 10 mm section as the
  other beams, half the lateral beams' length (60 mm);
- the tongue runs the sliding beam's whole length, so it can slide its full
  travel; it is 0.2 mm smaller than the slot on each flank and 0.2 mm short
  of the slot's top (6 mm at its root, 8 mm at its top, 4 mm high), sized
  from the longitudinal beam's slot;
- it slides laterally (along y), its shoulders against the longitudinal
  beam's underside;
- lateral along y (+y is the left), centred on x = 0 and y = 0, standing on
  z = 0 (the assembly lifts it to the longitudinal beam's underside).
"""
import cadquery as cq

beam = load_part("../beam")  # the longitudinal beam it slides under
lateral = load_part("../lateral_beam")

# parameters, in mm
length = lateral.length / 2  # lateral, along y: half the lateral beams
width = beam.width  # longitudinal, along x
height = beam.height  # vertical, along z, to the shoulders
slot_clearance = 0.2  # each flank of the tongue, and its top, in the slot
tongue_root = beam.slot_mouth - 2 * slot_clearance  # at the shoulders
tongue_top = beam.slot_top - 2 * slot_clearance
tongue_height = beam.slot_depth - slot_clearance

bar = cq.Workplane("XY").rect(width, length).extrude(height)
tongue = (
    cq.Workplane("XZ", origin=(0, 0, height))  # the dovetail's profile, run along y
    .polyline([(-tongue_root / 2, 0), (tongue_root / 2, 0),
               (tongue_top / 2, tongue_height), (-tongue_top / 2, tongue_height)])
    .close()
    .extrude(length / 2, both=True)
)
result = bar.union(tongue)

regions = {
    "tongue_top": result.faces(">Z"),
    "shoulders": result.faces(cq.selectors.NearestToPointSelector((width / 2 - 0.5, 0, height))),
    "left_end": result.faces(">Y"),
    "right_end": result.faces("<Y"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
