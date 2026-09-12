import copy
import json
from pathlib import Path
import sqlite3
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from atlas import connect, fixture, reconcile, cost, period, compare_window, ROOT


class AtlasContract(unittest.TestCase):
    def setUp(self):
        self.data = fixture()
        self.db = connect(self.data)

    def tearDown(self):
        self.db.close()

    def test_fixture_matches_committed_input(self):
        self.assertEqual(self.data, json.loads((ROOT / 'examples/synthetic-input.json').read_text()))

    def test_baseline_reconciliation(self):
        self.assertEqual(reconcile(self.db), [])

    def test_expected_counts(self):
        self.assertEqual(len(self.data['source']), 476)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM fact_daily').fetchone()[0], 357)

    def test_snapshot_isolation(self):
        args = ('2025-02-01', '2025-02-28')
        self.assertEqual(cost(self.db, 'DEMO-S1', *args), cost(self.db, 'DEMO-S2', *args))

    def test_mtd_on_month_rollover_without_data_is_unavailable(self):
        self.assertFalse(period(self.db, 'DEMO-S1')['available'])

    def test_lfm_on_month_rollover_is_february(self):
        self.assertEqual(period(self.db, 'DEMO-S1', 'LFM'),
                         dict(start='2025-02-01', end='2025-02-28', available=True))

    def test_mtd_uses_loaded_cutoff_not_today(self):
        self.assertEqual(period(self.db, 'DEMO-S2'),
                         dict(start='2025-03-01', end='2025-03-03', available=True))

    def test_historical_month_is_complete_when_covered(self):
        self.assertEqual(period(self.db, 'DEMO-S2', reference_month='2025-01')['end'], '2025-01-31')

    def test_future_month_is_unavailable(self):
        self.assertFalse(period(self.db, 'DEMO-S2', reference_month='2025-04')['available'])

    def test_comparison_caps_previous_month_length(self):
        self.assertEqual(compare_window(dict(start='2024-03-01', end='2024-03-31'), 'MTD')['end'], '2024-02-29')

    def test_missing_history_is_none(self):
        self.assertIsNone(cost(self.db, 'DEMO-S2', '2024-12-01', '2024-12-31'))

    def test_complete_day_without_activity_is_zero(self):
        self.assertEqual(cost(self.db, 'DEMO-S2', '2025-02-15', '2025-02-15'), 0)

    def test_missing_coverage_is_none(self):
        self.db.execute("DELETE FROM coverage WHERE snapshot_id='DEMO-S2' AND charge_date='2025-03-02'")
        self.assertIsNone(cost(self.db, 'DEMO-S2', '2025-03-01', '2025-03-03'))

    def test_fixed_expected_mtd_and_basis(self):
        self.assertEqual(cost(self.db, 'DEMO-S2', '2025-03-01', '2025-03-03'), 14190)
        self.assertEqual(cost(self.db, 'DEMO-S2', '2025-03-01', '2025-03-03', 'effective'), 13590)
        self.assertEqual(cost(self.db, 'DEMO-S2', '2025-03-01', '2025-03-03', 'list'), 15390)

    def test_credit_is_preserved(self):
        self.assertEqual(cost(self.db, 'DEMO-S2', '2025-02-10', '2025-02-10', service='Network'), -100)

    def test_service_filter_preserves_global_window(self):
        self.assertEqual(cost(self.db, 'DEMO-S2', '2025-03-01', '2025-03-03', service='Compute'), 6270)

    def test_duplicate_source_fails(self):
        self.data['source'].append(copy.deepcopy(self.data['source'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate key'):
            connect(self.data)

    def test_duplicate_dimension_fails(self):
        self.data['resources'].append(copy.deepcopy(self.data['resources'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate key'):
            connect(self.data)

    def test_unknown_resource_fails(self):
        self.data['source'][0]['resource_key'] = 'DEMO-MISSING'
        with self.assertRaisesRegex(ValueError, 'Unknown resource'):
            connect(self.data)

    def test_null_financial_value_fails(self):
        self.data['source'][0]['billing_cents'] = None
        with self.assertRaises(sqlite3.IntegrityError):
            connect(self.data)

    def test_fractional_cent_fails(self):
        self.data['source'][0]['billing_cents'] = 10.5
        with self.assertRaises(sqlite3.IntegrityError):
            connect(self.data)

    def test_unit_mismatch_fails(self):
        self.data['source'][0]['unit'] = 'GB'
        with self.assertRaisesRegex(ValueError, 'unit mismatch'):
            connect(self.data)

    def test_source_without_coverage_fails(self):
        self.data['coverage'] = self.data['coverage'][1:]
        with self.assertRaisesRegex(ValueError, 'outside received coverage'):
            connect(self.data)

    def test_no_cross_currency_sum(self):
        self.data['source'][0]['currency'] = 'USD'
        db = connect(self.data)
        self.assertEqual(cost(db, 'DEMO-S1', '2025-01-01', '2025-01-01', currency='USD'), 1010)
        self.assertEqual(cost(db, 'DEMO-S1', '2025-01-01', '2025-01-01'), 3680)

    def materialize(self):
        self.db.executescript('CREATE TABLE frozen AS SELECT * FROM fact_daily; DROP VIEW fact_daily; ALTER TABLE frozen RENAME TO fact_daily;')

    def test_missing_aggregate_row_is_detected(self):
        self.materialize()
        self.db.execute('DELETE FROM fact_daily WHERE rowid=1')
        self.assertTrue(reconcile(self.db))

    def test_offsetting_errors_cannot_hide_in_grand_total(self):
        self.materialize()
        self.db.execute('UPDATE fact_daily SET billing_cents=billing_cents+1 WHERE rowid=1')
        self.db.execute('UPDATE fact_daily SET billing_cents=billing_cents-1 WHERE rowid=2')
        self.assertEqual(len(reconcile(self.db)), 2)

    def test_credit_corruption_is_detected(self):
        self.materialize()
        self.db.execute('UPDATE fact_daily SET billing_credit_cents=0 WHERE billing_credit_cents<0')
        self.assertTrue(reconcile(self.db))

    def test_duplicate_aggregate_row_is_detected(self):
        self.materialize()
        self.db.execute('INSERT INTO fact_daily SELECT * FROM fact_daily LIMIT 1')
        self.assertTrue(reconcile(self.db))

    def test_invalid_basis_rejected(self):
        with self.assertRaises(ValueError):
            cost(self.db, 'DEMO-S2', '2025-03-01', '2025-03-03', 'savings')


if __name__ == '__main__':
    unittest.main()
