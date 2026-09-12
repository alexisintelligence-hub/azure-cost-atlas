# Semantic model contract

## Tables and relationships

`FactDaily` is the exported daily grain described in the architecture. `DimDate[charge_date]` and `DimResource[resource_key]` each have one-to-many, single-direction relationships into FactDaily. Mark DimDate as the date table. Do not add bidirectional relationships.

`Snapshot` and `Coverage` remain disconnected from the fact and each other in this small example. Measures explicitly apply the selected snapshot to FactDaily and Coverage. This keeps the coverage boundary independent of business filters. Snapshot has exactly one row per snapshot ID. Coverage has one row per snapshot and received day; it includes the received zero-activity day.

Create disconnected selectors `CostBasis`, `Period`, `ReferenceMonth` and `Currency` using the build guide. The only demo currency is EUR. Hide raw financial columns, keys and quantity columns from report authors so an implicit SUM cannot mix snapshots or currencies. Use explicit measures.

| Metric | Definition | Unit / caveat |
| --- | --- | --- |
| Billing | Sum of billing cents / 100 in the selected covered window | EUR; illustrative billing basis |
| Effective | Sum of effective cents / 100 in the same scope | EUR; independent economic interpretation |
| List | Sum of list cents / 100 in the same scope | EUR; independent reference basis |
| Variance | Current minus comparable selected-basis cost | EUR; BLANK when either window unavailable |
| Variance % | Variance / comparable cost | BLANK for missing or zero denominator; negative denominator requires contextual interpretation |
| Credits | Sum of negative source contributions for the selected basis | EUR; not inferred from a net daily amount |
| Source row count | Sum of original contribution counts at the daily grain | Not the number of daily fact rows |
| Quantity | Sum of milli-units / 1000 within one unit and covered scope | Never combine hours, GB and GB-month; no generic quantity total is supplied |

Price attributes are not additive and are omitted from the toy model. Differences among cost bases are not automatically savings or invoice reconciliation. Synthetic formulas illustrate contracts, not Azure pricing rules.

## Engine boundary

The included DAX covers selected-basis current, comparable and variance measures for MTD / LFM. Quantity, credit and allocation visual measures are defined here but left for an explicitly validated extension. Python tests validate the offline reference only. Evaluate DAX, CSV import types, totals, filters, persistence and refresh separately following [validation](validation.md).
