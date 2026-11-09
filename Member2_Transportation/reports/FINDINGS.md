# Findings from the frozen snapshots

## Member 2 Q1: distribution of known housing units and SIRTA records

Queens accounts for **13.3%** of known HPD counted units and **24.9%** of borough-located SIRTA records in 2022–2025, a **11.68 percentage-point** gap. The Bronx has 31.3% of known housing units and 19.8% of SIRTA records. These are distributions across different source populations. They do not measure crashes experienced by housing residents, population risk, transit access or unmet investment need. The housing denominator is the known subtotal (103,912 units), excluding two unknown counted-unit records, without filling either as zero. Source totals, missing-record counts and chart percentages are exported in `M2_Q1_borough_shares.csv`.

## Member 2 Q2: housing composition and severity

Across **18 complete borough-years**, new-construction share and recorded severely/fatally injured people per SIRTA record have Spearman **rho = 0.422**. This is a modest descriptive positive association in a very small repeated-geography panel. Two of the 20 candidate cells lack complete counted housing totals and are omitted. Severity per record can exceed one; it is not the probability of a crash and not a per-capita risk measure. Do not infer that new construction causes serious crashes.

## Member 3 Q1: activity trajectories

From 2022 to 2025, Queens' counted units increase **120.12%**, while its SIRTA record count increases **13.97%**; Manhattan's corresponding changes are **96.84%** and **2.81%**. These endpoint comparisons have known housing counts. The indexed chart deliberately leaves housing gaps for Bronx 2024 and Brooklyn 2023 because a contributing record is unknown. Each panel has its own y-scale. Staten Island rises from just **33** counted units in 2022 to **2,752** in 2025; its 8,239% change is dominated by a tiny baseline and must be described with the raw counts. Project timing, preservation mix and reporting can all drive different trajectories; the patterns do not establish cause.

## Member 3 Q2: secondary ZIP association

The secondary analysis has **308** eligible matched ZIP-years in 2023–2025; **306** have complete strict counted-unit values for the chart. Their pooled Spearman **rho = 0.196**, a weak descriptive positive association. Within-borough coefficients vary (Brooklyn approximately -0.009, Queens 0.005, Bronx 0.317). Pooling can hide those differences. Staten Island has only ten observations. No significance or causality claim is made; repeated ZIPs/years, reporting selection, unmeasured population/road exposure and missing ZIPs matter. Only observed source cells are included, so absence of a joined record never means zero crashes.

## Practical implication and limits

HPD and DOT could use these differences to select areas for coordinated local review and better data collection. The sources do not identify an individual building's crash exposure or measure transit accessibility. Borough totals are coarse; SIRTA is investigated serious crashes, not the whole NYC crash population; HPD includes preservation and project starts rather than all occupied new homes. 2026 stops in June and is excluded from full-year comparisons. These four completed questions are the Member 2/3 scopes; the team still owes the other four questions/charts and the interactive deployed website.
