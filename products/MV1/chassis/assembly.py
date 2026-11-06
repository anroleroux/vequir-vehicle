"""MV1 chassis

The longitudinal beam on two lateral beams, one under each end: each end
disc seated on a lateral beam's disc, the lateral beam's pin in its hole.
"""
import cadquery as cq

beam = load_part("beam")
lateral = load_part("lateral_beam")

seat_z = lateral.top  # the lateral beams' disc tops

result = cq.Assembly(name="chassis")
result.add(beam.result, name="beam", color=cq.Color(0.25, 0.40, 0.55),
           loc=cq.Location(cq.Vector(0, 0, seat_z)))
for name, x in (("front_lateral_beam", beam.length / 2), ("rear_lateral_beam", -beam.length / 2)):
    result.add(lateral.result, name=name, color=cq.Color(0.80, 0.45, 0.20),
               loc=cq.Location(cq.Vector(x, 0, 0)))

regions = {}
