---
name: sync-longform-pages
description: Reconcile this project's GitHub Pages HTML with human-approved longform Markdown, using the publication manifest and treating Markdown as the source of truth. Use for a requested or scheduled content sync.
---

# Sync Longform Pages from Markdown

Keep the published article HTML and homepage synchronized with approved Markdown manuscripts in this repository.

## Source of truth and scope

- `publishing/published-sources.txt` is the allowlist of human-reviewed manuscripts that may appear on the site.
- Listed `transcripts/assemblyai/<recording-stem>/<recording-stem>.publish-longform.md` files are the source of truth for article text, title, and deck.
- `scripts/build_site.py` regenerates `site/index.html` and `site/articles/*.html`; the Pages workflow publishes the `site/` directory after a push to `main`.
- Never add an unreviewed manuscript to the allowlist during a sync. New publication requires the `publish-longform-pages` review-and-publish workflow.

## Sync procedure

1. Inspect the branch and working tree before changing files. Run this only from `main`. If there are unrelated staged or unstaged changes, stop before building or committing and report them; do not disturb another task's work.
2. Read the allowlist. If a listed manuscript is missing, stop and report the stale entry rather than silently removing it. The builder performs this validation too.
3. Run `python3 scripts/build_site.py`, which generates output solely from listed sources. Review the diff for `site/index.html` and `site/articles/`; ensure all listed sources have matching pages and no unlisted draft appears.
4. If generated HTML is unchanged, make no commit and report that the published representation already matches the approved Markdown.
5. If output differs, stage only the allowlisted Markdown files that have tracked edits plus the generated `site/index.html` and `site/articles/` changes. Include deleted article pages when the generator removes them after an article is removed from the manifest. Do not stage audio, raw/intermediate transcripts, secrets, or unrelated files.
6. Commit the manuscript revisions and regenerated HTML together, then push the current `main` branch once to trigger the GitHub Pages deployment. Never force-push or rewrite history. If commit or push cannot safely proceed, preserve the work and report the error without retrying destructive Git operations.
7. If `gh` is available, check the Pages workflow for the pushed revision and report its status. If unavailable, state that the push triggered deployment but live status was not verified.

Make no editorial changes to Markdown. The automation copies its current content into HTML; it does not polish, redact, or reinterpret it.
