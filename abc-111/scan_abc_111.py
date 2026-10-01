"""Scan Materials Project for 1:1:1 ternaries A(+1) - B(group 14) - C(group 15)."""
from itertools import product

import pandas as pd
from mp_api.client import MPRester

ALKALI = ["Li", "Na", "K", "Rb", "Cs"]
OTHER_MONOCATIONS = ["Cu", "Ag", "Au", "Tl"]  # frequent +1 cations, flagged separately
GROUP14 = ["C", "Si", "Ge", "Sn", "Pb"]
GROUP15 = ["N", "P", "As", "Sb", "Bi"]

FIELDS = [
    "material_id", "formula_pretty", "composition_reduced", "symmetry", "nsites",
    "energy_above_hull", "is_stable", "formation_energy_per_atom",
    "band_gap", "is_gap_direct", "is_metal", "total_magnetization", "density", "theoretical",
]

chemsys = ["-".join(sorted(t)) for t in product(ALKALI + OTHER_MONOCATIONS, GROUP14, GROUP15)]

with MPRester() as mpr:
    docs = mpr.materials.summary.search(chemsys=chemsys, fields=FIELDS)

rows = []
for d in docs:
    comp = d.composition_reduced
    if sorted(comp.values()) != [1, 1, 1]:
        continue
    els = {str(e) for e in comp}
    a = next(e for e in els if e in ALKALI + OTHER_MONOCATIONS)
    rows.append({
        "material_id": str(d.material_id),
        "formula": d.formula_pretty,
        "cation": a,
        "cation_type": "alkali" if a in ALKALI else "other(+1)",
        "group14": next(e for e in els if e in GROUP14),
        "group15": next(e for e in els if e in GROUP15),
        "spacegroup": d.symmetry.symbol,
        "sg_number": d.symmetry.number,
        "crystal_system": str(d.symmetry.crystal_system),
        "nsites": d.nsites,
        "e_above_hull_eV": round(d.energy_above_hull, 4),
        "is_stable": d.is_stable,
        "e_form_eV_atom": round(d.formation_energy_per_atom, 4),
        "band_gap_eV": round(d.band_gap, 3),
        "gap_direct": d.is_gap_direct,
        "is_metal": d.is_metal,
        "magnetization": round(d.total_magnetization or 0, 3),
        "density": round(d.density, 3),
        "theoretical": d.theoretical,
    })

df = pd.DataFrame(rows).sort_values(["cation_type", "formula", "e_above_hull_eV"])
# lowest-energy polymorph per formula
df["ground_state_polymorph"] = ~df.duplicated("formula", keep="first")
df.to_csv("abc_111_monocation_g14_g15.csv", index=False)

print(f"{len(df)} entries, {df.formula.nunique()} distinct formulas, "
      f"{df.is_stable.sum()} on the hull, {(~df.theoretical).sum()} experimentally known (ICSD)")
print(df.groupby("cation_type").formula.nunique().to_string())
