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
        "MV1/chassis", "MV1/chassis/beam", "MV1/chassis/clip",
        "MV1/chassis/lateral_beam", "MV1/chassis/sliding_plate"]


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


def test_the_lateral_beam_runs_sideways_with_a_disc_and_pin_on_top(tmp_path):
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/lateral_beam/part.py",
                                  tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([20.0, 120.0, 21.0])  # 10 bar + 3 disc + 8 pin
    assert box["size"][1] == max(box["size"])  # lateral
    assert box["min"] == pytest.approx([-10.0, -60.0, 0.0])
    assert summary["face_types"]["CYLINDER"] == 2  # the disc's rim, the pin


def test_the_sliding_plate_is_a_dog_biscuit_with_two_hinges_at_each_end(tmp_path):
    """3 mm thick: a 60 x 10 mm bar, a 20 x 10 mm end past each end of it with
    its outer corners rounded to 5 mm, and two 3.4 mm hinge holes side by
    side (10 mm apart along x) through each end."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/sliding_plate/part.py",
                                  tmp_path / "out"))
    assert summary["bounding_box"]["size"] == pytest.approx([20.0, 80.0, 3.0])
    corner = (5.0 ** 2 - math.pi * 5.0 ** 2 / 4) * 3.0  # rounded off each outer corner
    ends = 2 * (20.0 * 10.0 * 3.0 - 2 * corner)
    holes = 4 * math.pi * 1.7 ** 2 * 3.0
    assert summary["volume_mm3"] == pytest.approx(60 * 10 * 3 + ends - holes, abs=0.01)
    assert summary["face_types"]["CYLINDER"] == 8  # 4 holes, 4 rounded corners
    assert summary["regions"]["left_hinges"]["count"] == 2
    assert summary["regions"]["right_hinges"]["count"] == 2


def test_the_chassis_carries_the_beam_and_the_sliding_plate_under_it(tmp_path):
    """Each end disc seated on a lateral beam's disc (the disc less the hole
    in contact), the pin in the hole with clearance; the sliding plate
    across the middle of the beam's bottom, held up by the clip around the
    beam. No interference."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/assembly.py", tmp_path / "out"))
    assert summary["interference"] == []
    contacts = {(c["a"], c["b"]): c["area_mm2"] for c in summary["contacts"]}
    seat = math.pi * (10.0 ** 2 - 1.7 ** 2)
    assert contacts == pytest.approx({
        ("chassis/beam", "chassis/front_lateral_beam"): seat,
        ("chassis/beam", "chassis/rear_lateral_beam"): seat,
        ("chassis/beam", "chassis/sliding_plate"): 10.0 * 10.0,  # the beam's width x the bar's
        # the clip's walls on the beam's sides, its lips on the top, its side walls under it
        ("chassis/beam", "chassis/clip"): 2 * 16.4 * 10.0 + 2 * 16.4 * 2.0 + 2 * 3.0 * 10.0,
        # the window's top, flush with the beam's bottom, beside the beam
        ("chassis/sliding_plate", "chassis/clip"): 2 * 2.0 * 10.0,
    }, rel=1e-3)
    beam, front, rear, plate, clip = summary["components"]
    assert beam["bounding_box_min"][2] == pytest.approx(13.0)  # on the 3 mm discs
    assert front["bounding_box_min"][0] == pytest.approx(90.0)
    assert rear["bounding_box_max"][0] == pytest.approx(-90.0)
    assert plate["name"] == "chassis/sliding_plate"
    assert plate["bounding_box_max"][2] == pytest.approx(beam["bounding_box_min"][2])
    assert plate["bounding_box_min"][:2] == pytest.approx([-10.0, -40.0])


def test_the_clip_rings_the_beam_and_holds_the_plate_in_its_window(tmp_path):
    """A snug ring around the beam, 2 mm walls, split on top for snapping on;
    a 10.4 x 3.2 mm window under the beam for the plate, a 2 mm floor."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/clip/part.py", tmp_path / "out"))
    assert summary["bounding_box"]["size"] == pytest.approx([16.4, 14.0, 17.2])
    body = 16.4 * 14.0 * 17.2
    beam = 16.4 * 10.0 * 10.0
    window = 10.4 * 14.0 * 3.2
    split = 16.4 * 6.0 * 2.0
    assert summary["volume_mm3"] == pytest.approx(body - beam - window - split, abs=0.01)
    assert summary["n_solids"] == 1
    assembly = _summary(build_part(PRODUCTS / "MV1/chassis/assembly.py", tmp_path / "asm"))
    beam_c, _, _, plate, clip = assembly["components"]
    assert clip["bounding_box_min"][2] == pytest.approx(plate["bounding_box_min"][2] - 2.2)
    assert clip["bounding_box_max"][2] == pytest.approx(beam_c["bounding_box_max"][2] + 2.0)
