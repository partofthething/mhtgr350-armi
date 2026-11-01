"""Load the generated blueprints in ARMI and check them against the benchmark specification."""

import collections
import math
import sys

import armi
from armi_openmc.app import OpenMCApp

armi.configure(OpenMCApp())
from armi import init

o = init(fName=sys.argv[1] if len(sys.argv) > 1 else "core-cold.yaml")
core = o.r.core
types = collections.Counter(a.getType() for a in core)
print("assemblies", len(core), dict(types))
fuel = [a for a in core if "fuel" in a.getType() or "RSC" in a.getType()]
print("fuel columns", len(fuel), "core height", core[0].getHeight())
for name in ("fuel", "RSC fuel 0", "RSC fuel 120"):
    b = next(b for b in core.iterBlocks() if b.getType() == name)
    comp = b.getComponentByName("fuel compact")
    kern = b.getComponentByName("fuel compact kernel")
    lbp = b.getComponentByName("LBP compact B4C kernel")
    print(
        f"{name}: compacts {comp.getDimension('mult'):.0f}, coolant {b.getComponentByName('coolant').getDimension('mult'):.0f}, "
        f"small {b.getComponentByName('small coolant').getDimension('mult'):.0f}, LBP {b.getComponentByName('LBP compact').getDimension('mult'):.0f}; "
        f"particles/compact/4.928cm {kern.getDimension('mult') / comp.getDimension('mult') * 4.928:.0f}; "
        f"U mass {b.getHMMass() / 1000:.3f} kg; area check {sum(c.getArea() for c in b) / (math.sqrt(3) / 2 * 36**2):.6f}"
    )
    ch = b.getComponentByName("RSC channel") if "RSC" in name else None
    if ch is not None:
        x, y, _ = ch.spatialLocator.getLocalCoordinates()
        print(f"   RSC channel at ({x:.3f}, {y:.3f})")
hm = sum(b.getHMMass() for b in core.iterBlocks())
print(f"core heavy metal {hm / 1e6:.3f} t")
