# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekt

„Knowledge-Hub Chronische Erkrankungen" — ein Rechercheportal zum Themenfeld Nicht übertragbare Krankheiten. Ein Angebot von **Monitor Versorgungsforschung** (Betreiber: eRelation AG – Content in Health, Bonn).

Live: https://ncd.m-vf.de/

Dieses Portal ist aus der **Vorlage** `mvf-portal/portal-vorlage` entstanden. Die Schwesterportale (wissen.m-vf.de, klima.m-vf.de, ki.m-vf.de) sind technisch gleich aufgebaut. Sie sind bewusst **getrennte Repositories**, weil GitHub Pages nur eine CNAME-Datei je Repo zulässt.

**Wer hier an der Mechanik etwas ändert, ändert es in der Vorlage** und spielt es von dort in alle Portale ein:

```
py vorlage-abgleich.py --alle                 # zeigt, wo Portale abweichen
py vorlage-abgleich.py ..\ncd-portal --uebernehmen
```

Was neutral ist und was diesem Portal gehört, steht in `vorlage.json` der Vorlage. Kurzfassung: Aussehen, Suche, Filter, Download, Rechtstexte und alle Skripte außer `scripts/thema.py` sind neutral; die fünf Marker-Blöcke in `index.html` und `scripts/thema.py` gehören diesem Portal.

Projektsprache ist **Deutsch** — Oberfläche, Inhalte, Commit-Messages und Code-Kommentare. In Texten des Portals wird **gesiezt**.

## Kein Build, kein Test, kein Framework

`index.html` ist eine vollständig eigenständige Datei (CSS + HTML + JS inline). Kein npm, kein Build-Schritt, kein Linter, keine Testsuite.

| Aufgabe | Vorgehen |
|---|---|
| Lokal ansehen | `index.html` direkt im Browser öffnen |
| Deployen | Commit auf `main` pushen — GitHub Pages baut automatisch (~1 Min) |
| Live prüfen | `curl -s "https://ncd.m-vf.de/?cb=$(date +%s)"` — Cache-Buster nötig |
| Pages-Status | `gh api repos/mvf-portal/ncd-portal/pages/builds/latest` |

`gh` liegt unter `C:\Program Files\GitHub CLI\gh.exe` (nicht im PATH), angemeldet als `mvf-portal`. Python heißt `py`.

## Architektur: datengetriebenes Rendering

Die Seite hat praktisch kein statisches Markup im Body — eine HTML-Shell plus vier JS-Konstanten, aus denen alles per DOM-Aufbau erzeugt wird. Alle vier stehen in **Marker-Blöcken**:

| Konstante | Erzeugt | Wichtig |
|---|---|---|
| `CATS` | Rubriken + Sprungnavigation | Array-Reihenfolge = Anzeigereihenfolge. `h` ist ein HSL-Farbton (0–360). `num` ist Anzeigetext und muss bei Umsortierung mitgepflegt werden. Optionales Feld `hinweis` setzt einen erklärenden Absatz über die Kacheln. |
| `DB` | Datenbank-Kacheln | `c` verweist auf `CATS[].id`. |
| `STUDIES` + `SNAP_DATE` | Studien-Frame rechts | Wird täglich maschinell ersetzt. |
| `CHIPS` | Schnellwahl-Buttons | Reine Strings. |
| `GLOSSAR` | Übersetzung deutscher Fachbegriffe | Steht in der Datei, wird nicht nachgeladen. |

### Der `%s`-Mechanismus (Kern der Anwendung)

Jeder `DB`-Eintrag hat einen Typ `t`:

- **`live`** — `u` enthält `%s`. `apply()` ersetzt es beim Absenden durch den URL-kodierten Suchbegriff.
- **`portal`** — feste URL (Anbieter ohne Deeplink-Suche).
- **`lic`** — feste URL, kostenpflichtig.

**HTTP 200 beweist keinen Deeplink.** Jeden `%s`-Link zweimal abrufen — mit echtem Begriff und mit einem Phantasiewort. Byte-gleiche Antworten heißen: Der Parameter wird gar nicht ausgewertet, also `t:"portal"`.

### Studien aktualisieren

`.github/workflows/update-studies.yml` läuft um 04:00 UTC (06:00 Uhr deutscher Sommerzeit): `scripts/update_studies.py` → PubMed → Claude-API → Marker-Block ersetzen → commit & push.

**`scripts/thema.py` hält alles Themenspezifische** — Suchabfrage, Rollenbeschreibung, Auswahlregeln, Anzahl. Wer die Auswahl ändern will, ändert dort Text, keinen Code. `update_studies.py` bleibt in allen Portalen wortgleich.

`studien-archiv.json` ist die vollständige Historie (dedupliziert über die PMID); `scripts/build_newsletter.py` erzeugt daraus RSS-Feed und Download-Dateien. Dessen Ausgabe ist **bewusst deterministisch** — alle Zeitstempel stammen aus dem Archivinhalt, nicht aus der Systemuhr. Wer dort Zeitstempel einführt, erzeugt täglich einen Commit samt Pages-Build.

## Geheimnisse im Repository

| Secret | Wofür | Fehlt es? |
|---|---|---|
| `NCDHUB` | Claude-API für die Studienauswahl | Der tägliche Lauf bricht ab, `index.html` bleibt unverändert |
| `NCDHUBMC` | Mailchimp-API für den Kampagnen-Entwurf | Nur dieser Schritt entfällt (`continue-on-error`) |

