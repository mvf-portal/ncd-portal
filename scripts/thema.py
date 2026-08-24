#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/ncd.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "ncd-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
        '(((("Noncommunicable Diseases"[Majr] OR "Chronic Disease"[Majr] '
        'OR "Multiple Chronic Conditions"[Majr] OR "Multimorbidity"[Majr]) '
        'OR ("noncommunicable disease*"[Title] OR "non-communicable disease*"[Title] '
        'OR "chronic disease*"[Title] OR "chronic illness"[Title] '
        'OR multimorbidity[Title] OR "chronic condition*"[Title] OR NCDs[Title])) '
        'NOT ("Artificial Intelligence"[Majr] OR "Machine Learning"[Majr] '
        'OR "Deep Learning"[Majr] OR "Telemedicine"[Majr] '
        'OR "Medical Informatics"[Majr] OR "Mobile Applications"[Majr] '
        'OR "Electronic Health Records"[Majr] '
        'OR "Nursing"[Majr] OR "Nursing Care"[Majr] OR "Long-Term Care"[Majr] '
        'OR "Nursing Homes"[Majr] OR "Caregivers"[Majr] OR "Home Care Services"[Majr] '
        'OR "Aging"[Majr] OR "Longevity"[Majr] OR "Frailty"[Majr] OR "Geriatrics"[Majr] '
        'OR "Health Literacy"[Majr] OR "Patient Education as Topic"[Majr] '
        'OR "Decision Making, Shared"[Majr] OR "Health Communication"[Majr] '
        'OR "Climate Change"[Majr] OR "Air Pollution"[Majr] OR "Hot Temperature"[Majr] '
        'OR "Vaccination"[Majr] OR "Vaccines"[Majr] OR "Immunization"[Majr]))'
)
_KONTEXT = (
        '("Delivery of Health Care"[MeSH Terms] OR "Health Services"[MeSH Terms] '
        'OR "Quality of Health Care"[MeSH Terms] OR "Patient Care"[MeSH Terms] '
        'OR "Health Policy"[MeSH Terms] OR "Public Health"[MeSH Terms] '
        'OR "health care"[Title/Abstract] OR "health services"[Title/Abstract] '
        'OR "patient outcome*"[Title/Abstract] OR "clinical practice"[Title/Abstract] '
        'OR implementation[Title/Abstract] OR patients[Title/Abstract])'
)
# "Humans"[MeSH] haelt Tier-, Labor- und reine Modellarbeiten heraus.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}) AND "Humans"[MeSH Terms])',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 30
POOL_ALLGEMEIN = 25
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 5
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
        "Du bist Fachredakteur fuer die Versorgung chronischer Erkrankungen. "
        "Aus einer Liste von PubMed-Abstracts waehlst du die relevantesten "
        "aktuellen Studien aus und fasst sie praezise auf Deutsch zusammen. "
        "Deine Leserschaft arbeitet im deutschen Gesundheitswesen: Praxen, "
        "Kliniken, Kostentraeger, Selbstverwaltung und Gesundheitspolitik. "
        "Sie will wissen, was die Versorgung chronisch Kranker verbessert - "
        "nicht, welcher Wirkmechanismus im Labor nachgewiesen wurde."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) die Versorgung, Praevention oder Krankheitslast chronischer, nicht uebertragbarer Erkrankungen untersuchen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
      1. Versorgung und Ergebnis: Was veraendert den Verlauf? Behandlungs-
         programme, Koordination, Nachsorge, Adhaerenz - gemessen an
         Krankenhauseinweisungen, Komplikationen, Sterblichkeit oder
         patientenberichteten Ergebnissen.
      2. Mehrfacherkrankung: Arbeiten, die den Menschen mit mehreren
         Erkrankungen zugleich betrachten statt einer Diagnose. Das ist der
         Regelfall in der Praxis und der Ausnahmefall in der Literatur -
         entsprechend hoch zu gewichten.
      3. Praevention und Risikofaktoren: Was verhindert Erkrankung oder
         Verschlechterung - von der Frueherkennung bis zur Verhaeltnispraevention.
      4. Ungleichheit: Wer wird schlechter versorgt - nach Einkommen, Bildung,
         Region, Sprache - und was hilft dagegen.
      5. Krankheitslast und Kosten, sofern daraus ein Handlungsbedarf erkennbar
         wird und nicht nur eine Zahl berichtet ist.

