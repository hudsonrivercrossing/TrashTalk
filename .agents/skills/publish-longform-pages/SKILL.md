---
name: publish-longform-pages
description: Publish a human-reviewed longform Markdown conversation to this project's GitHub Pages site. Use only after the user has approved the manuscript; the build script and publication manifest control what appears online.
---

# Publish Longform to GitHub Pages

Use this project-local workflow after the user has reviewed and approved a `*.publish-longform.md` manuscript.

## Project conventions

- Source manuscripts live in `transcripts/assemblyai/<recording-stem>/<recording-stem>.publish-longform.md`.
- `publishing/published-sources.txt` is the publication allowlist. The site builder only renders files listed there.
- `scripts/build_site.py` generates the homepage and article HTML under `site/`; `.github/workflows/pages.yml` deploys `site/` when changes are pushed to `main`.

## Workflow

1. Resolve the exact manuscript the user has reviewed. If not specified, list available publish-longform files and ask which approved file to publish. Do not infer approval merely from a file existing.
2. Inspect the manuscript's title, deck, speaker labels, and Markdown structure. Confirm that it is a publish-longform file inside the expected per-recording folder.
3. Add its repository-relative path to `publishing/published-sources.txt`, once only. Preserve existing entries. This is the explicit record that the source passed human review.
4. Run `python3 scripts/build_site.py`. Inspect the generated article and homepage to confirm the article appears and the HTML is well-formed enough for this site's simple renderer. Check `git diff` for accidental unrelated output changes.
5. Review `git status` and the current branch. Stage only the approved Markdown source, publication manifest, and generated files under `site/`. Do not stage audio, raw/intermediate transcripts, credentials, or unrelated edits. If unrelated work makes a safe targeted commit impossible, leave it untouched and report the specific blocker.
6. Commit the source, manifest, and generated site together with a concise publication message. Push to `main` so the existing Pages workflow deploys the site. Do not force-push or rewrite history. If the checkout is not on `main`, do not switch or push another branch; report the state and ask the user to continue from the intended branch.
7. When `gh` is available, inspect the deployment workflow and report its status and resulting Pages URL. Otherwise report that the push triggered the configured deployment and that live status could not be confirmed.

Never edit the conversation while publishing. If the manuscript needs content changes, return those to the review stage first.
