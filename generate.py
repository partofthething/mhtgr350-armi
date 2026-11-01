"""
Write the ARMI blueprints of the MHTGR-350 benchmark core.

Everything comes from the benchmark specification, NEA/NSC/R(2017)4 (Volume I), and the layouts
in ``layouts.py``:

* fuel element (Table I.3): 36 cm across flats, 79.3 cm tall, holes on a 1.8796 cm triangular
  pitch: 210 fuel, 102 large and 6 small coolant, 6 burnable poison (LBP); the reserve shutdown
  (RSC) element trades 24 fuel holes for a 9.525 cm channel;
* TRISO particle and compact (Table I.4): UC0.5O1.5 kernel at 15.5 wt% U-235, five layers,
  packing fraction 0.35 in a 1.245 cm compact; matrix density 1.74 g/cm3 (Table AIV.7);
* LBP (Table I.5): B4C grains, PyC coated, at 10.9 vol% in a 1.143 cm graphite compact;
* graphite: 1.85 g/cm3 block graphite with burnable impurities as 1.45 ppm natural boron
  equivalent, and the reflector composition the benchmark used for its reflector cross sections
  (Section I.7.3.1);
* core (Figure I.9, Table I.6): 66 fuel columns of 10 elements in a hexagonal annulus, 198.25 cm
  of bottom and 118.94 cm of top reflector, inside a 297.3 cm core barrel.

The model is the fresh core, cold and isothermal at 20 C, with every control rod withdrawn; the
benchmark itself specifies depleted equilibrium-cycle compositions only as cross sections, so this
is the configuration a continuous-energy code can build from the specification alone.

Run with the ARMI environment that has the particle fuel support::

    python generate.py

and it writes ``mhtgr350-blueprints.yaml``.
"""

import io
import math
import pathlib

import armi

if not armi.isConfigured():
    armi.configure()

from armi.reactor import geometry, grids
from armi.reactor.blueprints import gridBlueprint
from armi.utils import asciimaps

import layouts

HERE = pathlib.Path(__file__).parent
AVOGADRO = 0.602214076  # atoms/(b cm) per (mol/cm^3)

HOLE_PITCH = 1.8796
BLOCK_PITCH = 36.0
ELEMENT_HEIGHT = 79.3
BOTTOM_REFLECTOR = 198.25
TOP_REFLECTOR = 118.94
FUEL_ELEMENTS = 10
TEMPERATURE = 20.0

#: RSC channel center, 9.756 cm from the element center, and the orientation of each core code.
RSC_RADIUS = math.hypot(4.878, 8.449)
RSC_ROTATION = {"33": -60, "34": 0, "35": 60, "36": 120, "37": 180, "38": -120}


# ------------------------------------------------------------------------------------------------
# Compositions, atoms/(b cm)
def _carbon(density):
    return {"C": density * AVOGADRO / 12.011}


def kernel():
    """UC0.5O1.5 at 15.5 wt% U-235 and 10.5 g/cm3."""
    w235 = 0.155
    moles235, moles238 = w235 / 235.0439, (1.0 - w235) / 238.0508
    uranium = 1.0 / (moles235 + moles238)
    molecules = 10.5 * AVOGADRO / (uranium + 0.5 * 12.011 + 1.5 * 15.9994)
    x235 = moles235 / (moles235 + moles238)
    return {
        "U235": molecules * x235,
        "U238": molecules * (1.0 - x235),
        "C": 0.5 * molecules,
        "O": 1.5 * molecules,
    }


def siliconCarbide():
    n = 3.2 * AVOGADRO / (28.0855 + 12.011)
    return {"SI": n, "C": n}


def boronCarbide():
    """B4C grains, natural boron, 2.47 g/cm3."""
    n = 2.47 * AVOGADRO / (4 * 10.811 + 12.011)
    return {"B10": 4 * n * 0.199, "B11": 4 * n * 0.801, "C": n}


def blockGraphite():
    """1.85 g/cm3, with the burnable impurities as 1.45 ppm natural boron equivalent (Sec. I.7.3.1)."""
    nd = _carbon(1.85)
    nd["B10"] = 0.199 * 12.011 / 10.811 * nd["C"] * 1.45e-6
    return nd


def reflectorGraphite():
    """The benchmark's reflector composition (Section I.7.3.1)."""
    return {"C": 8.62465e-2, "B10": 2.76490e-8}


