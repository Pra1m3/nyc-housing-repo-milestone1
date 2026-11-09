# Output data contract

The complete source field maps are `references/*_schema.csv`. Output files are UTF-8 CSV with headers; empty cells mean unknown. Treat `zip`, `borough`, project/building IDs and collision IDs as text. Treat year and counts as nullable integers, shares/ratios as numbers, flags as booleans, and dates as ISO dates. `data/processed/integrated_borough_year.csv` is the main interface.

| Field | Meaning |
|---|---|
| `borough`, `zip`, `year` | Standardized geographic/calendar keys; housing year is project start, transport year is crash date |
| `housing_records` | Number of source project/building records, including records whose building ID is absent |
| `unique_buildings` | Distinct non-null Building IDs within this group; not additive across groups |
| `total_units` | Sum of all building units in the source records; NA if any contributing record is unknown |
| `counted_units` | Strict sum of HPD All Counted Units; NA if any record is unknown |
| `observed_counted_units` | Sum of known counted-unit values only, not a complete total if missing count > 0 |
| `missing_counted_unit_records` | Number of contributing rows whose counted units are unknown |
| `new_construction_units` | Strict sum of counted units on NEW CONSTRUCTION records; PRESERVATION contributes zero; unknown/unrecognized types propagate NA |
| `new_construction_share` | new construction counted units / strict counted units; zero denominator yields NA |
| `crash_count` | Number of cleaned SIRTA records, not all NYC crashes |
| `severe_injuries`, `fatalities`, `severe_or_fatal` | Strict sums of recorded people affected; people, not number of events |
| `known_severity_records` | Records with both severe-injury and fatality counts known |
| `observed_severe_or_fatal` | Sum over known severity records only |
| `severe_or_fatal_per_crash` | Strict affected-person sum divided by SIRTA record count; can exceed one |
| `join_status` | `both`, `left_only` (housing only), or `right_only` (transport only) |
| `analysis_eligible` | Both sources observed in 2022–2025; ZIP table additionally uses 2023–2025 and rejects ambiguous/mismatched geography. Charts may also require complete metric values. |
| `borough_mismatch` | ZIP table only: sources disagree on a uniquely mapped borough; exclude such rows |
| `source_row` | Original CSV row number including the header, allowing trace-back |
| `severity` | FATAL if fatalities > 0; SEVERE_NONFATAL if known zero fatalities and severe injuries > 0; otherwise known-zero or UNKNOWN |
| `construction_type` | Standardized HPD Reporting Construction Type: NEW CONSTRUCTION or PRESERVATION in this snapshot |
| `units_outlier`, `severity_outlier` | IQR flags retained for review, not exclusion criteria |
| `exclusion_reason` | Semicolon-separated reasons in quarantine tables |

Output tables: `housing_clean`, `transport_clean` retain cleaned full-source columns plus flags; `*_quarantine` preserve excluded records and reasons; `*_borough_year`, `*_zip_year` are domain aggregates; `integrated_*` are outer joins; `housing_borough_year_type`, `transport_borough_year_severity` support app category selection. `reports/geographic_coverage.csv` reports post-cleaning completeness, so its denominators differ from raw-source missingness.
