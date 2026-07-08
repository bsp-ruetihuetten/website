# Deployment

Testplattform: GitHub Pages im Repository `bsp-ruetihuetten/website`.

Zielplattform für die produktive Domain bleibt Cloudflare Pages.

## GitHub Pages Test

Die Website liegt im GitHub-Repository direkt im Repo-Root. Der Workflow
`.github/workflows/pages.yml` baut Hugo und publiziert `public/` als
GitHub-Pages-Artifact.

Wichtige Punkte:

- GitHub Pages in den Repository Settings auf `GitHub Actions` als Source stellen.
- Build erfolgt mit `HUGO_VERSION=0.164.0`.
- Der Workflow setzt `baseURL` automatisch auf die GitHub-Pages-URL.
- Die Templates sind subpath-tauglich, damit `https://bsp-ruetihuetten.github.io/website/`
  für den Test funktioniert.
- Cloudflare-spezifische `_redirects` werden von GitHub Pages nicht ausgewertet.

## Cloudflare Pages Build-Einstellungen

- Framework preset: Hugo
- Build command: `hugo --minify`
- Build output directory: `public`
- Environment variable: `HUGO_VERSION=0.164.0`

## Wichtige Konfiguration

- `timeZone: "Europe/Zurich"` für das Status-Banner.
- `buildFuture: true`, damit kommende Eventseiten gebaut werden.
- `static/_redirects` für alte Jimdo-URLs.

## Vor DNS-Umstellung prüfen

1. `hugo --minify` ohne Warnungen oder Fehler.
2. Startseite zeigt Status-Banner und nächste Termine.
3. `/kalender/` zeigt das Jahresprogramm.
4. `/kontakt-unterstuetzen/` zeigt drei Mailto-Aktionen.
5. `/medien/` zeigt externe Medienlinks und lokale PDF-Kopien.
6. Redirects aus `static/_redirects` in der Cloudflare-Vorschau testen.

## Rollback

Vor der DNS-Umstellung bleibt Jimdo produktiv. Nach der Umstellung kann der DNS-Eintrag zurück auf Jimdo gesetzt werden, falls ein kritischer Fehler auftritt.
