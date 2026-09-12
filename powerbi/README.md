# Build the synthetic Power BI example

These are source-level instructions, not a validated PBIX. Use a new blank local report. No organizational account, gateway or corporate connection is needed for the CSV demo. Do not reuse a configured corporate report.

1. Create text parameter `DemoFolder` with the absolute local path to this repository's `examples` directory.
2. Create a blank query named `LoadCsv` and paste [LoadCsv.pq](LoadCsv.pq) into Advanced Editor. Disable its load.
3. Create the following blank queries with these expressions (one query per table). Apply changes only after checking types and errors.

```powerquery
// FactDaily
LoadCsv("FactDaily.csv", {{"snapshot_id", type text}, {"charge_date", type date}, {"resource_key", type text}, {"currency", type text}, {"unit", type text}, {"source_row_count", Int64.Type}, {"quantity_milli", Int64.Type}, {"billing_cents", Int64.Type}, {"effective_cents", Int64.Type}, {"list_cents", Int64.Type}, {"billing_credit_cents", Int64.Type}, {"effective_credit_cents", Int64.Type}, {"list_credit_cents", Int64.Type}})

// DimResource
LoadCsv("DimResource.csv", {{"resource_key", type text}, {"service", type text}, {"application", type text}, {"unit", type text}})

// Snapshot
LoadCsv("Snapshot.csv", {{"snapshot_id", type text}, {"report_date", type date}, {"complete_through", type date}})

// Coverage
LoadCsv("Coverage.csv", {{"snapshot_id", type text}, {"charge_date", type date}})

// DimDate
LoadCsv("DimDate.csv", {{"charge_date", type date}})
```

4. Remove unwanted automatically detected relationships. Create only DimDate → FactDaily on charge_date and DimResource → FactDaily on resource_key, each one-to-many and single direction. Mark DimDate as the date table. Keep Snapshot and Coverage disconnected.
5. Add each selector below as a separate calculated table. Keep all selectors disconnected.

```dax
CostBasis = DATATABLE ( "Name", STRING, { { "Billing" }, { "Effective" }, { "List" } } )
Period = DATATABLE ( "Name", STRING, { { "MTD" }, { "LFM" } } )
Currency = DATATABLE ( "Code", STRING, { { "EUR" } } )
ReferenceMonth = SELECTCOLUMNS ( FILTER ( DimDate, DAY ( DimDate[charge_date] ) = 1 ), "MonthStart", DimDate[charge_date] )
```

6. Add the measures in [Measures.dax](Measures.dax), one definition at a time. Set date measures to Date, cost / variance to currency with two decimals, and variance percentage to Percentage. Hide raw FactDaily money, quantity and snapshot columns from report view; avoid implicit sums.
7. Add single-select slicers for Snapshot, Period, CostBasis and Currency. Select `DEMO-S2`, `MTD`, `Billing`, `EUR`. ReferenceMonth is optional: clear its selection for Automatic; select one month for Manual. Do not apply additional date filters to these period-level cards: measures intentionally control their date window.
8. Build cards for Current Cost, Comparable Cost, Cost Variance and Coverage Status; show Period Start / End and Comparable Start / End. Add a service table with Current Cost. Expected current = 141.90, comparable = 141.90, variance = 0.00, Compute = 62.70.
9. Switch to `DEMO-S1` + MTD: cost must be BLANK and status unavailable. Switch to LFM: period must be February. Review all acceptance scenarios in [validation](../docs/validation.md).

Save and clean reopen are distinct validation steps. A successful import does not prove DAX equivalence, report interactivity, Service refresh, deployment or production scale. Record actual results before updating the evidence status. The measures are period-level cards / rankings; a daily trend needs separate date-axis measures and tests.
