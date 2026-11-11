"""Wheel

A wheel bolted to the wheel hub's flange: a rim and tyre as one solid,
centred on the hub's spigot and held by three screws through the flange.

Assumptions where the description is silent:
- 60 mm across and 20 mm wide, the tyre's edges rounded to 5 mm; its
  bottom sets the vehicle's ground, 30 mm below the hub's axis;
- a 6.2 mm bore for the hub's 6 mm spigot, and three 2.2 mm holes on the
  flange's 13 mm bolt circle for its screws, through the wheel;
- a 30 mm wide, 5 mm deep dish in its outer face, the screws' heads in it;
- modelled with its axis along z, its inner face (against the hub's
  flange) on z = 0.
"""
import cadquery as cq

hub = load_part("../wheel_hub")  # the flange and spigot it fits

# parameters, in mm
diameter = 60.0
width = 20.0
tyre_round = 5.0  # the tyre's edges
bore = hub.spigot_diameter + 0.2
screw_hole = 2.2
dish_diameter = 30.0
dish_depth = 5.0

radius = diameter / 2

result = (
    cq.Workplane("XY").circle(radius).extrude(width)
    .edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(0, directionMax=True))
    .fillet(tyre_round)
)
result = (result
          .cut(cq.Workplane("XY", origin=(0, 0, -1)).circle(bore / 2).extrude(width + 2))
          .cut(cq.Workplane("XY", origin=(0, 0, -1)).polarArray(hub.bolt_circle / 2, 90, 360, 3)
               .circle(screw_hole / 2).extrude(width + 2))
          .cut(cq.Workplane("XY", origin=(0, 0, width - dish_depth)).circle(dish_diameter / 2)
               .extrude(dish_depth + 1)))

regions = {
    "tread": result.faces(cq.selectors.NearestToPointSelector((radius, 0, width / 2))),
    "inner_face": result.faces(cq.selectors.NearestToPointSelector((radius - tyre_round - 2, 0, 0))),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
