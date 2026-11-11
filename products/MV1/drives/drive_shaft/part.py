"""Drive shaft

The shaft between the drive motor's coupler and the wheel hub's coupler,
sliding in its two yokes as the suspension moves the hub.

Assumptions where the description is silent:
- 3 mm across, as long as the distance between the two couplers' joints
  with the arms level, less 7 mm at each end: its ends sit 7 mm from each
  joint, mid-way along the yokes' bores, free to slide 3 mm in and 7 mm
  out at each end;
- modelled standing up, along z from z = 0.
"""
import cadquery as cq

plate = load_part("../plate")  # the motor's place
arm = load_part("../arm")
wheel = load_part("../wheel_link")  # the hub's joint
motor = load_library("actuators/motor_130")
motor_yoke = load_part("../motor_yoke")

# parameters, in mm
diameter = 3.0
end_inset = 7.0  # each end, from its joint

# the couplers' joints with the arms level, in the linkage's frame: by the
# motor (along its shaft), and by the hub (on its axis)
motor_joint = plate.motor_face + plate.motor_axis * (motor.shaft_length + motor_yoke.bore_start + 0.2)
far_y = plate.axis_y + arm.length  # the wheel link's hinge axes
hub_joint = cq.Vector(0, far_y + wheel.axis_y - wheel.drive_joint_y,
                      wheel.hub_z - (wheel.axes_z[0] - plate.axes_z[0]))
length = (hub_joint - motor_joint).Length - 2 * end_inset

result = cq.Workplane("XY").circle(diameter / 2).extrude(length)

regions = {
    "shank": result.faces("%CYLINDER"),
}

if "show_object" in globals():  # CQ-editor
    show_object(result, name="part")
