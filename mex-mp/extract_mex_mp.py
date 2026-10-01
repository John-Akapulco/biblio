"""State of Materials Project for the 88 MEX compositions of the MCP project (mex/ campaign).

Same reference as mex/wf/tasks.py: MP entries GGA/GGA+U (thermo type GGA_GGA+U, MP2020 corrections).
For each composition M E X (M = Li..Cs, Cu, Ag, Au ; E = C, Si, Ge, Sn ; X = N, P, As ; no MCN):
  - MP polymorphs of MEX, their E_hull and the ground state (GS), ICSD or not;
  - prototype of the GS among the mex prototypes (R3m-MCP, P63mc-NaSnP, P63mc-KSnAs), if any;
  - competing phases: hull of the M-E-X system *without* any MEX polymorph, its decomposition at MEX
    and its energy (the reference every DFT candidate of mex/ is compared to).
Writes mex_mp.csv and mex_mp.json next to this script.
"""
import json
from pathlib import Path

import pandas as pd
from mp_api.client import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.core import Composition

OUT = Path(__file__).resolve().parent
METALS = ["Li", "Na", "K", "Rb", "Cs", "Cu", "Ag", "Au"]
PAIRS = [(e, x) for e in ("C", "Si", "Ge", "Sn") for x in ("N", "P", "As") if (e, x) != ("C", "N")]
PROTOTYPES = {"R3m-MCP": ("mp-1207095", {"Au": "M", "Si": "E", "P": "X"}),
              "P63mc-NaSnP": ("mp-29529", {"Na": "M", "Sn": "E", "P": "X"}),
              "P63mc-KSnAs": ("mp-3481", {"K": "M", "Sn": "E", "As": "X"})}


def mp_id(entry):
    return entry.data.get("material_id") or "-".join(str(entry.entry_id).split("-")[:2])


with MPRester() as mpr:
    proto = {name: (mpr.get_structure_by_material_id(mid), roles) for name, (mid, roles) in PROTOTYPES.items()}
    formulas = [Composition(f"{m}{e}{x}").reduced_formula for m in METALS for e, x in PAIRS]
    summ = {str(d.material_id): d for d in mpr.materials.summary.search(
        formula=formulas, fields=["material_id", "symmetry", "theoretical", "nsites"])}
    entries = {}
    for m in METALS:
        for e, x in PAIRS:
            entries[(m, e, x)] = mpr.get_entries_in_chemsys(
                [m, e, x], additional_criteria={"thermo_types": ["GGA_GGA+U"]})
            print(f"{m}-{e}-{x}: {len(entries[(m, e, x)])} entries", flush=True)

sm = StructureMatcher(primitive_cell=True, scale=True, attempt_supercell=False)


def prototype_of(structure, m, e, x):
    for name, (ref, roles) in proto.items():
        sub = {k: {"M": m, "E": e, "X": x}[v] for k, v in roles.items()}
        r = ref.copy()
        r.replace_species(sub)
        if sm.fit(r, structure):
            return name
    return ""


rows = []
for (m, e, x), ents in entries.items():
    comp = Composition(f"{m}{e}{x}")
    formula = comp.reduced_formula
    pd_all = PhaseDiagram(ents)
    mex = [en for en in ents if en.composition.reduced_formula == formula]
    others = [en for en in ents if en.composition.reduced_formula != formula]
    pd_ref = PhaseDiagram(others)
    decomp = pd_ref.get_decomposition(comp)
    e_ref = pd_ref.get_hull_energy_per_atom(comp)
    competing = " + ".join(f"{en.composition.reduced_formula} ({mp_id(en)})"
                           for en in sorted(decomp, key=lambda en: -decomp[en]))
    polys = []
    for en in mex:
        mid = mp_id(en)
        s = summ.get(mid)
        polys.append({
            "material_id": mid,
            "spacegroup": s.symmetry.symbol if s else "",
            "nsites": len(en.structure),
            "e_above_hull_eV": round(pd_all.get_e_above_hull(en), 4),
            # < 0 : MEX is below the hull of its competing phases (stable), > 0 : above it
            "e_vs_competing_eV": round(en.energy_per_atom - e_ref, 4),
            "icsd": bool(s is not None and not s.theoretical),
            "prototype": prototype_of(en.structure, m, e, x),
        })
    polys.sort(key=lambda p: p["e_above_hull_eV"])
    gs = polys[0] if polys else {}
    rows.append({
        "formula": formula, "M": m, "E": e, "X": x, "EX": f"{e}{x}",
        "M_type": "alcalin" if m in ("Li", "Na", "K", "Rb", "Cs") else "d10",
        "in_mp": bool(polys), "n_polymorphs": len(polys),
        "gs_id": gs.get("material_id", ""), "gs_spacegroup": gs.get("spacegroup", ""),
        "gs_prototype": gs.get("prototype", ""), "gs_icsd": gs.get("icsd", False),
        "gs_e_above_hull_eV": gs.get("e_above_hull_eV"),
        "gs_e_vs_competing_eV": gs.get("e_vs_competing_eV"),
        "any_icsd": any(p["icsd"] for p in polys),
        "competing_phases": competing,
        "hull_energy_ref_eV_atom": round(e_ref, 4),
        "polymorphs": polys,
    })

(OUT / "mex_mp.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
pd.DataFrame([{k: v for k, v in r.items() if k != "polymorphs"} for r in rows]).to_csv(OUT / "mex_mp.csv", index=False)
n = sum(r["in_mp"] for r in rows)
print(f"{len(rows)} compositions, {n} in MP, "
      f"{sum(r['gs_e_above_hull_eV'] == 0 for r in rows if r['in_mp'])} on the GGA hull, "
      f"{sum(r['any_icsd'] for r in rows)} with an ICSD polymorph")
