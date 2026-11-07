# vequir-vehicle

VequIR's model vehicles, designed with the
[CAD tool](https://github.com/anroleroux/vequir-standard/tree/main/tools/cad):
each vehicle a product, broken down into assemblies and parts, written as
CadQuery B-rep code from plain-language descriptions and built and checked
as exact solids.

Product page: **[anroleroux.co.za/vequir-vehicle](https://anroleroux.co.za/vequir-vehicle/)**

## Vehicle directions

Every part and assembly here is modelled in the vehicle's axes:

| Term | Axis | Meaning |
| --- | --- | --- |
| longitudinal | x | front–back; +x is the front |
| lateral | y | sideways; +y is the left (facing forward) |
| vertical | z | up; the vehicle stands on z = 0 |

## The catalogue

| Designation | What |
| --- | --- |
| `MV1` | product: the first model vehicle |
| `MV1/chassis` | assembly: the longitudinal beam carried on two lateral steering beams, its end discs seated on theirs, their pins in its holes, their T legs pointing inwards |
| `MV1/chassis/beam` | part: a beam running longitudinally (along x), 200 mm between the 20 mm discs at its ends, each with a hole through its middle |
| `MV1/chassis/lateral_beam` | part: a steering beam running laterally (along y), 120 mm, with a disc on top, a pin sticking up from its middle to turn about, a 40 mm T leg from its middle along x to steer by, and its ends extended down and widened into 30 × 50 mm uprights (the linkage plate's size) |
| `MV1/linkage` | assembly: a four-bar linkage moving in y-z: a fixed plate in the x-z plane, two equal arms hinged to its top and bottom, and a moving plate hinged to their far ends, kept parallel |
| `MV1/linkage/plate` | part: a 30 × 50 × 3 mm plate in the x-z plane with a hinge (two outer knuckles about an x axis) at its top and bottom; used for the fixed and the moving plate |
| `MV1/linkage/arm` | part: a 30 mm wide, 3 mm plate, 40 mm between the middle knuckles at its ends |
| `MV1/linkage/pin` | part: a 2 × 30 mm hinge pin |

```
products/<VEHICLE>/product.md                         "# Title", then a blurb
products/<VEHICLE>/<assembly>/assembly.md             an assembly
products/<VEHICLE>/<assembly>/assembly.py             optional: its parts placed together
products/<VEHICLE>/<assembly>/<part>/description.md   the instructions (source of truth)
products/<VEHICLE>/<assembly>/<part>/part.py          the CadQuery script
```

Bought-in parts (screws, cells, boards) come from
[vequir-standard](https://github.com/anroleroux/vequir-standard), which
`libraries.txt` names (`../vequir-standard/library`); place them with
`load_library("hardware/m1_2x6_countersunk")`.

## Working on it

Clone the libraries `libraries.txt` names beside this repository, install
the CAD tool (it comes with vequir-standard, under `tools/cad/`), and run
everything from this repository's root:

```bash
git clone https://github.com/anroleroux/vequir-standard ../vequir-standard
python -m venv .venv && source .venv/bin/activate
pip install -e "../vequir-standard/tools/cad[dev]"

python -m pytest -q tests                 # checks of the real parts
cad build MV1/chassis/beam                # one part
cad site --out results --site site        # every part, then the pages
```

`results/` and `site/` are build output and git-ignored. In a Claude Code
session, the `cad-part` skill (`.claude/skills/cad-part/`) takes a
designation plus modelling instructions through the same steps, reading
"longitudinal", "lateral" and "up" as x, y and z.

## CI and the product page

`.github/workflows/cad.yml` runs on every push to `main` and `claude/**`. It
clones vequir-standard beside the checkout (the branch of the same name
when it exists there, else the default branch), installs the CAD tool from
it, runs the tests, builds every part, and deploys the site to GitHub Pages:
**anroleroux.co.za/vequir-vehicle**. A part that fails to build fails the job.
Settings → Pages → Source must be GitHub Actions.

Actions → **cad** → *Run workflow*, with `design` set to a part directory
holding a `description.md`, has Claude write its script; it needs the
`ANTHROPIC_API_KEY` repository secret.
