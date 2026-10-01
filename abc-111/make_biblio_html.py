"""Build biblio/index.html (self-contained, sortable/filterable table) from the scan CSV."""
import json
from datetime import date
from pathlib import Path

import pandas as pd

SRC = "abc_111_monocation_g14_g15.csv"
OUT = Path("biblio")
OUT.mkdir(exist_ok=True)

df = pd.read_csv(SRC)
df["cyanide"] = (df.group14 == "C") & (df.group15 == "N")
cols = ["material_id", "formula", "cation", "cation_type", "group14", "group15", "spacegroup",
        "crystal_system", "nsites", "e_above_hull_eV", "is_stable", "e_form_eV_atom", "band_gap_eV",
        "gap_direct", "is_metal", "density", "theoretical", "ground_state_polymorph", "cyanide"]
data = json.loads(df[cols].to_json(orient="records"))
(OUT / SRC).write_text(df.to_csv(index=False))

html = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ABC 1:1:1 — A⁺ / groupe 14 / groupe 15</title>
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--muted:#6b6b66;--line:#e3e2dd;--card:#fff;--accent:#2f5d8a;--ok:#2e7d4f;--warn:#a0631c;--chip:#eef1f4}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe6;--muted:#9a9a93;--line:#30302d;--card:#1e1e1c;--accent:#8db4dc;--ok:#7cc79a;--warn:#e0a35f;--chip:#2a2d31}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding:24px 16px 48px}
main{max-width:1200px;margin:0 auto}
h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--muted);margin:0 0 20px}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:120px}
.stat b{display:block;font-size:20px;font-variant-numeric:tabular-nums}
.stat span{color:var(--muted);font-size:12px}
.controls{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-bottom:12px}
.controls input[type=search]{padding:7px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);min-width:200px;flex:1;max-width:280px}
.controls label{display:flex;gap:6px;align-items:center;color:var(--muted);cursor:pointer}
.controls select{padding:6px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;text-align:left;white-space:nowrap;border-bottom:1px solid var(--line)}
th{position:sticky;top:0;background:var(--card);font-weight:600;font-size:12px;color:var(--muted);cursor:pointer;user-select:none}
th:hover{color:var(--fg)}
th.asc::after{content:" ▲"}th.desc::after{content:" ▼"}
td.num{text-align:right}
tr:last-child td{border-bottom:0}
tr.poly td{color:var(--muted)}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.f{font-weight:600}
.tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:10px;background:var(--chip);color:var(--muted);margin-left:4px}
.stable{color:var(--ok);font-weight:600}
.near{color:var(--warn)}
footer{color:var(--muted);font-size:12px;margin-top:16px}
</style>
</head>
<body>
<main>
<h1>Composés ternaires ABC (1:1:1)</h1>
<p class="sub">A = monocation (alcalin, ou Cu/Ag/Au/Tl) · B = groupe 14 (C, Si, Ge, Sn, Pb) · C = groupe 15 (N, P, As, Sb, Bi) — source : Materials Project, extrait du __DATE__</p>
<div class="stats" id="stats"></div>
<div class="controls">
  <input type="search" id="q" placeholder="Filtrer (formule, élément, groupe d'espace…)">
  <label>Cation <select id="ctype"><option value="">tous</option><option value="alkali">alcalins</option><option value="other(+1)">Cu/Ag/Au/Tl</option></select></label>
  <label><input type="checkbox" id="gs" checked> polymorphe le plus stable seulement</label>
  <label><input type="checkbox" id="nocn"> exclure les cyanures</label>
  <label><input type="checkbox" id="st"> stables seulement (E<sub>hull</sub> = 0)</label>
