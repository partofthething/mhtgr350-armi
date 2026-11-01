"""
Hole and column layouts of the MHTGR-350 benchmark, as text patterns.

Transcribed from the 3D MHTGR mesh input of the INL Virtual Test Bed,
https://github.com/idaholab/virtual_test_bed (htgr/mhtgr/3D_mesh/3D_mhtgr_final.i, by O. Calvin,
J. Ortensi and Y.S. Jung), which follows Figures I.4, I.5 and I.9 of the benchmark specification
NEA/NSC/R(2017)4. Each row is a row of hexagons; ``generate.py`` turns them into ARMI grids.

Element codes: 0 burnable poison (LBP), 1 fuel, 2 large coolant, 3 graphite (the handling hole
region, modeled as graphite), 4 small coolant; in the RSC element, 4 marks graphite removed for the
RSC channel and 5 small coolant.

Core codes: 13 standard fuel column, 33-38 fuel columns with an RSC channel (six orientations),
26 not part of the core (permanent reflector), every other code a replaceable reflector column
(the VTB distinguishes them only to mesh control-rod holes).
"""

STANDARD_ELEMENT = [
    "0 1 2 1 1 2 1 1 2 1 0",
    "1 2 1 1 2 1 1 2 1 1 2 1",
    "2 1 1 2 1 1 2 1 1 2 1 1 2",
    "1 1 2 1 1 2 1 1 2 1 1 2 1 1",
    "1 2 1 1 2 1 1 2 1 1 2 1 1 2 1",
    "2 1 1 2 1 1 2 1 1 2 1 1 2 1 1 2",
    "1 1 2 1 1 2 1 1 2 1 1 2 1 1 2 1 1",
    "1 2 1 1 2 1 1 2 1 1 2 1 1 2 1 1 2 1",
    "2 1 1 2 1 1 2 1 1 4 1 1 2 1 1 2 1 1 2",
    "1 1 2 1 1 2 1 1 4 3 3 4 1 1 2 1 1 2 1 1",
    "0 2 1 1 2 1 1 2 1 3 3 3 1 2 1 1 2 1 1 2 0",
    "1 1 2 1 1 2 1 1 4 3 3 4 1 1 2 1 1 2 1 1",
    "2 1 1 2 1 1 2 1 1 4 1 1 2 1 1 2 1 1 2",
    "1 2 1 1 2 1 1 2 1 1 2 1 1 2 1 1 2 1",
    "1 1 2 1 1 2 1 1 2 1 1 2 1 1 2 1 1",
    "2 1 1 2 1 1 2 1 1 2 1 1 2 1 1 2",
    "1 2 1 1 2 1 1 2 1 1 2 1 1 2 1",
    "1 1 2 1 1 2 1 1 2 1 1 2 1 1",
    "2 1 1 2 1 1 2 1 1 2 1 1 2",
    "1 2 1 1 2 1 1 2 1 1 2 1",
    "0 1 2 1 1 2 1 1 2 1 0",
]

RSC_ELEMENT = [
    "0 1 2 1 1 2 1 1 2 1 0",
    "1 2 1 1 2 1 1 2 1 1 2 1",
    "2 1 1 2 1 1 2 1 1 2 1 1 2",
    "1 1 2 1 1 2 1 1 2 1 1 2 1 1",
    "1 2 1 1 2 1 1 2 1 1 4 4 4 4 1",
    "2 1 1 2 1 1 2 1 1 2 4 4 4 4 4 2",
    "1 1 2 1 1 2 1 1 2 1 4 4 4 4 4 4 1",
    "1 2 1 1 2 1 1 2 1 1 4 4 4 4 4 4 4 1",
    "2 1 1 2 1 1 2 1 1 5 1 4 4 4 4 4 4 1 2",
    "1 1 2 1 1 2 1 1 5 3 3 5 4 4 4 4 4 2 1 1",
    "0 2 1 1 2 1 1 2 1 3 3 3 1 4 4 4 4 1 1 2 0",
    "1 1 2 1 1 2 1 1 5 3 3 5 1 1 2 1 1 2 1 1",
    "2 1 1 2 1 1 2 1 1 5 1 1 2 1 1 2 1 1 2",
    "1 2 1 1 2 1 1 2 1 1 2 1 1 2 1 1 2 1",
    "1 1 2 1 1 2 1 1 2 1 1 2 1 1 2 1 1",
    "2 1 1 2 1 1 2 1 1 2 1 1 2 1 1 2",
    "1 2 1 1 2 1 1 2 1 1 2 1 1 2 1",
    "1 1 2 1 1 2 1 1 2 1 1 2 1 1",
    "2 1 1 2 1 1 2 1 1 2 1 1 2",
    "1 2 1 1 2 1 1 2 1 1 2 1",
    "0 1 2 1 1 2 1 1 2 1 0",
]

CORE = [
    "26 00 00 00 00 00 00 26",
    "00 00 24 10 17 30 23 00 00",
    "00 24 04 13 13 13 13 03 23 00",
    "00 29 13 13 13 13 13 13 13 09 00",
    "00 18 13 13 13 38 38 13 13 13 16 00",
    "00 11 13 13 33 01 27 06 37 13 13 31 00",
    "00 25 13 13 33 32 00 00 28 37 13 13 22 00",
    "26 00 05 13 13 02 00 00 00 05 13 13 02 00 26",
    "00 25 13 13 34 31 00 00 29 36 13 13 22 00",
    "00 28 13 13 34 03 30 04 36 13 13 08 00",
    "00 19 13 13 13 35 35 13 13 13 15 00",
    "00 12 13 13 13 13 13 13 13 32 00",
    "00 20 06 13 13 13 13 01 21 00",
    "00 00 20 27 14 07 21 00 00",
    "26 00 00 00 00 00 00 26",
]
