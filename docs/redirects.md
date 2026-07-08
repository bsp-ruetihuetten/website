# Redirects

Redirects liegen in `static/_redirects`.

Aktuelle Mapping-Regeln:

```text
/agenda/ /kalender/ 301
/über-uns/ /bauspielplatz/ 301
/ueber-uns/ /bauspielplatz/ 301
/gönner/ /kontakt-unterstuetzen/ 301
/goenner/ /kontakt-unterstuetzen/ 301
/presse/ /medien/ 301
/fotos/ /archiv/ 301
/about/ /rechtliches/impressum/ 301
/j/privacy/ /rechtliches/datenschutz/ 301
```

Die Content-Dateien behalten zusätzlich `legacy_urls` im Frontmatter. Das ist die pflegbare Quelle, falls die Redirect-Datei später automatisch erzeugt werden soll.
