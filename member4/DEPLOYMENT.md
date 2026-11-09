# Verified deployment

- URL: https://cityscope-nyc-housing.vercel.app/
- Provider: Vercel, project `cityscope-nyc-housing`
- Environment: production
- Status: READY
- Deployment ID: `dpl_9yMyhSmNZeL9EufyWA9RKdKj2sUL`
- Method: seven local static build files, deployed directly; no Git commit/push
- Source state at the initial deployment: uncommitted local `member4-cityscope` branch; original base commit `f2260896a4bd37dadb5f28046de97d77708146e8` unchanged
- Public access: verified without login; public-source aggregate data only

All seven live assets were fetched without credentials and matched against the local build byte-for-byte using SHA-256. The website data checksum and per-file evidence are in `reports/deployment.json`. The supplied student IDs are absent from deployed assets. The live browser showed the expected default 103,912 known units, 11,921 SIRTA records, 20 borough-year cells and 306 complete secondary ZIP-year cells.

Live search `Brooklyn 2022 new buildings nonfatal crashes` generated 5,362 known units, 809 SIRTA records and one matched borough-year cell. Reset restored defaults. No live-origin console errors were observed during these checks. Responsive layout was checked at 1440 × 1000 and 390 × 844; the browser viewport was then restored. Desktop and mobile previews are included in `reports/`.

For repeat deployment, use the root README's Vercel section. For verification only, rebuild the same unchanged source and run `python member4/verify_deployment.py`. This read-only checker does not publish or commit. Changes to the app require a new deployment before its asset hashes can match.

The user subsequently authorized publishing Member 4 source to the existing GitHub repository. This update excludes the separate Member 2/3 handoffs; a deployed website does not mean the full milestone submission is ready. See `SUBMISSION_STATUS.md` before using the prepared email draft.
