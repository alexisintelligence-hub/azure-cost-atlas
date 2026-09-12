# Validation status

## Power BI Desktop attempt — 2026-09-12: BLOCKED

The installed-app inventory identified Power BI Desktop with no running window. The attempt to launch a new blank instance through Windows Computer Use was rejected with: `Computer Use was not approved to use Power BI Desktop`. No alternate launch or control mechanism was used to bypass that restriction.

This is an access blocker, not an observed model or DAX failure. Power BI Desktop version could not be verified. No CSV import, model construction, measure evaluation, visual smoke, PBIX save, close or clean reopen was performed. No PBIX or application screenshot was published during that attempt. Subsequently added [redacted historical images](visual-references.md) do not validate this synthetic edition. The offline results below do not establish a Desktop PASS.

All requested Desktop scenarios remain **NOT RUN**: separate Billing/Effective/List; MTD; LFM; delayed-snapshot month rollover; manual historical month; missing history as BLANK; covered zero activity as zero; single/no/multiple snapshot selection; resource filtering; signed credits; expected-results equality; and persistence of relationships, measures, filters, values and selected snapshot after clean reopen.

Resume only after Computer Use access to Power BI Desktop is enabled. Use a new local synthetic-only report with the five committed CSVs, follow the model and M/DAX build instructions, record the actual Desktop version and per-scenario results, then save and clean reopen before updating any PASS claim. The PR remains a draft; main is unchanged.

## Executed locally on 2026-09-12

Python standard-library runtime with in-memory SQLite executed the actual committed aggregation and reconciliation SQL. All **29 tests passed**. The fixture contains 476 source rows and 357 analytical rows across two synthetic snapshots. Reconciliation returned zero daily-grain discrepancies. No enterprise source was contacted.

```sh
python src/atlas.py
python -m unittest discover -s tests -v
python scripts/check_publication.py
```

The tests check fixed expected MTD values for three independent bases; snapshot isolation; MTD and LFM at month rollover; historical and future reference months; leap-year comparison clamping; missing history; zero-activity received days; missing coverage; resource filtering; retained negative credits; duplicate keys; unknown dimensions; null and fractional-cent values; unit mismatch; currency isolation; and corruption that removes, duplicates or changes analytical rows. Offsetting errors cannot hide behind a correct grand total.

The publication checker verifies the exact allowed file set, rejects unapproved binary/private artifact extensions and common secret-like text strings, checks exact hashes of the two reviewed PNG exceptions, validates relative Markdown links, and regenerates examples for byte equality. It is a bounded automated check, not a guarantee against every possible sensitive string. The first-publication review must also inspect the entire diff.

## Pending engine and product gates

| Gate | Acceptance | Status |
| --- | --- | --- |
| Databricks | Same synthetic tables and results, zero reconciliation discrepancies, documented types | Not run |
| Power Query | All five CSV tables load with specified types and no errors | Not run |
| DAX | Both snapshots, MTD/LFM, all bases, reference months, missing and zero cases match reference | Not run |
| Power BI model | Unique dimension keys, only intended relationships, no mixed-snapshot implicit sums | Not run |
| UX | Slicers, Reset, cross-page state, unavailable labels and service filters behave as specified | Not run |
| Persistence | Save, close and reopen retain values and selected state | Not run |
| Refresh | Rebuild with a new synthetic snapshot and reconcile independently | Not run |
| Power BI Service | Deployment, permissions, gateway, concurrency and scheduled refresh | Out of scope |
| Performance / scale | Approved benchmark methodology and publishable receipts | Out of scope |
| Human publication review | Review all files and merge explicitly | Required before main |

For DAX validation, include multiple / no snapshot selection, missing comparison history, zero denominators, month rollover with delayed data, manual January / February, filtered Compute and Network, and all three cost bases. Confirm a current-window failure does not leave a misleading comparable or variance card visible. The Python test result is not a substitute for these engine-specific checks.

Every refresh changes the evidence snapshot. A previous reconciliation pass must never be reused as proof of the new snapshot.
