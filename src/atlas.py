"""Offline reference model. Synthetic data only; Python standard library."""
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path
import csv
import json
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('billing_cents', 'effective_cents', 'list_cents')
KEYS = ('snapshot_id', 'charge_date', 'resource_key', 'currency', 'unit')


def days(start, end):
    while start <= end:
        yield start
        start += timedelta(days=1)


def fixture():
    resources = [
        dict(resource_key='DEMO-COMPUTE', service='Compute', application='Demo Checkout', unit='hour'),
        dict(resource_key='DEMO-STORAGE', service='Storage', application='Demo Archive', unit='GB-month'),
        dict(resource_key='DEMO-NETWORK', service='Network', application='Unallocated', unit='GB'),
    ]
    snapshots = [
        dict(snapshot_id='DEMO-S1', report_date='2025-03-01', complete_through='2025-02-28'),
        dict(snapshot_id='DEMO-S2', report_date='2025-03-04', complete_through='2025-03-03'),
    ]
    rows, coverage = [], []
    for snap in snapshots:
        for day in days(date(2025, 1, 1), date.fromisoformat(snap['complete_through'])):
            coverage.append(dict(snapshot_id=snap['snapshot_id'], charge_date=day.isoformat()))
            # A fully received day with zero activity has coverage, but no cost rows.
            if day == date(2025, 2, 15):
                continue
            for index, resource in enumerate(resources):
                for part in range(2 if index == 0 else 1):
                    base = 1000 + day.day * 10 + index * 200 + part * 50
                    if index == 2 and day.day == 10:
                        base = -100  # Credit is retained, never clipped to zero.
                    rows.append(dict(
                        snapshot_id=snap['snapshot_id'],
                        line_id=f"DEMO-{day.isoformat()}-{index}-{part}",
                        charge_date=day.isoformat(), resource_key=resource['resource_key'],
                        currency='EUR', unit=resource['unit'], quantity_milli=1000,
                        billing_cents=base, effective_cents=base - 50,
                        list_cents=base + 100))
    return dict(resources=resources, snapshots=snapshots, coverage=coverage, source=rows)


def connect(data):
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.executescript((ROOT / 'sql/schema.sql').read_text())
    for table in ('resources', 'snapshots', 'coverage', 'source'):
        for row in data[table]:
            columns = ','.join(row)
            db.execute(f"INSERT INTO {table} ({columns}) VALUES ({','.join('?' for _ in row)})", tuple(row.values()))
    validate_source(db)
    db.executescript((ROOT / 'sql/aggregate.sql').read_text())
    return db


def validate_source(db):
    # Fail closed: no silent dropping, multiplying, coercing, or stale-day inference.
    for table, key in [('resources', 'resource_key'), ('snapshots', 'snapshot_id'),
                       ('coverage', 'snapshot_id, charge_date'), ('source', 'snapshot_id, line_id')]:
        if db.execute(f'SELECT 1 FROM {table} GROUP BY {key} HAVING COUNT(*) > 1').fetchone():
            raise ValueError('Duplicate key: ' + table)
    if db.execute('SELECT 1 FROM source s LEFT JOIN resources r USING(resource_key) WHERE r.resource_key IS NULL').fetchone():
        raise ValueError('Unknown resource')
    if db.execute('SELECT 1 FROM source s JOIN resources r USING(resource_key) WHERE s.unit <> r.unit').fetchone():
        raise ValueError('Resource unit mismatch')
    for table in ('source', 'coverage'):
        if db.execute(f'SELECT 1 FROM {table} s LEFT JOIN snapshots d USING(snapshot_id) WHERE d.snapshot_id IS NULL').fetchone():
            raise ValueError('Unknown snapshot')
    if db.execute('SELECT 1 FROM source s LEFT JOIN coverage c USING(snapshot_id,charge_date) WHERE c.charge_date IS NULL').fetchone():
        raise ValueError('Source outside received coverage')
    for s in db.execute('SELECT * FROM snapshots'):
        report, complete = date.fromisoformat(s['report_date']), date.fromisoformat(s['complete_through'])
        if complete >= report:
            raise ValueError('Complete-through must precede report date in this demo')
        for c in db.execute('SELECT charge_date FROM coverage WHERE snapshot_id=?', (s['snapshot_id'],)):
            if date.fromisoformat(c[0]) > complete:
                raise ValueError('Coverage exceeds complete-through')


def reconcile(db):
    return [dict(r) for r in db.execute((ROOT / 'sql/reconcile.sql').read_text())]


