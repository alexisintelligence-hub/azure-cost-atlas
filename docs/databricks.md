# Databricks / SQL adaptation

The aggregation and signed reconciliation queries use a small portable SQL subset and run in SQLite in this edition. No Databricks workspace, warehouse, catalog, storage endpoint or authentication is included. **Databricks execution is pending**, including query plans and type / overflow behavior.

In an authorized disposable environment:

1. Generate the fixture and flatten `examples/synthetic-input.json` into the four documented tables, preserving every key. This fixture is not a FOCUS export and the mapping is not an ingestion connector.
2. Map dates to DATE, keys to STRING, and fixture money / quantities to BIGINT. Run equivalent integrity gates before aggregation. SQLite's `typeof` checks in `schema.sql` are local-only and must not be pasted as Databricks DDL.
3. Register the synthetic `source` table in the current isolated schema. Execute `aggregate.sql`, using `CREATE OR REPLACE TEMP VIEW fact_daily AS` for the initial view line when appropriate. Resolve source names in that isolated schema; do not point the script at production data.
4. Execute `reconcile.sql`. Require zero returned rows. Compare the fixture row counts and every exported daily row with the local result.
5. Inspect `EXPLAIN`, grouping cardinality, shuffle size, overflow behavior and refresh strategy before discussing scale. Record runtime version, warehouse size, query, snapshot, timings and repeated-run conditions if benchmarking.

For a real approved cost schema, map Billing / Effective / List independently to the documented source definitions. Real costs may have sub-cent precision: choose a suitable `DECIMAL(p,s)`, preserve that precision through aggregation, and round only at the agreed reporting boundary. Do not cast raw high-precision cost lines to integer cents before summation. The public fixture's cent arithmetic deliberately does not validate that adaptation.

Partitioning, incremental extraction, late corrections, idempotent publication, atomic snapshot activation and dimension history are production design work outside this edition. A snapshot should become visible only after coverage and reconciliation pass together; a failed candidate should leave the previous approved snapshot active. This activation mechanism is proposed, not implemented here.
