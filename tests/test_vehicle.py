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
        "MV1", "MV1/chassis", "MV1/chassis/beam", "MV1/chassis/lateral_beam",
        "MV1/chassis/slider", "MV1/chassis/steering_pin",
        "MV1/linkage", "MV1/linkage/arm", "MV1/linkage/pin", "MV1/linkage/plate",
        "MV1/linkage/shock_body", "MV1/linkage/shock_pin", "MV1/linkage/shock_rod",
        "MV1/linkage/wheel_link", "MV1/linkage/wheel_pin"]


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
    assert summary["regions"]["servo_hole"]["count"] == 1
    assert box["min"][0] == pytest.approx(-110.0)
    assert box["min"][2] == pytest.approx(0.0)
    assert summary["n_solids"] == 1
    assert summary["regions"]["front_hole"]["count"] == 1
    assert summary["regions"]["rear_hole"]["count"] == 1
    assert summary["regions"]["bottom"]["count"] == 1  # one flat seat


def test_the_steering_beam_is_built_from_plates_with_curved_gussets(tmp_path):
    """60 mm along y, 10 mm wide, 50 mm tall at its uprights: a 2 mm top
    plate turning down into 2 mm end plates, 1.5 mm gussets along both side
    edges; a 40 mm T leg along -x; a disc and a 3 mm pin on top."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/lateral_beam/part.py",
                                  tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([55.0, 60.0, 63.0])  # leg to disc; 50 + 10 disc + 3 pin
    assert box["size"][1] > box["size"][0]  # lateral
    assert box["min"] == pytest.approx([-45.0, -30.0, 0.0])
    assert summary["n_solids"] == 1
    for region in ("seat", "pin", "leg_end", "left_end", "right_end"):
        assert summary["regions"][region]["count"] == 1
    assert summary["regions"]["slot"]["count"] == 4  # the slider's slot along the leg
    # far lighter than a solid 10 x 10 mm bar of the same outline: it is plates
    solid = 10 * 60 * 10 + 2 * 10 * 10 * 40 + 40 * 10 * 10
    assert summary["volume_mm3"] < 0.75 * solid
    # the gussets' curves: cylinder faces besides the disc's rim and the pin
    assert summary["face_types"]["CYLINDER"] > 2


def test_the_chassis_seats_the_beam_on_the_steering_beams_legs_inwards(tmp_path):
    """Each end disc seated on a steering beam's disc (the disc less the hole
    in contact), the pin in the hole with clearance; both T legs pointing
    inwards under the main beam, clear of it; the servo upside down on the
    main beam, its horn under it, the slider in the front leg's slot. No
    interference."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/assembly.py", tmp_path / "out"))
    assert summary["interference"] == []
    contacts = {(c["a"], c["b"]): c["area_mm2"] for c in summary["contacts"]}
    seat = math.pi * (10.0 ** 2 - 1.7 ** 2)
    assert contacts[("chassis/beam", "chassis/front_lateral_beam")] == pytest.approx(seat, rel=1e-3)
    assert contacts[("chassis/beam", "chassis/rear_lateral_beam")] == pytest.approx(seat, rel=1e-3)
    for pair in (("chassis/beam", "chassis/servo"), ("chassis/servo", "chassis/horn"),
                 ("chassis/front_lateral_beam", "chassis/slider")):
        assert contacts[pair] > 0  # resting on each other
    beam, front, rear, servo, horn, slider, pin = summary["components"]
    assert beam["bounding_box_min"][2] == pytest.approx(60.0)  # 40 uprights, 10 bar, 10 disc
    assert servo["bounding_box_max"][2] == pytest.approx(63.0 + 22.7)  # upside down on the plate
    assert horn["bounding_box_min"][2] > front["bounding_box_max"][2] - 13.0  # above the leg's top
    assert [front["bounding_box_min"][0], front["bounding_box_max"][0]] == pytest.approx([55.0, 110.0])  # leg end to disc
    assert [rear["bounding_box_min"][0], rear["bounding_box_max"][0]] == pytest.approx([-110.0, -55.0])
    assert front["bounding_box_min"][2] == pytest.approx(0.0)  # standing on its uprights


