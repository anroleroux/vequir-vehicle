"""MV1 chassis

The main beam (a flat plate) on two lateral steering beams, one under each
end: each round end seated on a steering beam's disc, the steering beam's
pin in its hole, so the steering beam turns about it. Each steering beam's
T leg points inwards, under the main beam. The front steering beam
carries the cab's posts, forward of its ends.

Two SG90 steering servos stand upside down on the main beam, between its
gussets, symmetrical front and back, their output shafts down through the
plate; each one's horn points in towards the middle, away from its pivot,
and carries a pin down into the slider in that steering beam's slot, so
turning the horn turns the steering beam. Shown with the horns along the slots (steer = 0); front_steer
and rear_steer turn the horns, positive anticlockwise seen from above.
"""
import math

import cadquery as cq

beam = load_part("beam")
lateral = load_part("steering_beam")
front_beam = load_part("front_steering_beam")  # with the cab's posts
slider = load_part("slider")
pin = load_part("steering_pin")
servo = load_library("actuators/sg90")
horn = load_library("actuators/sg90_horn")

front_steer = 0.0  # degrees, the front servo's horn about its shaft
rear_steer = 0.0  # degrees, the rear servo's horn about its shaft

seat_z = lateral.top  # the lateral beams' disc tops: the main beam's bottom
plate_top = seat_z + beam.thickness
housing_bottom = plate_top + servo.case_height - servo.housing_top  # where the horns sit
slot_bottom = lateral.height - lateral.plate_thickness

result = cq.Assembly(name="chassis")
result.add(beam.result, name="beam", color=cq.Color(0.25, 0.40, 0.55),
           loc=cq.Location(cq.Vector(0, 0, seat_z)))

for end, name, steer in ((1, "front", front_steer), (-1, "rear", rear_steer)):
    pivot_x = end * beam.length / 2
    shaft_x = end * beam.servo_x
    # the horn points in, towards the middle; its pin, and the steering beam
    # turned so its slot runs through it, the slider at the pin
    arm = (180.0 if end > 0 else 0.0) + steer  # the horn's direction, about z
    pin_x = shaft_x + horn.arm_length * math.cos(math.radians(arm))
    pin_y = horn.arm_length * math.sin(math.radians(arm))
    # the leg runs along the steering beam's -x: towards -x at the front,
    # turned a half turn at the rear
    lean = math.degrees(math.atan2(end * -pin_y, end * (pivot_x - pin_x)))
    facing = lean if end > 0 else 180.0 + lean
    part = front_beam if end > 0 else lateral
    result.add(part.result, name=f"{name}_steering_beam", color=cq.Color(0.80, 0.45, 0.20),
               loc=cq.Location(cq.Vector(pivot_x, 0, 0), cq.Vector(0, 0, 1), facing))
    # the servo, upside down: its case's top on the plate's top, the shaft
    # down, the case reaching in towards the middle
    result.add(servo.result, name=f"{name}_servo", color=cq.Color(0.15, 0.35, 0.80),
               loc=cq.Location(cq.Vector(shaft_x, 0, plate_top + servo.case_height),
                               cq.Vector(0, 0, 1), 0.0 if end > 0 else 180.0)
               * cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180))
    # the horn on the shaft, its servo face against the gear housing
    result.add(horn.result, name=f"{name}_horn", color=cq.Color(0.95, 0.95, 0.95),
               loc=cq.Location(cq.Vector(shaft_x, 0, housing_bottom), cq.Vector(0, 0, 1), arm)
               * cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180))
    # the slider in the slot, the pin from the horn's top face down into it
    result.add(slider.result, name=f"{name}_slider", color=cq.Color(0.30, 0.30, 0.30),
               loc=cq.Location(cq.Vector(pin_x, pin_y, slot_bottom), cq.Vector(0, 0, 1), lean))
    result.add(pin.result, name=f"{name}_steering_pin", color=cq.Color(0.70, 0.70, 0.72),
               loc=cq.Location(cq.Vector(pin_x, pin_y, slot_bottom + 0.2)))

regions = {}