def period(db, snapshot_id, mode='MTD', reference_month=None):
    s = db.execute('SELECT * FROM snapshots WHERE snapshot_id=?', (snapshot_id,)).fetchone()
    if s is None:
        raise ValueError('Unknown snapshot')
    anchor = date.fromisoformat(reference_month + '-01') if reference_month else date.fromisoformat(s['report_date']).replace(day=1)
    complete = date.fromisoformat(s['complete_through'])
    if mode == 'MTD':
        start, end = anchor, min(complete, anchor.replace(day=monthrange(anchor.year, anchor.month)[1]))
    elif mode == 'LFM':
        # Previous month of the explicit reporting anchor, including at month rollover.
        end = anchor - timedelta(days=1)
        start = end.replace(day=1)
    else:
        raise ValueError('Supported periods: MTD, LFM')
    expected = {d.isoformat() for d in days(start, end)}
    available = {r[0] for r in db.execute('SELECT charge_date FROM coverage WHERE snapshot_id=?', (snapshot_id,))}
    return dict(start=start.isoformat(), end=end.isoformat(), available=bool(expected) and expected <= available)


def compare_window(window, mode):
    start, end = date.fromisoformat(window['start']), date.fromisoformat(window['end'])
    prev_end = start.replace(day=1) - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    if mode == 'MTD':
        prev_end = prev_end.replace(day=min(end.day, prev_end.day))
    return dict(start=prev_start.isoformat(), end=prev_end.isoformat())


def cost(db, snapshot_id, start, end, basis='billing', currency='EUR', service=None):
    if basis not in ('billing', 'effective', 'list'):
        raise ValueError('Unknown cost basis')
    if currency not in {r[0] for r in db.execute('SELECT DISTINCT currency FROM source')}:
        raise ValueError('Unknown currency')
    if not db.execute('SELECT 1 FROM snapshots WHERE snapshot_id=?', (snapshot_id,)).fetchone():
        raise ValueError('Unknown snapshot')
    if service is not None and service not in {r[0] for r in db.execute('SELECT DISTINCT service FROM resources')}:
        raise ValueError('Unknown service')
    expected = {d.isoformat() for d in days(date.fromisoformat(start), date.fromisoformat(end))}
    coverage = {r[0] for r in db.execute('SELECT charge_date FROM coverage WHERE snapshot_id=?', (snapshot_id,))}
    if not expected or not expected <= coverage:
        return None
    query = f'''SELECT COALESCE(SUM(f.{basis}_cents),0) FROM fact_daily f
        JOIN resources r USING(resource_key)
        WHERE snapshot_id=? AND charge_date BETWEEN ? AND ? AND currency=?'''
    args = [snapshot_id, start, end, currency]
    if service is not None:
        query += ' AND r.service=?'
        args.append(service)
    return db.execute(query, args).fetchone()[0]


def read_fixture():
    return json.loads((ROOT / 'examples/synthetic-input.json').read_text())


def export_demo(destination):
    data = fixture()
    db = connect(data)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'synthetic-input.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    for name, query in [('FactDaily', 'SELECT * FROM fact_daily ORDER BY snapshot_id, charge_date, resource_key'),
                        ('DimResource', 'SELECT * FROM resources'), ('Snapshot', 'SELECT * FROM snapshots'),
                        ('Coverage', 'SELECT * FROM coverage')]:
        cursor = db.execute(query)
        with (destination / (name + '.csv')).open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow([c[0] for c in cursor.description])
            writer.writerows(cursor)
    calendar = list(days(date(2025, 1, 1), date(2025, 3, 31)))
    with (destination / 'DimDate.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['charge_date'])
        writer.writerows([[d.isoformat()] for d in calendar])
    checks = reconcile(db)
    if checks:
        raise ValueError('Reconciliation failed')
    window = period(db, 'DEMO-S2')
    previous = compare_window(window, 'MTD')
    current = cost(db, 'DEMO-S2', window['start'], window['end'])
    prior = cost(db, 'DEMO-S2', previous['start'], previous['end'])
    receipt = dict(kind='synthetic-offline-run', source_rows=len(data['source']),
                   analytical_rows=db.execute('SELECT COUNT(*) FROM fact_daily').fetchone()[0],
                   reconciliation_mismatches=len(checks), snapshot='DEMO-S2',
                   current_window=window, previous_window=previous,
                   billing_current_cents=current, billing_previous_cents=prior,
                   billing_variance_cents=current-prior)
    (destination / 'expected-results.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'work/demo')
    export_demo(parser.parse_args().output)
