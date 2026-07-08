# Pflegeanleitung

## Kalender pflegen

Die zentrale Datei ist `data/kalender.yaml`.

Wichtige Felder:

- `datum`: Datum im Format `YYYY-MM-DD`
- `titel`: sichtbarer Titel
- `typ`: `open`, `event`, `holiday` oder `closed`
- `offen`: `true`, wenn der Bauspielplatz an diesem Tag offen ist
- `faellt_aus`: `true`, wenn ein eigentlich offener Tag kurzfristig ausfällt
- `ausfall_hinweis`: Text für das Banner bei Ausfall
- `beginn` und `ende`: Öffnungszeiten

Beispiel Ausfall:

```yaml
- datum: "2026-07-11"
  titel: "Bauspielplatz offen"
  typ: "open"
  offen: true
  faellt_aus: true
  beginn: "14:00"
  ende: "17:30"
  ausfall_hinweis: "Fällt heute leider aus."
```

## Wichtige Anlässe pflegen

Anlässe wie Pfuus, Böögg oder Castagnata stehen ebenfalls in `data/kalender.yaml`.

```yaml
- datum: "2026-11-01"
  titel: "Castagnata"
  typ: "event"
  offen: true
  faellt_aus: false
  beginn: "14:00"
  ende: "17:30"
  hinweis: "Herbstfest mit Kastanien und Saisonabschluss."
```

`typ: event` sorgt dafür, dass der Anlass automatisch bei den nächsten Terminen erscheint.

## Kontaktaktionen pflegen

Die Mailto-Buttons stehen in `data/kontakt_aktionen.yaml`.

Pro Eintrag werden `beschriftung`, `email`, `betreff` und `text` gepflegt.

## Bilder organisieren

Empfohlene Ordner:

```text
assets/images/site/
assets/images/events/2026_pfuus/
assets/images/events/2026_booegg/
assets/images/events/2026_castagnata/
```

Regeln:

- Dateinamen klein, ohne Leerzeichen und ohne Umlaute.
- Event-Ordner mit Jahr beginnen, z.B. `2026_pfuus`.
- Nur kuratierte und freigegebene Bilder übernehmen.
- Bildrechte in `data/bildrechte.yaml` dokumentieren.

## Rückblicke und Galerien

Eventseiten liegen unter `content/de/events/<jahr>/`. Wenn eine Eventseite Text oder eine Galerie hat und ihr Datum in der Vergangenheit liegt, erscheint sie automatisch auf der Startseite im Abschnitt `Rückblicke`. Es werden maximal die drei neuesten Rückblicke angezeigt.

Für eine Galerie:

```yaml
galerie: "events/2026_pfuus"
```

Die Bilder dazu liegen dann unter:

```text
assets/images/events/2026_pfuus/
```

Wenn im Ordner echte Bilddateien liegen, verwendet die Startseite automatisch das erste Bild als Vorschau. Optional kann im Frontmatter ein kurzer `teaser` gesetzt werden; sonst wird der erste Textabsatz der Eventseite verwendet.

## Logo und Icons

Das Header-Logo liegt unter `static/logo/bauspielplatz-ruetihuetten-logo.png`. Quelle ist die in Statuten und Formularen verwendete Wort-/Bildmarke.

Dark Mode ist die Standarddarstellung. Dafür wird automatisch `static/logo/bauspielplatz-ruetihuetten-logo-dark-transparent.png` verwendet. Diese Variante ist aus demselben Logo abgeleitet, hat einen transparenten Hintergrund und eine aufgehellte Wortmarke.

Das Favicon liegt separat unter `static/favicon.ico` und `static/icons/bauspielplatz-icon-32.png`. Dafür wird nur das einfache Baumzeichen verwendet, weil das vollständige Logo in sehr kleinen Browser-Icons nicht lesbar ist.

Die Grundfarben stehen in `assets/css/main.css` als CSS-Variablen. Dunkel ist der Standard in `:root`; die helle Darstellung wird über `html[data-theme="light"]` gepflegt. Der Umschalter in der Navigation speichert die Auswahl lokal im Browser.

## Downloads

Öffentliche Dateien liegen unter `static/downloads/`.

Beispiele:

- `static/downloads/programm/jahresprogramm-2026.pdf`
- `static/downloads/statuten/statuten-bauspielplatz-2015.pdf`

Die Website sieht diese Dateien später unter `/downloads/...`.

## Jahresberichte

Jahresberichte stehen in `data/jahresberichte.yaml` und die PDF-Dateien unter:

```text
static/downloads/jahresberichte/
```

Ein neuer öffentlicher Jahresbericht bekommt:

```yaml
- jahr: 2026
  titel: Jahresbericht 2026
  pfad: /downloads/jahresberichte/jahresbericht-2026.pdf
  status: public
```

Entwürfe bleiben mit `status: draft` oder als Markdown-Datei mit `draft: true` unveröffentlicht.

## Externe Medienlinks archivieren

Externe Medienlinks stehen in `data/medien_eintraege.yaml`.

Für die öffentliche Website gilt:

- Titel, Datum, Quelle und Original-Link anzeigen.
- Eine kurze eigene Zusammenfassung schreiben.
- Externe Artikel nicht vollständig auf der Website republizieren.
- Lokale PDF-Kopien nur verwenden, wenn sie bereits publiziert waren und rechtlich vertretbar sind.

Für das interne Arbeitsarchiv können alle bekannten Links geparst werden:

```sh
python3 -B scripts/archive-external-media.py
```

Fotos und andere relevante Bilddateien aus den externen HTML-Quellen werden separat gesammelt:

```sh
python3 -B scripts/archive-external-media-images.py
```

Das Skript schreibt die Ergebnisse nach:

```text
../Archiv/2026-07-07-externe-medien/
```

Zusätzlich ergänzt es in `data/medien_eintraege.yaml` die Felder `archiv_markdown`, `archiv_rohdatei` und `archiv_parse_status`.

Der Bild-Sammler ergänzt `archiv_bilder`, `archiv_bilder_anzahl` und `archiv_bilder_status`. Diese Bilder bleiben internes Arbeitsmaterial. Vor einer öffentlichen Verwendung müssen Quelle, Nutzungsrecht und Personenfreigabe geprüft und in `data/bildrechte.yaml` dokumentiert werden.

## Alte URLs

Alte Jimdo-URLs stehen in `legacy_urls` im Frontmatter und zusätzlich in `static/_redirects`.

Neue Seiten sollten stabile, kurze URLs erhalten, z.B.:

- `/kalender/`
- `/bauspielplatz/`
- `/kontakt-unterstuetzen/`
- `/medien/`
