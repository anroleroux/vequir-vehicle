"""The model vehicles: each part checked against its description, in the
vehicle's axes (x longitudinal, +x front; y lateral, +y left; z up).

The CAD tool comes from vequir-standard, which ``libraries.txt`` expects
beside this repository (CI clones it there).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from cad.catalog import discover_all
from cad.part import build_part

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "products"


def _summary(result):
    assert result.ok, result.error
    return json.loads(result.files["summary"].read_text())


def test_the_catalogue_holds_the_mv1_chassis():
    assert sorted(e.designation for e in discover_all(PRODUCTS)) == [
        "MV1", "MV1/bed", "MV1/bed/leg", "MV1/bed/tray", "MV1/belt_drives",
        "MV1/belt_drives/base_link", "MV1/belt_drives/bottom_link",
        "MV1/belt_drives/top_link", "MV1/belt_drives/wheel_link", "MV1/cab", "MV1/cab/body",
        "MV1/chassis", "MV1/chassis/beam", "MV1/chassis/front_steering_beam",
        "MV1/chassis/slider", "MV1/chassis/steering_beam", "MV1/chassis/steering_pin",
        "MV1/drives", "MV1/drives/arm", "MV1/drives/drive_shaft", "MV1/drives/hub_yoke",
        "MV1/drives/motor_yoke", "MV1/drives/pin", "MV1/drives/plate",
        "MV1/drives/shaft_yoke", "MV1/drives/shock_body", "MV1/drives/shock_pin",
        "MV1/drives/shock_rod", "MV1/drives/wheel", "MV1/drives/wheel_hub",
        "MV1/drives/wheel_link", "MV1/drives/wheel_pin"]


def test_the_main_beam_is_a_flat_plate_flaring_out_in_the_middle(tmp_path):
    """A horizontal 3 mm plate along x, centred on the centreline, standing
    on z = 0: 20 mm round ends with a 3.4 mm hole at the steering rotation
    points (x = +-100), tapering out sharply to a straight section 100 mm
    wide and 80 mm long in the middle."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/beam/part.py", tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([220.0, 100.0, 9.0], abs=1e-3)  # 3 mm plate, 6 mm on top
    assert box["size"][0] == max(box["size"])  # longitudinal
    assert box["size"][2] == min(box["size"])  # flat, horizontal
    assert summary["regions"]["front_servo_hole"]["count"] == 1
    assert summary["regions"]["rear_servo_hole"]["count"] == 1
    assert box["min"][0] == pytest.approx(-110.0)
    assert box["min"][2] == pytest.approx(0.0)
    assert summary["n_solids"] == 1
    assert summary["regions"]["front_hole"]["count"] == 1
    assert summary["regions"]["rear_hole"]["count"] == 1
    assert summary["regions"]["bottom"]["count"] == 1  # one flat seat


