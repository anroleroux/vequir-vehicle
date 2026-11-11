"""MV1 chassis

The main beam (a flat plate) on two lateral steering beams, one under each
end: each round end seated on a steering beam's disc, the steering beam's
pin in its hole, so the steering beam turns about it. Each steering beam's
T leg points inwards, under the main beam.

The SG90 steering servo stands upside down on the main beam, between its
gussets, its output shaft down through the plate; the horn on the shaft
carries a pin down into the slider in the front steering beam's slot, so
turning the horn turns the front steering beam. Shown with the horn along
the slot (steer = 0); steer turns the horn, positive anticlockwise seen
from above.
"""
import math

import cadquery as cq

beam = load_part("beam")
lateral = load_part("lateral_beam")
slider = load_part("slider")
pin = load_part("steering_pin")
servo = load_library("actuators/sg90")
horn = load_library("actuators/sg90_horn")

steer = 0.0  # degrees, the servo's horn about its shaft

seat_z = lateral.top  # the lateral beams' disc tops: the main beam's bottom
plate_top = seat_z + beam.thickness
pivot_x = beam.length / 2  # the front steering beam's pivot

# the horn's pin, and the front steering beam turned so its slot runs
# through it, the slider at the pin
turn = math.radians(steer)
pin_x = beam.servo_x + horn.arm_length * math.cos(turn)
pin_y = horn.arm_length * math.sin(turn)
lean = math.degrees(math.atan2(-pin_y, pivot_x - pin_x))  # the front steering beam

result = cq.Assembly(name="chassis")
result.add(beam.result, name="beam", color=cq.Color(0.25, 0.40, 0.55),
           loc=cq.Location(cq.Vector(0, 0, seat_z)))
# the leg runs along the part's -x: turned by the servo at the front, a half
# turn about z at the rear
result.add(lateral.result, name="front_lateral_beam", color=cq.Color(0.80, 0.45, 0.20),
           loc=cq.Location(cq.Vector(pivot_x, 0, 0), cq.Vector(0, 0, 1), lean))
result.add(lateral.result, name="rear_lateral_beam", color=cq.Color(0.80, 0.45, 0.20),
           loc=cq.Location(cq.Vector(-pivot_x, 0, 0), cq.Vector(0, 0, 1), 180))

# the servo, upside down: its case's top on the plate's top, the shaft down
servo_flip = cq.Location(cq.Vector(beam.servo_x, 0, plate_top + servo.case_height),
                         cq.Vector(1, 0, 0), 180)
result.add(servo.result, name="servo", color=cq.Color(0.15, 0.35, 0.80), loc=servo_flip)
# the horn on the shaft, its servo face against the gear housing, turned by steer
housing_bottom = plate_top + servo.case_height - servo.housing_top
result.add(horn.result, name="horn", color=cq.Color(0.95, 0.95, 0.95),
           loc=cq.Location(cq.Vector(beam.servo_x, 0, housing_bottom), cq.Vector(0, 0, 1), steer)
           * cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180))
# the slider in the slot, the pin from the horn's top face down into it
slot_bottom = lateral.height - lateral.plate_thickness
result.add(slider.result, name="slider", color=cq.Color(0.30, 0.30, 0.30),
           loc=cq.Location(cq.Vector(pin_x, pin_y, slot_bottom), cq.Vector(0, 0, 1), lean))
pin_bottom = slot_bottom + 0.2
result.add(pin.result, name="steering_pin", color=cq.Color(0.70, 0.70, 0.72),
           loc=cq.Location(cq.Vector(pin_x, pin_y, pin_bottom)))

regions = {}
