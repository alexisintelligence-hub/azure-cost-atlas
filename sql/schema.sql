-- Offline SQLite fixture schema. Not an Azure export schema or a production DDL.
CREATE TABLE resources(resource_key TEXT NOT NULL, service TEXT NOT NULL,
  application TEXT NOT NULL, unit TEXT NOT NULL);
CREATE TABLE snapshots(snapshot_id TEXT NOT NULL, report_date TEXT NOT NULL, complete_through TEXT NOT NULL);
CREATE TABLE coverage(snapshot_id TEXT NOT NULL, charge_date TEXT NOT NULL);
CREATE TABLE source(snapshot_id TEXT NOT NULL, line_id TEXT NOT NULL,
  charge_date TEXT NOT NULL, resource_key TEXT NOT NULL, currency TEXT NOT NULL,
  unit TEXT NOT NULL, quantity_milli INTEGER NOT NULL CHECK(typeof(quantity_milli)='integer'),
  billing_cents INTEGER NOT NULL CHECK(typeof(billing_cents)='integer'),
  effective_cents INTEGER NOT NULL CHECK(typeof(effective_cents)='integer'),
  list_cents INTEGER NOT NULL CHECK(typeof(list_cents)='integer'));
