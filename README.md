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
| `MV1` | product, assembled: the chassis with a linkage mounted on each upright of its steering beams, four in all, raised 15 mm (30 % of the linkage plate's height) |
| `MV1/chassis` | assembly: the main beam carried on two lateral steering beams, its round ends seated on their discs, their pins in its holes, their T legs pointing inwards; two SG90 servos upside down on the main beam, symmetrical front and back, each horn pointing in towards the middle, its pin in a slider in that leg's slot, steering that beam |
| `MV1/chassis/beam` | part: the main beam, a thin (3 mm) horizontal plate along x: a straight section 100 mm wide and 80 mm long in the middle, tapering sharply in to 20 mm round ends at the steering rotation points, 200 mm apart, each with a hole for the steering beam's pin; on top, a 6 mm cylinder at each pivot and two gussets, straight in the middle just far enough apart for the SG90 and angled in to the pivots, with the two servos' holes and tab blocks |
| `MV1/chassis/lateral_beam` | part: a steering beam running laterally (along y), 60 mm, built from plates: a top plate turning down into the end plates of its uprights (from 15 to 50 mm up, where the linkages mount), curved gussets along both side edges, the full beam and uprights; a 10 mm disc and pin on top to turn about; a 60 mm T leg along x to steer by, slotted for the slider |
| `MV1/chassis/slider` | part: a 6 × 3.6 mm block with a flange, running in the steering leg's slot, the horn's pin turning in it |
| `MV1/chassis/steering_pin` | part: a 2 × 8.3 mm pin from the servo horn down into the slider |
| `MV1/linkage` | assembly: a four-bar linkage moving in y-z: a fixed plate in the x-z plane, two equal arms hinged to its top and bottom, the wheel link hinged to their far ends, kept parallel, and a shock absorber from the fixed plate's joint over the top arm, down through both arms' openings to the wheel link's tab, travelling ±15° |
| `MV1/linkage/plate` | part: an I link: a straight 9.6 × 50 × 3 mm strip in the x-z plane, as wide as the middle knuckle of the hinge (about an x axis) at its top and bottom, flush with its flat back face, which mounts on an upright; carried on up and out over the top arm's opening to the shock absorber's upper joint; the fixed side link (the wheel link extends it on the other side) |
| `MV1/linkage/wheel_link` | part: the wheel-side I link: a 19.6 mm strip for the wider wheel-side hinges, extended 30 mm down below its bottom hinge, where the wheel will come, with the shock's lower tab below the bottom arm |
| `MV1/linkage/arm` | part: an H link: a 3 mm plate, 55 mm between its hinges, its legs angled out from 30 mm wide at the chassis hinge to 40 mm at the wheel hinge; the wheel-end slot runs 35 mm in and is cut 3 mm back into the legs, room for a shock absorber or suspension to pass; filleted crossbar corners |
| `MV1/linkage/pin` | part: a 2 × 30 mm hinge pin |
| `MV1/linkage/wheel_pin` | part: a 2 × 40 mm hinge pin for the wider wheel-side hinges |
| `MV1/linkage/shock_body` | part: the shock absorber's body: a 10 mm tube, 46 mm long with a 4.4 mm bore, on a fork at its lower end |
| `MV1/linkage/shock_rod` | part: the shock absorber's 4 mm rod, sliding in the body, on a fork at its upper end |
| `MV1/linkage/shock_pin` | part: a 2 × 7.4 mm pin through a shock fork and its tab |

```
products/<VEHICLE>/product.md                         "# Title", then a blurb
products/<VEHICLE>/<assembly>/assembly.md             an assembly
products/<VEHICLE>/<assembly>/assembly.py             optional: its parts placed together
products/<VEHICLE>/<assembly>/<part>/description.md   the instructions (source of truth)
products/<VEHICLE>/<assembly>/<part>/part.py          the CadQuery script
```

The steering servo (`actuators/sg90`) and its horn (`actuators/sg90_horn`)
are bought in, from vequir-standard. Bought-in parts (screws, cells, boards, servos) come from
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
