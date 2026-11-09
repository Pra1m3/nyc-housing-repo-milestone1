# Member 4 research findings

## Q1: Do borough-level housing/crash share gaps persist across years?

The heatmap compares each borough's share of known HPD counted units with its share of borough-located SIRTA records within the same calendar year. Gap = SIRTA share minus known housing-unit share, measured in percentage points. Both denominators cover all five boroughs. Main years are 2022–2025; the two records with unknown counted units are excluded from known-unit subtotals, without imputation.

Queens has a positive gap in all four years: +12.99, +12.13, +9.40 and +13.40 percentage points. The Bronx has a negative gap in all four: −10.51, −12.20, −13.86 and −9.24 points. Brooklyn moves from negative gaps to +1.69 in 2025. The differences are persistent in some boroughs, rather than simply a single year's pattern.

These are distribution gaps between two source populations, not injuries among affordable-housing residents. No claim of underinvestment, resident risk or construction causation follows from them. HPD/DOT could use persistent differences to frame local follow-up work with actual exposure data.

## Q2: Is housing activity more concentrated across matched ZIPs than SIRTA activity?

Use 2023–2025 only, following the prior handoff's geographic exclusions. Aggregate each domain by ZIP/year, join one-to-one, discard incomplete counted-unit cells and pool years within each ZIP. For each borough/domain, calculate HHI = sum of squared within-borough ZIP shares. Effective ZIP count = 1/HHI: the number of equally weighted ZIPs that would yield the same concentration. Lower effective count means greater concentration.

Housing counted units are more concentrated than SIRTA records in all five boroughs **within this common observed subset**. Effective housing/SIRTA ZIP counts are Bronx 11.85/17.81, Brooklyn 19.06/28.63, Manhattan 17.90/24.82, Queens 10.89/19.04 and Staten Island 2.48/5.12. There are 306 complete matched ZIP-years, pooled across 131 distinct borough/ZIP combinations. These concentration measures sum over individual source activities, not housing stock, residents or road exposure.

The conclusion is conditional on matched coverage. Missing ZIP codes, unequal ZIP areas/populations, record selection, varying activity over years and only seven observed Staten Island ZIPs limit interpretation. A missing joined cell is never treated as zero. No statistical-significance or causal claim is made.

## Chart delivery

`member4/reports/M4_Q1_share_gap_heatmap.png` and `M4_Q2_effective_zips.png` are notebook/export figures. The website implements both interactively, alongside the four existing Member 2/3 research charts. Every Generate Report action updates all six plots and the associated captions, narrative, metrics and evidence table. A filter can legitimately yield an empty secondary view: ZIP research is limited to 2023–2025, and narrower domain-category filters require new observed matches.
