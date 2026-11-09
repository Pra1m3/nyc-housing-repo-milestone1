# Verification record

## Automated checks

- Ten Node tests pass: search interpretation, unsupported/conflicting searches, independent source-category filtering and citywide denominators, missing-unit and unmatched-domain preservation, effective-ZIP concentration, default source totals/ZIP coverage, all 270 offered single-year dropdown combinations, export/render transaction completion, failed-render export safety and form-control/native-method separation.
- JavaScript syntax check and production static build pass.
- The Member 4 notebook executed all code cells with zero errors; both research figures are embedded.
- Independent Python research matches the default JavaScript totals, 306 complete ZIP-year cells and effective-ZIP results.
- Browser-downloaded default CSV has 20 rows, sums to 103,912 known units and 11,921 SIRTA records, and retains two unknown strict housing totals.
- Vercel reported READY. All seven deployed app assets returned successful unauthenticated responses and matched the local build by SHA-256; no student IDs occur in them.

## Browser checks

- Default report loads all six interactive views with expected counts.
- Changing dropdowns leaves the active report unchanged until Generate Report.
- Brooklyn / 2022 / new construction produces 5,362 units and 885 SIRTA records.
- Text search Queens / 2023–2025 / preservation / fatal produces 4,002 units and 201 SIRTA records.
- An unrecognized London search shows the error and preserves the previous report.
- Selecting 2026 displays the through-June warning; it yields 11,585 known units, 1,332 SIRTA records, five matched borough-years and an empty secondary view.
- Reset restores the default full-year view.
- Desktop (1440 × 1000) and mobile (390 × 844) controls/layout render without horizontal page overflow.
- CSV export was downloaded and its values independently checked.
- The deployed URL was checked in the browser, including a new-building/nonfatal search and Reset. No live-origin console errors were observed.

## Review fixes

Browser QA exposed a Reset button ID shadowing the native form reset method. Its control was renamed and a failing regression test was made to pass. Independent review found a render/export timing issue: CSV/print could reference a prior active report while a new chart render was pending. A tested report-session controller now serializes generation, locks controls, hides exportable state during rendering and clears it after a failed render. All chart promises settle before success/failure handling.

Print-report wiring and print styles are included; no physical printer action was performed. Hover/zoom/pan/PNG export are supplied by the pinned Plotly library. This record does not claim that Member 1's missing two research contributions are present or that the email was sent.