</div>
<div class="wrap"><table id="t"><thead><tr></tr></thead><tbody></tbody></table></div>
<footer>Clic sur un en-tête pour trier. E<sub>hull</sub> et gap : DFT (GGA/GGA+U/r²SCAN) Materials Project — les gaps sont sous-estimés. « ICSD » = structure connue expérimentalement. Données brutes : <a href="__CSV__">__CSV__</a>.</footer>
</main>
<script>
const DATA = __DATA__;
const COLS = [
  ["formula","Formule"],["material_id","MP id"],["cation","A"],["group14","B"],["group15","C"],
  ["spacegroup","Groupe d'espace"],["crystal_system","Système"],["nsites","Sites",1],
  ["e_above_hull_eV","E_hull (eV/at)",1],["e_form_eV_atom","E_form (eV/at)",1],
  ["band_gap_eV","Gap (eV)",1],["gap_direct","Gap direct"],["density","ρ (g/cm³)",1],["theoretical","Origine"]];
let sortKey="e_above_hull_eV", dir=1;
const $=id=>document.getElementById(id);
const head=document.querySelector("thead tr");
COLS.forEach(([k,l])=>{const th=document.createElement("th");th.textContent=l;th.dataset.k=k;
  th.onclick=()=>{dir = sortKey===k ? -dir : 1; sortKey=k; render();};head.appendChild(th);});
function cell(r,k){
  const v=r[k];
  switch(k){
    case "formula": return `<span class="f">${v}</span>${r.cyanide?'<span class="tag">cyanure</span>':''}${r.ground_state_polymorph?'':'<span class="tag">polymorphe</span>'}`;
    case "material_id": return `<a href="https://next-gen.materialsproject.org/materials/${v}" target="_blank" rel="noopener">${v}</a>`;
    case "e_above_hull_eV": return v===0?'<span class="stable">0 ✓</span>':`<span class="${v<=0.05?'near':''}">${v.toFixed(3)}</span>`;
    case "e_form_eV_atom": return v.toFixed(3);
    case "band_gap_eV": return r.is_metal?'0 <span class="tag">métal</span>':v.toFixed(2);
    case "gap_direct": return r.is_metal?'—':(v?'oui':'non');
    case "density": return v.toFixed(2);
    case "theoretical": return v?'prédit':'<b>ICSD</b>';
    default: return v;
  }
}
function render(){
  const q=$("q").value.trim().toLowerCase(), ct=$("ctype").value;
  let rows=DATA.filter(r=>(!$("gs").checked||r.ground_state_polymorph)&&(!$("nocn").checked||!r.cyanide)
    &&(!$("st").checked||r.is_stable)&&(!ct||r.cation_type===ct)
    &&(!q||[r.formula,r.material_id,r.spacegroup,r.cation,r.group14,r.group15,r.crystal_system].join(" ").toLowerCase().includes(q)));
  rows.sort((a,b)=>{const x=a[sortKey],y=b[sortKey];return (x>y?1:x<y?-1:0)*dir;});
  document.querySelectorAll("th").forEach(th=>th.className=th.dataset.k===sortKey?(dir>0?"asc":"desc"):"");
  document.querySelector("tbody").innerHTML=rows.map(r=>`<tr class="${r.ground_state_polymorph?'':'poly'}">${
    COLS.map(([k,,n])=>`<td class="${n?'num':''}">${cell(r,k)}</td>`).join("")}</tr>`).join("");
  const s=[[rows.length,"entrées affichées"],[new Set(rows.map(r=>r.formula)).size,"formules"],
    [rows.filter(r=>r.is_stable).length,"stables"],[rows.filter(r=>!r.theoretical).length,"connues (ICSD)"]];
  $("stats").innerHTML=s.map(([n,l])=>`<div class="stat"><b>${n}</b><span>${l}</span></div>`).join("");
}
["q","ctype","gs","nocn","st"].forEach(id=>$(id).addEventListener("input",render));
render();
</script>
</body>
</html>
"""
html = (html.replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__CSV__", SRC).replace("__DATE__", date.today().strftime("%d/%m/%Y")))
(OUT / "index.html").write_text(html, encoding="utf-8")
print("written", OUT / "index.html", len(data), "rows")
