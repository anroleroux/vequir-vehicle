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
        "MV1/chassis/sliding_beam"]


def test_the_chassis_beam_runs_longitudinally_with_a_holed_disc_at_each_end(tmp_path):
    """Longest along x, centred on the centreline, standing on z = 0; a 20 mm
    disc on each end, its centre line in z, with a hole through it; a guide
    open to the top and closed at the bottom at the middle: a U-channel
    40 mm along y, past each side of the beam, its floor flush with the
    beam's top."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/beam/part.py", tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([220.0, 40.0, 15.0])  # 200 between disc centres; the guide
    assert box["min"] == pytest.approx([-110.0, -20.0, 0.0])
    assert summary["n_solids"] == 1
    assert summary["face_types"]["CYLINDER"] == 4  # two disc rims, two holes
    u_section = 16.4 * 8.0 - 10.4 * 5.0  # 3 mm floor and cheeks around the 10.4 mm channel
    in_the_bar = 16.4 * 3.0 * 10.0  # the floor where the beam already is
    bar_and_discs = 24188.3783  # the bar and its two holed discs
    assert summary["volume_mm3"] == pytest.approx(
        bar_and_discs + u_section * 40.0 - in_the_bar, abs=0.01)
    for region in ("guide_floor", "guide_underside", "guide_front_cheek", "guide_rear_cheek"):
        assert summary["regions"][region]["count"] == 1
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


def test_the_lateral_beams_carry_the_beam_on_their_discs_and_pins(tmp_path):
    """Each end disc seated on a lateral beam's disc (the disc less the hole
    in contact), the pin in the hole with clearance: no interference."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/assembly.py", tmp_path / "out"))
    assert summary["interference"] == []
    seat = math.pi * (10.0 ** 2 - 1.7 ** 2)
    contacts = {(c["a"], c["b"]): c["area_mm2"] for c in summary["contacts"]}
    assert sorted(contacts) == [
        ("chassis/beam", "chassis/front_lateral_beam"),
        ("chassis/beam", "chassis/rear_lateral_beam"),
        ("chassis/beam", "chassis/sliding_beam")]
    assert contacts[("chassis/beam", "chassis/front_lateral_beam")] == pytest.approx(seat, rel=1e-3)
    assert contacts[("chassis/beam", "chassis/rear_lateral_beam")] == pytest.approx(seat, rel=1e-3)
    beam, front, rear, sliding = summary["components"]
    assert beam["bounding_box_min"][2] == pytest.approx(13.0)  # on the 3 mm discs
    assert front["bounding_box_min"][0] == pytest.approx(90.0)
    assert rear["bounding_box_max"][0] == pytest.approx(-90.0)


def test_the_sliding_beam_rests_in_the_guide_on_top_of_the_beam(tmp_path):
    """Lateral, half the lateral beams' length, on the beam's top at x = 0
    (the beam goes underneath it), between the guide's cheeks with 0.2 mm
    clearance each side."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/assembly.py", tmp_path / "out"))
    beam, front, rear, sliding = summary["components"]
    assert sliding["name"] == "chassis/sliding_beam"
    size = [sliding["bounding_box_max"][i] - sliding["bounding_box_min"][i] for i in range(3)]
    assert size == pytest.approx([10.0, 60.0, 10.0])  # half the lateral beams' 120
    assert sliding["bounding_box_min"][:2] == pytest.approx([-5.0, -30.0])
    assert sliding["bounding_box_min"][2] == pytest.approx(beam["bounding_box_min"][2] + 10.0)
    assert summary["interference"] == []  # clear of the cheeks
    area = {c["b"]: c["area_mm2"] for c in summary["contacts"]}["chassis/sliding_beam"]
    assert area == pytest.approx(10.0 * 40.0)  # on the guide's floor, its whole length


def test_the_sliding_beams_ends_are_forks_with_a_hinge_through_both_plates(tmp_path):
    """At each end a 3 mm top and bottom plate, 10 mm long, a 4 mm gap
    between them, and a 3.4 mm hinge hole through both, 5 mm in from the end."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/sliding_beam/part.py",
                                  tmp_path / "out"))
    assert summary["bounding_box"]["size"] == pytest.approx([10.0, 60.0, 10.0])
    gaps = 2 * 10.0 * 10.0 * 4.0
    holes = 4 * math.pi * 1.7 ** 2 * 3.0  # one through each plate
    assert summary["volume_mm3"] == pytest.approx(10 * 60 * 10 - gaps - holes, abs=0.01)
    assert summary["face_types"]["CYLINDER"] == 4
    assert summary["regions"]["left_hinge"]["count"] == 2  # top and bottom plate
    assert summary["regions"]["right_hinge"]["count"] == 2
