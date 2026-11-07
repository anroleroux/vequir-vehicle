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
        "MV1/chassis", "MV1/chassis/beam", "MV1/chassis/lateral_beam",
        "MV1/linkage", "MV1/linkage/arm", "MV1/linkage/pin", "MV1/linkage/plate"]


def test_the_chassis_beam_runs_longitudinally_with_a_holed_disc_at_each_end(tmp_path):
    """Longest along x, centred on the centreline, standing on z = 0; a 20 mm
    disc on each end, its centre line in z, with a hole through it."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/beam/part.py", tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([220.0, 20.0, 10.0])  # 200 between disc centres
    assert box["size"][0] == max(box["size"])  # longitudinal
    assert box["min"] == pytest.approx([-110.0, -10.0, 0.0])
    assert summary["n_solids"] == 1
    assert summary["face_types"] == {"CYLINDER": 4, "PLANE": 4}  # disc rims, holes; a plain bar
    assert summary["regions"]["front_hole"]["count"] == 1
    assert summary["regions"]["rear_hole"]["count"] == 1


def test_the_lateral_beam_runs_sideways_with_a_disc_pin_and_steering_leg(tmp_path):
    """A 120 mm bar along y with a disc and pin on top, and a 40 mm T leg from
    its middle along -x, the bar's section."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/lateral_beam/part.py",
                                  tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([55.0, 120.0, 21.0])  # 10 bar + 40 leg; 10 + 3 disc + 8 pin
    assert box["size"][1] == max(box["size"])  # lateral
    assert box["min"] == pytest.approx([-45.0, -60.0, 0.0])
    assert summary["face_types"]["CYLINDER"] == 2  # the disc's rim, the pin
    disc = math.pi * 10.0 ** 2 * 3.0
    pin = math.pi * 1.6 ** 2 * 8.0
    assert summary["volume_mm3"] == pytest.approx(
        10 * 120 * 10 + 40 * 10 * 10 + disc + pin, abs=0.01)


def test_the_chassis_seats_the_beam_on_the_steering_beams_legs_inwards(tmp_path):
    """Each end disc seated on a steering beam's disc (the disc less the hole
    in contact), the pin in the hole with clearance; both T legs pointing
    inwards under the longitudinal beam, clear of it. No interference."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/assembly.py", tmp_path / "out"))
    assert summary["interference"] == []
    contacts = {(c["a"], c["b"]): c["area_mm2"] for c in summary["contacts"]}
    seat = math.pi * (10.0 ** 2 - 1.7 ** 2)
    assert contacts == pytest.approx({
        ("chassis/beam", "chassis/front_lateral_beam"): seat,
        ("chassis/beam", "chassis/rear_lateral_beam"): seat,
    }, rel=1e-3)
    beam, front, rear = summary["components"]
    assert beam["bounding_box_min"][2] == pytest.approx(13.0)  # on the 3 mm discs
    assert [front["bounding_box_min"][0], front["bounding_box_max"][0]] == pytest.approx([55.0, 110.0])
    assert [rear["bounding_box_min"][0], rear["bounding_box_max"][0]] == pytest.approx([-110.0, -55.0])


def test_the_linkage_plate_stands_in_x_z_with_a_hinge_top_and_bottom(tmp_path):
    """30 x 50 mm, 3 mm thick along y; two outer knuckles about an x axis at
    its top and bottom, a 2.2 mm hole through them."""
    summary = _summary(build_part(PRODUCTS / "MV1/linkage/plate/part.py", tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([30.0, 6.0, 50.0])  # 3 mm plate, 6 mm knuckles
    assert box["size"][1] == min(box["size"])  # thin along y: in the x-z plane
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


@pytest.mark.parametrize("swing", [0.0, 25.0, -25.0])
def test_the_four_bar_linkage_moves_in_y_z_without_collisions(tmp_path, swing):
    """Fixed plate, two equal arms, moving plate, four pins: no interference
    level or swung 25 degrees either way, the moving plate kept upright and
    moved only in y-z, the pins on the arms' far hinges."""
    summary = _linkage(tmp_path, swing)
    assert summary["interference"] == []
    parts = {c["name"].split("/")[-1]: c for c in summary["components"]}
    assert set(parts) == {"fixed_plate", "moving_plate", "bottom_arm", "top_arm",
                          "fixed_bottom_pin", "fixed_top_pin", "moving_bottom_pin",
                          "moving_top_pin"}
    fixed, moving = parts["fixed_plate"], parts["moving_plate"]
    turn = math.radians(swing)
    rise = 40.0 * math.sin(turn)
    run = 40.0 * math.cos(turn)
    for i in (0, 1):  # x and y extents: the same plate, upright, moved in y-z
        assert moving["bounding_box_max"][i] - moving["bounding_box_min"][i] == pytest.approx(
            fixed["bounding_box_max"][i] - fixed["bounding_box_min"][i], abs=1e-3)
    assert moving["bounding_box_min"][0] == pytest.approx(fixed["bounding_box_min"][0], abs=1e-3)
    # the summary rounds to 4 decimals
    assert moving["bounding_box_min"][2] == pytest.approx(fixed["bounding_box_min"][2] + rise, abs=1e-3)
    pin = parts["moving_bottom_pin"]
    centre = [(pin["bounding_box_min"][i] + pin["bounding_box_max"][i]) / 2 for i in (1, 2)]
    assert centre == pytest.approx([1.5 + run, 3.0 + rise], abs=1e-3)
