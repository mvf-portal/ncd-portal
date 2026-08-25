# Nicht übertragbare Krankheiten · Rechercheportal

Ein Rechercheportal zum Themenfeld **Nicht übertragbare Krankheiten**: 101 Datenbanken in 11 Rubriken,
davon 41 mit Live-Suche, dazu eine täglich aus PubMed kuratierte Studienauswahl mit
deutschen Zusammenfassungen.

Ein Angebot von **Monitor Versorgungsforschung** (eRelation AG – Content in Health, Bonn).

https://ncd.m-vf.de/

## Wie es funktioniert

Ein Suchbegriff, eingegeben an einer Stelle, stellt sämtliche Datenbankkacheln darauf ein;
ein Klick führt direkt in die Trefferliste der jeweiligen Datenbank. Deutsche Fachbegriffe
werden für internationale Datenbanken automatisch in den Ausdruck übersetzt, unter dem sie
dort indexiert sind (154 Begriffe).

| | |
|---|---|
| Datenbanken | 101 in 11 Rubriken |
| Live-Suche | 41 |
| Portal (feste URL) | 43 |
| Lizenz nötig | 5 |
| Suchglossar | 154 Begriffe |
| Studienauswahl | täglich 6 Uhr aus PubMed, KI-kuratiert |

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | die gesamte Anwendung (CSS + HTML + JS inline) |
| `ueber.html`, `newsletter.html` | Begleitseiten |
| `scripts/thema.py` | **alles Themenspezifische** der Studienauswahl |
| `scripts/update_studies.py` | PubMed → Claude → Marker-Block (in allen Portalen gleich) |
| `scripts/build_newsletter.py` | RSS-Feed und Download-Dateien aus dem Archiv |
| `scripts/mailchimp_entwurf.py` | Kampagnen-Entwurf zur Freigabe |
| `studien-archiv.json` | vollständige Historie aller gezeigten Studien |
| `portal.json` | die Werte dieses Portals — Grundlage des Vorlagen-Abgleichs |

Dieses Portal ist aus der Vorlage `mvf-portal/portal-vorlage` entstanden. Änderungen an der
Mechanik gehören dorthin und werden von dort in alle Portale eingespielt.

## Betrieb

Kein Build, kein Framework. Commit auf `main` → GitHub Pages baut automatisch.

Secrets im Repository: `NCDHUB` (Claude-API) und `NCDHUBMC` (Mailchimp).
