# Cityscope — NYC Housing & Street Safety

Interactive housing/transport research dashboard for Milestone 1. It uses the full H2 affordable-housing and T4 SIRTA source selections from the original Member 1 work, with the cleaning and integration from the Member 2/3 handoff.

**Live website:** https://cityscope-nyc-housing.vercel.app/
**Existing team repository:** https://github.com/Pra1m3/nyc-housing-repo-milestone1
**Publication scope:** this repository update adds **Member 4's work only**: website source, compact app data, research notebook/figures, tests, deployment documentation and submission draft. The original Member 1 notebook is unchanged. The separate Member 2/3 handoffs are not added by this update. The public Vercel deployment was originally created directly from the local app build.

## Run locally

Requires Node.js 20+ for tests/build and Python 3 for the local file server. No npm package installation or server database is needed.

```bash
cd website
npm test
npm run build
python3 -m http.server 4173 --directory dist
```

Open http://localhost:4173/ . Serve through HTTP rather than double-clicking index.html, because the app loads a local JSON snapshot. The chart library is pinned to Plotly.js 4.1.1 from the official Plotly CDN; Google Fonts is cosmetic, with system-font fallbacks. Internet access is required for Plotly. Source data do not depend on live NYC API availability.

The site includes four dropdowns (borough/year/housing type/crash severity), a text-search mode, Generate Report, six interactive research charts, dynamic story/limits, sources, an evidence table, CSV export and print-report support. Charts provide hover, zoom, pan, reset and PNG export. On mobile the filters move above the report. Text-query errors retain the last valid report. Generate Report locks controls and withholds CSV/print while all charts finish so the export always matches the visible completed report.

Example searches:

- `Brooklyn 2022 new buildings`
- `Queens 2023-2025 preservation fatal crashes`
- `Bronx 2024 nonfatal`

Search supports one borough (including common aliases), a year/range between 2022 and 2026, housing type and crash severity. Unknown terms, unsupported years or conflicting categories show a clear error. Dropdown changes remain pending until generation; Reset restores the default report immediately.

## Dataset meaning and integration