ISOTOPICS = {
    "MHTGR kernel": kernel(),
    "buffer carbon": _carbon(1.0),
    "PyC": _carbon(1.9),
    "TRISO SiC": siliconCarbide(),
    "compact matrix": _carbon(1.74),
    "block graphite": blockGraphite(),
    "reflector graphite": reflectorGraphite(),
    "B4C grains": boronCarbide(),
    "LBP buffer": _carbon(1.0),
    "LBP PyC": _carbon(1.87),
    "LBP matrix": _carbon(0.94),
}


# ------------------------------------------------------------------------------------------------
# Geometry helpers
def _textSites(rows, pitch):
    """((x, y), code) of every hexagon in a text pattern whose rows are rows of hexagons."""
    middle = len(rows) // 2
    sites = []
    for r, row in enumerate(rows):
        codes = row.split()
        y = (middle - r) * pitch * math.sqrt(3.0) / 2.0
        for k, code in enumerate(codes):
            sites.append(((k - (len(codes) - 1) / 2.0) * pitch, y, code))
    return sites


def _rotate(x, y, degrees):
    a = math.radians(degrees)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def _indexer(grid, rings):
    """Coordinates (rounded) -> grid indices, for every site within ``rings``."""
    lookup = {}
    for ring in range(1, rings + 1):
        for pos in range(1, grid.getPositionsInRing(ring) + 1):
            i, j = grid.getIndicesFromRingAndPos(ring, pos)
            x, y, _ = grid[i, j, 0].getLocalCoordinates()
            lookup[(round(x, 3), round(y, 3))] = (i, j)
    return lookup


def _latticeMap(geom, contents):
    """An ARMI ascii lattice map of {(i, j): label}, written the way ARMI itself writes one."""
    aMap = asciimaps.asciiMapFromGeomAndDomain(geom, geometry.DomainType.FULL_CORE)()
    iOff, jOff = gridBlueprint._getAsciiMapOffset(geom, "full", contents.keys())
    aMap.asciiLabelByIndices = {(i - iOff, j - jOff): v for (i, j), v in contents.items()}
    aMap.gridContentsToAscii()
    stream = io.StringIO()
    aMap.writeAscii(stream)
    return stream.getvalue()


# In the final core frame of the VTB model the core is flats-up and each element has been turned
# 180 degrees from its text pattern (the MOOSE pattern generator rotates every patterned mesh by
# 90 degrees, once for the element and once for the core). RSC elements turn a further RSC_ROTATION.
ELEMENT_TURN = 180.0
CORE_TURN = 90.0

STANDARD_CODES = {"0": "L", "1": "F", "2": "C", "4": "S"}  # 3: graphite (no hole)
RSC_CODES = {"0": "L", "1": "F", "2": "C", "5": "S"}  # 3, 4: graphite


def elementGrid(rows, codes, turn):
    grid = grids.HexGrid.fromPitch(HOLE_PITCH, numRings=12, cornersUp=True)
    lookup = _indexer(grid, 12)
    contents = {}
    removed = []
    for x, y, code in _textSites(rows, HOLE_PITCH):
        xr, yr = _rotate(x, y, turn)
        ij = lookup[(round(xr, 3), round(yr, 3))]
        if code in codes:
            contents[ij] = codes[code]
        elif code == "4" and codes is RSC_CODES:
            removed.append((xr, yr))
    return contents, removed


def rscChannel(angle):
    a = math.radians(210.0 + angle)
    return RSC_RADIUS * math.cos(a), RSC_RADIUS * math.sin(a)


def coreGrid():
    grid = grids.HexGrid.fromPitch(BLOCK_PITCH, numRings=9)
    lookup = _indexer(grid, 9)
    contents = {}
    for x, y, code in _textSites(layouts.CORE, BLOCK_PITCH):
        if code == "26":
            continue
        xr, yr = _rotate(x, y, CORE_TURN)
        ij = lookup[(round(xr, 3), round(yr, 3))]
        if code == "13":
            contents[ij] = "F"
        elif code in RSC_ROTATION:
            contents[ij] = f"R{RSC_ROTATION[code] % 360}"
        else:
            contents[ij] = "RF"
    return contents


# ------------------------------------------------------------------------------------------------
# Blueprints text
def _component(name, lines, indent=8):
    pad = " " * indent
    out = [f"{pad}{name}:"]
    out += [f"{pad}    {line}" for line in lines]
    return "\n".join(out)


def _temps():
    return [f"Tinput: {TEMPERATURE}", f"Thot: {TEMPERATURE}"]


