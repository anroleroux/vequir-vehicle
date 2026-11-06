"""The model vehicles: each part checked against its description, in the
vehicle's axes (x longitudinal, +x front; y lateral, +y left; z up).

The CAD tool comes from vequir-standard, which ``libraries.txt`` expects
beside this repository (CI clones it there).
"""

from __future__ import annotations

import json
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
    assert sorted(e.designation for e in discover_all(PRODUCTS)) == ["MV1/chassis/beam"]


def test_the_chassis_beam_runs_longitudinally(tmp_path):
    """Longest along x, centred on the vehicle's centreline, standing on z = 0."""
    summary = _summary(build_part(PRODUCTS / "MV1/chassis/beam/part.py", tmp_path / "out"))
    box = summary["bounding_box"]
    assert box["size"] == pytest.approx([200.0, 10.0, 10.0])
    assert box["size"][0] == max(box["size"])  # longitudinal
    assert box["min"] == pytest.approx([-100.0, -5.0, 0.0])
    assert summary["n_solids"] == 1
    assert set(summary["regions"]) == {"front_end", "rear_end", "top", "bottom",
                                       "left_side", "right_side"}
