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
| `MV1/chassis` | assembly: the longitudinal beam carried on two lateral beams, its end discs seated on theirs, their pins in its holes |
| `MV1/chassis/beam` | part: a beam running longitudinally (along x), 200 mm between the 20 mm discs at its ends, each with a hole through its middle |
| `MV1/chassis/lateral_beam` | part: a shorter beam running laterally (along y), 120 mm, with a disc on top and a pin sticking up from its middle |

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