def fuelBlock(name, gridName, channel=None):
    parts = [
        f"    {name}: &block_{name.replace(' ', '_')}",
        f"        grid name: {gridName}",
        _component(
            "fuel compact",
            [
                "shape: Circle",
                "material: Graphite",
                "isotopics: compact matrix",
                *_temps(),
                "od: 1.245",
                "latticeIDs: [F]",
                "particles: TRISO",
                "packingFraction: 0.35",
                "flags: fuel",
            ],
        ),
        _component(
            "fuel gap",
            [
                "shape: Circle",
                "material: Helium",
                *_temps(),
                "id: fuel compact.od",
                "od: 1.27",
                "latticeIDs: [F]",
            ],
        ),
        _component(
            "LBP compact",
            [
                "shape: Circle",
                "material: Graphite",
                "isotopics: LBP matrix",
                *_temps(),
                "od: 1.143",
                "latticeIDs: [L]",
                "particles: B4C grain",
                "packingFraction: 0.109",
                "flags: poison",
            ],
        ),
        _component(
            "LBP gap",
            [
                "shape: Circle",
                "material: Helium",
                *_temps(),
                "id: LBP compact.od",
                "od: 1.27",
                "latticeIDs: [L]",
            ],
        ),
        _component(
            "coolant",
            ["shape: Circle", "material: Helium", *_temps(), "od: 1.588", "latticeIDs: [C]"],
        ),
        _component(
            "small coolant",
            ["shape: Circle", "material: Helium", *_temps(), "od: 1.27", "latticeIDs: [S]"],
        ),
    ]
    if channel is not None:
        parts.append(
            _component(
                "RSC channel",
                [
                    "shape: Circle",
                    "material: Helium",
                    *_temps(),
                    "od: 9.525",
                    f"origin: [{channel[0]:.4f}, {channel[1]:.4f}]",
                ],
            )
        )
    parts += [
        _component(
            "block graphite",
            ["shape: DerivedShape", "material: Graphite", "isotopics: block graphite", *_temps()],
        ),
        _component(
            "outline",
            [
                "shape: Hexagon",
                "material: Void",
                *_temps(),
                f"ip: {BLOCK_PITCH}",
                f"op: {BLOCK_PITCH}",
            ],
        ),
    ]
    return "\n".join(parts)


def reflectorBlock(name):
    return "\n".join(
        [
            f"    {name}: &block_{name.replace(' ', '_')}",
            _component(
                "reflector graphite",
                [
                    "shape: Hexagon",
                    "material: Graphite",
                    "isotopics: reflector graphite",
                    *_temps(),
                    "ip: 0.0",
                    f"op: {BLOCK_PITCH}",
                ],
            ),
        ]
    )


def assembly(name, specifier, fuelBlockName, xsType):
    blocks = (
        ["*block_reflector"] + [f"*block_{fuelBlockName}"] * FUEL_ELEMENTS + ["*block_reflector"]
    )
    heights = [BOTTOM_REFLECTOR] + [ELEMENT_HEIGHT] * FUEL_ELEMENTS + [TOP_REFLECTOR]
    xs = ["C"] + [xsType] * FUEL_ELEMENTS + ["C"]
    return "\n".join(
        [
            f"    {name}:",
            f"        specifier: {specifier}",
            f"        blocks: [{', '.join(blocks)}]",
            f"        height: [{', '.join(str(h) for h in heights)}]",
            f"        axial mesh points: [{', '.join('1' for _ in heights)}]",
            f"        xs types: [{', '.join(xs)}]",
        ]
    )