NICHT in die Auswahl gehoeren:
Grundlagenforschung, Molekularbiologie und Tiermodelle, Studien zur Wirksamkeit einzelner Wirkstoffe ohne Versorgungsbezug, Phase-I- und Phase-II-Studien, Validierungen von Messgeraeten oder Bildgebung ohne Ergebnisbezug, Fallberichte und Fallserien, reine Praevalenzmeldungen ohne Bezugsgroesse sowie Uebersichten, die nichts Eigenes berichten.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
      1. MINDESTENS DREI der sechs Studien muessen aus Europa stammen oder ein
         europaeisches Gesundheitssystem betreffen. Liegen weniger als drei solche
         Arbeiten vor, nimm die verbleibenden Plaetze aus dem Rest - aber schoepfe
         die europaeischen zuerst aus.
      2. HOECHSTENS ZWEI der sechs duerfen dieselbe Krankheitsgruppe betreffen
         (Diabetes und Stoffwechsel, Herz-Kreislauf, Krebs, Atemwege, psychische
         Erkrankungen, Muskel-Skelett, Niere, Neurologie). Ohne diese Grenze
         bestuende die Ausgabe regelmaessig zur Haelfte aus Diabetesarbeiten - das
         ist der mit Abstand groesste Literaturbestand des Feldes und sagt nichts
         ueber die Bedeutung der uebrigen.
      3. HOECHSTENS EINE darf eine digitale Anwendung, ein Vorhersagemodell oder
         ein Verfahren des maschinellen Lernens im Mittelpunkt haben. Die Abfrage
         schliesst solche Arbeiten bereits aus, wenn sie dort das Hauptthema sind;
         diese Quote faengt die uebrigen. Sie gehoeren in das Schwesterportal
         ki.m-vf.de, und ohne die Grenze verschoebe sich der Hub binnen Wochen
         dorthin.
      4. HOECHSTENS EINE darf ausschliesslich Praevalenz oder Krankheitslast
         beschreiben, ohne eine Massnahme, eine Ursache oder eine Folge zu
         untersuchen.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Chronikerversorgung haengt an der Struktur, die sie traegt. Massgeblich sind die Trennung von ambulant und stationaer, die Frage, ob es einen Lotsen gibt (in Deutschland der Hausarzt ohne verbindliche Steuerung, in den Niederlanden und Grossbritannien mit), die Verguetung koordinierender Leistungen und das Vorhandensein strukturierter Programme - Deutschland hat mit den DMP ein flaechendeckendes System, das international selten ist. Ordne die Systeme nach Vergleichbarkeit: hoch bei DACH, Niederlanden, Belgien und Frankreich, mittel bei Skandinavien, Grossbritannien, Kanada und Australien, gering bei den USA. Nenne im Feld transfer ausdruecklich, woran die Uebertragbarkeit haengt - meist an der Koordination oder an der Verguetung.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
      **Er MUSS das Ergebnis nennen, nicht nur die Krankheit.** Abstracts sind
      nach der Diagnose betitelt; uebernimmt der Titel das, liest sich der Hub wie
      ein Diagnoseverzeichnis. Die Krankheit darf vorkommen - sie ist hier anders
      als in den Schwesterportalen oft die Sache selbst -, aber sie darf nicht
      allein stehen. Nicht "Typ-2-Diabetes in der Hausarztpraxis: eine
      Kohortenstudie", sondern "Strukturierte Nachsorge senkte
      Krankenhauseinweisungen bei Typ-2-Diabetes um ...".
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Beispiele fuer Begriffe, die englisch bleiben: Disease Management, Chronic Care Model, Self-Management, Case Management, Patient-Reported Outcomes. Uebersetze dagegen, was im Deutschen eine gaengige Entsprechung hat: aus "multimorbidity" wird die Mehrfacherkrankung, aus "adherence" die Therapietreue, aus "care pathway" der Versorgungspfad, aus "burden of disease" die Krankheitslast.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""