- H2: [Affordable Housing Production by Building](https://data.cityofnewyork.us/d/hg8x-zxpr), original 9,551 rows and 41 columns.
- T4: [SIRTA](https://data.cityofnewyork.us/d/xeqp-qz8h), original 13,754 rows and 23 columns.

Exactly two sources, both in the supplied catalog; neither was sampled. The compact category-aware app data are derived from the prior Member 2/3 cleaning/integration handoff. Source links, field schemas and input hashes are recorded in `member4/reports/data_provenance.json`. Those separate handoffs are not included in this Member 4 commit. The original Member 1 notebook remains unchanged at `notebooks/M1_Housing_Cleaning.ipynb`.

Primary geography is borough × project-start/crash year. Default full years are 2022–2025: 20 matched borough-year cells, 103,912 known counted housing units and 11,921 borough-located SIRTA records. Two contributing housing records have unknown counted units; strict totals remain unknown while known subtotals are labeled separately. Housing includes preservation and project starts, not all new occupied homes. SIRTA is investigated serious crashes, not all NYC crashes or transit access.

2026 stops on June 30. It is available as an explicitly partial single-year view and excluded by default. Secondary ZIP research uses 2023–2025 only: 2022 SIRTA ZIP completeness is only 16.26%. Ambiguous geography, unmatched source cells and incomplete strict housing totals are excluded from the research comparison. There are 306 complete matched ZIP-years. Missing joined records are never zero-imputed.

Housing and crash categories filter **each source independently**, then reaggregate and join. They do not link individual projects and crashes. Citywide share denominators still cover all five boroughs when one borough is displayed. Ratios are recalculated from counts. ZIP charts can correctly be empty for 2022/2026 or a category with no common observed coverage.

## Rebuild app data and research

The prepared website data are already bundled. To regenerate them from the separately supplied Member 3 handoff, extract that ZIP and use its absolute folder path:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r member4/requirements.txt
python member4/prepare_data.py --member3 /path/to/Member3_Integration
python member4/research.py
```

The preparation script generates `website/data/nyc.json` from cleaned housing and SIRTA records, retaining domain/category aggregates and the documented eligible ZIP geography. Compact row schemas, source hashes and source links are in `member4/reports/data_provenance.json` and the JSON metadata. No student IDs or contributor details are deployed; only public-source aggregates and ordinary page assets are uploaded.

Open `notebooks/M4_Website_Research.ipynb` for Member 4's executed questions, charts, calculations, tests, contribution table and prompts. Install JupyterLab separately if you want to rerun interactively. The prior Member 2/3 analysis notebooks remain in their separate handoff ZIPs. Rebuilding the web output after any source/data change requires `cd website && npm run build`.

## Research delivered

| Member | Question / website view | Evidence |
|---|---|---|
| 2 | Borough distributions of known housing units and SIRTA records | Prior notebook + interactive grouped bars |
| 2 | Housing composition versus affected people per SIRTA record | Prior notebook + interactive scatter |
| 3 | Borough housing/SIRTA trajectories | Prior notebook + interactive indexed panels |
| 3 | Matched ZIP-year housing/crash association | Prior notebook + interactive log scatter |
| 4 | Do yearly borough share gaps persist? | M4 notebook + heatmap |
| 4 | Is housing activity more concentrated across matched ZIPs? | M4 notebook + effective-ZIP bars |

Member 4 Q1 finds positive Queens and negative Bronx gaps in every full year. Q2 finds greater housing concentration within the matched ZIP subset in all five boroughs. Definitions, tabular evidence and limitations are in `member4/FINDINGS.md`. These are descriptive comparisons, not resident risk, causal estimates or significance claims.

## Vercel deployment

Current project: `cityscope-nyc-housing`, in the connected Vercel team. It serves the static output directly, with no server functions, API keys, database or paid add-ons introduced. The production deployment is public so the course team can open it without a Vercel login. Only this newly created public-data project was configured for public access.

The current deployment was created from the seven files in `website/dist/`. It did not use a Git commit. The exact deployment ID, source-asset hashes, public URL and verification results are recorded in `member4/DEPLOYMENT.md` and `member4/reports/deployment.json`.

For a future manual deployment after reviewing changes:

1. Run the tests and rebuild locally using the commands above.
2. From the repository root, run `npx vercel link` and select the existing `cityscope-nyc-housing` project in the intended team.
3. Run `npx vercel --prod`. The root `vercel.json` declares the build command and output directory. This direct deployment does not require making a Git commit.
4. Check the production URL, default totals, a category/search report, partial-year warning and CSV export before sharing it.

For future Git-based deployment after reviewing the intended source and branch, publish the reviewed source to the team repository, then connect that repository to this existing Vercel project. Use Framework Preset **Other**, Build Command `cd website && npm run build`, Output Directory `website/dist`, and Install Command `echo No runtime package installation required`. Verify the intended production branch before enabling automatic production deploys. This commit contains Member 4 source only; publish the separate Member 2/3 handoffs when the team authorizes that work.

## Team and actual contributions

| Assigned member | Name | Student ID | Status |
|---|---|---|---|
| 1 | Mohamed Walid | 16002100 | Original housing cleaning supplied; two research questions/charts missing |
| 2 | Omar Aziz | 16007095 | Transportation scope completed in prior assisted handoff |
| 3 | Ahmad Salah | 16008995 | Integration/notebook scope completed in prior assisted handoff |
| 4 | Mohamed Khaled | 16003895 | Website, deployment, two research questions/charts, setup/deployment documentation and submission draft |

Member 4 requested the Member 2/3 preparation with AI assistance. Assigned ownership is not a claim that those members independently authored the resulting work. See `member4/CONTRIBUTIONS.csv`, `member4/PROMPTS_USED.md` and the prior analysis disclosure.

## Remaining submission steps

Member 4's requested implementation and deployment are complete. Before submission, review the work, add Member 1's two missing cross-domain questions/charts to reach the required eight, update the assembled notebook/website accordingly, then publish any remaining approved team source. The prepared `member4/submission_email.eml` has the supplied team names/IDs, official dataset links, existing repository link and actual deployment URL. It is a **draft, not sent**, and must not be sent until the repository contains all reviewed team work and the missing research is added. `member4/SUBMISSION_STATUS.md` records these gates explicitly.
