# Validation and independent review

Both notebooks were executed end to end against local frozen snapshots with zero error outputs. The transportation notebook embeds its two research figures and two EDA figures; the assembled integration notebook embeds all four completed research figures plus both EDA figures.

Four transformation/join tests pass: whole-value ZIP validation, unknown severity/conflicting event handling, unmatched-value preservation/duplicate-key rejection, and unknown construction categories propagating to unknown new-construction units. Acceptance checks in `validation_results.json` verify input checksums and row counts, row accounting, aggregate conservation, unique join keys, nullable joined metrics and the primary full-year window.

An independent review checked the code, executed notebooks, exported denominators and documented exclusions against the requirements. No critical or important frozen-snapshot issues were found. It independently confirmed 103,912 known housing counted units and 11,921 borough-located SIRTA records for the main distribution comparison. A minor future-data issue with unknown construction categories was reproduced by a failing test, corrected to preserve uncertainty, and verified by the full passing test suite and reexecuted notebooks. The correction does not change this snapshot's findings because all construction categories here are known.

The four research figures and two EDA figures were visually checked for readable labels, legends, chart scales and missingness notes. The delivered ZIPs were checked for archive integrity and reproduced from separate clean extraction folders. No deployment, GitHub publication or submission is claimed.
