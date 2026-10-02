# biblio

Tableaux de composés extraits de [Materials Project](https://materialsproject.org), consultables en ligne :
**https://john-akapulco.github.io/biblio/**

| Tableau | Description |
|---|---|
| [`mex-rank/`](mex-rank/) | MEX candidates ranked by ΔE_hull (MACE), CHGNet cross-check, DFT priorities (English; same list as the report of `mex/prescreen_ml/`) |
| [`mex-ml/`](mex-ml/) | Pré-criblage MACE-MP des 266 candidats MEX : ΔE vs phases concurrentes, meilleur prototype par composition |
| [`mex-mp/`](mex-mp/) | Les 88 compositions MEX du projet MCP dans Materials Project : état fondamental, prototype, phases concurrentes, référence d'enveloppe |
| [`abc-111/`](abc-111/) | Ternaires ABC 1:1:1 — A⁺ (alcalin, Cu/Ag/Au/Tl), B groupe 14, C groupe 15 |

Chaque dossier contient la page (`index.html`), les données (`.csv`) et les scripts pour les régénérer
(environnement conda `mp-api`, clé `MP_API_KEY`).
