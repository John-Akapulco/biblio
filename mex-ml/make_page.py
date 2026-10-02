"""Build index.html (self-contained) from prescreen_mace.csv (copied from MCP/mex/prescreen_ml/) and ../mex-mp/mex_mp.csv."""
import json
from datetime import date
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / "prescreen_mace.csv")
cons = pd.read_csv(HERE / "prescreen_consensus.csv", dtype={"priority": str}).fillna({"priority": ""})
df = df.merge(cons[["candidate", "dE_mix_meV_chgnet", "chgnet_top", "priority"]], on="candidate")
mp = pd.read_csv(HERE.parent / "mex-mp" / "mex_mp.csv").set_index("formula")
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
pretty_sg = lambda sg: "".join(c.translate(SUB) if i and sg[i - 1] == "_" else c for i, c in enumerate(sg)).replace("_", "")
df["spacegroup"] = df.spacegroup.map(pretty_sg)
df["EX"] = df.E + df.X
df["M_type"] = df.M.map(lambda m: "d10" if m in ("Cu", "Ag", "Au") else "alcalin")
df["caveat"] = df.apply(lambda r: "N" if r.X == "N" else ("C" if r.E == "C" else ""), axis=1)
df["dft_mp_meV"] = df.formula.map(lambda f: round(1000 * mp.loc[f, "gs_e_vs_competing_eV"]) if f in mp.index and mp.loc[f, "in_mp"] else None)
df["mp_gs"] = df.formula.map(lambda f: mp.loc[f, "gs_id"] if f in mp.index and mp.loc[f, "in_mp"] else "")
df["rank_mix"] = df.groupby("formula").dE_mix_meV.rank(method="first").astype(int) - 1
cols = ["candidate", "formula", "M", "E", "X", "EX", "M_type", "prototype", "dE_mix_meV", "dE_ml_meV", "rank_mix",
        "spacegroup", "volume_change_pct", "caveat", "dft_mp_meV", "mp_gs", "dE_mix_meV_chgnet", "chgnet_top", "priority"]
rows = json.loads(df[cols].to_json(orient="records", force_ascii=False))

