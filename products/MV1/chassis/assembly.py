"""MV1 chassis

The main beam (a flat plate) on two lateral steering beams, one under each
end:
each end disc seated on a steering beam's disc, the steering beam's pin in
its hole, so the steering beam turns about it. Each steering beam's T leg
points inwards, under the main beam.
"""
import cadquery as cq

beam = load_part("beam")
lateral = load_part("lateral_beam")

seat_z = lateral.top  # the lateral beams' disc tops

result = cq.Assembly(name="chassis")
result.add(beam.result, name="beam", color=cq.Color(0.25, 0.40, 0.55),
           loc=cq.Location(cq.Vector(0, 0, seat_z)))
# the leg runs along the part's -x: as is at the front, a half turn about z at the rear
result.add(lateral.result, name="front_lateral_beam", color=cq.Color(0.80, 0.45, 0.20),
           loc=cq.Location(cq.Vector(beam.length / 2, 0, 0)))
result.add(lateral.result, name="rear_lateral_beam", color=cq.Color(0.80, 0.45, 0.20),
           loc=cq.Location(cq.Vector(-beam.length / 2, 0, 0), cq.Vector(0, 0, 1), 180))

regions = {}
