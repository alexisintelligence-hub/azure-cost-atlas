# Validation status

## Executed locally on 2026-09-12

Python standard-library runtime with in-memory SQLite executed the actual committed aggregation and reconciliation SQL. All **29 tests passed**. The fixture contains 476 source rows and 357 analytical rows across two synthetic snapshots. Reconciliation returned zero daily-grain discrepancies. No enterprise source was contacted.

```sh
python src/atlas.py
python -m unittest discover -s tests -v
python scripts/check_publication.py
```

The tests check fixed expected MTD values for three independent bases; snapshot isolation; MTD and LFM at month rollover; historical and future reference months; leap-year comparison clamping; missing history; zero-activity received days; missing coverage; resource filtering; retained negative credits; duplicate keys; unknown dimensions; null and fractional-cent values; unit mismatch; currency isolation; and corruption that removes, duplicates or changes analytical rows. Offsetting errors cannot hide behind a correct grand total.

The publication checker verifies the exact allowed file set, rejects binary/private artifact extensions and common secret-like strings, validates relative Markdown links, and regenerates examples for byte equality. It is a bounded automated check, not a guarantee against every possible sensitive string. The first-publication review must also inspect the entire diff.

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
