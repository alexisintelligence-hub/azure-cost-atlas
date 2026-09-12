# Synthetic fixtures

All labels, costs, dates and quantities were invented for this public edition. No corporate data was transformed into these files. `synthetic-input.json` is the reproducible input, not an Azure / FOCUS export.

Two replacement snapshots cover January 1 to February 28 and January 1 to March 3, 2025. February 15 has received-day coverage but zero activity. Compute has two source lines per active day, collapsed to one daily analytical row. Network has a credit on each covered day 10. Quantities use distinct units by resource.

There are 476 stored source rows and 357 stored analytical rows across both snapshots. Do not sum across snapshots as spend. `expected-results.json` records the selected-snapshot example. CSVs are exact table exports for the Power BI build guide; `DimDate.csv` also includes uncovered calendar days so missing coverage can remain visible.

Regenerate locally with `python src/atlas.py --output work/demo`. `python scripts/check_publication.py` compares regenerated files byte-for-byte with these committed examples.
