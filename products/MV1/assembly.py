"""MV1

The chassis with a drive mounted on each upright of its steering beams:
four drives, each fixed plate's flat back face on an upright's end face,
the drive reaching outwards (along y, away from the centreline), moving in
y-z; each base link's bottom on its upright's bottom, 29 mm up (its bottom
hinge 32 mm up).

The cab rests on the front drives' base links' tops and the front steering
beam's posts, turning with the front steering about the front pivot; the
rear bed stands on the base plate, fixed. cab_turn turns the cab about the
front pivot, as the front steering does (the drives and the steering beam
are shown straight ahead).
"""
import cadquery as cq

chassis = load_part("chassis")
drive = load_part("drives")
cab = load_part("cab")
bed = load_part("bed")
beam = load_part("chassis/beam")
steering = load_part("chassis/steering_beam")
plate = load_part("drives/plate")

cab_turn = 0.0  # degrees, the cab about the front pivot, anticlockwise from above

end_x = beam.length / 2  # each steering beam, front and rear
end_y = steering.length / 2  # its uprights' end faces, left and right

result = cq.Assembly(name="MV1")
result.add(chassis.result, name="chassis")
for axle, x in (("front", end_x), ("rear", -end_x)):
    # the drive reaches along its +y: as is on the left, a half turn about z on the right
    result.add(drive.result, name=f"{axle}_left_drive",
               loc=cq.Location(cq.Vector(x, end_y, steering.upright_bottom)))
    result.add(drive.result, name=f"{axle}_right_drive",
               loc=cq.Location(cq.Vector(x, -end_y, steering.upright_bottom),
                               cq.Vector(0, 0, 1), 180))
# the cab on the front base links' tops, over the front pivot
result.add(cab.result, name="cab",
           loc=cq.Location(cq.Vector(end_x, 0, steering.upright_bottom + plate.tower_top),
                           cq.Vector(0, 0, 1), cab_turn))
# the bed on the base plate's top
result.add(bed.result, name="bed",
           loc=cq.Location(cq.Vector(0, 0, steering.top + beam.thickness)))

regions = {}
