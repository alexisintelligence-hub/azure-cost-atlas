# Technical decisions

| Decision | Reason | Trade-off / alternative |
| --- | --- | --- |
| New standalone history | Avoid disclosing private commit history or artifacts | Public code is a reconstruction; it cannot substantiate private implementation equivalence |
| Daily fact | Supports MTD and month boundaries while reducing repeated detail | Discards line-level drilldown; retain the original approved source privately for investigation |
| Snapshot in every fact key | Prevents confusing historical revisions with new charges | Consumers must select one snapshot; appending and summing all snapshots is invalid |
| Separate coverage manifest | Distinguishes a received zero-activity day from a missing day | Requires upstream completeness attestation in real deployments |
| Explicit report-date anchor | Correct month rollover independent of workstation time | Freshness is exposed rather than silently repaired |
| Integer cents in the toy fixture | Exact offline money equality with no binary float rounding | Real sub-cent pricing needs DECIMAL precision, rounding rules and overflow tests |
| Separate cost bases | Billing, Effective and List answer different questions | More explicit controls; their differences are not automatically realized savings |
| Keep credits and unit grain | Prevents inflated spend and meaningless quantity sums | Cross-unit totals are intentionally unavailable |
| Star schema with one-way dimensions | Explicit filter flow and uniqueness | More setup than a flat table; production RLS and role design remain separate |
| Global coverage under service filters | A low-activity service must not move the report's time cutoff | Does not establish per-service ingestion completeness without more metadata |
| Daily reconciliation plus corruption tests | Totals alone can hide compensating errors | Full-grain comparisons are more expensive at production scale |
| Standard-library offline runtime | Reviewers can reproduce behavior without cloud access | Does not test distributed execution, refresh, DAX or deployment |

## Future Applied AI work

A possible extension is an explanation assistant grounded in reconciled metrics and explicit snapshot context. It is **not implemented**. Before shipping: define questions and access boundaries, bind responses to metric IDs and selected periods, refuse unavailable comparisons, create a synthetic evaluation set with adversarial missing-data cases, measure answer accuracy, and retain source traceability. Do not label rule-based filters or this roadmap as runtime AI.
