# Architecture and data contract

## Public reconstruction

The public reference implements the core analytics problem with invented data. It does not reproduce a private deployment, schema or history. Design themes were informed by author-provided project context; original context files and operational values are excluded.

## Grain and flow

1. `source`: one line per `(snapshot_id, line_id)`. A snapshot is a complete replacement view of the covered history, not an incremental batch to append to other snapshots.
2. `coverage`: one successfully received day per `(snapshot_id, charge_date)`. In this demo the author controls the manifest. In a real pipeline its production must be independently tied to successful extraction and completeness checks.
3. `resources`: one row per resource key; application and service are dimensions. Unknown business allocation is the explicit label `Unallocated`.
4. `fact_daily`: one row per `(snapshot_id, charge_date, resource_key, currency, unit)`, retaining source-row count, cost bases, credits and quantity. The synthetic source has split compute lines; aggregation collapses those without losing sums.
5. Validate at the same grain. The signed union compares source contributions with analytical contributions. Zero discrepancies is a gate, not a chart annotation that can be ignored.
6. Select exactly one snapshot and currency. Compute time windows from its report date and completeness boundary. A resource or service filter must not change that global boundary.

Daily reconciliation is stronger than checking only monthly and grand totals: offsetting errors on different days or resources remain visible. A daily pass implies additive rollups reconcile at month and grand-total levels for the same snapshot, currency, unit and measure. It does not establish that an external invoice or upstream source is correct.

## Integrity gates

Reject duplicate fact-line, dimension, snapshot and coverage keys; unknown resource/snapshot; source dates without coverage; unit mismatches; null or fractional-cent money; and coverage beyond the declared complete-through date. Signed money retains credits. The implementation never infers receipt from a nonempty fact table alone.

One synthetic day has valid coverage and no activity. Its cost is zero. A day outside coverage returns `None` in Python and should return `BLANK` in Power BI. These are different states.

## Time contract

- `report_date` is an explicit as-of date; the demo does not use the machine clock.
- `complete_through` is the last fully received charge day. It precedes `report_date` in this edition.
- Automatic reference month is the month of `report_date`; manual reference month is an explicit `YYYY-MM`.
- MTD starts on day one of that month, ending at the earlier of its last day and `complete_through`. An inverted or incompletely covered window is unavailable.
- LFM is the calendar month immediately before the reference month. At March rollover it is February, even when the source cutoff is February 28.
- MTD comparison uses the same day count in the previous month, capped to that month's length. LFM comparison is the whole previous month. Each comparison is gated against coverage separately.
- Missing comparison history stays unavailable; variance must stay unavailable too. Do not coerce it to zero or label the whole prior month a like-for-like MTD comparison.

## Layer ownership

Python creates fixtures, validates input, evaluates periods and exports tables. SQLite executes the committed SQL. Power Query and DAX are adaptation examples for a manual Desktop build. The Power BI specification is downstream of the same data contract, but its behavior must be evaluated in its own engine before claiming equivalence. No Python pass is reported as a DAX, Power Query or Databricks pass.