def test_the_linkage_plate_stands_in_x_z_with_a_hinge_top_and_bottom(tmp_path):
    """An I link: a straight 9.6 x 50 mm strip, 3 mm thick along y, only as
    wide as the middle knuckle about an x axis at its top and bottom, with a
    2.2 mm hole through it, flush with the flat back face (y = 0) it mounts
    by; carried on up to 74 mm and out over the top arm in a 6 mm bar, a tab
    hanging from its end for the shock's upper joint."""
    summary = _summary(build_part(PRODUCTS / "MV1/linkage/plate/part.py", tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([9.6, 38.0, 74.0])  # the bar 38 mm out, the tower 74 mm up
    assert summary["regions"]["back"]["count"] == 1  # one flat face, in the x-z plane
    assert box["min"] == pytest.approx([-4.8, 0.0, 0.0])  # nothing behind the back face
    knuckles = 2 * (math.pi * 3.0 ** 2 / 2 - math.pi * 1.1 ** 2) * 9.6  # the half proud, less the hole
    tower = 9.6 * 3.0 * 24.0
    bar = 9.6 * 35.0 * 6.0
    tab = (8.0 * 6.0 + math.pi * 4.0 ** 2 / 2 - math.pi * 1.1 ** 2) * 3.0
    assert summary["volume_mm3"] == pytest.approx(
        9.6 * 3.0 * 50.0 + knuckles + tower + bar + tab, abs=0.01)
    assert summary["regions"]["shock_joint"]["count"] == 1
    assert summary["n_solids"] == 1
    assert summary["regions"]["bottom_hinge"]["count"] == 1
    assert summary["regions"]["top_hinge"]["count"] == 1


def _linkage(tmp_path, swing):
    """The linkage assembly, built with its arms swung ``swing`` degrees."""
    import shutil
    root = tmp_path / f"swing_{swing}"
    shutil.copytree(PRODUCTS / "MV1/linkage", root / "linkage")
    script = root / "linkage/assembly.py"
    script.write_text(script.read_text().replace("swing = 0.0", f"swing = {swing}"))
    return _summary(build_part(script, root / "out"))


@pytest.mark.parametrize("swing", [0.0, 15.0, -15.0])
def test_the_four_bar_linkage_moves_in_y_z_without_collisions(tmp_path, swing):
    """Fixed plate, two equal arms, wheel link, four pins and the shock
    absorber: no interference level or swung 15 degrees either way (the
    shock's travel), the wheel link kept upright and moved only in y-z, the
    pins on the arms' far hinges, the shock's ends on its joints."""
    summary = _linkage(tmp_path, swing)
    assert summary["interference"] == []
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    assert set(parts) == {"fixed_plate", "wheel_link", "bottom_arm", "top_arm",
                          "fixed_bottom_pin", "fixed_top_pin", "wheel_bottom_pin",
                          "wheel_top_pin", "shock_body", "shock_rod", "upper_shock_pin",
                          "lower_shock_pin"}
    fixed, moving = parts["fixed_plate"], parts["wheel_link"]
    turn = math.radians(swing)
    rise = 55.0 * math.sin(turn)  # the arms' 55 mm
    run = 55.0 * math.cos(turn)
    # upright, moved only in y-z: centred on x = 0, 3 mm thick plus its knuckles
    assert [moving["bounding_box_min"][0], moving["bounding_box_max"][0]] == pytest.approx(
        [-9.8, 9.8], abs=1e-3)
    assert moving["bounding_box_max"][1] - moving["bounding_box_min"][1] == pytest.approx(
        17.0, abs=1e-3)  # with the shock tab
    # the summary rounds to 4 decimals; the wheel link reaches 30 mm lower
    assert moving["bounding_box_min"][2] == pytest.approx(
        fixed["bounding_box_min"][2] + rise - 30.0, abs=1e-3)
    assert moving["bounding_box_max"][2] == pytest.approx(50.0 + rise, abs=1e-3)  # its top hinge's
    pin = parts["wheel_bottom_pin"]
    centre = [(pin["bounding_box_min"][i] + pin["bounding_box_max"][i]) / 2 for i in (1, 2)]
    assert centre == pytest.approx([3.0 + run, 3.0 + rise], abs=1e-3)
    # the shock's ends: the fixed plate's joint over the top arm (34 mm out,
    # 62 mm up), the wheel link's tab (10 mm in from the wheel hinge axis,
    # 18 mm below the arm)
    for name, at in (("upper_shock_pin", [34.0, 62.0]),
                     ("lower_shock_pin", [3.0 + run - 10.0, -18.0 + rise])):
        pin = parts[name]
        centre = [(pin["bounding_box_min"][i] + pin["bounding_box_max"][i]) / 2 for i in (1, 2)]
        assert centre == pytest.approx(at, abs=1e-3)


def test_mv1_mounts_a_linkage_on_each_upright_of_the_steering_beams(tmp_path):
    """Four linkages, each fixed plate's back face flat on an upright's end
    face (the 9.6 x 50 mm strip), reaching outwards along y. No
    interference."""
    summary = _summary(build_part(PRODUCTS / "MV1/assembly.py", tmp_path / "out"))
    assert summary["interference"] == []
    names = [c["name"] for c in summary["components"]]
    assert names == ["MV1/chassis", "MV1/front_left_linkage", "MV1/front_right_linkage",
                     "MV1/rear_left_linkage", "MV1/rear_right_linkage"]
    contacts = {c["b"]: c["area_mm2"] for c in summary["contacts"]}
    assert set(contacts) == set(names[1:])
    for area in contacts.values():
        assert area == pytest.approx(9.6 * 50.0)
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    for name, x, side in (("front_left_linkage", 100.0, 1), ("front_right_linkage", 100.0, -1),
                          ("rear_left_linkage", -100.0, 1), ("rear_right_linkage", -100.0, -1)):
        box_min, box_max = parts[name]["bounding_box_min"], parts[name]["bounding_box_max"]
        assert [box_min[0], box_max[0]] == pytest.approx([x - 20.0, x + 20.0])  # the arms' wheel ends
        inner = box_min[1] if side > 0 else box_max[1]
        assert inner == pytest.approx(side * 30.0)  # on the upright's end face
        assert [box_min[2], box_max[2]] == pytest.approx([-30.0, 74.0])  # wheel link; shock tower


def test_the_arm_is_an_h_wider_at_the_wheel_and_the_wheel_link_reaches_down(tmp_path):
    """The arm: 55 mm between hinges, 30 mm wide at the chassis hinge, 40 mm
    at the wheel hinge, a 35 mm deep slot at the wheel end, trimmed 3 mm into
    the legs; the wheel link: a 19.6 mm strip for the
    wheel end's wider gap, 30 mm longer at the bottom; the wheel pins 40 mm."""
    arm = _summary(build_part(PRODUCTS / "MV1/linkage/arm/part.py", tmp_path / "arm"))
    assert arm["bounding_box"]["size"] == pytest.approx([40.0, 61.0, 6.0])
    assert arm["n_solids"] == 1
    wheel = _summary(build_part(PRODUCTS / "MV1/linkage/wheel_link/part.py", tmp_path / "wheel"))
    assert wheel["bounding_box"]["size"] == pytest.approx([19.6, 17.0, 80.0])  # with its shock tab
    assert wheel["regions"]["wheel_end"]["count"] == 1
    assert wheel["regions"]["shock_tab"]["count"] == 1
    pin = _summary(build_part(PRODUCTS / "MV1/linkage/wheel_pin/part.py", tmp_path / "pin"))
    assert pin["bounding_box"]["size"] == pytest.approx([2.0, 2.0, 40.0])


@pytest.mark.parametrize("swing, collides", [(15.0, False), (25.0, True)])
def test_the_shock_travels_15_degrees_and_bottoms_out_beyond(tmp_path, swing, collides):
    """Its rod slides in the body between 67 and 95 mm between the joints;
    past +15 degrees the rod's end runs into the body's floor."""
    summary = _linkage(tmp_path, swing)
    pairs = {(c["a"].split("/")[-1], c["b"].split("/")[-1]) for c in summary["interference"]}
    if collides:
        assert ("shock_body", "shock_rod") in pairs
    else:
        assert pairs == set()


def _chassis(tmp_path, steer):
    """The chassis assembly, built with the servo's horn turned ``steer`` degrees."""
    import shutil
    root = tmp_path / f"steer_{steer}"
    shutil.copytree(PRODUCTS, root / "products")
    script = root / "products/MV1/chassis/assembly.py"
    script.write_text(script.read_text().replace("steer = 0.0", f"steer = {steer}"))
    (root / "libraries.txt").write_text(
        f"{(ROOT.parent / 'vequir-standard/library').resolve()}\n")
    return _summary(build_part(script, root / "out"))


@pytest.mark.parametrize("steer, lean", [(0.0, 0.0), (45.0, 15.8), (-45.0, -15.8)])
def test_the_servo_steers_the_front_beam_through_the_slider(tmp_path, steer, lean):
    """The horn's pin, 14 mm from the shaft at x = 55, in the slider in the
    front leg's slot: turning the horn 45 degrees turns the front steering
    beam about 15.8 degrees about its pivot (x = 100), without
    interference."""
    summary = _chassis(tmp_path, steer)
    assert summary["interference"] == []
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    pin = parts["steering_pin"]
    centre = [(pin["bounding_box_min"][i] + pin["bounding_box_max"][i]) / 2 for i in (0, 1)]
    turn = math.radians(steer)
    assert centre == pytest.approx([55.0 + 14.0 * math.cos(turn), 14.0 * math.sin(turn)], abs=1e-3)
    assert math.degrees(math.atan2(centre[1], 100.0 - centre[0])) == pytest.approx(lean, abs=0.1)