def blueprints(lbpBoron=True):
    standard, _ = elementGrid(layouts.STANDARD_ELEMENT, STANDARD_CODES, ELEMENT_TURN)
    out = [HEADER]
    out.append("custom isotopics:")
    isotopics = dict(ISOTOPICS)
    if not lbpBoron:
        # The B4C grains emptied of boron: the same particles, carbon only.
        isotopics["B4C grains"] = {"C": ISOTOPICS["B4C grains"]["C"]}
    for name, nd in isotopics.items():
        out.append(f"    {name}:")
        out.append("        input format: number densities")
        out += [f"        {nuc}: {value:.6e}" for nuc, value in nd.items()]
    out.append(PARTICLES)
    out.append("blocks:")
    out.append(fuelBlock("fuel", "standard element"))
    rscGrids = {}
    for angle in sorted({a % 360 for a in RSC_ROTATION.values()}):
        contents, removed = elementGrid(layouts.RSC_ELEMENT, RSC_CODES, ELEMENT_TURN + angle)
        channel = rscChannel(angle)
        _checkChannel(removed, channel)
        rscGrids[angle] = contents
        out.append(fuelBlock(f"RSC fuel {angle}", f"RSC element {angle}", channel))
    out.append(reflectorBlock("reflector"))
    out.append("assemblies:")
    out.append(assembly("fuel column", "F", "fuel", "A"))
    for angle in rscGrids:
        out.append(assembly(f"RSC column {angle}", f"R{angle}", f"RSC_fuel_{angle}", "B"))
    out.append(
        "\n".join(
            [
                "    reflector column:",
                "        specifier: RF",
                "        blocks: [" + ", ".join(["*block_reflector"] * (FUEL_ELEMENTS + 2)) + "]",
                "        height: ["
                + ", ".join(
                    str(h)
                    for h in [BOTTOM_REFLECTOR] + [ELEMENT_HEIGHT] * FUEL_ELEMENTS + [TOP_REFLECTOR]
                )
                + "]",
                "        axial mesh points: ["
                + ", ".join("1" for _ in range(FUEL_ELEMENTS + 2))
                + "]",
                "        xs types: [" + ", ".join("C" for _ in range(FUEL_ELEMENTS + 2)) + "]",
            ]
        )
    )
    out.append(SYSTEMS)
    out.append("grids:")
    out.append(_grid("core", "hex", coreGrid(), BLOCK_PITCH))
    out.append(_grid("standard element", "hex_corners_up", standard, HOLE_PITCH))
    for angle, contents in rscGrids.items():
        out.append(_grid(f"RSC element {angle}", "hex_corners_up", contents, HOLE_PITCH))
    return "\n".join(out) + "\n"


def _grid(name, geom, contents, pitch):
    lattice = _latticeMap(geom, contents)
    body = "\n".join("            " + line for line in lattice.rstrip("\n").split("\n"))
    return "\n".join(
        [
            f"    {name}:",
            f"        geom: {geom}",
            "        symmetry: full",
            "        lattice pitch:",
            f"            hex: {pitch}",
            "        lattice map: |",
            body,
        ]
    )


def _checkChannel(removed, channel):
    """The graphite removed for the RSC channel must sit around the channel's center."""
    cx = sum(x for x, _ in removed) / len(removed)
    cy = sum(y for _, y in removed) / len(removed)
    if math.hypot(cx - channel[0], cy - channel[1]) > 0.1:
        raise ValueError(f"RSC channel at {channel} but removed graphite centered at ({cx}, {cy})")


HEADER = """\
# MHTGR-350 benchmark core (NEA/NSC/R(2017)4): fresh fuel, 20 C isothermal, rods withdrawn.
# Written by generate.py; edit that, not this.
nuclide flags:
    U235: {burn: false, xs: true}
    U238: {burn: false, xs: true}
    O: {burn: false, xs: true}
    C: {burn: false, xs: true}
    SI: {burn: false, xs: true}
    B10: {burn: false, xs: true}
    B11: {burn: false, xs: true}
    HE4: {burn: false, xs: true}"""

PARTICLES = """\
particles:
    TRISO:
        kernel: {material: UCO, isotopics: MHTGR kernel, od: 0.0425, flags: fuel depletable}
        buffer: {material: Graphite, isotopics: buffer carbon, od: 0.0625}
        inner PyC: {material: Graphite, isotopics: PyC, od: 0.0695}
        SiC: {material: SiC, isotopics: TRISO SiC, od: 0.0765}
        outer PyC: {material: Graphite, isotopics: PyC, od: 0.0845}
    B4C grain:
        # ARMI's B4C expansion is only defined from 25 C; the grains sit at 25 C instead of 20.
        B4C kernel: {material: B4C, isotopics: B4C grains, od: 0.0200, flags: poison, Tinput: 25.0, Thot: 25.0}
        B4C buffer: {material: Graphite, isotopics: LBP buffer, od: 0.0236}
        B4C PyC: {material: Graphite, isotopics: LBP PyC, od: 0.0282}"""

SYSTEMS = """\
systems:
    core:
        grid name: core
        origin:
            x: 0.0
            y: 0.0
            z: 0.0"""


if __name__ == "__main__":
    for name, boron in (
        ("mhtgr350-blueprints.yaml", True),
        ("mhtgr350-blueprints-no-lbp-boron.yaml", False),
    ):
        text = blueprints(lbpBoron=boron)
        if not boron:
            text = text.replace(
                "rods withdrawn.\n",
                "rods withdrawn.\n# Variant: the burnable poison grains hold no boron.\n",
                1,
            )
        (HERE / name).write_text(text)
        print(f"wrote {name} ({len(text.splitlines())} lines)")
