-- Zero rows means PASS. Bidirectional at daily grain, preserving currency/unit.
-- Signed union detects missing/extra groups and offsets; do not check only totals.
WITH signed AS (
 SELECT snapshot_id, charge_date, resource_key, currency, unit,
        1 AS n, quantity_milli AS q, billing_cents AS b, effective_cents AS e, list_cents AS l,
        CASE WHEN billing_cents < 0 THEN billing_cents ELSE 0 END AS bc,
        CASE WHEN effective_cents < 0 THEN effective_cents ELSE 0 END AS ec,
        CASE WHEN list_cents < 0 THEN list_cents ELSE 0 END AS lc
 FROM source
 UNION ALL
 SELECT snapshot_id, charge_date, resource_key, currency, unit,
        -source_row_count, -quantity_milli, -billing_cents, -effective_cents, -list_cents,
        -billing_credit_cents, -effective_credit_cents, -list_credit_cents
 FROM fact_daily
)
SELECT snapshot_id, charge_date, resource_key, currency, unit,
       SUM(n) AS row_delta, SUM(q) AS quantity_delta,
       SUM(b) AS billing_delta, SUM(e) AS effective_delta, SUM(l) AS list_delta,
       SUM(bc) AS billing_credit_delta, SUM(ec) AS effective_credit_delta, SUM(lc) AS list_credit_delta
FROM signed
GROUP BY snapshot_id, charge_date, resource_key, currency, unit
HAVING SUM(n) <> 0 OR SUM(q) <> 0 OR SUM(b) <> 0 OR SUM(e) <> 0 OR SUM(l) <> 0
    OR SUM(bc) <> 0 OR SUM(ec) <> 0 OR SUM(lc) <> 0;