Die Namen unterscheiden sich um zwei Buchstaben. Wer sie verwechselt, bekommt keine Fehlermeldung, die das sagt — sondern eine Authentifizierung, die beim jeweils anderen Dienst scheitert.

**Alle Portale schreiben in dasselbe Mailchimp-Konto.** `mailchimp_entwurf.py` erkennt seine eigenen Kampagnen am Titel-Präfix `MVF NCD-Newsletter`. Der Präfix muss sich **vollständig** von den Schwesterportalen unterscheiden: `datum_aus_titel()` prüft mit `startswith()`, ein bloßer Zusatz reicht nicht.

Mailchimp-Gruppe dieses Portals: `group[16143][131072]` („Studien Newsletter NCD"). **Gruppen-Nummern sind Identitäten, keine Beschriftungen** — wer eine umbenennt, verschiebt Menschen, nicht Wörter.

## Gestaltung: das Erscheinungsbild von m-vf.de

| Merkmal | Wert |
|---|---|
| Schrift | **Lato** 300/400/700, selbst gehostet in `fonts/` |
| Hausfarbe | `#0051A1` |
| Handlungsfarbe | `#BE9E53` (nur auf Knöpfen) |
| Seitengrund | `#EDF2FA` |

- **Nur Lato.** Keine zweite Schriftfamilie, kein Google Fonts (das wäre ein Verbindungsaufbau zu Dritten und widerspräche den Datenschutzhinweisen).
- **Nur die Stärken 300/400/700 existieren.** Zwischenstärken rasten auf 700 ein.
- **Gold nur auf Knöpfen** — als Textfarbe erreicht `#BE9E53` nur 3,0:1. Knopfschrift auf Gold ist dunkles `#2A2207`.
- **Das Logo wird im Dark Mode nicht umgefärbt**, sondern auf eine weiße Fläche gestellt.

## Versand: Torwächter und Veto-Fenster

Seit dem 18.08.2026 wird der Newsletter **nicht mehr von Hand freigegeben**. Der nächtliche Lauf legt den Entwurf an, `scripts/torwaechter.py` prüft ihn, und `mailchimp_entwurf.py` **terminiert** die Kampagne auf `TERMIN_LOKAL` (10:00 Uhr deutscher Ortszeit — bewusst nicht in UTC festgeschrieben, sonst verschöbe die Zeitumstellung den Versand). Bis dahin lässt sie sich in Mailchimp mit einem Klick absagen — *Unschedule*.

Der Grund für diese Bauweise: Versand ist der einzige Schritt der Kette, der sich nicht zurücknehmen lässt. Der Torwächter fängt **mechanischen** Unfug (fehlende Felder, Platzhalter, erfundene Zeitschriften — gegen PubMed geprüft, englisch gebliebene Zusammenfassungen, Dubletten, leeres Empfängersegment). Er fängt **nicht** die Zusammenfassung, die flüssig klingt und die Studie falsch wiedergibt; dafür ist das Zeitfenster da.

**Schlägt eine Prüfung an, wird nicht terminiert.** Der Entwurf bleibt liegen, die Redaktion bekommt die Testausgabe mit Freigabekasten, und der Grund steht in `versand-status.json`. Lieber ein Tag ohne Newsletter als ein falscher.

`versand-status.json` wird vom Workflow mitcommittet. Das Repo `mvf-portal/knowledge-hubs` liest sie von allen Portalen ein und macht daraus **eine** GitHub-Issue statt fünf E-Mails (`scripts/versand_bericht.py`, täglich 04:45 UTC).

Qualitative Interviewstudien und Expertenpapiere sind ausdrücklich **zugelassen** — der Torwächter verlangt deshalb Substanz im Ergebnisfeld, aber keine Zahl.

## Fallstricke

- **`const` vor seiner Definition benutzen legt die ganze Seite lahm.** Das gesamte JS liegt in einem Block; ein `ReferenceError` verhindert, dass Kacheln *und* Studien gerendert werden. Nach Skriptänderungen immer die Browser-Konsole prüfen.
- **Kein HTML-Escaping.** Alles wird per `innerHTML` eingesetzt — `<`, `>`, `&` in `DB`- oder `STUDIES`-Einträgen zerlegen das Markup.
- **Keine geraden doppelten Anführungszeichen in `STUDIES`-Strings** — die Objekte stehen in inline-JS; ein `"` bricht das Skript und die Seite bleibt leer.
- **Deutsches Zahlenformat** in Studientexten (`0,63` statt `0.63`).
- **Impressum und Datenschutzhinweise sind rechtlich erforderlich** (§ 5 DDG, § 18 Abs. 2 MStV) — nicht beiläufig umformulieren. Sie beschreiben eine statische Seite ohne Cookies und Tracking; das muss stimmen, wenn Skripte hinzukommen.
- **Python-Escapes beim Erzeugen von JS/CSS:** `\226` wird als Oktalzahl gelesen, `\n` wird zum echten Umbruch. Rohstrings verwenden oder direkt mit dem Edit-Werkzeug schreiben.
- **Dark Mode.** Farben laufen über CSS-Variablen mit drei Quellen: `prefers-color-scheme`, `:root[data-theme="dark"]`, `:root[data-theme="light"]`. Neue Farbwerte in allen Blöcken ergänzen.