def test_the_steering_beam_is_built_from_plates_with_curved_gussets(tmp_path):
    """60 mm along y, 10 mm wide, its top 50 mm up, its uprights reaching
    down to 15 mm: a 2 mm top plate turning down into 2 mm end plates,
    1.5 mm gussets along both side edges; a 60 mm T leg along -x; a disc and
    a 3 mm pin on top."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/steering_beam/part.py",
                                  tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([75.0, 60.0, 31.0])  # leg to disc; 29 to 50, 7 disc, 3 pin
    assert box["min"] == pytest.approx([-65.0, -30.0, 29.0])
    assert summary["n_solids"] == 1
    for region in ("seat", "pin", "leg_end", "left_end", "right_end"):
        assert summary["regions"][region]["count"] == 1
    assert summary["regions"]["slot"]["count"] == 4  # the slider's slot along the leg
    # far lighter than a solid 10 x 10 mm bar of the same outline: it is plates
    solid = 10 * 60 * 10 + 2 * 10 * 10 * 11 + 60 * 10 * 10
    assert summary["volume_mm3"] < 0.75 * solid
    # the gussets' curves: cylinder faces besides the disc's rim and the pin
    assert summary["face_types"]["CYLINDER"] > 2


def test_the_chassis_seats_the_beam_on_the_steering_beams_legs_inwards(tmp_path):
    """Each end disc seated on a steering beam's disc (the disc less the hole
    in contact), the pin in the hole with clearance; both T legs pointing
    inwards under the main beam, clear of it; a servo upside down on the
    main beam at each end, its horn under it pointing in, the slider in that
    leg's slot. No interference."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/assembly.py", tmp_path / "out"))
    assert summary["interference"] == []
    contacts = {(c["a"], c["b"]): c["area_mm2"] for c in summary["contacts"]}
    seat = math.pi * (10.0 ** 2 - 1.7 ** 2)
    assert contacts[("chassis/beam", "chassis/front_steering_beam")] == pytest.approx(seat, rel=1e-3)
    assert contacts[("chassis/beam", "chassis/rear_steering_beam")] == pytest.approx(seat, rel=1e-3)
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    for end in ("front", "rear"):
        for pair in (("beam", f"{end}_servo"), (f"{end}_servo", f"{end}_horn"),
                     (f"{end}_steering_beam", f"{end}_slider")):
            assert contacts[tuple(f"chassis/{p}" for p in pair)] > 0  # resting on each other
        servo, horn = parts[f"{end}_servo"], parts[f"{end}_horn"]
        assert servo["bounding_box_max"][2] == pytest.approx(60.0 + 22.7)  # upside down on the plate
        assert horn["bounding_box_min"][2] == pytest.approx(52.0)  # 1 mm over the slider's flange
    beam, front, rear = parts["beam"], parts["front_steering_beam"], parts["rear_steering_beam"]
    assert beam["bounding_box_min"][2] == pytest.approx(57.0)  # 50 to the beam's top, 7 disc
    # the legs reach in past the servos' shafts, to the horns' pins
    # the front one reaching forward to its cab posts, 30 mm ahead of its pivot
    assert [front["bounding_box_min"][0], front["bounding_box_max"][0]] == pytest.approx([35.0, 130.0])
    assert [rear["bounding_box_min"][0], rear["bounding_box_max"][0]] == pytest.approx([-110.0, -35.0])
    assert front["bounding_box_min"][2] == pytest.approx(29.0)  # the uprights' bottoms
    # symmetrical front and back
    for name in ("servo", "horn", "slider", "steering_pin"):
        f, r = parts[f"front_{name}"], parts[f"rear_{name}"]
        assert f["bounding_box_min"][0] == pytest.approx(-r["bounding_box_max"][0], abs=1e-3)


def test_the_linkage_plate_stands_in_x_z_with_a_hinge_top_and_bottom(tmp_path):
    """An I link: a straight 9.6 x 50 mm strip, 3 mm thick along y, only as
    wide as the middle knuckle about an x axis at its top and bottom, with a
    2.2 mm hole through it, flush with the flat back face (y = 0) it mounts
    by; carried on up to 74 mm and out over the top arm in a 6 mm bar, a tab
    hanging from its end for the shock's upper joint."""
    summary = _summary(build_part(PRODUCTS / "MV1/drives/plate/part.py", tmp_path / "out"))
    box = summary["bounding_box"]
    # the bar 38 mm out, the tower 74 mm up; the motor's bracket, 22 mm wide,
    # tilted down below the bottom hinge, reaching behind the back face
    assert box["size"] == pytest.approx([22.0, 39.458, 85.074], abs=1e-3)
    assert summary["regions"]["back"]["count"] == 1  # one flat face, in the x-z plane
    assert box["max"][1] == pytest.approx(38.0) and box["max"][2] == pytest.approx(62.0)
    assert summary["regions"]["motor_bracket"]["count"] == 1
    knuckles = 2 * (math.pi * 3.0 ** 2 / 2 - math.pi * 1.1 ** 2) * 9.6  # the half proud, less the hole
    tower = 9.6 * 3.0 * 24.0
    bar = 9.6 * 35.0 * 6.0
    tab = (8.0 * 5.0 + math.pi * 4.0 ** 2 / 2 - math.pi * 1.1 ** 2) * 3.0
    strip = 9.6 * 3.0 * 38.0 + knuckles + tower + bar + tab
    hanger = 9.6 * 6.0 * 3.5
    bracket = 22.0 * 22.0 * 2.0 - math.pi * (3.3 ** 2 + 2 * 1.1 ** 2) * 2.0
    # the bracket's plate overlaps the hanger a little where they join
    assert strip + hanger + bracket - 80.0 < summary["volume_mm3"] < strip + hanger + bracket
    assert summary["regions"]["shock_joint"]["count"] == 1
    assert summary["n_solids"] == 1
    assert summary["regions"]["bottom_hinge"]["count"] == 1
    assert summary["regions"]["top_hinge"]["count"] == 1


