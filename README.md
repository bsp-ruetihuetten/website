# Bauspielplatz Rütihütten Website

Statische Hugo-Website für `www.ruetihuetten.ch`.

Die Struktur bleibt bewusst einfach: eine Sprache, wenige Hauptseiten, Kalender als zentrale Datenquelle und Mailto-Aktionen statt Kontaktformular.

## Pflegebereiche

- `content/de/` - Seiten und Archivtexte
- `data/kalender.yaml` - Öffnungstage, Ausfälle und Anlässe
- `data/kontakt_aktionen.yaml` - Mailto-Aktionen
- `data/medien_eintraege.yaml` - externe Medienberichte und Archivkopien
- `assets/images/` - kuratierte Website-Bilder
- `static/downloads/` - öffentlich verlinkte PDFs und Formulare

## Lokal entwickeln

```sh
hugo server --disableFastRender
```

Falls Hugo noch nicht installiert ist, zuerst Hugo Extended installieren.

## Build

```sh
hugo --minify
```

`public/` wird automatisch erzeugt und nicht von Hand bearbeitet.

## Prüfen

```sh
make check
```

Der Check baut die Website, validiert YAML, prüft bekannte Download-Dateien und kontrolliert interne Links im erzeugten `public/`.

## Wichtigste Datenlogik

- Status-Banner: kommt aus `data/kalender.yaml`.
- `offen: true` und `faellt_aus: false` zeigt "Bauspielplatz heute offen".
- `offen: true` und `faellt_aus: true` zeigt "Fällt heute leider aus".
- `typ: event` wird als kommender Anlass angezeigt.
