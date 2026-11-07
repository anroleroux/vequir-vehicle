"""MV1

The chassis with a four-bar linkage mounted on each upright of its two
steering beams: four linkages, each fixed plate's flat back face on an
upright's end face, the linkage reaching outwards (along y, away from the
centreline), moving in y-z.
"""
import cadquery as cq

chassis = load_part("chassis")
linkage = load_part("linkage")
beam = load_part("chassis/beam")
steering = load_part("chassis/lateral_beam")

end_x = beam.length / 2  # each steering beam, front and rear
end_y = steering.length / 2  # its uprights' end faces, left and right

result = cq.Assembly(name="MV1")
result.add(chassis.result, name="chassis")
for axle, x in (("front", end_x), ("rear", -end_x)):
    # the linkage reaches along its +y: as is on the left, a half turn about z on the right
    result.add(linkage.result, name=f"{axle}_left_linkage",
               loc=cq.Location(cq.Vector(x, end_y, 0)))
    result.add(linkage.result, name=f"{axle}_right_linkage",
               loc=cq.Location(cq.Vector(x, -end_y, 0), cq.Vector(0, 0, 1), 180))

regions = {}
