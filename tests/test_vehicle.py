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
        "MV1/chassis", "MV1/chassis/beam", "MV1/chassis/lateral_beam"]


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
