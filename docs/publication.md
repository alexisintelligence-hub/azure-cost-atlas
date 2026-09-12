# Public edition policy

Only files enumerated in `public-manifest.json` are candidates for publication. They contain newly authored code / documentation, deterministic synthetic examples, an original wireframe, review automation, and two owner-authorized redacted historical visual references. No private repository was cloned into this edition and no private history is a parent of its commits.

Excluded: company/client identities, tenant/subscription/resource identifiers, internal paths and URLs, underlying operational financial data, unredacted screenshots, original context files or work logs, secrets, cloud exports, PBIX/PBIT/ABF files and service credentials. Adding such artifacts requires a new explicit review; .gitignore alone is insufficient because tracked and historical files can still disclose data.

The narrow exception is the two PNGs documented in [visual references](visual-references.md): the owner explicitly requested masking identities while retaining displayed aggregates. These are AI-edited visual context, not synthetic outputs or validated quantitative evidence. Their exact hashes are pinned in the manifest; other binary artifacts remain excluded.

The public repository may contain a minimal initialization notice on main so a PR has a base. The actual portfolio content belongs on the proposal branch. A public PR and its branch are public before merge: perform sanitization and local checks **before pushing**. Do not enable auto-merge, push the portfolio directly to main, or claim branch protection is enforced unless it has been verified in GitHub settings.

Human reviewers should inspect the PR file list and contents, verify the new standalone history, reproduce tests, confirm all executable demo data is synthetic and the historical images carry accurate provenance labels, assess the evidence matrix and pending engine gates, and decide whether to merge. GitHub check success is technical evidence, not human authorization.

The workflow uses `pull_request`, read-only contents permissions and no credentials or deployment step. There is no auto-publish or auto-merge workflow. Reviewers should keep these constraints when extending it.
