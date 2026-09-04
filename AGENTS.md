# Bauspielplatz Website Codex Instructions

## Purpose And Ownership

- Treat this repository as the canonical public Hugo website source for `www.ruetihuetten.ch`.
- Open Codex at `/Users/martin/git/knowledge-personal/bauspielplatz-website` and read `README.md` plus `docs/deployment.md` before content, asset, build, publication, or DNS changes.
- Keep private board, donor, contact, reporting, correspondence, and planning material in `/Users/martin/git/knowledge-personal/bauspielplatz-internal`.

## Content, Privacy, And Rights

- Only add content approved for public release. Do not copy internal records into this repository merely because they are relevant to the website.
- Preserve image rights, creator attribution, consent, privacy, download provenance, and the declarations in `data/bildrechte.yaml`.
- Treat names, photographs of people, contact details, forms, minutes, donor material, and reporting documents as publication-sensitive.
- Edit source files only. `public/` and `resources/` are generated outputs and must not be committed or hand-edited.

## Build And Validation

- Use Hugo Extended at the version declared by the deployment workflow.
- Run `make check` after content, data, template, asset, redirect, or configuration changes; it builds the site, validates YAML and downloads, and checks internal links.
- For local preview use `make serve`. Keep generated build output and caches out of Git.

## Deployment And Rollback

- `origin` is `git@github.com:bsp-ruetihuetten/website.git`; `main` is the public deployment branch.
- A push to `main` triggers the GitHub Pages workflow and is an external publication action. Push only when public release is authorized, then verify the workflow and rendered site.
- Cloudflare Pages is the intended production platform for the public domain. Follow `docs/deployment.md` for build settings, pre-DNS checks, cutover, and rollback.
- Do not change DNS, Cloudflare configuration, GitHub Pages settings, repository visibility, or access permissions unless explicitly in scope.

## Related Repositories And Closeout

- Inspect `/Users/martin/git/knowledge-personal/bauspielplatz-internal` read-only when approved internal source context is required; declare it before any edit and never move private material across the publication boundary implicitly.
- Before closeout, run `git diff --check`, `make check`, and `git status --short --branch`; report content and assets changed, rights/privacy review, commit/push state, GitHub Pages result, Cloudflare/DNS state, verification, rollback, and residue.

