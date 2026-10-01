"""Build index.html (self-contained) from mex_mp.json."""
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "mex_mp.json").read_text())
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
pretty_sg = lambda sg: "".join(c.translate(SUB) if i and sg[i - 1] == "_" else c for i, c in enumerate(sg)).replace("_", "")
for r in rows:
    r["gs_spacegroup"] = pretty_sg(r["gs_spacegroup"])
    for p in r["polymorphs"]:
        p["spacegroup"] = pretty_sg(p["spacegroup"])

html = r"""<title>MEX dans Materials Project</title>
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--muted:#6b6b66;--faint:#9a9a93;--line:#e3e2dd;--card:#fff;--accent:#2f5d8a;
 --b0:#0d366b;--b1:#1c5cab;--b2:#3987e5;--b3:#6da7ec;--b4:#9ec5f4;--b5:#cde2fb;--t0:#fff;--t1:#fff;--t2:#fff;--t3:#1d1d1b;--t4:#1d1d1b;--t5:#1d1d1b;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161615;--fg:#ecebe6;--muted:#9a9a93;--faint:#6b6b66;--line:#30302d;--card:#1e1e1c;--accent:#8db4dc;
 --b0:#cde2fb;--b1:#9ec5f4;--b2:#6da7ec;--b3:#3987e5;--b4:#256abf;--b5:#184f95;--t0:#161615;--t1:#161615;--t2:#161615;--t3:#fff;--t4:#fff;--t5:#fff;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#161615;--fg:#ecebe6;--muted:#9a9a93;--faint:#6b6b66;--line:#30302d;--card:#1e1e1c;--accent:#8db4dc;
 --b0:#cde2fb;--b1:#9ec5f4;--b2:#6da7ec;--b3:#3987e5;--b4:#256abf;--b5:#184f95;--t0:#161615;--t1:#161615;--t2:#161615;--t3:#fff;--t4:#fff;--t5:#fff;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding-inline:16px}
main{max-width:1200px;margin:0 auto;padding-block:24px 48px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 4px}
.sub,.note{color:var(--muted);margin:0 0 16px;max-width:860px}
.note{font-size:13px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 8px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:130px}
.stat b{display:block;font-size:22px;font-variant-numeric:tabular-nums}.stat span{color:var(--muted);font-size:12px}
.scroll{overflow-x:auto}
.grid{display:grid;grid-template-columns:52px repeat(11,minmax(58px,1fr));gap:2px;min-width:720px}
.grid .h{font-size:12px;color:var(--muted);display:flex;align-items:flex-end;justify-content:center;padding-bottom:4px;font-weight:600}
.grid .r{font-size:13px;font-weight:600;display:flex;align-items:center;justify-content:flex-end;padding-right:8px}
.cell{height:46px;border-radius:4px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;
 font-variant-numeric:tabular-nums;font-size:13px;font-weight:600;position:relative;outline-offset:1px}
.cell small{font-size:10px;font-weight:500;opacity:.85}
.cell:hover,.cell:focus-visible{outline:2px solid var(--fg)}
.cell.absent{background:repeating-linear-gradient(45deg,transparent 0 5px,var(--line) 5px 6px);color:var(--faint);border:1px solid var(--line)}
.cell .icsd{position:absolute;top:3px;right:4px;width:7px;height:7px;border-radius:50%;background:currentColor}
.sep{grid-column:1/-1;height:6px}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;margin:10px 0 0;font-size:12px;color:var(--muted);align-items:center}
.legend i{display:inline-block;width:14px;height:14px;border-radius:3px;vertical-align:-3px;margin-right:4px}
.legend i.absent{background:repeating-linear-gradient(45deg,transparent 0 3px,var(--line) 3px 4px);border:1px solid var(--line)}
.legend .dot{width:7px;height:7px;border-radius:50%;background:var(--fg);display:inline-block;margin-right:4px}
#tip{position:fixed;pointer-events:none;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px 10px;
 font-size:12px;box-shadow:0 4px 16px rgba(0,0,0,.12);max-width:340px;z-index:10}
#tip b{font-size:13px}#tip .k{color:var(--muted)}
.controls{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin:8px 0 12px}
.controls input[type=search]{padding:7px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);flex:1;min-width:180px;max-width:280px}
.controls label{display:flex;gap:6px;align-items:center;color:var(--muted);cursor:pointer}
.controls select{padding:6px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:600;font-size:12px;color:var(--muted);cursor:pointer;user-select:none;white-space:nowrap;background:var(--card)}
th:hover{color:var(--fg)}th.asc::after{content:" ▲"}th.desc::after{content:" ▼"}
td{white-space:nowrap}td.num{text-align:right}td.comp{white-space:normal;min-width:260px;color:var(--muted);font-size:13px}
tbody tr:last-child td{border-bottom:0}
tr.flash{animation:fl 1.6s}@keyframes fl{0%{background:var(--b5)}100%{background:transparent}}
.f{font-weight:600}.tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:10px;border:1px solid var(--line);color:var(--muted)}
.tag.proto{border-color:var(--accent);color:var(--accent)}
.muted{color:var(--faint)}
details summary{cursor:pointer;color:var(--accent)}details table{margin-top:6px;font-size:12px}details td,details th{padding:3px 8px;border:0}
footer{color:var(--muted);font-size:12px;margin-top:16px}
</style>
<main>
<p class="note"><a href="../">← Biblio</a></p>
<h1>Compositions MEX dans Materials Project</h1>
<p class="sub">Les 88 compositions de la campagne <code>mex/</code> du projet MCP : M = Li, Na, K, Rb, Cs, Cu, Ag, Au ;
E = C, Si, Ge, Sn ; X = N, P, As (sans MCN). Ce que Materials Project en sait déjà, et la référence
d'enveloppe convexe à laquelle chaque candidat DFT sera comparé. Extrait du __DATE__.</p>
<div class="stats" id="stats"></div>

<h2>E<sub>hull</sub> de l'état fondamental MP (meV/atome)</h2>
<p class="note">Survol : détails ; clic : ligne correspondante du tableau. Le point en haut à droite signale un polymorphe
connu expérimentalement (ICSD). Case hachurée : composition absente de MP.</p>
<div class="scroll"><div class="grid" id="grid"></div></div>
<div class="legend" id="legend"></div>

<h2>Tableau</h2>
<div class="controls">
  <input type="search" id="q" placeholder="Filtrer (formule, phase concurrente, groupe d'espace…)">
  <label>M <select id="mt"><option value="">tous</option><option value="alcalin">alcalins</option><option value="d10">Cu, Ag, Au</option></select></label>
  <label><input type="checkbox" id="inmp"> présentes dans MP seulement</label>
</div>
<div class="wrap"><table id="t"><thead><tr></tr></thead><tbody></tbody></table></div>
<footer>
<p><b>Référence</b> (identique à <code>mex/wf/tasks.py</code>) : entrées MP de type GGA/GGA+U avec corrections MP2020, système M–E–X complet.
<b>E<sub>hull</sub></b> : distance de l'état fondamental MP à l'enveloppe de toutes ces entrées.
<b>Phases concurrentes</b> : décomposition de la composition MEX sur l'enveloppe construite <i>sans</i> aucun polymorphe MEX ;
<b>E<sub>réf</sub></b> est l'énergie de cette enveloppe à la composition MEX (eV/atome, MP2020) — un candidat DFT d'énergie inférieure est stable.
<b>ΔE vs concurrentes</b> = E(état fondamental MP) − E<sub>réf</sub> (négatif : stable).
<b>Prototype</b> : correspondance (StructureMatcher, espèces substituées) avec les prototypes de <code>mex/</code> : R3m-MCP (AuSiP, mp-1207095),
P6<sub>3</sub>mc-NaSnP (mp-29529 ; P6<sub>3</sub>mc-KSnAs, mp-3481, en est l'image miroir, identique pour StructureMatcher).
R3m-oct n'a pas d'équivalent dans MP.</p>
<p>Données : <a href="mex_mp.csv">mex_mp.csv</a> · <a href="mex_mp.json">mex_mp.json</a> (avec tous les polymorphes) ·
scripts <a href="extract_mex_mp.py">extract_mex_mp.py</a>, <a href="make_page.py">make_page.py</a>.</p>
</footer>
</main>
<div id="tip" hidden></div>
<script>
const DATA=__DATA__;
const METALS=["Li","Na","K","Rb","Cs","Cu","Ag","Au"];
const EX=["CP","CAs","SiN","SiP","SiAs","GeN","GeP","GeAs","SnN","SnP","SnAs"];
const BINS=[[0,"stable (0)"],[25,"≤ 25"],[50,"25–50"],[100,"50–100"],[200,"100–200"],[Infinity,"> 200"]];
const bin=v=>v<=0.0005?0:BINS.findIndex(([t])=>v*1000<=t);
const mev=v=>Math.round(v*1000);
const $=id=>document.getElementById(id);
const byKey=Object.fromEntries(DATA.map(r=>[r.M+r.EX,r]));
const link=id=>`<a href="https://next-gen.materialsproject.org/materials/${id}" target="_blank" rel="noopener">${id}</a>`;

// stats
const inmp=DATA.filter(r=>r.in_mp);
$("stats").innerHTML=[[DATA.length,"compositions"],[inmp.length,"présentes dans MP"],
 [inmp.filter(r=>r.gs_e_above_hull_eV===0).length,"stables (E_hull = 0)"],
 [DATA.filter(r=>r.any_icsd).length,"avec polymorphe ICSD"],
 [inmp.filter(r=>r.gs_prototype).length,"état fondamental = prototype mex"]]
 .map(([n,l])=>`<div class="stat"><b>${n}</b><span>${l}</span></div>`).join("");

// grid
let g=`<div></div>`+EX.map(e=>`<div class="h">${e.replace(/^(C|Si|Ge|Sn)/,"$1–")}</div>`).join("");
METALS.forEach((m,i)=>{
  if(i===5) g+=`<div class="sep"></div>`;
  g+=`<div class="r">${m}</div>`;
  EX.forEach(ex=>{const r=byKey[m+ex];
    if(!r.in_mp){g+=`<div class="cell absent" tabindex="0" data-k="${m+ex}">—</div>`;return;}
    const b=bin(r.gs_e_above_hull_eV);
    g+=`<div class="cell" tabindex="0" data-k="${m+ex}" style="background:var(--b${b});color:var(--t${b})">${mev(r.gs_e_above_hull_eV)}`+
       `<small>${r.gs_spacegroup}</small>${r.any_icsd?'<span class="icsd"></span>':''}</div>`;});
});
$("grid").innerHTML=g;
$("legend").innerHTML=BINS.map(([,l],i)=>`<span><i style="background:var(--b${i})"></i>${l}</span>`).join("")+
 `<span><i class="absent"></i>absente de MP</span><span><span class="dot"></span>polymorphe ICSD</span>`;

const tip=$("tip");
function showTip(el,ev){const r=byKey[el.dataset.k];
  tip.innerHTML=`<b>${r.formula}</b><br>`+(r.in_mp?
   `<span class="k">État fondamental MP :</span> ${r.gs_id} (${r.gs_spacegroup})${r.gs_prototype?` — ${r.gs_prototype}`:""}<br>`+
   `<span class="k">E_hull :</span> ${mev(r.gs_e_above_hull_eV)} meV/at · <span class="k">polymorphes :</span> ${r.n_polymorphs}${r.any_icsd?" · ICSD":""}<br>`
   :`<span class="k">Absente de Materials Project</span><br>`)+
   `<span class="k">Phases concurrentes :</span> ${r.competing_phases.replace(/ \(mp-[0-9]+\)/g,"")}`;
  tip.hidden=false;const x=Math.min(ev.clientX+14,innerWidth-tip.offsetWidth-8),y=ev.clientY+14+tip.offsetHeight>innerHeight?ev.clientY-tip.offsetHeight-10:ev.clientY+14;
  tip.style.left=x+"px";tip.style.top=y+"px";}
document.querySelectorAll(".cell").forEach(c=>{
  c.addEventListener("mousemove",e=>showTip(c,e));c.addEventListener("mouseleave",()=>tip.hidden=true);
  c.addEventListener("focus",()=>{const b=c.getBoundingClientRect();showTip(c,{clientX:b.right,clientY:b.bottom});});
  c.addEventListener("blur",()=>tip.hidden=true);
  const go=()=>{$("q").value="";$("mt").value="";$("inmp").checked=false;render();
    const tr=document.getElementById("row-"+c.dataset.k);tr.scrollIntoView({behavior:"smooth",block:"center"});
    tr.classList.remove("flash");void tr.offsetWidth;tr.classList.add("flash");};
  c.addEventListener("click",go);c.addEventListener("keydown",e=>{if(e.key==="Enter")go();});
});

// table
const COLS=[["formula","Formule"],["M","M"],["EX","EX"],["gs_id","État fond. MP"],["gs_spacegroup","Groupe"],
 ["gs_prototype","Prototype mex"],["gs_e_above_hull_eV","E_hull (meV/at)",1],["gs_e_vs_competing_eV","ΔE vs concurrentes (meV/at)",1],
 ["any_icsd","ICSD"],["competing_phases","Phases concurrentes"],["hull_energy_ref_eV_atom","E_réf (eV/at)",1],["n_polymorphs","Polymorphes",1]];
let sortKey=null,dir=1;
const head=document.querySelector("thead tr");
COLS.forEach(([k,l])=>{const th=document.createElement("th");th.textContent=l;th.dataset.k=k;
 th.onclick=()=>{dir=sortKey===k?-dir:1;sortKey=k;render();};head.appendChild(th);});
function cell(r,k){const v=r[k];
 switch(k){
  case "formula":return `<span class="f">${v}</span>`;
  case "gs_id":return v?link(v):'<span class="muted">absente</span>';
  case "gs_prototype":return v?`<span class="tag proto">${v}</span>`:'';
  case "gs_e_above_hull_eV":case "gs_e_vs_competing_eV":return v===null?'':mev(v);
  case "any_icsd":return v?'<b>ICSD</b>':'';
  case "competing_phases":return v.replace(/\((mp-[0-9]+)\)/g,(_,id)=>`(${link(id)})`);
  case "hull_energy_ref_eV_atom":return v.toFixed(4);
  case "n_polymorphs":return v>1?`<details><summary>${v}</summary><table>${r.polymorphs.map(p=>
    `<tr><td>${link(p.material_id)}</td><td>${p.spacegroup}</td><td class="num">${mev(p.e_above_hull_eV)} meV</td><td>${p.icsd?"ICSD":""}</td><td>${p.prototype}</td></tr>`).join("")}</table></details>`:(v||'');
  default:return v;}}
function render(){
 const q=$("q").value.trim().toLowerCase(),mt=$("mt").value;
 let rows=DATA.filter(r=>(!mt||r.M_type===mt)&&(!$("inmp").checked||r.in_mp)&&
  (!q||[r.formula,r.gs_id,r.gs_spacegroup,r.gs_prototype,r.competing_phases].join(" ").toLowerCase().includes(q)));
 if(sortKey)rows.sort((a,b)=>{let x=a[sortKey],y=b[sortKey];if(x===null||x==="")return 1;if(y===null||y==="")return -1;return (x>y?1:x<y?-1:0)*dir;});
 document.querySelectorAll("thead th").forEach(th=>th.className=th.dataset.k===sortKey?(dir>0?"asc":"desc"):"");
 document.querySelector("#t tbody").innerHTML=rows.map(r=>`<tr id="row-${r.M+r.EX}">${COLS.map(([k,,n])=>
  `<td class="${n?'num':''}${k==='competing_phases'?' comp':''}">${cell(r,k)}</td>`).join("")}</tr>`).join("");
}
["q","mt","inmp"].forEach(id=>$(id).addEventListener("input",render));
render();
</script>
"""
page = ("<!doctype html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        + html.replace("<main>", "</head>\n<body>\n<main>", 1)
              .replace("__DATA__", json.dumps(rows, ensure_ascii=False))
              .replace("__DATE__", date.today().strftime("%d/%m/%Y"))
        + "</body>\n</html>\n")
(HERE / "index.html").write_text(page, encoding="utf-8")
print("written", HERE / "index.html")