def _linkage(tmp_path, swing):
    """The drive assembly, built with its arms swung ``swing`` degrees."""
    import shutil
    root = tmp_path / f"swing_{swing}"
    shutil.copytree(PRODUCTS / "MV1/drives", root / "drives")
    script = root / "drives/assembly.py"
    script.write_text(script.read_text().replace("swing = 0.0", f"swing = {swing}"))
    (root / "libraries.txt").write_text(  # the motor, from vequir-standard
        f"{(ROOT.parent / 'vequir-standard/library').resolve()}\n")
    return _summary(build_part(script, root / "out"))


@pytest.mark.parametrize("swing", [0.0, 10.0, -10.0])
def test_the_four_bar_linkage_moves_in_y_z_without_collisions(tmp_path, swing):
    """Fixed plate, two equal arms, wheel link, four pins and the shock
    absorber: no interference level or swung 10 degrees either way (the
    shock's travel), the wheel link kept upright and moved only in y-z, the
    pins on the arms' far hinges, the shock's ends on its joints."""
    summary = _linkage(tmp_path, swing)
    assert summary["interference"] == []
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    assert set(parts) == {"fixed_plate", "wheel_link", "bottom_arm", "top_arm",
                          "fixed_bottom_pin", "fixed_top_pin", "wheel_bottom_pin",
                          "wheel_top_pin", "shock_body", "shock_rod", "upper_shock_pin",
                          "lower_shock_pin", "motor", "motor_yoke", "motor_shaft_yoke",
                          "drive_shaft", "hub_shaft_yoke", "hub_yoke", "wheel_hub", "wheel"}
    fixed, moving = parts["fixed_plate"], parts["wheel_link"]
    turn = math.radians(swing)
    rise = 55.0 * math.sin(turn)  # the arms' 55 mm
    run = 55.0 * math.cos(turn)
    # upright, moved only in y-z: centred on x = 0, 3 mm thick plus its knuckles
    assert [moving["bounding_box_min"][0], moving["bounding_box_max"][0]] == pytest.approx(
        [-9.8, 9.8], abs=1e-3)
    assert moving["bounding_box_max"][1] - moving["bounding_box_min"][1] == pytest.approx(
        21.0, abs=1e-3)  # with the shock tab and the hub's boss
    # the summary rounds to 4 decimals; the wheel link reaches 40 mm lower
    assert moving["bounding_box_min"][2] == pytest.approx(-22.0 + rise, abs=1e-3)
    # the hub on its axis through the wheel link, 32 mm below the bottom hinge
    hub = parts["wheel_hub"]
    centre = [(hub["bounding_box_min"][i] + hub["bounding_box_max"][i]) / 2 for i in (0, 2)]
    assert centre == pytest.approx([0.0, -14.0 + rise], abs=1e-3)
    assert hub["bounding_box_min"][1] == pytest.approx(3.0 + run + 3.0 - 14.0 + 4.2, abs=1e-3)
    assert moving["bounding_box_max"][2] == pytest.approx(38.0 + rise, abs=1e-3)  # its top hinge's
    pin = parts["wheel_bottom_pin"]
    centre = [(pin["bounding_box_min"][i] + pin["bounding_box_max"][i]) / 2 for i in (1, 2)]
    assert centre == pytest.approx([3.0 + run, 3.0 + rise], abs=1e-3)
    # the shock's ends: the fixed plate's joint over the top arm (34 mm out,
    # 62 mm up), the wheel link's tab (10 mm in from the wheel hinge axis,
    # 18 mm below the arm)
    for name, at in (("upper_shock_pin", [34.0, 51.0]),
                     ("lower_shock_pin", [3.0 + run - 10.0, 3.0 + rise])):
        pin = parts[name]
        centre = [(pin["bounding_box_min"][i] + pin["bounding_box_max"][i]) / 2 for i in (1, 2)]
        assert centre == pytest.approx(at, abs=1e-3)


