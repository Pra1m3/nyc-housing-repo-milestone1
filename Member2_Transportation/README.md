# NYC housing activity and serious-crash investigations

This handoff completes the requested **Member 2 transportation** and **Member 3 integration/notebook** scopes using the two datasets already selected in the supplied Member 1 notebook. Each archive runs independently. All analysis is descriptive; SIRTA is a selected set of DOT-investigated serious crashes, not all crashes or transit provision.

## Start here

1. Extract the ZIP completely. Keep its folders together.
2. Read `REVIEW_AND_DECISIONS.md` and `reports/FINDINGS.md`.
3. Open the executed notebook in `notebooks/`. Its saved outputs can be read without running anything.
4. To rebuild from the bundled snapshots, use Python 3.9+ (tested on Python 3.9.6):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py
python -m unittest discover -s tests -v
```

Windows activation: `.venv\Scripts\activate`.
To rerun the notebook, install JupyterLab (`python -m pip install jupyterlab`), launch `python -m jupyter lab`, and open it. The first cell finds the package root. No API keys, network downloads, absolute machine paths, or hidden local inputs are needed after dependencies are installed. In Colab, upload the full extracted package, set the working directory to it, and open/upload the notebook; uploading only the notebook omits its local data and modules.

## Dataset choice and temporal scope

- Catalog **H2**, [Affordable Housing Production by Building](https://data.cityofnewyork.us/d/hg8x-zxpr): **9,551 rows, 41 columns**, 2014–June 2026 project starts.
- Catalog **T4**, [Serious Injury Response, Tracking & Analysis Program (SIRTA)](https://data.cityofnewyork.us/d/xeqp-qz8h): **13,754 rows, 23 columns**, dated records January 2022–June 2026.

Both exceed the nine-column minimum and appear in the supplied catalog. Both full datasets were downloaded; **no filtered or random sample** was used. A 20,000 API limit exceeds the separately queried source row counts. The JSON API succeeded after CSV-download errors. Frozen CSVs preserve API column names. Retrieval URLs, UTC times, source update timestamps, source counts and SHA-256 checksums are in `data/raw/source_manifest.json`; complete official metadata and field mappings are in `references/`.

The primary key is **borough × project-start/crash calendar year**. Primary charts use **2022–2025**, the common full calendar years. This describes co-occurring activity, not housing completions, occupancy, or the total housing stock. Partial 2026 is retained in tables and excluded from primary analysis. ZIP × year is a secondary view restricted to 2023–2025, with missing/ambiguous geography and unmatched rows explicitly handled.

## Contents

- `pipeline.py`: modular, audited cleaning, aggregations and validated outer joins.
- `charts.py`: four cross-domain research figures and two EDA figures; reusable chart code shared by both handoffs.
- `reproduce.py`: offline rebuild of tables, figures and validation report.
- `validate.py`, `tests/`: source checksums, key uniqueness, aggregation conservation, unknown-value preservation and failure-sensitive transformation checks.
- `data/raw/`: frozen full CSV snapshots and provenance manifest.
- `data/processed/`: clean records, quarantine rows, borough/year and ZIP/year aggregates, integrated data and category-specific tables for the future app.
- `reports/`: EDA profiles, missingness, cleaning/join audits, chart evidence and findings.
- `references/M1_Housing_Cleaning_original.ipynb`: byte-for-byte original supplied notebook; not silently rewritten.
- `CONTRIBUTIONS.csv`, `PROMPTS_USED.md`: assigned responsibilities versus actual work disclosed.

The Member 2 notebook focuses on transportation plus the housing context required for its two cross-domain questions. The Member 3 notebook assembles both domains, integration and all four completed questions. Shared files are intentionally included in each ZIP so neither needs the other to run. Member 3 is the combined base for the next website step; do not copy both shared pipelines over one another.

## Research questions delivered

| Assigned scope | Question | Research figure |
|---|---|---|
| Member 2, Q1 | How does each borough's share of known HPD counted units compare with its share of SIRTA crash records in 2022–2025? | `M2_Q1_borough_shares.png` |
| Member 2, Q2 | Are borough-years with higher new-construction shares associated with more recorded severe injuries/fatalities per SIRTA crash? | `M2_Q2_composition_severity.png` |
| Member 3, Q1 | Do borough-level housing and SIRTA activity follow similar trajectories from 2022 to 2025? | `M3_Q1_indexed_trends.png` |
| Member 3, Q2 | Within matched ZIP-years, are higher counted housing-unit volumes associated with more SIRTA records, and does the pattern differ by borough? | `M3_Q2_zip_association.png` |

## Handoff to Member 4

Use `data/processed/integrated_borough_year.csv`, retaining only `analysis_eligible == True` for the default view. Load ZIP as a string in the secondary table. `housing_borough_year_type.csv` and `transport_borough_year_severity.csv` support domain-category dropdowns; **filter each domain independently, reaggregate, and rejoin on borough/year**. They are not linked project-to-crash records. A housing category filter does not imply the crashes occurred at those buildings. Preserve NA as unknown and recompute ratios from summed numerators/denominators; never average already-aggregated ratios. Unique-building counts cannot be added across years/categories without deduplication. CSV boolean values must be parsed as booleans, not nonempty strings.

No website, deployment or submission email is claimed in these handoffs. The full four-person submission still needs Member 1's two questions/charts, Member 4's two questions/charts, interactive website, deployment, team IDs, GitHub upload and submission email. See `SUBMISSION_GAPS.md`. No files have been published or messages sent.