html = r"""<title>MEX : pré-criblage MACE</title>
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--muted:#6b6b66;--faint:#9a9a93;--line:#e3e2dd;--card:#fff;--accent:#2f5d8a;--warn:#a0631c;
 --b0:#0d366b;--b1:#1c5cab;--b2:#3987e5;--b3:#6da7ec;--b4:#9ec5f4;--b5:#cde2fb;--t0:#fff;--t1:#fff;--t2:#fff;--t3:#1d1d1b;--t4:#1d1d1b;--t5:#1d1d1b;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161615;--fg:#ecebe6;--muted:#9a9a93;--faint:#6b6b66;--line:#30302d;--card:#1e1e1c;--accent:#8db4dc;--warn:#e0a35f;
 --b0:#cde2fb;--b1:#9ec5f4;--b2:#6da7ec;--b3:#3987e5;--b4:#256abf;--b5:#184f95;--t0:#161615;--t1:#161615;--t2:#161615;--t3:#fff;--t4:#fff;--t5:#fff;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#161615;--fg:#ecebe6;--muted:#9a9a93;--faint:#6b6b66;--line:#30302d;--card:#1e1e1c;--accent:#8db4dc;--warn:#e0a35f;
 --b0:#cde2fb;--b1:#9ec5f4;--b2:#6da7ec;--b3:#3987e5;--b4:#256abf;--b5:#184f95;--t0:#161615;--t1:#161615;--t2:#161615;--t3:#fff;--t4:#fff;--t5:#fff;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding-inline:16px}
main{max-width:1200px;margin:0 auto;padding-block:24px 48px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 4px}
.sub,.note{color:var(--muted);margin:0 0 16px;max-width:880px}.note{font-size:13px}
.warnbox{border-left:3px solid var(--warn);padding:8px 12px;background:var(--card);border-radius:4px;font-size:13px;max-width:880px;margin:0 0 16px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 8px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:130px}
.stat b{display:block;font-size:22px;font-variant-numeric:tabular-nums}.stat span{color:var(--muted);font-size:12px}
.scroll{overflow-x:auto}
.grid{display:grid;grid-template-columns:52px repeat(11,minmax(62px,1fr));gap:2px;min-width:760px}
.grid .h{font-size:12px;color:var(--muted);display:flex;align-items:flex-end;justify-content:center;padding-bottom:4px;font-weight:600}
.grid .h.cav{color:var(--warn)}
.grid .r{font-size:13px;font-weight:600;display:flex;align-items:center;justify-content:flex-end;padding-right:8px}
.cell{height:48px;border-radius:4px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;
 font-variant-numeric:tabular-nums;font-size:13px;font-weight:600;position:relative}
.cell small{font-size:10px;font-weight:500;opacity:.85}
.cell:hover,.cell:focus-visible{outline:2px solid var(--fg);outline-offset:1px}
.cell.cav{background-image:repeating-linear-gradient(135deg,transparent 0 6px,rgba(128,128,128,.28) 6px 7px)}
.sep{grid-column:1/-1;height:6px}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;margin:10px 0 0;font-size:12px;color:var(--muted);align-items:center}
.legend i{display:inline-block;width:14px;height:14px;border-radius:3px;vertical-align:-3px;margin-right:4px}
.legend i.cav{background:repeating-linear-gradient(135deg,var(--b4) 0 3px,rgba(128,128,128,.5) 3px 4px)}
#tip{position:fixed;pointer-events:none;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px 10px;
 font-size:12px;box-shadow:0 4px 16px rgba(0,0,0,.12);max-width:360px;z-index:10}
#tip b{font-size:13px}#tip .k{color:var(--muted)}#tip table{border-collapse:collapse;margin-top:4px}#tip td{padding:1px 6px 1px 0;border:0}
.controls{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin:8px 0 12px}
.controls input[type=search]{padding:7px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);flex:1;min-width:180px;max-width:280px}
.controls label{display:flex;gap:6px;align-items:center;color:var(--muted);cursor:pointer}
.controls select{padding:6px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table.t{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
.t th,.t td{padding:7px 10px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap}
.t th{font-weight:600;font-size:12px;color:var(--muted);cursor:pointer;user-select:none;background:var(--card)}
.t th:hover{color:var(--fg)}.t th.asc::after{content:" ▲"}.t th.desc::after{content:" ▼"}
.t td.num{text-align:right}.t tbody tr:last-child td{border-bottom:0}
tr.flash{animation:fl 1.6s}@keyframes fl{0%{background:var(--b5)}100%{background:transparent}}
.f{font-weight:600}.tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:10px;border:1px solid var(--line);color:var(--muted)}
.tag.proto{border-color:var(--accent);color:var(--accent)}.tag.cav{border-color:var(--warn);color:var(--warn)}
.neg{font-weight:700}.muted{color:var(--faint)}
footer{color:var(--muted);font-size:12px;margin-top:16px;max-width:880px}
</style>
<main>
<p class="note"><a href="../">← Biblio</a> · voir aussi <a href="../mex-mp/">MEX dans Materials Project</a></p>
<h1>MEX : pré-criblage MACE-MP</h1>
<p class="sub">Les 266 candidats de la campagne <code>mex/</code> du projet MCP (88 compositions × prototypes R3m-MCP,
R3m-oct, P6<sub>3</sub>mc-NaSnP, + états fondamentaux MP), relaxés avec le potentiel universel MACE-MP
(<code>medium-mpa-0</code>) à symétrie fixée. Énergie par rapport à l'enveloppe DFT MP (GGA/GGA+U, MP2020) des phases
concurrentes. Indicatif : sert à ordonner la file DFT, pas à conclure. Calcul du __DATE__.</p>
<div class="warnbox"><b>Fiabilité.</b> Validé à ~10 meV/at contre la DFT pour E = Si, Ge, Sn et X = P, As (AuSiP : −108 contre −109 ;
NaSnP : −47 contre −46 ; écart R3m-MCP − P6<sub>3</sub>mc de NaSnP : 183 contre 182 meV). Colonnes hachurées :
<b>X = N</b> (azotures concurrents mal décrits par le potentiel ; la valeur affichée, contre l'enveloppe DFT, reste correcte pour les états fondamentaux MP)
et <b>E = C</b> (pas de phase C–P dans MP : les MCP sortent à 400–480 meV/at contre ≈ 250–320 en DFT).
Second avis <b>CHGNet</b> : 59 meV/at d'erreur moyenne contre la DFT (MACE : 9), échelle d'énergie comprimée ; il ne sert qu'à confirmer
le classement (✓ : candidat dans le premier quart CHGNet).</div>
<div class="stats" id="stats"></div>

<h2>Meilleur candidat par composition : ΔE vs phases concurrentes (meV/atome)</h2>
<p class="note">Valeur = dE<sub>mix</sub> du prototype le plus bas ; en dessous, ce prototype. Survol : tous les prototypes de la composition ;
clic : lignes du tableau.</p>
<div class="scroll"><div class="grid" id="grid"></div></div>
<div class="legend" id="legend"></div>

<h2>Tous les candidats</h2>
<div class="controls">
  <input type="search" id="q" placeholder="Filtrer (candidat, prototype, groupe d'espace…)">
  <label>M <select id="mt"><option value="">tous</option><option value="alcalin">alcalins</option><option value="d10">Cu, Ag, Au</option></select></label>
  <label>Prototype <select id="pt"><option value="">tous</option><option>R3m-MCP</option><option>R3m-oct</option><option>P63mc-NaSnP</option><option value="mp">état fondamental MP</option></select></label>
  <label><input type="checkbox" id="best"> meilleur par composition</label>
  <label><input type="checkbox" id="ok"> sans réserve (ni N, ni C)</label>
  <label><input type="checkbox" id="prio"> priorité 1 ou 2</label>
</div>
<div class="wrap"><table class="t" id="t"><thead><tr></tr></thead><tbody></tbody></table></div>
<footer>
<p><b>dE<sub>mix</sub></b> = E(candidat, MACE, corrigé MP2020) − E(enveloppe DFT MP des phases concurrentes, sans aucun MEX), à la composition MEX.
<b>dE<sub>ML</sub></b> : même chose contre l'enveloppe des mêmes phases relaxées avec MACE (erreurs systématiques compensées, sauf phases mal décrites).
<b>Priorité</b> (candidats sans réserve, selon MACE) : 1 si dE<sub>mix</sub> &lt; 0, 2 si 0–50 meV/at.
<b>CHGNet</b> : dE<sub>mix</sub> avec CHGNet 0.3.0, même protocole ; ✓ = premier quart du classement CHGNet.
<b>DFT MP</b> : valeur DFT de l'état fondamental MP de la composition (s'il existe), même référence. Négatif : sous l'enveloppe.
<b>ΔV</b> : variation de volume depuis le POSCAR.init (volume DLS).</p>
<p>Données : <a href="prescreen_mace.csv">prescreen_mace.csv</a> · <a href="prescreen_consensus.csv">prescreen_consensus.csv</a> (MACE + CHGNet) · méthode, validation et limites : README de
<code>mex/prescreen_ml/</code> (dépôt MCP) · page générée par <a href="make_page.py">make_page.py</a>.</p>
</footer>
</main>
<div id="tip" hidden></div>
<script>
const DATA=__DATA__;
const METALS=["Li","Na","K","Rb","Cs","Cu","Ag","Au"];
const EX=["CP","CAs","SiN","SiP","SiAs","GeN","GeP","GeAs","SnN","SnP","SnAs"];
const BINS=[[0,"< 0 (sous l'enveloppe)"],[25,"0–25"],[50,"25–50"],[100,"50–100"],[200,"100–200"],[Infinity,"> 200"]];
const bin=v=>v<0?0:BINS.findIndex(([t])=>v<=t);
const $=id=>document.getElementById(id);
const fmt=v=>v===null||v===undefined?'':Math.round(v);
const byComp={};DATA.forEach(r=>(byComp[r.M+r.EX]??=[]).push(r));
Object.values(byComp).forEach(a=>a.sort((x,y)=>x.dE_mix_meV-y.dE_mix_meV));
const link=id=>`<a href="https://next-gen.materialsproject.org/materials/${id}" target="_blank" rel="noopener">${id}</a>`;
const protoName=p=>p.startsWith("mp-")?"MP "+p:p;

const best=Object.values(byComp).map(a=>a[0]);
$("stats").innerHTML=[[DATA.length,"candidats"],[DATA.filter(r=>r.dE_mix_meV<0).length,"sous l'enveloppe DFT"],
 [DATA.filter(r=>r.priority==="1").length+" / "+DATA.filter(r=>r.priority==="2").length,"candidats priorité 1 / 2"],
 [best.filter(r=>r.dE_mix_meV<0&&!r.caveat).length,"compositions < 0, sans réserve"],
 [best.filter(r=>r.dE_mix_meV<0&&!r.caveat&&r.dft_mp_meV===null).length,"dont absentes de MP"],
 [best.filter(r=>r.dE_mix_meV<=50&&!r.caveat).length,"compositions ≤ 50 meV, sans réserve"]]
 .map(([n,l])=>`<div class="stat"><b>${n}</b><span>${l}</span></div>`).join("");

let g=`<div></div>`+EX.map(e=>`<div class="h${/N$|^C/.test(e)?' cav':''}">${e.replace(/^(C|Si|Ge|Sn)/,"$1–")}</div>`).join("");
METALS.forEach((m,i)=>{
  if(i===5)g+=`<div class="sep"></div>`;
  g+=`<div class="r">${m}</div>`;
  EX.forEach(ex=>{const r=byComp[m+ex][0],b=bin(r.dE_mix_meV);
    g+=`<div class="cell${r.caveat?' cav':''}" tabindex="0" data-k="${m+ex}" style="background-color:var(--b${b});color:var(--t${b})">${fmt(r.dE_mix_meV)}<small>${protoName(r.prototype).replace("P63mc-","P6₃mc-")}</small></div>`;});
});
$("grid").innerHTML=g;
$("legend").innerHTML=BINS.map(([,l],i)=>`<span><i style="background:var(--b${i})"></i>${l}</span>`).join("")+
 `<span><i class="cav"></i>avec réserve (X = N ou E = C)</span>`;

const tip=$("tip");
function showTip(el,ev){const a=byComp[el.dataset.k],r=a[0];
  tip.innerHTML=`<b>${r.formula}</b>${r.mp_gs?` · MP ${r.mp_gs} : ${r.dft_mp_meV} meV (DFT)`:' · absente de MP'}<table>`+
   a.map(c=>`<tr><td>${protoName(c.prototype)}</td><td style="text-align:right">${fmt(c.dE_mix_meV)} meV</td><td class="k">CHGNet ${fmt(c.dE_mix_meV_chgnet)}</td><td class="k">${c.spacegroup}</td></tr>`).join("")+`</table>`+
   (r.caveat?`<span class="k">Réserve : ${r.caveat==="N"?"nitrure (azotures concurrents)":"E = C (peu de données C–P)"}</span>`:"");
  tip.hidden=false;const x=Math.min(ev.clientX+14,innerWidth-tip.offsetWidth-8),y=ev.clientY+14+tip.offsetHeight>innerHeight?ev.clientY-tip.offsetHeight-10:ev.clientY+14;
  tip.style.left=x+"px";tip.style.top=y+"px";}
document.querySelectorAll(".cell").forEach(c=>{
  c.addEventListener("mousemove",e=>showTip(c,e));c.addEventListener("mouseleave",()=>tip.hidden=true);
  c.addEventListener("focus",()=>{const b=c.getBoundingClientRect();showTip(c,{clientX:b.right,clientY:b.bottom});});
  c.addEventListener("blur",()=>tip.hidden=true);
  const go=()=>{const r=byComp[c.dataset.k][0];$("q").value=r.formula;$("mt").value="";$("pt").value="";$("best").checked=false;$("ok").checked=false;render();
    const tr=document.querySelector("#t tbody tr");if(!tr)return;tr.scrollIntoView({behavior:"smooth",block:"center"});
    document.querySelectorAll("#t tbody tr").forEach(t=>{t.classList.remove("flash");void t.offsetWidth;t.classList.add("flash");});};
  c.addEventListener("click",go);c.addEventListener("keydown",e=>{if(e.key==="Enter")go();});
});

const COLS=[["candidate","Candidat"],["formula","Formule"],["prototype","Prototype"],["dE_mix_meV","dE_mix (meV/at)",1],
 ["priority","Priorité"],["dE_mix_meV_chgnet","CHGNet (meV/at)",1],["chgnet_top","CHGNet ✓"],["dE_ml_meV","dE_ML (meV/at)",1],["rank_mix","Rang",1],["spacegroup","Groupe (relaxé)"],["volume_change_pct","ΔV (%)",1],
 ["dft_mp_meV","DFT MP (meV/at)",1],["caveat","Réserve"]];
let sortKey="dE_mix_meV",dir=1;
const head=document.querySelector("#t thead tr");
COLS.forEach(([k,l])=>{const th=document.createElement("th");th.textContent=l;th.dataset.k=k;
 th.onclick=()=>{dir=sortKey===k?-dir:1;sortKey=k;render();};head.appendChild(th);});
function cell(r,k){const v=r[k];
 switch(k){
  case "candidate":return `<span class="f">${v}</span>`;
  case "prototype":return v.startsWith("mp-")?link(v):`<span class="tag proto">${v}</span>`;
  case "dE_mix_meV":return `<span class="${v<0?'neg':''}">${fmt(v)}</span>`;
  case "dE_ml_meV":return `<span class="${r.caveat?'muted':''}">${fmt(v)}</span>`;
  case "priority":return v?`<span class="tag proto">${v}</span>`:'';
  case "dE_mix_meV_chgnet":return `<span class="muted">${fmt(v)}</span>`;
  case "chgnet_top":return v?'✓':'';
  case "rank_mix":return v===0?'1<sup>er</sup>':v+1;
  case "volume_change_pct":return v.toFixed(1);
  case "dft_mp_meV":return v===null?'':`${fmt(v)} <span class="muted">(${link(r.mp_gs)})</span>`;
  case "caveat":return v==="N"?'<span class="tag cav">nitrure</span>':v==="C"?'<span class="tag cav">E = C</span>':'';
  default:return v;}}
function render(){
 const q=$("q").value.trim().toLowerCase(),mt=$("mt").value,pt=$("pt").value;
 let rows=DATA.filter(r=>(!mt||r.M_type===mt)&&(!pt||(pt==="mp"?r.prototype.startsWith("mp-"):r.prototype===pt))&&
  (!$("best").checked||r.rank_mix===0)&&(!$("prio").checked||r.priority)&&(!$("ok").checked||!r.caveat)&&
  (!q||[r.candidate,r.formula,r.prototype,r.spacegroup].join(" ").toLowerCase().includes(q)));
 rows.sort((a,b)=>{let x=a[sortKey],y=b[sortKey];if(x===null||x==="")return 1;if(y===null||y==="")return -1;return (x>y?1:x<y?-1:0)*dir;});
 document.querySelectorAll("#t thead th").forEach(th=>th.className=th.dataset.k===sortKey?(dir>0?"asc":"desc"):"");
 document.querySelector("#t tbody").innerHTML=rows.map(r=>`<tr>${COLS.map(([k,,n])=>`<td class="${n?'num':''}">${cell(r,k)}</td>`).join("")}</tr>`).join("");
}
["q","mt","pt","best","ok","prio"].forEach(id=>$(id).addEventListener("input",render));
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
print("written", HERE / "index.html", len(rows), "rows")