def test_mv1_mounts_a_drive_on_each_upright_and_the_cab_and_bed(tmp_path):
    """Four drives, each fixed plate's back face flat on an upright's end face
    (9.6 x 25 mm), reaching outwards along y to their wheels; the cab on the
    front drives' base links' tops and the front steering beam's posts; the
    bed's legs on the base plate. No interference."""
    summary = _summary(build_part(PRODUCTS / "MV1/assembly.py", tmp_path / "out"))
    assert summary["interference"] == []
    names = [c["name"] for c in summary["components"]]
    assert names == ["MV1/chassis", "MV1/front_left_drive", "MV1/front_right_drive",
                     "MV1/rear_left_drive", "MV1/rear_right_drive", "MV1/cab", "MV1/bed"]
    contacts = {(c["a"], c["b"]): c["area_mm2"] for c in summary["contacts"]}
    for name in names[1:5]:
        assert contacts[("MV1/chassis", name)] == pytest.approx(9.6 * 21.0)  # the uprights' 21 mm
    # the cab on the two posts (6 x 6 mm less the screw holes) and the bars' tops
    posts = 2 * (6.0 * 6.0 - math.pi * 1.1 ** 2)
    assert contacts[("MV1/chassis", "MV1/cab")] == pytest.approx(posts, rel=1e-3)
    for side in ("left", "right"):
        assert contacts[(f"MV1/front_{side}_drive", "MV1/cab")] == pytest.approx(9.6 * 38.0)
    assert contacts[("MV1/chassis", "MV1/bed")] == pytest.approx(4 * 6.0 * 6.0)  # its legs' feet
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    for name, x, side in (("front_left_drive", 100.0, 1), ("front_right_drive", 100.0, -1),
                          ("rear_left_drive", -100.0, 1), ("rear_right_drive", -100.0, -1)):
        box_min, box_max = parts[name]["bounding_box_min"], parts[name]["bounding_box_max"]
        assert [box_min[0], box_max[0]] == pytest.approx([x - 30.0, x + 30.0])  # the 60 mm wheel
        # the motors reach in under the steering beam, 3 mm short of the centreline
        inner = box_min[1] if side > 0 else box_max[1]
        assert inner == pytest.approx(side * 3.7, abs=0.1)
        outer = box_max[1] if side > 0 else box_min[1]
        assert outer == pytest.approx(side * 118.5, abs=0.1)  # the wheel's outer face
        # the wheel's bottom (the ground); the base links' tops: raised 25 mm
        assert [box_min[2], box_max[2]] == pytest.approx([-15.0, 91.0])
    cab, bed = parts["cab"], parts["bed"]
    assert cab["bounding_box_min"][2] == pytest.approx(91.0)  # on the base links' tops
    assert bed["bounding_box_max"][2] == pytest.approx(93.0 + 22.0)  # 2 mm over the rear drives


def _mv1(tmp_path, cab_turn):
    """MV1, built with the cab turned ``cab_turn`` degrees about the front pivot."""
    import shutil
    root = tmp_path / f"cab_{cab_turn}"
    shutil.copytree(PRODUCTS, root / "products")
    script = root / "products/MV1/assembly.py"
    script.write_text(script.read_text().replace("cab_turn = 0.0", f"cab_turn = {cab_turn}"))
    (root / "libraries.txt").write_text(
        f"{(ROOT.parent / 'vequir-standard/library').resolve()}\n")
    return _summary(build_part(script, root / "out"))


@pytest.mark.parametrize("turn, hits", [(17.3, False), (-17.3, False), (25.0, True)])
def test_the_cab_turns_clear_of_the_fixed_bed(tmp_path, turn, hits):
    """The cab turns with the front steering, at most about 17.3 degrees (the
    servo's horn at 90 degrees): its back clears the bed's front by 5 mm
    there; turned further, it would hit."""
    summary = _mv1(tmp_path, turn)
    pairs = {(c["a"].split("/")[-1], c["b"].split("/")[-1]) for c in summary["interference"]}
    assert (("cab", "bed") in pairs) is hits
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    if not hits:
        gap = parts["cab"]["bounding_box_min"][0] - parts["bed"]["bounding_box_max"][0]
        assert gap == pytest.approx(5.0, abs=0.1)


