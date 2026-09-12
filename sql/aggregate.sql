-- Portable SQL reference, executed in SQLite by the offline tests.
-- Apply approved type/schema mapping and gates before adapting to Databricks.
CREATE VIEW fact_daily AS
SELECT snapshot_id, charge_date, resource_key, currency, unit,
       COUNT(*) AS source_row_count,
       SUM(quantity_milli) AS quantity_milli,
       SUM(billing_cents) AS billing_cents,
       SUM(effective_cents) AS effective_cents,
       SUM(list_cents) AS list_cents,
       SUM(CASE WHEN billing_cents < 0 THEN billing_cents ELSE 0 END) AS billing_credit_cents,
       SUM(CASE WHEN effective_cents < 0 THEN effective_cents ELSE 0 END) AS effective_credit_cents,
       SUM(CASE WHEN list_cents < 0 THEN list_cents ELSE 0 END) AS list_credit_cents
FROM source
GROUP BY snapshot_id, charge_date, resource_key, currency, unit;
