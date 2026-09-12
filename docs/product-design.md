# Product brief and information architecture

## Audience and decision

Leadership needs to understand spend and change. Application owners need attribution. FinOps practitioners need explainable cost bases and confidence in the numbers. The public design answers: what period is actually available, what changed, where is it concentrated, who owns it, and which financial interpretation is selected?

| Page | Primary question | Main content / interaction |
| --- | --- | --- |
| Overview | What is the current cost and comparable change? | Billing / Effective / List selector; amount, comparable, variance; explicit period caption |
| Concentration & change | Which services or resources explain the amount? | Ranked contributions and drill target; distinguish negative credits from positive spend |
| Applications | How is cost attributed? | Application totals with visible Unallocated category; drill to resource |
| Cloud composition | What services and consumption units are involved? | Service mix, then separate unit-specific consumption views |
| Billing & price context | Which basis and credits explain the financial reading? | Side-by-side bases, basis differences, credit detail; no automatic savings label |

Confidence is a persistent strip on every page: selected snapshot, report date, complete-through date, coverage and reconciliation status. A dedicated confidence page is a possible extension, not shipped UI. The wireframe implements the overview composition only; other pages are a design specification.

## Interaction contract

- Select one snapshot and one currency; disable or blank financial visuals when either is ambiguous.
- Keep Period, Reference month and Cost basis consistent across pages. Reset returns a documented default, not an arbitrary saved filter state.
- Report date and completeness stay global under application / service selection. Show the selected window and comparable range in text.
- Show `Unavailable — missing coverage` for an incomplete window, and `0.00` for a covered window with no charges. Comparison unavailable means variance unavailable.
- Preserve keyboard focus, visible selected states and labels that do not depend on color. Provide a table alternative for rankings. Accessibility and cross-page behavior require actual Desktop validation.
- Never label source completeness as “live”. Never present three alternative bases as a combined total.

## Acceptance examples

At `DEMO-S1`, automatic MTD is unavailable on March 1 because only February is complete. LFM is February, not January. At `DEMO-S2`, March 1–3 is available. Changing service to Compute leaves the date window unchanged. Selecting an uncovered historical month shows unavailable. A zero-activity received day remains a real zero.

The SVG wireframe is original design evidence using computed demo values. It is not a screenshot of an installed or corporate Power BI report, and it does not establish user adoption or measured UX impact.