def test_the_front_steering_beam_carries_the_cabs_posts(tmp_path):
    """The steering beam with two posts forward of its ends, opposite its
    leg, up to the drives' base links' tops (91 mm)."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/front_steering_beam/part.py",
                                  tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["min"] == pytest.approx([-65.0, -30.0, 29.0])
    assert box["max"] == pytest.approx([30.0, 30.0, 91.0])
    assert summary["n_solids"] == 1
    assert summary["regions"]["left_post_top"]["count"] == 1
    assert summary["regions"]["right_post_top"]["count"] == 1


def test_the_arm_is_an_h_wider_at_the_wheel_and_the_wheel_link_reaches_down(tmp_path):
    """The arm: 55 mm between hinges, 30 mm wide at the chassis hinge, 40 mm
    at the wheel hinge, a 35 mm deep slot at the wheel end, trimmed 3 mm into
    the legs; the wheel link: a 19.6 mm strip for the
    wheel end's wider gap, 30 mm longer at the bottom; the wheel pins 40 mm."""
    arm = _summary(build_part(PRODUCTS / "MV1/drives/arm/part.py", tmp_path / "arm"))
    assert arm["bounding_box"]["size"] == pytest.approx([40.0, 61.0, 6.0])
    assert arm["n_solids"] == 1
    wheel = _summary(build_part(PRODUCTS / "MV1/drives/wheel_link/part.py", tmp_path / "wheel"))
    # with its shock tab and the hub's boss
    assert wheel["bounding_box"]["size"] == pytest.approx([19.6, 21.0, 60.0])
    assert wheel["regions"]["hub_bore"]["count"] == 1
    assert wheel["regions"]["wheel_end"]["count"] == 1
    assert wheel["regions"]["shock_tab"]["count"] == 1
    pin = _summary(build_part(PRODUCTS / "MV1/drives/wheel_pin/part.py", tmp_path / "pin"))
    assert pin["bounding_box"]["size"] == pytest.approx([2.0, 2.0, 40.0])


@pytest.mark.parametrize("swing, collides", [(10.0, False), (12.0, True)])
def test_the_shock_travels_10_degrees_and_bottoms_out_beyond(tmp_path, swing, collides):
    """Its rod slides in the body between 40.6 and 59 mm between the joints;
    past +10 degrees the rod's end runs into the body's floor."""
    summary = _linkage(tmp_path, swing)
    pairs = {(c["a"].split("/")[-1], c["b"].split("/")[-1]) for c in summary["interference"]}
    if collides:
        assert ("shock_body", "shock_rod") in pairs
    else:
        assert pairs == set()


def _chassis(tmp_path, front, rear):
    """The chassis assembly, built with the servos' horns turned ``front`` and
    ``rear`` degrees."""
    import shutil
    root = tmp_path / f"steer_{front}_{rear}"
    shutil.copytree(PRODUCTS, root / "products")
    script = root / "products/MV1/chassis/assembly.py"
    script.write_text(script.read_text()
                      .replace("front_steer = 0.0", f"front_steer = {front}")
                      .replace("rear_steer = 0.0", f"rear_steer = {rear}"))
    (root / "libraries.txt").write_text(
        f"{(ROOT.parent / 'vequir-standard/library').resolve()}\n")
    return _summary(build_part(script, root / "out"))


@pytest.mark.parametrize("steer, lean", [(0.0, 0.0), (45.0, -10.2), (-45.0, 10.2),
                                         (90.0, -17.3), (-90.0, 17.3)])
def test_the_servos_steer_the_beams_through_the_sliders(tmp_path, steer, lean):
    """Each horn points in towards the middle, its pin 14 mm from the shaft at
    x = +-55 in the slider in that leg's slot: turning the horns 45 degrees
    (the rear one the other way) turns both steering beams about 10.2
    degrees about their pivots (x = +-100), the full 90 degrees about 17.3,
    symmetrically, without interference."""
    summary = _chassis(tmp_path, steer, -steer)
    assert summary["interference"] == []
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    turn = math.radians(steer)
    for end in (1, -1):
        pin = parts["front_steering_pin" if end > 0 else "rear_steering_pin"]
        centre = [(pin["bounding_box_min"][i] + pin["bounding_box_max"][i]) / 2 for i in (0, 1)]
        assert centre == pytest.approx(
            [end * (55.0 - 14.0 * math.cos(turn)), -14.0 * math.sin(turn)], abs=1e-3)
        assert math.degrees(math.atan2(centre[1], 100.0 - abs(centre[0]))) == pytest.approx(
            lean, abs=0.1)


