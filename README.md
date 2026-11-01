# MHTGR-350 with ARMI and OpenMC

ARMI inputs for the OECD/NEA MHTGR-350 benchmark core
([NEA/NSC/R(2017)4](https://www.oecd-nea.org/upload/docs/application/pdf/2020-01/dir1/nsc-r2017-4.pdf)),
run with [OpenMC](https://docs.openmc.org) through the
[armi-openmc](https://github.com/partofthething/armi-openmc-plugin) plugin, with every TRISO
particle modeled explicitly. This is the input set proposed in
[terrapower/armi#224](https://github.com/terrapower/armi/issues/224); the TRISO support it needed
([#228](https://github.com/terrapower/armi/issues/228)) is in the
[partofthething ARMI fork](https://github.com/partofthething/armi).

> Made with large language models (Anthropic's Claude) under the direction of a human developer.
> Check anything that matters to you against independent calculations.

## The model

`generate.py` writes `mhtgr350-blueprints.yaml` from the specification, with the hole and column
layouts of the INL Virtual Test Bed model (`layouts.py`):

| | |
|---|---|
| Core | 66 fuel columns (54 standard, 12 with a reserve shutdown channel in six orientations) of 10 elements, 97 graphite reflector columns, 198.25 cm bottom and 118.94 cm top reflector, 297.3 cm core barrel (Tables I.2, I.6) |
| Fuel element | 36 cm across flats, 79.3 cm tall; on a 1.8796 cm triangular pitch 210 fuel compacts, 102 + 6 coolant holes, 6 burnable poison (LBP) compacts; RSC elements trade 24 compacts for a 9.525 cm channel (Table I.3) |
| TRISO | UC0.5O1.5 kernel, 15.5 wt% U-235, 10.5 g/cm3; buffer, IPyC, SiC, OPyC; packing fraction 0.35 in a 1.245 cm compact with a 1.74 g/cm3 matrix (Tables I.4, AIV.7) |
| LBP | natural-boron B4C grains (200 um, PyC coated) at 10.9 vol% in a 1.143 cm graphite compact (Table I.5) |
| Graphite | block graphite 1.85 g/cm3 with burnable impurities as 1.45 ppm natural boron equivalent; reflectors at the benchmark's reflector composition (Section I.7.3.1) |
| State | fresh fuel, 20 C isothermal, every control and shutdown rod withdrawn |

The benchmark's own exercises use cross sections of depleted, equilibrium-cycle compositions that
it never publishes as number densities, so a continuous-energy code cannot reproduce them. The
fresh, cold, all-rods-out core is the configuration the specification fully defines.

In ARMI each TRISO layer and each B4C grain layer is a component of its block
(`particles:` in the blueprints); the plugin packs the particles at random in each compact and
tracks them on a Cartesian mesh.

## Running

With the ARMI fork and armi-openmc installed (see the plugin's docs), and OpenMC data at the
path in the settings files:

```bash
python generate.py                                                   # rewrite the blueprints
python check.py                                                      # check them against the spec
python -m armi_openmc openmc-xs block-kinf.yaml --xs-ids AA --output ISOAA-explicit
python -m armi_openmc openmc-xs block-kinf-homogenized.yaml --xs-ids AA --output ISOAA-homogenized
python -m armi_openmc run core-cold.yaml                             # the whole core
```

## Results

ENDF/B-VIII.1, OpenMC 0.15.3.

RESULTS_TABLE

The standard element alone (infinite lattice, the XS ID `AA` the ISOTXS files hold) shows:

* **Double heterogeneity.** Modeling the particles instead of smearing them in their compacts is
  worth +3009 pcm, in the range reported for prismatic HTGR fuel.
* **The cross sections close.** The k-infinity rebuilt from each ISOTXS (homogenized medium,
  ARMI's macroscopic cross sections) is 0.89502 (explicit) and 0.87119 (homogenized), against
  OpenMC's 0.89478 ± 0.00057 and 0.87132 ± 0.00049.
* **The burnable poison is heavy.** Without the LBP boron the element's k-infinity is
  1.4885 ± 0.0006: the LBPs as Table I.5 describes them hold down about 44,600 pcm when fresh,
  far more than in a real core. The benchmark's LBP data serve its equilibrium-cycle model, in
  which the poison has partly burned; Table I.5 does not say how much boron a fresh LBP holds,
  and natural boron in coated B4C particles at 10.9 vol% is the reading used here (counting the
  10.9% as B4C kernels would mean even more boron). Hence a fresh core well below critical.

## Notes on the specification

* **Particle count.** A packing fraction of 0.35 (Table I.4) puts 6,647 particles in each
  4.928 cm compact. The core totals of Table I.2 (1.2186e10 particles in 2.0358e6 compacts)
  imply 5,986, a packing fraction of 0.315. These inputs follow Table I.4, the data marked for
  lattice calculations; the core holds 5.44 t of uranium.
* **RSC element.** The VTB layout used here has 89 large and 6 small coolant holes in the RSC
  element; Table I.3 says 88 and 7.
* **Handling hole.** The 3.5 cm fuel-handling hole (top third of the element) is modeled as
  graphite, as in the VTB model.
* **B4C temperature.** ARMI's B4C expansion data start at 25 C, so the grains sit at 25 C; their
  densities come from the inputs, not the expansion, so this changes nothing but their
  cross-section temperature.

## Credits

Layouts from the INL Virtual Test Bed MHTGR model (O. Calvin, J. Ortensi, Y.S. Jung); benchmark
specification by the OECD/NEA and INL (G. Strydom et al.).
