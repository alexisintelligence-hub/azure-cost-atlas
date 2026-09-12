# Evidence register and claim boundaries

| Claim | Evidence in this repository | Status |
| --- | --- | --- |
| Public edition authored from scratch | Independent initial Git history and public-only artifact manifest | Inspectable in the PR |
| Daily aggregation preserves money and source contribution counts | Executed SQL plus baseline and intentional corruption tests | Verified offline with synthetic data |
| Snapshot-aware MTD / LFM / historical month | Python contract tests including late source at month rollover | Verified offline |
| 476 source / 357 analytical stored rows | Deterministic generator and expected results | Verified synthetic fixture only |
| Semantic and Power BI integration | DAX, M, CSV tables and build instructions | Source-level example; engine validation pending |
| Databricks integration | Portable query and environment adaptation instructions | Design / SQL source; cluster execution pending |
| UX and information architecture | Newly authored product brief and wireframe | Design evidence; not a production screenshot or usability study |
| Historical scale and production results | No approved public execution receipt included | Not asserted |
| AI assistance in this reconstruction | Development process of this public edition | Process statement only |
| Runtime AI | No implementation exists in this edition | Not claimed |

Author-provided context was used only to identify design themes. A historical summary or profile statement is not an authorized execution receipt. Different snapshots cannot be substituted for each other to establish a scale figure. No corporate row counts, financial totals, benchmark timings, screenshots, identifiers or operational artifacts from those files are copied into this repository.

To add a historical quantitative claim later, obtain both permission to publish the exact aggregate and a sanitized evidence record that identifies the measurement date, snapshot, count definition, source and analytical grain, filters, query or method, validation status and limitations. Never attach a private log or configured report as a shortcut. Public demo measurements do not validate historical scale or business impact.

## External design references

- [XSIAM Analytics Connector public README](https://github.com/alexisintelligence-hub/xsiam-analytics-connector): editorial reference for separating executable evidence, runtime limits and AI-assisted development. No source code or image copied.
- [Microsoft: star schema guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema): reference for fact / dimension roles.
- [Microsoft: model relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand): reference for filter propagation and cardinality.
- [Databricks: SUM](https://docs.databricks.com/aws/en/sql/language-manual/functions/sum): reference for numeric result types and overflow considerations.

These references support design choices, not claims of runtime validation or product endorsement. Consulted 2026-09-12.