@pytest.mark.parametrize("swing", [0.0, 10.0, -10.0])
def test_the_drive_follows_the_suspension_in_its_couplers(tmp_path, swing):
    """The motor on the fixed plate's bracket, tilted down; the drive shaft
    between the two couplers' joints, its ends in the shaft yokes' bores
    (4.2 to 14 mm from each joint) over the linkage's travel: no
    interference."""
    summary = _linkage(tmp_path, swing)
    assert summary["interference"] == []
    contacts = {(c["a"].split("/")[-1], c["b"].split("/")[-1]) for c in summary["contacts"]}
    assert ("fixed_plate", "motor") in contacts  # on its bracket
    # the couplers' joints: along the motor's shaft (13.8 mm from its front
    # face, tilted 22.6 degrees down), and on the hub's axis, moving with it
    tilt = math.atan2(14.0 - 12.0, 47.0 + 1.0)
    motor_joint = (-1.0 + 13.8 * math.cos(tilt), -12.0 - 13.8 * math.sin(tilt))
    turn = math.radians(swing)
    hub_joint = (3.0 + 55.0 * math.cos(turn) + 3.0 - 14.0, -14.0 + 55.0 * math.sin(turn))
    span = math.dist(motor_joint, hub_joint)
    level = math.dist(motor_joint, (47.0, -14.0))  # the joints' span with the arms level
    shaft = level - 14.0  # the drive shaft: that, less 7 mm a side
    end = (span - shaft) / 2  # each end, from its joint
    assert 4.2 <= end <= 14.0


def test_the_belt_drives_links_make_a_four_bar_linkage(tmp_path):
    """The second suspension concept's links: a Y base link (one hinge at the
    bottom middle, two top ends either side of the top hinge, each extended
    out and up to a shock joint), a single flat bar on top, an H of two bars
    with two shock lugs at the bottom, and the wheel link, the same Y with
    its stem carried down to the hub; both uprights seat the drive shaft half
    way between the links. Assembled, nothing interferes."""
    links = PRODUCTS / "MV1/belt_drives"
    base = _summary(build_part(links / "base_link/part.py", tmp_path / "base"))
    assert base["bounding_box"]["size"] == pytest.approx([26.4, 18.0, 62.0], abs=1e-3)
    assert base["bounding_box"]["min"][1] == pytest.approx(0.0, abs=1e-6)  # a flat back
    assert base["n_solids"] == 1
    for region in ("bottom_hinge", "top_hinge_left", "top_hinge_right", "shaft_bearing",
                   "shock_joint_left", "shock_joint_right", "back"):
        assert base["regions"][region]["count"] == 1
    top = _summary(build_part(links / "top_link/part.py", tmp_path / "top"))
    # 8 mm wide, 220 mm between its axes
    assert top["bounding_box"]["size"] == pytest.approx([8.0, 226.0, 6.0], abs=1e-3)
    bottom = _summary(build_part(links / "bottom_link/part.py", tmp_path / "bottom"))
    assert bottom["bounding_box"]["size"] == pytest.approx([26.4, 226.0, 14.0], abs=1e-3)
    assert bottom["n_solids"] == 1  # the two bars, joined by the crossbar
    assert bottom["regions"]["shock_joint_left"]["count"] == 1
    assert bottom["regions"]["shock_joint_right"]["count"] == 1
    wheel = _summary(build_part(links / "wheel_link/part.py", tmp_path / "wheel"))
    # the base link's 46 mm of hinges, on 22 mm of stem; the hub's boss 4 mm proud
    assert wheel["bounding_box"]["size"] == pytest.approx([26.4, 10.0, 68.0], abs=1e-3)
    assert wheel["regions"]["hub_bore"]["count"] == 1
    assert wheel["regions"]["shaft_bearing"]["count"] == 1
    drive = _summary(build_part(links / "assembly.py", tmp_path / "drive"))
    assert sorted(c["name"].split("/")[-1] for c in drive["components"]) == [
        "base_link", "bottom_link", "top_link", "wheel_link"]
    assert drive["interference"] == []
    # the wheel link's stem reaches 22 mm below the base link's bottom
    assert drive["bounding_box"]["min"][2] == pytest.approx(-22.0, abs=1e-3)
