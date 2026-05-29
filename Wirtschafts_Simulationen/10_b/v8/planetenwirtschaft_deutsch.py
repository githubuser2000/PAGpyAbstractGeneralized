#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Planetary Effect Economy Simulation
===================================

PyPy3-compatible simulation of a planetary economy built from the concepts in
this chat: no money, no commodity price, no national GDP core. The system
coordinates real states and effects: causality, time, intensity, existence,
potencies, effects, substance, matter, difference, determination, phenomena, and
angle-direction.

Deutsch: Dies ist eine Planetenwirtschafts-Simulation, keine Volkswirtschaft.
Die primäre Frage ist nicht: "Was ist profitabel?" sondern:
"Welche reale Differenz zwischen Bedarf, Substanz, Potenzen und Wirkung muss
innerhalb planetarer Grenzen aufgelöst werden?"

Run:
    pypy3 planetary_effect_economy.py --steps 120 --scenario planetary_commons --out out
or, if PyPy3 is not installed:
    python3 planetary_effect_economy.py --steps 120 --out out

Outputs:
    summary.json        final system metrics
    timeline.csv          global time series
    macro_accounts.csv    planetary accounts by domain/sector/need/gap
    effect_flow_audit.csv last-step buy/sell replacement: causal effect flows
    trade_contracts_report.md human-readable trade/contracts in all truth dimensions
    trade_dimension_catalog.csv what is traded: products, jobs, services, ecology, climate
    dimension_guide.csv   meaning of each stacked truth dimension
    communes_final.csv    final commune-level states
    truth_audit.csv       top truth-vector priorities from the last step
    manifest.md           human-readable interpretation of the simulation

The model is intentionally synthetic. It is for concept development,
experimentation, and policy/game/simulation design, not a calibrated forecast.

Version note: this extended build adds macroeconomic replacements for sector
accounts, labour contribution, capital/investment, public coordination,
knowledge, resilience, material circulation and external trade. All remain
non-monetary: no price, wage, profit, rent, GDP, import value or export value.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Core vocabulary: stacked logical truth values
# ---------------------------------------------------------------------------

TRUTH_DIMS = (
    "causality",          # confidence that a chosen intervention actually acts on the cause
    "time",               # urgency in time
    "intensity",          # strength/severity of the phenomenon
    "existence",          # how real/present the phenomenon is
    "potencies",          # how much solvable possibility exists
    "effects",            # expected positive systemic effect if solved
    "substance",          # input/substance availability
    "matter",             # material/infrastructure proximity
    "difference",         # gap between need and state
    "determination",      # democratically confirmed priority / social determination
    "phenomena",          # visible or reported appearance of the issue
    "angle_direction",    # alignment of the action with planetary regeneration and human freedom
)

TRUTH_WEIGHTS = {
    "causality": 0.08,
    "time": 0.12,
    "intensity": 0.12,
    "existence": 0.08,
    "potencies": 0.08,
    "effects": 0.12,
    "substance": 0.07,
    "matter": 0.07,
    "difference": 0.14,
    "determination": 0.08,
    "phenomena": 0.07,
    "angle_direction": 0.09,
}

# Domains are not "markets". They are real need/effect fields.
DOMAINS = (
    "water",
    "food",
    "energy",
    "shelter",
    "health",
    "care",
    "education",
    "mobility",
    "manufacturing",
    "storage",
    "governance",
    "knowledge",
    "resilience",
    "repair",
    "ecology",
    "waste",
)

# Sectors replace national-account categories such as agriculture, industry,
# services, state, capital formation and foreign trade. They are not markets;
# they are fields of planetary reproduction.
SECTOR_FOR_DOMAIN = {
    "water": "primary_reproduction",
    "food": "primary_reproduction",
    "energy": "infrastructure_energy",
    "shelter": "social_infrastructure",
    "health": "care_reproduction",
    "care": "care_reproduction",
    "education": "knowledge_reproduction",
    "mobility": "logistics_circulation",
    "manufacturing": "material_transformation",
    "storage": "resilience_capital",
    "governance": "institutional_coordination",
    "knowledge": "knowledge_reproduction",
    "resilience": "risk_protection",
    "repair": "circular_industry",
    "ecology": "planetary_regeneration",
    "waste": "material_difference_resolution",
}

CONSUMABLE_DOMAINS = ("water", "food", "energy")
SERVICE_DOMAINS = ("health", "care", "education", "mobility", "governance", "knowledge", "resilience")
CAPACITY_DOMAINS = ("shelter", "manufacturing", "storage")
MACRO_CAPACITY_DOMAINS = CAPACITY_DOMAINS + SERVICE_DOMAINS

# One simulation step = one month. Units are normalized person-months or
# capability-months. These are not prices and not exchange values.
NEED_PER_PERSON = {
    "water": 1.0,
    "food": 1.0,
    "energy": 1.0,
    "shelter": 1.0,   # capacity for one person
    "health": 0.22,   # average monthly health service need
    "care": 0.18,     # care load, higher for children/elders/unwell cohorts
    "education": 0.20,
    "mobility": 0.23,
    "manufacturing": 0.12,  # tools, basic industry, replacement parts
    "storage": 0.08,        # buffers, warehouses, grid/storage systems
    "governance": 0.06,     # democratic coordination and dispute resolution
    "knowledge": 0.07,      # research, open plans, technical learning
    "resilience": 0.09,     # emergency readiness and redundancy
}

# Planetary pressure names. Pressure > 1 means overshoot beyond safe operating space.
BOUNDARY_NAMES = (
    "climate",
    "biosphere",
    "freshwater",
    "soil",
    "pollution",
    "material_throughput",
    "energy_throughput",
)

BOUNDARY_WEIGHTS = {
    "climate": 1.3,
    "biosphere": 1.25,
    "freshwater": 1.1,
    "soil": 1.0,
    "pollution": 1.05,
    "material_throughput": 0.85,
    "energy_throughput": 0.85,
}


# ---------------------------------------------------------------------------
# Visible trade vocabulary: what is traded when there is no price/value trade
# ---------------------------------------------------------------------------

# The dimension guide is deliberately verbose. In this model a "contract" is not
# a money contract. It is a condition set for a causal effect flow: what is
# accepted, contributed, transferred, protected, limited and corrected.
DIMENSION_GUIDE_DE = {
    "causality": {
        "name_de": "Kausalität",
        "short": "K",
        "question": "Trifft die Handlung die reale Ursache oder nur ein Symptom?",
        "contract_role": "Ohne genügende Kausalität ist ein Vertrag nur ein Versuch und muss experimentell/prüfend sein.",
        "economic_replacement": "ersetzt Preissignal durch Ursache-Wirkung-Nachweis",
    },
    "time": {
        "name_de": "Zeit",
        "short": "Z",
        "question": "Wie dringend ist die Wirkung, und in welchem Zeitfenster muss sie eintreten?",
        "contract_role": "Bestimmt Frist, Priorität, Notfallstufe und Dauer der Verpflichtung.",
        "economic_replacement": "ersetzt Liefertermin als Marktbedingung durch reale Dringlichkeit",
    },
    "intensity": {
        "name_de": "Intensität",
        "short": "I",
        "question": "Wie stark ist Bedarf, Mangel, Schaden oder positive Wirkung?",
        "contract_role": "Bestimmt Einsatzstärke, Personalzeit, Schutzgrad und Eskalation.",
        "economic_replacement": "ersetzt Zahlungsbereitschaft durch Stärke des Phänomens",
    },
    "existence": {
        "name_de": "Existenz",
        "short": "E",
        "question": "Ist das Phänomen wirklich vorhanden, gemessen, gemeldet und überprüfbar?",
        "contract_role": "Bestimmt, ob der Vertrag auf Realität oder auf Vermutung steht.",
        "economic_replacement": "ersetzt Eigentums-/Besitznachweis durch Existenznachweis des Zustands",
    },
    "potencies": {
        "name_de": "Potenzen",
        "short": "P",
        "question": "Welche Möglichkeiten, Fähigkeiten, Reserven und Lösungswege sind vorhanden?",
        "contract_role": "Bestimmt, ob eine Wirkung sofort, teilweise oder erst nach Aufbau möglich ist.",
        "economic_replacement": "ersetzt Kapitalrendite durch reale Fähigkeit zur Transformation",
    },
    "effects": {
        "name_de": "Wirkungen",
        "short": "W",
        "question": "Welche positiven und negativen Systemfolgen entstehen?",
        "contract_role": "Bestimmt Zielwirkung, Nebenwirkungsprüfung und Rechenschaft.",
        "economic_replacement": "ersetzt Profit durch reale Wirkung auf Menschen, Natur und Infrastruktur",
    },
    "substance": {
        "name_de": "Substanz",
        "short": "S",
        "question": "Welche Stoffe, Energie, Nahrung, Wasser, Wissen oder Pflegezeit sind verfügbar?",
        "contract_role": "Bestimmt Materialfreigabe, Stoffbegrenzung und Kreislaufpflicht.",
        "economic_replacement": "ersetzt Warenwert durch stoffliche Bedingung",
    },
    "matter": {
        "name_de": "Materie",
        "short": "M",
        "question": "Wo befindet sich die materielle Infrastruktur, und ist sie erreichbar?",
        "contract_role": "Bestimmt Ort, Logistik, Nähe, Transportlast und lokale Durchführbarkeit.",
        "economic_replacement": "ersetzt Handelsort/Marktzugang durch reale materielle Lage",
    },
    "difference": {
        "name_de": "Differenz",
        "short": "D",
        "question": "Wie groß ist die Lücke zwischen Bedarf und vorhandener Wirklichkeit?",
        "contract_role": "Bestimmt, ob überhaupt gehandelt werden soll und wie viel Widerspruch gelöst wird.",
        "economic_replacement": "ersetzt Nachfrage durch Bedarfslücke",
    },
    "determination": {
        "name_de": "Bestimmung",
        "short": "B",
        "question": "Ist die Handlung sozial/demokratisch bestätigt und sinnvoll bestimmt?",
        "contract_role": "Bestimmt Legitimation, Mitbestimmung, Widerspruchsrecht und Verantwortlichkeit.",
        "economic_replacement": "ersetzt Vertragspartnermacht durch kollektive Bestimmung",
    },
    "phenomena": {
        "name_de": "Phänomene",
        "short": "Ph",
        "question": "Wie zeigt sich der Zustand sichtbar, messbar und in Berichten Betroffener?",
        "contract_role": "Bestimmt Beweisgrundlage, Beobachtung, Audit und Korrekturpflicht.",
        "economic_replacement": "ersetzt Marktbeobachtung durch Erscheinungs-/Rückmeldelogik",
    },
    "angle_direction": {
        "name_de": "Winkelrichtung",
        "short": "R",
        "question": "In welche Richtung wirkt die Handlung: regenerativ, neutral, ausbeutend oder kontrollierend?",
        "contract_role": "Bestimmt, ob die Handlung erlaubt, bedingt erlaubt, umgebaut oder blockiert wird.",
        "economic_replacement": "ersetzt Wachstumsrichtung durch Wirkungsrichtung",
    },
}

# What is "traded" here: not exchange value, not amount-for-price, not commodity
# ownership. Each domain contains product-like things, jobs, services, and
# ecological/climate constraints, but the traded object is the causal effect.
TRADE_CATALOG = {
    "water": {
        "trade_object": "Wasserwirkung: Trinkwasser, Reinigung, Leitung, Speicher, Quellschutz",
        "meant_as": "Existenzsicherung für Durst, Hygiene, Gesundheit, Landwirtschaft und Feuer-/Krisenschutz",
        "products": "Trinkwasser, Filter, Pumpen, Rohrteile, Speicher, Messsensoren, Entsalzungs-/Reinigungseinheiten",
        "workplaces": "Wassertechniker:in; Hydrolog:in; Leitungsbau; Laborprüfung; Notwasserteam; Quellschutzgruppe",
        "services": "Aufbereitung, Lecksuche, Notverteilung, Qualitätsmessung, Brunnen-/Leitungswartung",
        "ecology": "Wassereinzugsgebiet darf nicht leergezogen werden; Renaturierung und Leckreduktion sind Vertragsauflagen",
        "climate": "Dürre, Starkregen und Pumpenergie werden mitgerechnet; energieintensive Lösungen brauchen erneuerbare Deckung",
    },
    "food": {
        "trade_object": "Nahrungswirkung: Kalorien, Nährstoffe, Bodenfruchtbarkeit, Saatgut, Erntezeit",
        "meant_as": "Körperliche Reproduktion, Gesundheit, lokale Ernährungssicherheit und kulturell passende Versorgung",
        "products": "Getreide, Gemüse, Hülsenfrüchte, Obst, Saatgut, Kühl-/Lagerkisten, Kücheninfrastruktur",
        "workplaces": "Landwirt:in; Saatgutpflege; Lebensmittelverarbeitung; Gemeinschaftsküche; Agrarökologie-Team",
        "services": "Anbauplanung, Ernte, Verarbeitung, Lagerung, Verteilung, Gemeinschaftsverpflegung, Ernährungsberatung",
        "ecology": "Bodenaufbau, Wasserverbrauch, Biodiversität und Pestizid-/Schadstofflast sind bindende Bedingungen",
        "climate": "Methan, Dünger, Transport, Kühlung und klimaresiliente Anbaumuster gehen in die Winkelrichtung ein",
    },
    "energy": {
        "trade_object": "Energiewirkung: Licht, Wärme, Antrieb, Netzstabilität, Speicherladung",
        "meant_as": "Bedingung für Versorgung, Kommunikation, Produktion, Pflege, Mobilität und Katastrophenschutz",
        "products": "Strom, Wärme, Solarpaneele, Windkomponenten, Batterien, Wärmepumpen, Leitungen, Steuergeräte",
        "workplaces": "Elektriker:in; Netzplanung; Speicherwartung; Solar-/Windmontage; Energiegenossenschaft; Lastmanagement",
        "services": "Erzeugung, Verteilung, Lastverschiebung, Reparatur, Dämm-/Effizienzberatung, Notstrompriorisierung",
        "ecology": "Materialabbau, Flächenverbrauch und Rückbau/Recycling sind Teil des Vertrags",
        "climate": "Fossilanteil, Effizienz, Erneuerbarkeit und Emissionswirkung bestimmen Zulassung und Priorität",
    },
    "shelter": {
        "trade_object": "Wohnwirkung: Schutz, Raum, Wärme, Sicherheit, Nähe zu Versorgung",
        "meant_as": "Stabile Existenzgrundlage statt Miete/Eigentum als Ausschlussmechanismus",
        "products": "Wohnraum, Dämmmaterial, Reparaturteile, Sanitärtechnik, modulare Bauteile, Gemeinschaftsräume",
        "workplaces": "Bauhandwerk; Sanierung; Architektur; Leerstandserfassung; Haustechnik; Konfliktmoderation Wohnen",
        "services": "Zuweisung nach Bedarf, Instandhaltung, Umbau, Barrierefreiheit, energetische Sanierung, Nachbarschaftspflege",
        "ecology": "Umbau vor Neubau; Bodenversiegelung, Materialkreislauf und lokale Grünwirkung sind Auflagen",
        "climate": "Heizenergie, Dämmung, Hitzeschutz und graue Emissionen bestimmen die Winkelrichtung",
    },
    "health": {
        "trade_object": "Heilungswirkung: Diagnose, Behandlung, Prävention, Medikamente, Pflegezeit",
        "meant_as": "Körperliche und psychische Stabilisierung nach Dringlichkeit statt Zahlungsfähigkeit",
        "products": "Medizin, Verbandstoffe, Diagnostikgeräte, Betten, Reha-Hilfen, Hygieneausstattung",
        "workplaces": "Ärzt:in; Pflege; Labor; Rettung; Therapie; Prävention; Medizintechnik-Wartung",
        "services": "Diagnose, Behandlung, Notfallversorgung, Prävention, Therapie, Rehabilitation, Gesundheitsbildung",
        "ecology": "Medizinabfälle, Wasser-/Energiebedarf und Schadstoffpfade müssen geschlossen werden",
        "climate": "Hitze, neue Krankheitslast, Notfallresilienz und klimafeste Infrastruktur fließen in Zeit/Intensität ein",
    },
    "care": {
        "trade_object": "Sorgewirkung: Pflege, Begleitung, Schutz, Zeit, Beziehung, Entlastung",
        "meant_as": "Erhaltung von Würde, Alltag, Abhängigkeitssicherheit und sozialer Bindung",
        "products": "Pflegehilfen, Rollstühle, Betten, Hygieneartikel, Assistenztechnik, barrierearme Ausstattung",
        "workplaces": "Pflegekraft; Assistenz; Sozialarbeit; Familienentlastung; Demenzbegleitung; Nachbarschaftsteam",
        "services": "Grundpflege, Betreuung, Kinderbetreuung, Altenhilfe, Behindertenassistenz, Entlastungsangebote",
        "ecology": "Kurze Wege und materialarme Fürsorge werden bevorzugt; Abfall/Hygiene muss sicher geführt werden",
        "climate": "Hitze- und Krisenvorsorge für verletzliche Menschen ist Bestandteil der Sorgeverträge",
    },
    "education": {
        "trade_object": "Bildungswirkung: Fähigkeit, Urteilskraft, Wissen, Selbstbestimmung, Zukunftspotenzial",
        "meant_as": "Entwicklung von Potenzen statt Ausbildung nur für Marktverwertbarkeit",
        "products": "Lernräume, Bücher, Geräte, Werkstätten, offene Lehrpläne, Lernmaterial, digitale Zugänge",
        "workplaces": "Lehrkraft; Mentor:in; Werkstattleitung; Bildungskoordination; Sprach-/Inklusionsarbeit",
        "services": "Unterricht, Erwachsenenbildung, berufliche Umqualifizierung, politische Bildung, offene Labore",
        "ecology": "Ökologisches Wissen, Reparaturfähigkeit und Stoffkreisläufe werden als Bildungsinhalt behandelt",
        "climate": "Klimakompetenz, Anpassungswissen und Energieverbrauch der Lerninfrastruktur werden mitgeführt",
    },
    "mobility": {
        "trade_object": "Bewegungswirkung: Zugang, Transport, Nähe, Rettungsweg, Güterfluss",
        "meant_as": "Erreichbarkeit realer Bedürfnisse statt verkaufter Kilometer oder Ticketwert",
        "products": "Fahrräder, Busse, Bahnen, Ladepunkte, Wege, Ersatzteile, Logistiksoftware, Rettungsfahrzeuge",
        "workplaces": "Fahrer:in; Streckenplanung; Fahrrad-/Bahnreparatur; Logistik; Barrierefreiheitsdienst; Rettungstransport",
        "services": "ÖPNV, Gütertransport, Notfalltransport, Schulwege, Pflegefahrten, gemeinschaftliche Lieferketten",
        "ecology": "Flächenverbrauch, Lärm, Luftschadstoffe und Zerschneidung von Lebensräumen sind Vertragsbedingungen",
        "climate": "Emission pro Bewegungswirkung, Elektrifizierung und Vermeidung unnötiger Wege bestimmen die Richtung",
    },
    "manufacturing": {
        "trade_object": "Herstellungswirkung: Werkzeuge, Ersatzteile, Maschinenfähigkeit, Reparaturbasis",
        "meant_as": "Materielle Transformationsfähigkeit ohne Profitzwang und ohne künstliche Obsoleszenz",
        "products": "Werkzeuge, Ersatzteile, Maschinenmodule, Gehäuse, Pumpen, medizinische Teile, Landwirtschaftsgeräte",
        "workplaces": "Maschinenbau; Fertigung; FabLab; Qualitätsprüfung; Materialplanung; zirkuläres Design",
        "services": "Herstellung, Umbau, Normierung, Werkzeugverleih, offene Produktionspläne, Qualitätskontrolle",
        "ecology": "Neumaterial ist nachrangig; Reparierbarkeit, Recycling und Schadstofffreiheit sind Vertragsauflage",
        "climate": "Energieintensität, Prozesswärme, Lieferwege und Materialdurchsatz begrenzen die Freigabe",
    },
    "storage": {
        "trade_object": "Speicherwirkung: Puffer, Haltbarkeit, Netzreserve, Krisenlager, Zeitbrücke",
        "meant_as": "Sicherung gegen Schwankungen, Schocks und zeitliche Ungleichheit von Bedarf und Produktion",
        "products": "Lebensmittellager, Wassertanks, Batterien, Wärmespeicher, Kühlketten, Ersatzteillager",
        "workplaces": "Lagerkoordination; Speichertechnik; Vorratsprüfung; Kühlkettenwartung; Notfalllogistik",
        "services": "Einlagerung, Haltbarkeitskontrolle, Reserveverwaltung, Netzpufferung, Priorisierung bei Krisen",
        "ecology": "Verderb, Kühlmittel, Lagerflächen und Materialeinsatz werden als Substanz-/Materiebedingungen geführt",
        "climate": "Speicher senkt Verschwendung, kann aber energie-/materialintensiv sein; beides geht in die Richtung ein",
    },
    "governance": {
        "trade_object": "Bestimmungswirkung: Entscheidung, Recht, Konfliktlösung, Schutzrechte, Wahrheitskorrektur",
        "meant_as": "Legitimation und Fehlerkorrektur der Planetenwirtschaft statt Markt-/Staatsautomatismus",
        "products": "Regeln, Protokolle, Beschlussregister, Datenschutzwerkzeuge, Auditberichte, Konfliktverfahren",
        "workplaces": "Moderation; Rechtsarbeit; Datenschutz; Bürgerrat; Mediator:in; Audit; Ombudsstelle",
        "services": "Mitbestimmung, Widerspruchsverfahren, Wahrheitsprüfung, Ressourcenfreigabe, Konfliktlösung",
        "ecology": "Ökologische Grenzen werden demokratisch überwacht und dürfen nicht überstimmt werden",
        "climate": "Klimaverträge brauchen Transparenz, Langfristigkeit und Rechte gegen Verdrängung/Technokratie",
    },
    "knowledge": {
        "trade_object": "Erkenntniswirkung: Forschung, offene Pläne, Diagnose, Simulation, Lernkurven",
        "meant_as": "Erhöhung der Potenzen und Senkung von Wahrheitsfehlern",
        "products": "Open-Source-Pläne, Messdaten, Modelle, Lehrmaterial, Bauanleitungen, Diagnoseprotokolle",
        "workplaces": "Forschung; Datenpflege; Simulation; Bibliothek; Techniktransfer; lokale Lernwerkstatt",
        "services": "Analyse, Beratung, Entwicklung, Dokumentation, Wissensübertragung, Fehlerauswertung",
        "ecology": "Wissen muss Stofffolgen sichtbar machen und darf Externalisierung nicht verstecken",
        "climate": "Klimamodelle, Anpassungswissen und Technikfolgenabschätzung sind Kerninhalte",
    },
    "resilience": {
        "trade_object": "Resilienzwirkung: Redundanz, Notfallfähigkeit, Krisenschutz, Ersatzwege",
        "meant_as": "Schutz gegen Schocks, Klimaereignisse, Lieferausfälle und soziale Brüche",
        "products": "Notlager, Funknetze, mobile Wasserfilter, Reserveenergie, Schutzräume, Evakuierungspläne",
        "workplaces": "Katastrophenschutz; Sanitätsdienst; Netzredundanz; Risikoanalyse; Gemeindeübungen; Notlogistik",
        "services": "Krisenplanung, Übungen, Notversorgung, Redundanzaufbau, Risiko-Monitoring, Wiederaufbaukoordination",
        "ecology": "Resilienz darf Natur nicht als Opferreserve behandeln; Naturpuffer gelten selbst als Schutzinfrastruktur",
        "climate": "Hitze, Flut, Dürre und Ernteausfall erhöhen Zeit/Intensität und erlauben schnellere Umverteilung",
    },
    "repair": {
        "trade_object": "Reparaturwirkung: Lebensdauer, Wiederverwendung, Ersatzteilgewinn, Kapazitätserhalt",
        "meant_as": "Auflösung materieller Differenz statt Neukauf und Wegwerfen",
        "products": "Ersatzteile, aufgearbeitete Geräte, reparierte Kleidung, Bauteile, Werkzeugsätze, Recyclingmaterial",
        "workplaces": "Reparaturwerkstatt; Kreislaufdesign; Sortierung; Instandhaltung; Elektronik-/Textil-/Bau-Reparatur",
        "services": "Reparatur, Wartung, Diagnose, Refurbishment, Materialrückgewinnung, Produktverlängerung",
        "ecology": "Reduziert Abfall, Rohstoffdruck und Schadstoffe; Schadstoffsicherheit bleibt Bedingung",
        "climate": "Senkt graue Emissionen und Materialdurchsatz; energieintensive Reparatur muss sich ökologisch lohnen",
    },
    "ecology": {
        "trade_object": "Regenerationswirkung: Boden, Biodiversität, Wasserhaushalt, Kühlung, Lebensraum",
        "meant_as": "Planetare Lebensgrundlage als aktive Wirtschaftsleistung, nicht als kostenloser Hintergrund",
        "products": "Renaturierungsflächen, Saatgut, Feuchtgebiete, Agroforst, Stadtgrün, Bodenschutzmaterial",
        "workplaces": "Ökolog:in; Renaturierungsteam; Forst-/Agroforstpflege; Gewässerpflege; Biodiversitätsmonitoring",
        "services": "Bodenaufbau, Wiedervernässung, Aufforstung, Artenmonitoring, Gewässerrenaturierung, Kühlflächenplanung",
        "ecology": "Dies ist direkt ökologische Grundfunktion; Ausbeutung darf nicht als Regeneration verbucht werden",
        "climate": "Bindung, Kühlung, Wasserrückhalt und Klimaanpassung erhöhen Winkelrichtung und Wirkung",
    },
    "waste": {
        "trade_object": "Abfalldifferenz-Auflösung: Sortierung, Schadstoffsicherung, Rückführung, Kompostierung",
        "meant_as": "Müll ist kein Nebenprodukt, sondern sichtbare ungelöste Materialdifferenz",
        "products": "Sekundärrohstoffe, Kompost, sortierte Metalle, Kunststoffe, sichere Deponieeinheiten, Reparaturmaterial",
        "workplaces": "Sortierung; Recycling; Schadstoffprüfung; Kompostierung; Kreislauflogistik; Materialaudit",
        "services": "Abholung, Trennung, Dekontamination, Rückgewinnung, Wiederverwendung, sichere Endlagerung",
        "ecology": "Schadstoffe müssen aus Boden, Wasser und Körpern herausgehalten werden; Kreislauf vor Deponie",
        "climate": "Methan, Verbrennung, Transport und vermiedene Neuproduktion bestimmen Klimawirkung",
    },
}

CONTRACT_VALIDITY_LABELS = {
    "valid": "gültig",
    "conditional": "bedingt gültig",
    "experimental": "experimentell",
    "blocked": "blockiert/neu bestimmen",
}


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < 1e-12:
        return default
    return a / b


def scale4(x: float) -> float:
    """Convert a 0..1 normalized number to the 0..4 truth scale."""
    return 4.0 * clamp(x)


def mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = list(values)
    if not vals:
        return default
    return sum(vals) / float(len(vals))


def weighted_mean(items: Iterable[Tuple[float, float]], default: float = 0.0) -> float:
    total_w = 0.0
    total = 0.0
    for value, weight in items:
        total += value * weight
        total_w += weight
    if total_w <= 1e-12:
        return default
    return total / total_w


def weighted_gini(items: Iterable[Tuple[float, float]]) -> float:
    """Weighted Gini for inequality of satisfaction/wellbeing.

    0 means equal distribution. 1 would mean maximum inequality.
    This is distributional diagnostics, not moral value in money terms.
    """
    data = [(max(0.0, v), max(0.0, w)) for v, w in items if w > 0.0]
    if not data:
        return 0.0
    data.sort(key=lambda x: x[0])
    total_w = sum(w for _, w in data)
    total_xw = sum(v * w for v, w in data)
    if total_w <= 1e-12 or total_xw <= 1e-12:
        return 0.0
    cum_w = 0.0
    cum_xw = 0.0
    area = 0.0
    prev_w_share = 0.0
    prev_x_share = 0.0
    for value, weight in data:
        cum_w += weight
        cum_xw += value * weight
        w_share = cum_w / total_w
        x_share = cum_xw / total_xw
        area += (x_share + prev_x_share) * (w_share - prev_w_share) / 2.0
        prev_w_share = w_share
        prev_x_share = x_share
    return clamp(1.0 - 2.0 * area)


def normalized_need_gap(need: float, available: float) -> float:
    """0 means covered, 1 means almost completely missing."""
    if need <= 1e-12:
        return 0.0
    return clamp((need - available) / need)


def sat_ratio(available: float, need: float) -> float:
    if need <= 1e-12:
        return 1.0
    return clamp(available / need)


def lognormal_near(rng: random.Random, center: float, spread: float) -> float:
    """Small helper to avoid relying on statistics/numpy."""
    return center * math.exp(rng.gauss(0.0, spread))


def format_big(x: float) -> str:
    abs_x = abs(x)
    if abs_x >= 1_000_000_000:
        return "%.3fb" % (x / 1_000_000_000.0)
    if abs_x >= 1_000_000:
        return "%.3fm" % (x / 1_000_000.0)
    if abs_x >= 1_000:
        return "%.3fk" % (x / 1_000.0)
    return "%.3f" % x


def truth_digit(value: float) -> int:
    """Convert a 0..4 truth value to a stacked digit 0..4."""
    return int(round(clamp(value, 0.0, 4.0)))


def truth_stack_score_0_4(values: Dict[str, float]) -> float:
    """Weighted stacked truth score on 0..4 scale. Not price, not value."""
    total = 0.0
    weight_sum = 0.0
    for dim in TRUTH_DIMS:
        weight = TRUTH_WEIGHTS.get(dim, 0.0)
        total += clamp(values.get(dim, 0.0), 0.0, 4.0) * weight
        weight_sum += weight
    if weight_sum <= 0.0:
        return 0.0
    return total / weight_sum


def truth_stack_base5(values: Dict[str, float]) -> str:
    """Stack the 12 dimensions into a base-5 code in TRUTH_DIMS order.

    Example: 343233223433 means:
    causality=3, time=4, intensity=3, ... angle_direction=3.
    This is a number-like truth signature, not money.
    """
    return "".join(str(truth_digit(values.get(dim, 0.0))) for dim in TRUTH_DIMS)


def truth_stack_decimal(values: Dict[str, float]) -> int:
    code = truth_stack_base5(values)
    try:
        return int(code, 5)
    except ValueError:
        return 0


def compact_truth_stack(values: Dict[str, float]) -> str:
    parts = []
    for dim in TRUTH_DIMS:
        guide = DIMENSION_GUIDE_DE.get(dim, {})
        short = guide.get("short", dim[:2])
        parts.append("%s=%.2f" % (short, clamp(values.get(dim, 0.0), 0.0, 4.0)))
    return " | ".join(parts)


def dimension_meaning_summary(values: Dict[str, float]) -> str:
    """Readable interpretation of the strongest and weakest dimensions."""
    if not values:
        return "keine Wahrheitswerte vorhanden"
    sorted_dims = sorted(TRUTH_DIMS, key=lambda d: values.get(d, 0.0), reverse=True)
    strongest = sorted_dims[:3]
    weakest = sorted_dims[-3:]
    strong_txt = ", ".join("%s %.2f" % (DIMENSION_GUIDE_DE[d]["name_de"], values.get(d, 0.0)) for d in strongest)
    weak_txt = ", ".join("%s %.2f" % (DIMENSION_GUIDE_DE[d]["name_de"], values.get(d, 0.0)) for d in weakest)
    return "stark: %s; schwach/zu prüfen: %s" % (strong_txt, weak_txt)


def contract_conditions_for_flow(kind: str, domain: str, values: Dict[str, float]) -> Tuple[str, str]:
    """Return (validity, condition_text) for a non-monetary contract."""
    if not values:
        return "experimental", "Wahrheitswerte fehlen; nur als beobachtender Versuch zulässig."

    conditions: List[str] = []
    causality = values.get("causality", 0.0)
    time_v = values.get("time", 0.0)
    intensity = values.get("intensity", 0.0)
    existence = values.get("existence", 0.0)
    potencies = values.get("potencies", 0.0)
    effects = values.get("effects", 0.0)
    substance = values.get("substance", 0.0)
    matter = values.get("matter", 0.0)
    difference = values.get("difference", 0.0)
    determination = values.get("determination", 0.0)
    phenomena = values.get("phenomena", 0.0)
    angle = values.get("angle_direction", 0.0)

    if causality < 1.6:
        conditions.append("Kausalität niedrig: erst Ursachenprüfung, Pilotversuch oder lokale Diagnose.")
    elif causality >= 3.0:
        conditions.append("Kausalität hoch: Wirkungskette ist plausibel und darf priorisiert werden.")
    else:
        conditions.append("Kausalität mittel: Vertrag enthält Audit- und Korrekturpflicht.")

    if time_v >= 3.0:
        conditions.append("Zeit hoch: Notfall-/Schnellpfad, kurze Frist, spätere Nachprüfung.")
    elif time_v < 1.5:
        conditions.append("Zeit niedrig: planbar, keine Notfallverdrängung anderer Felder.")

    if intensity >= 3.0:
        conditions.append("Intensität hoch: Einsatzstärke darf über Normalanteil steigen.")
    if existence < 1.5:
        conditions.append("Existenz unsicher: Betroffenenberichte und Messung nachfordern.")
    if potencies < 1.8:
        conditions.append("Potenzen knapp: zuerst Fähigkeiten, Werkzeuge oder Gruppenfähigkeit aufbauen.")
    if effects >= 3.0:
        conditions.append("Wirkung hoch: positive Systemfolge wird als gesellschaftlicher Nutzen anerkannt.")
    if substance < 1.8:
        conditions.append("Substanz knapp: Stofffreigabe begrenzen, Kreislauf-/Ersatzquelle sichern.")
    if matter < 1.8:
        conditions.append("Materie/Ort ungünstig: Logistik, Nähe oder lokale Infrastruktur klären.")
    if difference >= 3.0:
        conditions.append("Differenz hoch: reale Lücke zwischen Bedarf und Zustand legitimiert Handlung.")
    elif difference < 1.2 and kind != "contribution_offer":
        conditions.append("Differenz niedrig: keine Vorrangbehandlung; nur Erhaltung oder Prävention.")
    if determination < 1.8:
        conditions.append("Bestimmung schwach: demokratische Rückkopplung/Widerspruchsrecht erforderlich.")
    if phenomena < 1.6:
        conditions.append("Phänomenlage schwach: Sichtbarkeit/Meldungen/Audit verbessern.")
    if angle < 1.5:
        conditions.append("Winkelrichtung negativ: Handlung neu entwerfen, ökologische/soziale Schäden verhindern.")
    elif angle >= 3.0:
        conditions.append("Winkelrichtung regenerativ: Handlung passt zur planetaren Richtung.")
    else:
        conditions.append("Winkelrichtung bedingt: Nebenfolgen und Klimawirkung begrenzen.")

    cat = TRADE_CATALOG.get(domain, {})
    if cat.get("ecology"):
        conditions.append("Ökologiebedingung: %s" % cat["ecology"])
    if cat.get("climate"):
        conditions.append("Klimabedingung: %s" % cat["climate"])

    # Hard validity logic. A contract can be urgent and still blocked if its
    # direction is destructive or if the causal claim is too weak.
    if angle < 1.2 or (causality < 1.2 and effects < 2.0):
        validity = "blocked"
    elif causality < 1.8 or existence < 1.5 or determination < 1.5:
        validity = "experimental"
    elif substance < 1.6 or matter < 1.6 or angle < 2.1 or potencies < 1.6:
        validity = "conditional"
    else:
        validity = "valid"
    return validity, " ".join(conditions)


def catalog_value(domain: str, key: str) -> str:
    return TRADE_CATALOG.get(domain, {}).get(key, "")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class TruthVector:
    """Stacked logical truth values on a 0..4 scale."""

    domain: str
    values: Dict[str, float]
    commune: str = ""
    region: str = ""
    explanation: str = ""

    def priority(self) -> float:
        """Priority is not price. It is weighted urgency/effect/difference."""
        total = 0.0
        weight_sum = 0.0
        for dim in TRUTH_DIMS:
            weight = TRUTH_WEIGHTS.get(dim, 0.0)
            total += clamp(self.values.get(dim, 0.0), 0.0, 4.0) * weight
            weight_sum += weight
        if weight_sum <= 0.0:
            return 0.0
        return total / (4.0 * weight_sum)

    def as_row(self, step: int) -> Dict[str, object]:
        row = {
            "step": step,
            "region": self.region,
            "commune": self.commune,
            "domain": self.domain,
            "priority": round(self.priority(), 6),
            "explanation": self.explanation,
        }
        for dim in TRUTH_DIMS:
            row[dim] = round(self.values.get(dim, 0.0), 6)
        return row


@dataclass
class EffectFlow:
    """A non-market action record.

    It replaces buy/sell/import/export with causal effect activation:
    - need_acceptance: what older language would call buying/consuming
    - contribution_offer: what older language would call selling/labour supply
    - planetary_transfer: what older language would call trade/import/export

    The numeric field is called activated_effect, not price, worth or value.
    """

    step: int
    kind: str
    legacy_term_replaced: str
    action: str
    domain: str
    sector: str
    from_region: str
    from_commune: str
    to_region: str
    to_commune: str
    activated_effect: float
    causal_link: str
    direction_vector: str
    values: Dict[str, float]
    note: str = ""
    trade_object: str = ""
    meant_as: str = ""
    product_examples: str = ""
    workplace_examples: str = ""
    service_examples: str = ""
    ecological_clause: str = ""
    climate_clause: str = ""
    contract_validity: str = ""
    contract_conditions: str = ""
    truth_stack_score_0_4: float = 0.0
    truth_stack_priority_0_1: float = 0.0
    truth_stack_base5: str = ""
    truth_stack_decimal: int = 0
    truth_stack_compact: str = ""
    dimension_meaning: str = ""

    def as_row(self) -> Dict[str, object]:
        row = {
            "step": self.step,
            "kind": self.kind,
            "legacy_term_replaced": self.legacy_term_replaced,
            "action": self.action,
            "domain": self.domain,
            "sector": self.sector,
            "trade_object": self.trade_object,
            "meant_as": self.meant_as,
            "product_examples": self.product_examples,
            "workplace_examples": self.workplace_examples,
            "service_examples": self.service_examples,
            "ecological_clause": self.ecological_clause,
            "climate_clause": self.climate_clause,
            "contract_validity": self.contract_validity,
            "contract_conditions": self.contract_conditions,
            "truth_stack_score_0_4": round(self.truth_stack_score_0_4, 6),
            "truth_stack_priority_0_1": round(self.truth_stack_priority_0_1, 6),
            "truth_stack_base5": self.truth_stack_base5,
            "truth_stack_decimal": self.truth_stack_decimal,
            "truth_stack_compact": self.truth_stack_compact,
            "dimension_meaning": self.dimension_meaning,
            "from_region": self.from_region,
            "from_commune": self.from_commune,
            "to_region": self.to_region,
            "to_commune": self.to_commune,
            "activated_effect": round(self.activated_effect, 6),
            "causal_link": self.causal_link,
            "direction_vector": self.direction_vector,
            "note": self.note,
        }
        for dim in TRUTH_DIMS:
            row[dim] = round(self.values.get(dim, 0.0), 6)
        return row


@dataclass
class MacroAccountRow:
    """Planetary macro-account row without monetary value categories."""

    step: int
    domain: str
    sector: str
    need: float
    available: float
    gap: float
    satisfaction: float
    priority: float
    labor_share: float
    contribution_time: float
    stock_or_capacity: float
    boundary_penalty: float
    truth_error: float
    democratic_quality: float
    activated_flows: int

    def as_row(self) -> Dict[str, object]:
        return {
            "step": self.step,
            "domain": self.domain,
            "sector": self.sector,
            "need": round(self.need, 6),
            "available": round(self.available, 6),
            "gap": round(self.gap, 6),
            "satisfaction": round(self.satisfaction, 6),
            "priority": round(self.priority, 6),
            "labor_share": round(self.labor_share, 6),
            "contribution_time": round(self.contribution_time, 6),
            "stock_or_capacity": round(self.stock_or_capacity, 6),
            "boundary_penalty": round(self.boundary_penalty, 6),
            "truth_error": round(self.truth_error, 6),
            "democratic_quality": round(self.democratic_quality, 6),
            "activated_flows": self.activated_flows,
        }


@dataclass
class BoundaryState:
    """Planetary operating space. Values are pressures; >1.0 means overshoot."""

    pressures: Dict[str, float]

    def overshoot(self) -> float:
        return sum(max(0.0, self.pressures.get(name, 0.0) - 1.0) for name in BOUNDARY_NAMES)

    def mean_pressure(self) -> float:
        return mean(self.pressures.get(name, 0.0) for name in BOUNDARY_NAMES)

    def worst(self) -> Tuple[str, float]:
        if not self.pressures:
            return "none", 0.0
        return max(self.pressures.items(), key=lambda kv: kv[1])

    def penalty(self) -> float:
        """Overshoot reduces system effectiveness but never makes action impossible."""
        overs = self.overshoot()
        # Smooth penalty. At zero overshoot = 1.0, at severe overshoot maybe ~0.55.
        return clamp(1.0 / (1.0 + 0.33 * overs), 0.45, 1.0)

    def apply_impacts(self, impacts: Dict[str, float], regeneration: Dict[str, float]) -> None:
        # Scale constants keep values stable for synthetic runs.
        for name in BOUNDARY_NAMES:
            before = self.pressures.get(name, 0.7)
            pressure = before
            pressure += impacts.get(name, 0.0)
            pressure -= regeneration.get(name, 0.0)
            # Natural repair is slow if under low pressure; degradation is sticky above 1.
            if pressure < 0.75:
                pressure += 0.005 * (0.75 - pressure)
            if pressure > 1.0:
                pressure += 0.002 * (pressure - 1.0)
            self.pressures[name] = clamp(pressure, 0.2, 2.2)


@dataclass
class PopulationCohort:
    name: str
    size: float
    health: float
    education: float
    autonomy: float
    trust: float
    skill: Dict[str, float]
    age_factor: float = 1.0

    def productive_time(self) -> float:
        # Labour is not bought/sold. This is available contribution time.
        return self.size * self.age_factor * clamp(0.35 + 0.65 * self.health) * clamp(0.45 + 0.55 * self.autonomy)

    def update_from_satisfaction(self, satisfaction: Dict[str, float], governance_quality: float, privacy_pressure: float) -> None:
        basic = 0.40 * satisfaction.get("water", 1.0) + 0.35 * satisfaction.get("food", 1.0) + 0.25 * satisfaction.get("shelter", 1.0)
        service = 0.45 * satisfaction.get("health", 1.0) + 0.25 * satisfaction.get("care", 1.0) + 0.20 * satisfaction.get("education", 1.0) + 0.10 * satisfaction.get("mobility", 1.0)
        civic = 0.34 * satisfaction.get("governance", 1.0) + 0.33 * satisfaction.get("knowledge", 1.0) + 0.33 * satisfaction.get("resilience", 1.0)
        energy = satisfaction.get("energy", 1.0)
        # Health moves slowly; severe basic deficits hit it fast.
        health_delta = 0.018 * (basic - 0.78) + 0.010 * (service - 0.75) + 0.006 * (energy - 0.70)
        self.health = clamp(self.health + health_delta, 0.05, 1.0)
        # Education responds to education satisfaction, not instantly.
        self.education = clamp(self.education + 0.006 * (satisfaction.get("education", 1.0) - 0.55) + 0.003 * (satisfaction.get("knowledge", 1.0) - 0.55), 0.05, 1.0)
        # Autonomy drops under unmet basics and high privacy/control pressure; it rises with civic capability.
        self.autonomy = clamp(self.autonomy + 0.010 * (mean(satisfaction.values(), 0.9) - 0.72) + 0.006 * (civic - 0.65) - 0.018 * privacy_pressure, 0.05, 1.0)
        # Trust is a local truth-feedback quality. It falls when the system claims truth but fails people.
        self.trust = clamp(self.trust + 0.018 * (mean(satisfaction.values(), 0.9) - 0.70) + 0.016 * (governance_quality - 0.5) + 0.008 * (civic - 0.65) - 0.012 * privacy_pressure, 0.02, 1.0)
        # Skills improve with education and degrade slowly if health is bad.
        for k in list(self.skill.keys()):
            self.skill[k] = clamp(self.skill[k] + 0.003 * (self.education - 0.5) + 0.002 * (self.health - 0.5), 0.05, 1.0)


@dataclass
class Commune:
    name: str
    region_name: str
    biome: str
    cohorts: List[PopulationCohort]
    stocks: Dict[str, float]
    capacities: Dict[str, float]
    environment: Dict[str, float]
    group_base: Dict[str, float]
    democratic_quality: float
    truth_error: float = 0.15
    last_satisfaction: Dict[str, float] = field(default_factory=dict)
    last_priorities: Dict[str, float] = field(default_factory=dict)
    last_labor_shares: Dict[str, float] = field(default_factory=dict)
    last_truth_values: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def population(self) -> float:
        return sum(c.size for c in self.cohorts)

    def productive_time(self) -> float:
        return sum(c.productive_time() for c in self.cohorts)

    def average_health(self) -> float:
        return weighted_mean(((c.health, c.size) for c in self.cohorts), default=0.7)

    def average_education(self) -> float:
        return weighted_mean(((c.education, c.size) for c in self.cohorts), default=0.6)

    def average_autonomy(self) -> float:
        return weighted_mean(((c.autonomy, c.size) for c in self.cohorts), default=0.7)

    def average_trust(self) -> float:
        return weighted_mean(((c.trust, c.size) for c in self.cohorts), default=0.6)

    def skill(self, field_name: str) -> float:
        return weighted_mean(((c.skill.get(field_name, 0.4), c.size) for c in self.cohorts), default=0.4)

    def need(self, domain: str) -> float:
        pop = self.population()
        if domain == "health":
            # More need if health is low.
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.75 * (1.0 - self.average_health()))
        if domain == "care":
            child_elder_share = 0.0
            for c in self.cohorts:
                if c.name in ("children", "elders"):
                    child_elder_share += c.size
            dependency = safe_div(child_elder_share, pop, 0.33)
            return pop * NEED_PER_PERSON[domain] * (0.65 + 1.35 * dependency)
        if domain == "education":
            # Higher education demand if education is low; still lifelong education if high.
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.75 * (1.0 - self.average_education()))
        if domain == "mobility":
            return pop * NEED_PER_PERSON[domain] * (0.8 + 0.3 * self.environment.get("remoteness", 0.5))
        if domain == "governance":
            # Coordination need rises with complexity, low trust and truth error.
            complexity = 0.45 + 0.35 * self.environment.get("remoteness", 0.5) + 0.20 * self.truth_error
            legitimacy_gap = 1.0 - 0.5 * self.democratic_quality - 0.5 * self.average_trust()
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.55 * complexity + 0.60 * max(0.0, legitimacy_gap))
        if domain == "knowledge":
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.65 * (1.0 - self.average_education()) + 0.25 * (1.0 - self.environment.get("renewable_infrastructure", 0.5)))
        if domain == "manufacturing":
            repair_gap = normalized_need_gap(max(1.0, pop * 0.18), self.stocks.get("repair_materials", 0.0))
            capacity_gap = normalized_need_gap(max(1.0, pop * NEED_PER_PERSON[domain]), self.capacities.get("manufacturing", 0.0))
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.65 * repair_gap + 0.40 * capacity_gap)
        if domain == "storage":
            basic_need = self.need("water") + self.need("food") + self.need("energy")
            basic_stock = self.stocks.get("water", 0.0) + self.stocks.get("food", 0.0) + self.stocks.get("energy", 0.0)
            buffer_gap = normalized_need_gap(1.20 * basic_need, basic_stock)
            return pop * NEED_PER_PERSON[domain] * (0.70 + 1.10 * buffer_gap)
        if domain == "resilience":
            climate_exposure = self.environment.get("local_pollution", 0.2) + (1.0 - self.environment.get("watershed", 0.7))
            buffer_gap = normalized_need_gap(max(1.0, pop * 0.60), self.stocks.get("water", 0.0) + self.stocks.get("food", 0.0))
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.45 * climate_exposure + 0.55 * buffer_gap)
        if domain in NEED_PER_PERSON:
            return pop * NEED_PER_PERSON[domain]
        return 0.0

    def available_for_need(self, domain: str) -> float:
        if domain in CONSUMABLE_DOMAINS:
            return self.stocks.get(domain, 0.0)
        if domain in SERVICE_DOMAINS:
            return self.capacities.get(domain, 0.0)
        if domain in CAPACITY_DOMAINS:
            return self.capacities.get(domain, 0.0)
        if domain == "repair":
            return self.stocks.get("repair_materials", 0.0)
        if domain == "ecology":
            # Deficit relative to healthy ecosystems.
            pop = self.population()
            soil_gap = max(0.0, 1.0 - self.environment.get("soil_health", 0.7))
            bio_gap = max(0.0, 1.0 - self.environment.get("biodiversity", 0.7))
            water_gap = max(0.0, 1.0 - self.environment.get("watershed", 0.7))
            return pop * (1.0 - mean([soil_gap, bio_gap, water_gap]))
        if domain == "waste":
            return self.stocks.get("waste", 0.0)
        return 0.0

    def ecology_need(self) -> float:
        pop = self.population()
        soil_gap = max(0.0, 1.0 - self.environment.get("soil_health", 0.7))
        bio_gap = max(0.0, 1.0 - self.environment.get("biodiversity", 0.7))
        water_gap = max(0.0, 1.0 - self.environment.get("watershed", 0.7))
        pollution = self.environment.get("local_pollution", 0.25)
        return pop * (0.18 + 0.50 * mean([soil_gap, bio_gap, water_gap, pollution]))

    def waste_need(self) -> float:
        # Waste is an unresolved material difference. High stock => high need.
        return max(1.0, self.population() * 0.10)

    def truth_vector(self, domain: str, global_boundary: BoundaryState, planner: "EffectPlanner") -> TruthVector:
        pop = self.population()
        env_penalty = 1.0 - global_boundary.penalty()
        if domain == "ecology":
            need = self.ecology_need()
            # Ecology availability is environmental integrity.
            available = max(0.0, pop * mean([
                self.environment.get("soil_health", 0.7),
                self.environment.get("biodiversity", 0.7),
                self.environment.get("watershed", 0.7),
                1.0 - self.environment.get("local_pollution", 0.2),
            ]))
            gap = clamp(need / max(pop * 0.70, 1.0))
        elif domain == "waste":
            need = self.waste_need()
            available = max(0.0, need - self.stocks.get("waste", 0.0))
            gap = clamp(self.stocks.get("waste", 0.0) / max(need, 1.0))
        else:
            need = self.need(domain)
            available = self.available_for_need(domain)
            gap = normalized_need_gap(need, available)

        domain_skill = self.skill(planner.skill_for_domain(domain))
        group_strength = self.group_base.get(planner.group_for_domain(domain), 0.4)
        local_potencies = clamp(0.45 * domain_skill + 0.35 * group_strength + 0.20 * self.democratic_quality)
        substance = clamp(0.35 * sat_ratio(self.stocks.get("repair_materials", 0.0), max(1.0, pop * 0.05)) +
                          0.25 * sat_ratio(self.stocks.get("energy", 0.0), max(1.0, self.need("energy") * 0.35)) +
                          0.20 * self.environment.get("watershed", 0.7) +
                          0.20 * self.environment.get("soil_health", 0.7))
        matter = clamp(0.55 * (1.0 - self.environment.get("remoteness", 0.5)) + 0.45 * sat_ratio(self.capacities.get("mobility", 0.0), max(1.0, self.need("mobility"))))
        criticality = planner.domain_criticality.get(domain, 0.5)
        time_urgency = clamp(0.45 * gap + 0.40 * criticality + 0.15 * env_penalty)
        intensity = clamp(0.70 * gap + 0.20 * criticality + 0.10 * (1.0 - self.average_health()))
        # Democracy should influence determination, but not allow a majority to erase critical needs.
        collective_claim = clamp(0.55 * gap + 0.25 * self.democratic_quality + 0.20 * self.average_trust())
        # Phenomena combines measured and reported reality; truth_error is noise/uncertainty.
        phenomena = clamp(gap * (1.0 - 0.50 * self.truth_error) + self.average_trust() * 0.15 + self.democratic_quality * 0.10)
        angle = planner.angle_alignment(domain, global_boundary, self)
        values = {
            "causality": scale4(planner.causal_confidence.get(domain, 0.65)),
            "time": scale4(time_urgency),
            "intensity": scale4(intensity),
            "existence": scale4(clamp(0.7 * gap + 0.3 * criticality)),
            "potencies": scale4(local_potencies),
            "effects": scale4(planner.effect_weight.get(domain, 0.6)),
            "substance": scale4(substance),
            "matter": scale4(matter),
            "difference": scale4(gap),
            "determination": scale4(collective_claim),
            "phenomena": scale4(phenomena),
            "angle_direction": scale4(angle),
        }
        return TruthVector(
            domain=domain,
            values=values,
            commune=self.name,
            region=self.region_name,
            explanation="need_gap=%.3f potencies=%.3f trust=%.3f boundary_penalty=%.3f" % (
                gap, local_potencies, self.average_trust(), global_boundary.penalty()
            ),
        )

    def update_truth_error(self, avg_satisfaction: float, planner: "EffectPlanner") -> None:
        # More democratic feedback and trust reduces truth error. High centralization raises it.
        correction = 0.018 * self.democratic_quality * self.average_trust() * planner.democratic_feedback
        failure = 0.014 * max(0.0, 0.68 - avg_satisfaction)
        central_error = 0.010 * planner.centralization * (1.0 - self.democratic_quality)
        self.truth_error = clamp(self.truth_error - correction + failure + central_error, 0.02, 0.75)


@dataclass
class Region:
    name: str
    biome: str
    communes: List[Commune]
    logistic_hub: float
    climate_risk: float

    def population(self) -> float:
        return sum(c.population() for c in self.communes)


@dataclass
class GlobalMetrics:
    step: int
    population: float
    wellbeing: float
    unmet_basic: float
    avg_trust: float
    avg_autonomy: float
    avg_health: float
    avg_education: float
    avg_truth_error: float
    overshoot: float
    mean_boundary_pressure: float
    worst_boundary: str
    worst_boundary_pressure: float
    waste_stock: float
    repair_materials: float
    food_stock: float
    water_stock: float
    energy_stock: float
    global_transfers: float
    contribution_time: float
    contribution_time_per_person: float
    satisfaction_inequality: float
    resilience_index: float
    circularity_index: float
    coordination_quality: float
    basic_buffer_months: float
    macro_capacity: float
    planetary_reproduction_index: float

    def as_row(self) -> Dict[str, object]:
        return {
            "step": self.step,
            "population": round(self.population, 3),
            "wellbeing": round(self.wellbeing, 6),
            "unmet_basic": round(self.unmet_basic, 6),
            "avg_trust": round(self.avg_trust, 6),
            "avg_autonomy": round(self.avg_autonomy, 6),
            "avg_health": round(self.avg_health, 6),
            "avg_education": round(self.avg_education, 6),
            "avg_truth_error": round(self.avg_truth_error, 6),
            "overshoot": round(self.overshoot, 6),
            "mean_boundary_pressure": round(self.mean_boundary_pressure, 6),
            "worst_boundary": self.worst_boundary,
            "worst_boundary_pressure": round(self.worst_boundary_pressure, 6),
            "waste_stock": round(self.waste_stock, 3),
            "repair_materials": round(self.repair_materials, 3),
            "food_stock": round(self.food_stock, 3),
            "water_stock": round(self.water_stock, 3),
            "energy_stock": round(self.energy_stock, 3),
            "global_transfers": round(self.global_transfers, 3),
            "contribution_time": round(self.contribution_time, 3),
            "contribution_time_per_person": round(self.contribution_time_per_person, 6),
            "satisfaction_inequality": round(self.satisfaction_inequality, 6),
            "resilience_index": round(self.resilience_index, 6),
            "circularity_index": round(self.circularity_index, 6),
            "coordination_quality": round(self.coordination_quality, 6),
            "basic_buffer_months": round(self.basic_buffer_months, 6),
            "macro_capacity": round(self.macro_capacity, 3),
            "planetary_reproduction_index": round(self.planetary_reproduction_index, 6),
        }


# ---------------------------------------------------------------------------
# Planner / policy logic
# ---------------------------------------------------------------------------


@dataclass
class EffectPlanner:
    """Coordinates effects, not prices."""

    democratic_feedback: float = 0.75
    centralization: float = 0.30
    privacy_pressure: float = 0.10
    cooperation: float = 0.82
    sufficiency_norm: float = 0.80
    climate_discipline: float = 0.78
    redistribution_strength: float = 0.85
    innovation_rate: float = 0.40
    logistics_efficiency: float = 0.76
    renewable_bias: float = 0.72

    domain_criticality: Dict[str, float] = field(default_factory=lambda: {
        "water": 1.00,
        "food": 0.95,
        "energy": 0.78,
        "shelter": 0.86,
        "health": 0.90,
        "care": 0.76,
        "education": 0.62,
        "mobility": 0.50,
        "manufacturing": 0.66,
        "storage": 0.64,
        "governance": 0.74,
        "knowledge": 0.68,
        "resilience": 0.82,
        "repair": 0.58,
        "ecology": 0.92,
        "waste": 0.70,
    })

    causal_confidence: Dict[str, float] = field(default_factory=lambda: {
        "water": 0.88,
        "food": 0.82,
        "energy": 0.78,
        "shelter": 0.73,
        "health": 0.76,
        "care": 0.81,
        "education": 0.70,
        "mobility": 0.66,
        "manufacturing": 0.72,
        "storage": 0.77,
        "governance": 0.67,
        "knowledge": 0.69,
        "resilience": 0.63,
        "repair": 0.82,
        "ecology": 0.69,
        "waste": 0.84,
    })

    effect_weight: Dict[str, float] = field(default_factory=lambda: {
        "water": 0.97,
        "food": 0.94,
        "energy": 0.80,
        "shelter": 0.88,
        "health": 0.91,
        "care": 0.80,
        "education": 0.75,
        "mobility": 0.57,
        "manufacturing": 0.74,
        "storage": 0.77,
        "governance": 0.86,
        "knowledge": 0.82,
        "resilience": 0.88,
        "repair": 0.72,
        "ecology": 0.96,
        "waste": 0.76,
    })

    def group_for_domain(self, domain: str) -> str:
        mapping = {
            "water": "water",
            "food": "agriculture",
            "energy": "energy",
            "shelter": "housing",
            "health": "health",
            "care": "care",
            "education": "education",
            "mobility": "logistics",
            "manufacturing": "manufacturing",
            "storage": "storage",
            "governance": "governance",
            "knowledge": "knowledge",
            "resilience": "resilience",
            "repair": "repair",
            "ecology": "ecology",
            "waste": "repair",
        }
        return mapping.get(domain, domain)

    def skill_for_domain(self, domain: str) -> str:
        mapping = {
            "water": "infrastructure",
            "food": "agriculture",
            "energy": "energy",
            "shelter": "construction",
            "health": "health",
            "care": "care",
            "education": "education",
            "mobility": "logistics",
            "manufacturing": "manufacturing",
            "storage": "storage",
            "governance": "governance",
            "knowledge": "knowledge",
            "resilience": "resilience",
            "repair": "repair",
            "ecology": "ecology",
            "waste": "repair",
        }
        return mapping.get(domain, "general")

    def angle_alignment(self, domain: str, boundary: BoundaryState, commune: Commune) -> float:
        # Positive direction means the action solves need while respecting planetary boundaries.
        overs = boundary.overshoot()
        climate = boundary.pressures.get("climate", 0.9)
        pollution = boundary.pressures.get("pollution", 0.8)
        material = boundary.pressures.get("material_throughput", 0.8)
        if domain in ("ecology", "repair", "waste"):
            return clamp(0.82 + 0.16 * min(1.0, overs))
        if domain in ("water", "food", "health", "care"):
            return clamp(0.78 - 0.08 * max(0.0, material - 1.0) + 0.06 * commune.democratic_quality)
        if domain == "energy":
            return clamp(0.55 + 0.35 * self.renewable_bias - 0.20 * max(0.0, climate - 1.0))
        if domain == "mobility":
            return clamp(0.58 + 0.18 * self.logistics_efficiency - 0.16 * max(0.0, climate - 1.0) - 0.08 * max(0.0, pollution - 1.0))
        if domain == "shelter":
            # Repair/reuse shelter is better than new material throughput.
            reuse = sat_ratio(commune.stocks.get("repair_materials", 0.0), max(1.0, commune.population() * 0.10))
            return clamp(0.58 + 0.20 * reuse - 0.12 * max(0.0, material - 1.0))
        if domain == "manufacturing":
            circular = sat_ratio(commune.stocks.get("repair_materials", 0.0), max(1.0, commune.population() * 0.18))
            return clamp(0.50 + 0.25 * circular + 0.18 * self.sufficiency_norm - 0.18 * max(0.0, material - 1.0))
        if domain == "storage":
            return clamp(0.68 + 0.20 * self.sufficiency_norm - 0.06 * max(0.0, material - 1.0))
        if domain in ("governance", "knowledge", "resilience"):
            democratic_direction = 0.50 + 0.35 * commune.democratic_quality + 0.20 * self.democratic_feedback - 0.22 * self.privacy_pressure
            if domain == "resilience":
                democratic_direction += 0.10 * min(1.0, overs)
            return clamp(democratic_direction)
        return clamp(0.65 - 0.08 * max(0.0, overs))

    def labor_shares(self, truth_vectors: List[TruthVector], commune: Commune, boundary: BoundaryState) -> Dict[str, float]:
        # Base shares prevent neglect of long-term fields. Priorities redirect contribution time.
        base = {
            "water": 0.070,
            "food": 0.120,
            "energy": 0.085,
            "shelter": 0.070,
            "health": 0.085,
            "care": 0.075,
            "education": 0.065,
            "mobility": 0.050,
            "manufacturing": 0.060,
            "storage": 0.040,
            "governance": 0.045,
            "knowledge": 0.045,
            "resilience": 0.050,
            "repair": 0.070,
            "ecology": 0.095,
            "waste": 0.070,
        }
        priority = {tv.domain: tv.priority() for tv in truth_vectors}
        # Planetary overshoot boosts ecology/repair/waste and moderates material-heavy sectors.
        overs = boundary.overshoot()
        for domain in ("ecology", "repair", "waste", "resilience", "storage"):
            priority[domain] = priority.get(domain, 0.0) + 0.16 * min(1.0, overs)
        if boundary.pressures.get("material_throughput", 0.0) > 1.0:
            priority["repair"] = priority.get("repair", 0.0) + 0.08
            priority["manufacturing"] = max(0.0, priority.get("manufacturing", 0.0) - 0.05)
        if boundary.pressures.get("climate", 0.0) > 1.0:
            priority["energy"] = priority.get("energy", 0.0) + 0.10 * self.renewable_bias
            priority["resilience"] = priority.get("resilience", 0.0) + 0.06
            priority["mobility"] = priority.get("mobility", 0.0) - 0.04 * boundary.pressures.get("climate", 1.0)
        # Centralization dampens local truth. Democratic feedback amplifies it.
        local_weight = clamp(0.45 + 0.45 * commune.democratic_quality * self.democratic_feedback - 0.25 * self.centralization)
        raw = {}
        for d in DOMAINS:
            raw[d] = max(0.005, base[d] * (1.0 - local_weight) + priority.get(d, 0.0) * local_weight)
        total = sum(raw.values())
        return {d: raw[d] / total for d in DOMAINS}


# ---------------------------------------------------------------------------
# Synthetic planet generator
# ---------------------------------------------------------------------------


BIOME_LIBRARY = {
    "equatorial_forest": {
        "soil_health": 0.78, "biodiversity": 0.92, "watershed": 0.88, "solar": 0.75,
        "wind": 0.42, "agri": 0.58, "remoteness": 0.45, "pollution": 0.22,
    },
    "temperate_mixed": {
        "soil_health": 0.72, "biodiversity": 0.63, "watershed": 0.70, "solar": 0.55,
        "wind": 0.62, "agri": 0.78, "remoteness": 0.28, "pollution": 0.34,
    },
    "drylands": {
        "soil_health": 0.43, "biodiversity": 0.48, "watershed": 0.32, "solar": 0.90,
        "wind": 0.58, "agri": 0.38, "remoteness": 0.52, "pollution": 0.25,
    },
    "coastal_delta": {
        "soil_health": 0.67, "biodiversity": 0.70, "watershed": 0.78, "solar": 0.68,
        "wind": 0.66, "agri": 0.82, "remoteness": 0.20, "pollution": 0.38,
    },
    "mountain_water": {
        "soil_health": 0.60, "biodiversity": 0.72, "watershed": 0.90, "solar": 0.62,
        "wind": 0.70, "agri": 0.42, "remoteness": 0.66, "pollution": 0.18,
    },
    "urban_corridor": {
        "soil_health": 0.42, "biodiversity": 0.32, "watershed": 0.55, "solar": 0.58,
        "wind": 0.50, "agri": 0.25, "remoteness": 0.12, "pollution": 0.55,
    },
    "steppe_grainland": {
        "soil_health": 0.66, "biodiversity": 0.54, "watershed": 0.48, "solar": 0.70,
        "wind": 0.73, "agri": 0.88, "remoteness": 0.40, "pollution": 0.24,
    },
    "subpolar_periphery": {
        "soil_health": 0.52, "biodiversity": 0.58, "watershed": 0.66, "solar": 0.35,
        "wind": 0.80, "agri": 0.22, "remoteness": 0.72, "pollution": 0.16,
    },
}

REGION_NAMES = [
    "Aqua-North Basin", "Forest Equator Belt", "Delta Commons", "Temperate Ring",
    "Dryland Solar Arc", "Mountain Water Towers", "Steppe Grain Commons", "Urban Repair Web",
    "Coastal Wind Belt", "Subpolar Storage Rim", "Island Commons", "Highland Care Ring",
    "Inland Logistics Mesh", "Rainfed Agroforest Zone", "Desert Edge Settlements", "River City Chain",
]

GROUP_NAMES = ("water", "agriculture", "energy", "housing", "health", "care", "education", "logistics", "manufacturing", "storage", "governance", "knowledge", "resilience", "repair", "ecology")
SKILL_NAMES = ("infrastructure", "agriculture", "energy", "construction", "health", "care", "education", "logistics", "manufacturing", "storage", "governance", "knowledge", "resilience", "repair", "ecology", "general")


def make_cohorts(rng: random.Random, population: float, base_health: float, base_education: float, democracy: float) -> List[PopulationCohort]:
    child_share = clamp(rng.uniform(0.18, 0.28), 0.12, 0.35)
    elder_share = clamp(rng.uniform(0.10, 0.20), 0.05, 0.28)
    adult_share = max(0.45, 1.0 - child_share - elder_share)
    shares = [("children", child_share, 0.10), ("adults", adult_share, 1.0), ("elders", elder_share, 0.15)]
    cohorts = []
    for name, share, age_factor in shares:
        skill = {}
        for sk in SKILL_NAMES:
            if name == "children":
                val = base_education * rng.uniform(0.35, 0.65)
            elif name == "elders":
                val = base_education * rng.uniform(0.55, 1.05)
            else:
                val = base_education * rng.uniform(0.75, 1.25)
            skill[sk] = clamp(val, 0.05, 1.0)
        if name == "children":
            health = clamp(base_health * rng.uniform(0.90, 1.10), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.55, 0.85), 0.05, 1.0)
        elif name == "elders":
            health = clamp(base_health * rng.uniform(0.65, 0.95), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.85, 1.15), 0.05, 1.0)
        else:
            health = clamp(base_health * rng.uniform(0.85, 1.15), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.85, 1.15), 0.05, 1.0)
        cohorts.append(PopulationCohort(
            name=name,
            size=population * share,
            health=health,
            education=education,
            autonomy=clamp(rng.uniform(0.55, 0.88) * (0.75 + 0.35 * democracy), 0.05, 1.0),
            trust=clamp(rng.uniform(0.45, 0.82) * (0.70 + 0.45 * democracy), 0.02, 1.0),
            skill=skill,
            age_factor=age_factor,
        ))
    return cohorts


def create_commune(rng: random.Random, region_name: str, biome: str, population: float, scenario: str) -> Commune:
    b = BIOME_LIBRARY[biome]
    base_health = clamp(rng.uniform(0.55, 0.84) - (0.06 if scenario == "scarcity_shock" else 0.0), 0.1, 1.0)
    base_education = clamp(rng.uniform(0.50, 0.86) - (0.05 if scenario == "technocratic_control" else 0.0), 0.1, 1.0)
    democracy = clamp(rng.uniform(0.45, 0.86), 0.1, 1.0)
    if scenario == "technocratic_control":
        democracy *= 0.62
    if scenario == "local_democracy":
        democracy = clamp(democracy * 1.20, 0.1, 1.0)

    cohorts = make_cohorts(rng, population, base_health, base_education, democracy)
    pop = population

    # Initial stocks/capacities. They represent normalized person-months.
    water_stock = pop * rng.uniform(0.55, 1.75) * (0.65 + b["watershed"])
    food_stock = pop * rng.uniform(0.50, 1.60) * (0.55 + b["agri"])
    energy_stock = pop * rng.uniform(0.45, 1.35) * (0.55 + 0.50 * max(b["solar"], b["wind"]))
    if scenario == "scarcity_shock":
        water_stock *= 0.70
        food_stock *= 0.68
        energy_stock *= 0.78

    shelter_capacity = pop * rng.uniform(0.78, 1.18)
    if biome == "urban_corridor":
        shelter_capacity *= rng.uniform(0.88, 1.15)
    health_cap = pop * NEED_PER_PERSON["health"] * rng.uniform(0.55, 1.25) * (0.65 + base_education)
    care_cap = pop * NEED_PER_PERSON["care"] * rng.uniform(0.60, 1.20) * (0.65 + base_health)
    edu_cap = pop * NEED_PER_PERSON["education"] * rng.uniform(0.60, 1.30) * (0.65 + base_education)
    mobility_cap = pop * NEED_PER_PERSON["mobility"] * rng.uniform(0.55, 1.25) * (1.1 - b["remoteness"])
    manufacturing_cap = pop * NEED_PER_PERSON["manufacturing"] * rng.uniform(0.45, 1.15) * (0.70 + base_education)
    storage_cap = pop * NEED_PER_PERSON["storage"] * rng.uniform(0.45, 1.30) * (0.70 + (1.0 - b["remoteness"]))
    governance_cap = pop * NEED_PER_PERSON["governance"] * rng.uniform(0.55, 1.25) * (0.65 + democracy)
    knowledge_cap = pop * NEED_PER_PERSON["knowledge"] * rng.uniform(0.45, 1.25) * (0.65 + base_education)
    resilience_cap = pop * NEED_PER_PERSON["resilience"] * rng.uniform(0.40, 1.10) * (0.65 + democracy)

    stocks = {
        "water": water_stock,
        "food": food_stock,
        "energy": energy_stock,
        "repair_materials": pop * rng.uniform(0.05, 0.22),
        "waste": pop * rng.uniform(0.06, 0.23) * (1.0 + b["pollution"]),
    }
    capacities = {
        "shelter": shelter_capacity,
        "health": health_cap,
        "care": care_cap,
        "education": edu_cap,
        "mobility": mobility_cap,
        "manufacturing": manufacturing_cap,
        "storage": storage_cap,
        "governance": governance_cap,
        "knowledge": knowledge_cap,
        "resilience": resilience_cap,
    }
    environment = {
        "soil_health": clamp(b["soil_health"] * rng.uniform(0.82, 1.12), 0.05, 1.0),
        "biodiversity": clamp(b["biodiversity"] * rng.uniform(0.78, 1.12), 0.05, 1.0),
        "watershed": clamp(b["watershed"] * rng.uniform(0.80, 1.15), 0.05, 1.0),
        "solar": clamp(b["solar"] * rng.uniform(0.90, 1.10), 0.05, 1.0),
        "wind": clamp(b["wind"] * rng.uniform(0.90, 1.10), 0.05, 1.0),
        "agri": clamp(b["agri"] * rng.uniform(0.82, 1.15), 0.05, 1.0),
        "remoteness": clamp(b["remoteness"] * rng.uniform(0.85, 1.20), 0.02, 1.0),
        "local_pollution": clamp(b["pollution"] * rng.uniform(0.80, 1.25), 0.02, 1.0),
        "renewable_infrastructure": clamp(rng.uniform(0.30, 0.70) * (0.65 + max(b["solar"], b["wind"])), 0.05, 1.0),
    }

    group_base = {}
    for g in GROUP_NAMES:
        val = rng.uniform(0.35, 0.85)
        if g == "agriculture":
            val *= 0.65 + b["agri"]
        elif g == "energy":
            val *= 0.65 + max(b["solar"], b["wind"])
        elif g == "ecology":
            val *= 0.70 + 0.35 * b["biodiversity"]
        elif g == "logistics":
            val *= 1.15 - 0.55 * b["remoteness"]
        elif g == "water":
            val *= 0.70 + 0.50 * b["watershed"]
        elif g == "manufacturing":
            val *= 0.75 + base_education
        elif g == "storage":
            val *= 0.80 + 0.25 * (1.0 - b["remoteness"])
        elif g == "governance":
            val *= 0.65 + democracy
        elif g == "knowledge":
            val *= 0.70 + base_education
        elif g == "resilience":
            val *= 0.70 + 0.25 * democracy + 0.20 * b["watershed"]
        group_base[g] = clamp(val, 0.05, 1.0)

    return Commune(
        name="%s Commune %03d" % (region_name[:9].replace(" ", ""), rng.randint(1, 999)),
        region_name=region_name,
        biome=biome,
        cohorts=cohorts,
        stocks=stocks,
        capacities=capacities,
        environment=environment,
        group_base=group_base,
        democratic_quality=democracy,
        truth_error=clamp(rng.uniform(0.08, 0.26) + (0.12 if scenario == "technocratic_control" else 0.0), 0.02, 0.75),
    )


def create_planet(seed: int, total_population: float, regions_count: int, communes_per_region: int, scenario: str) -> Tuple[List[Region], BoundaryState, EffectPlanner]:
    rng = random.Random(seed)
    biomes = list(BIOME_LIBRARY.keys())
    rng.shuffle(biomes)
    region_pops_raw = [lognormal_near(rng, 1.0, 0.75) for _ in range(regions_count)]
    pop_sum = sum(region_pops_raw)
    regions: List[Region] = []
    for i in range(regions_count):
        name = REGION_NAMES[i % len(REGION_NAMES)]
        if i >= len(REGION_NAMES):
            name += " %d" % (i + 1)
        biome = biomes[i % len(biomes)]
        b = BIOME_LIBRARY[biome]
        region_pop = total_population * region_pops_raw[i] / pop_sum
        commune_raw = [lognormal_near(rng, 1.0, 0.60) for _ in range(communes_per_region)]
        commune_sum = sum(commune_raw)
        communes = []
        for j in range(communes_per_region):
            cpop = region_pop * commune_raw[j] / commune_sum
            communes.append(create_commune(rng, name, biome, cpop, scenario))
        regions.append(Region(
            name=name,
            biome=biome,
            communes=communes,
            logistic_hub=clamp((1.0 - b["remoteness"]) * rng.uniform(0.70, 1.15), 0.05, 1.0),
            climate_risk=clamp(rng.uniform(0.25, 0.75) + (0.25 if biome in ("drylands", "coastal_delta") else 0.0), 0.05, 1.0),
        ))

    if scenario == "ecological_crisis":
        pressures = {
            "climate": 1.18,
            "biosphere": 1.12,
            "freshwater": 1.08,
            "soil": 1.04,
            "pollution": 1.06,
            "material_throughput": 1.10,
            "energy_throughput": 1.08,
        }
    elif scenario == "scarcity_shock":
        pressures = {
            "climate": 1.02,
            "biosphere": 0.96,
            "freshwater": 1.07,
            "soil": 0.98,
            "pollution": 0.95,
            "material_throughput": 1.03,
            "energy_throughput": 1.00,
        }
    else:
        pressures = {
            "climate": 0.96,
            "biosphere": 0.92,
            "freshwater": 0.88,
            "soil": 0.86,
            "pollution": 0.91,
            "material_throughput": 0.94,
            "energy_throughput": 0.93,
        }
    boundary = BoundaryState(pressures=pressures)

    if scenario == "technocratic_control":
        planner = EffectPlanner(democratic_feedback=0.35, centralization=0.82, privacy_pressure=0.42,
                                cooperation=0.72, redistribution_strength=0.72, climate_discipline=0.70,
                                innovation_rate=0.36, renewable_bias=0.66)
    elif scenario == "local_democracy":
        planner = EffectPlanner(democratic_feedback=0.92, centralization=0.16, privacy_pressure=0.06,
                                cooperation=0.88, redistribution_strength=0.82, climate_discipline=0.76,
                                innovation_rate=0.42, renewable_bias=0.75)
    elif scenario == "ecological_crisis":
        planner = EffectPlanner(democratic_feedback=0.78, centralization=0.34, privacy_pressure=0.12,
                                cooperation=0.86, redistribution_strength=0.88, climate_discipline=0.88,
                                innovation_rate=0.46, renewable_bias=0.84)
    elif scenario == "scarcity_shock":
        planner = EffectPlanner(democratic_feedback=0.76, centralization=0.35, privacy_pressure=0.13,
                                cooperation=0.83, redistribution_strength=0.91, climate_discipline=0.80,
                                innovation_rate=0.38, renewable_bias=0.74)
    else:
        planner = EffectPlanner()
    return regions, boundary, planner


# ---------------------------------------------------------------------------
# Simulation dynamics
# ---------------------------------------------------------------------------


@dataclass
class StepImpacts:
    step: int = 0
    impacts: Dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BOUNDARY_NAMES})
    regeneration: Dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BOUNDARY_NAMES})
    global_transfers: float = 0.0
    truth_vectors: List[TruthVector] = field(default_factory=list)
    flows: List[EffectFlow] = field(default_factory=list)
    domain_labor: Dict[str, float] = field(default_factory=lambda: {domain: 0.0 for domain in DOMAINS})
    domain_outputs: Dict[str, float] = field(default_factory=lambda: {domain: 0.0 for domain in DOMAINS})

    def add_impact(self, name: str, value: float) -> None:
        self.impacts[name] = self.impacts.get(name, 0.0) + value

    def add_regen(self, name: str, value: float) -> None:
        self.regeneration[name] = self.regeneration.get(name, 0.0) + value

    def add_labor(self, domain: str, value: float) -> None:
        self.domain_labor[domain] = self.domain_labor.get(domain, 0.0) + value

    def add_output(self, domain: str, value: float) -> None:
        self.domain_outputs[domain] = self.domain_outputs.get(domain, 0.0) + value

    def add_flow(self, flow: EffectFlow) -> None:
        self.flows.append(flow)


def flow_values(commune: Commune, domain: str) -> Dict[str, float]:
    values = commune.last_truth_values.get(domain, {})
    if values:
        return dict(values)
    return {dim: 0.0 for dim in TRUTH_DIMS}


def make_effect_flow(step: int, kind: str, legacy_term_replaced: str, action: str, domain: str,
                     source: Commune, target: Commune, activated_effect: float, note: str = "") -> EffectFlow:
    values = flow_values(target, domain)
    validity, conditions = contract_conditions_for_flow(kind, domain, values)
    score_0_4 = truth_stack_score_0_4(values)
    priority_0_1 = safe_div(score_0_4, 4.0)
    base5 = truth_stack_base5(values)
    direction = "angle=%.3f; difference=%.3f; determination=%.3f; validity=%s" % (
        values.get("angle_direction", 0.0),
        values.get("difference", 0.0),
        values.get("determination", 0.0),
        CONTRACT_VALIDITY_LABELS.get(validity, validity),
    )
    causal_link = "%s:%s->%s" % (domain, source.name, target.name)
    return EffectFlow(
        step=step,
        kind=kind,
        legacy_term_replaced=legacy_term_replaced,
        action=action,
        domain=domain,
        sector=SECTOR_FOR_DOMAIN.get(domain, "unmapped"),
        from_region=source.region_name,
        from_commune=source.name,
        to_region=target.region_name,
        to_commune=target.name,
        activated_effect=max(0.0, activated_effect),
        causal_link=causal_link,
        direction_vector=direction,
        values=values,
        note=note,
        trade_object=catalog_value(domain, "trade_object"),
        meant_as=catalog_value(domain, "meant_as"),
        product_examples=catalog_value(domain, "products"),
        workplace_examples=catalog_value(domain, "workplaces"),
        service_examples=catalog_value(domain, "services"),
        ecological_clause=catalog_value(domain, "ecology"),
        climate_clause=catalog_value(domain, "climate"),
        contract_validity=CONTRACT_VALIDITY_LABELS.get(validity, validity),
        contract_conditions=conditions,
        truth_stack_score_0_4=score_0_4,
        truth_stack_priority_0_1=priority_0_1,
        truth_stack_base5=base5,
        truth_stack_decimal=truth_stack_decimal(values),
        truth_stack_compact=compact_truth_stack(values),
        dimension_meaning=dimension_meaning_summary(values),
    )


def produce_local_effects(commune: Commune, shares: Dict[str, float], boundary: BoundaryState, planner: EffectPlanner, step_impacts: StepImpacts) -> None:
    pop = commune.population()
    labor = commune.productive_time()
    boundary_penalty = boundary.penalty()
    education = commune.average_education()
    health = commune.average_health()
    cooperation = planner.cooperation * (0.65 + 0.35 * commune.average_trust())
    # A normalized labour productivity unit. 0.12 means full adult-time roughly covers monthly needs with tech/capacity factors.
    base_prod = 12.0 * labor * boundary_penalty * cooperation

    # Local effect domains. All outputs are person-month-ish normalized units.
    for domain in DOMAINS:
        domain_labor = base_prod * shares.get(domain, 0.0)
        if domain_labor <= 0.0:
            continue
        step_impacts.add_labor(domain, domain_labor)
        step_impacts.add_output(domain, domain_labor)
        step_impacts.add_flow(make_effect_flow(
            step_impacts.step,
            kind="contribution_offer",
            legacy_term_replaced="sell/labour_supply",
            action="activate_causal_effect",
            domain=domain,
            source=commune,
            target=commune,
            activated_effect=domain_labor,
            note="contribution time directed by truth-vector priority, not wage/price",
        ))
        if domain == "water":
            skill = commune.skill("infrastructure")
            watershed = commune.environment.get("watershed", 0.7)
            energy_use = 0.09 * domain_labor
            actual_energy = min(commune.stocks.get("energy", 0.0), energy_use)
            energy_factor = 0.45 + 0.55 * sat_ratio(actual_energy, energy_use)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - actual_energy
            output = domain_labor * (0.9 + 1.1 * watershed) * (0.55 + skill) * energy_factor
            commune.stocks["water"] = commune.stocks.get("water", 0.0) + output
            step_impacts.add_impact("freshwater", 0.0000000000016 * output * max(0.2, 1.1 - watershed))
            step_impacts.add_impact("energy_throughput", 0.0000000000002 * actual_energy)

        elif domain == "food":
            skill = commune.skill("agriculture")
            soil = commune.environment.get("soil_health", 0.7)
            water_need = 0.20 * domain_labor * (1.05 - 0.35 * soil)
            energy_need = 0.08 * domain_labor
            water_used = min(commune.stocks.get("water", 0.0), water_need)
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["water"] = commune.stocks.get("water", 0.0) - water_used
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            input_factor = 0.30 + 0.45 * sat_ratio(water_used, water_need) + 0.25 * sat_ratio(energy_used, energy_need)
            regenerative = clamp(0.25 + 0.45 * shares.get("ecology", 0.0) + 0.20 * planner.climate_discipline)
            output = domain_labor * (0.55 + skill) * (0.55 + commune.environment.get("agri", 0.6)) * (0.55 + soil) * input_factor
            commune.stocks["food"] = commune.stocks.get("food", 0.0) + output
            # Soil can degrade or improve depending on regenerative direction.
            commune.environment["soil_health"] = clamp(soil + 0.0015 * regenerative - 0.0018 * (1.0 - regenerative))
            step_impacts.add_impact("freshwater", 0.0000000000012 * water_used)
            step_impacts.add_impact("soil", 0.0000000000010 * output * (1.0 - regenerative))
            step_impacts.add_regen("soil", 0.0000000000011 * output * regenerative)

        elif domain == "energy":
            skill = commune.skill("energy")
            renewable = commune.environment.get("renewable_infrastructure", 0.5)
            solar_wind = max(commune.environment.get("solar", 0.5), commune.environment.get("wind", 0.5))
            repair_need = 0.10 * domain_labor * (0.85 - 0.45 * renewable)
            repair_used = min(commune.stocks.get("repair_materials", 0.0), max(0.0, repair_need))
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - repair_used
            output = domain_labor * (0.60 + skill) * (0.55 + solar_wind) * (0.70 + renewable)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) + output
            # Infrastructure improves with material and innovation.
            commune.environment["renewable_infrastructure"] = clamp(renewable + 0.0015 * planner.innovation_rate * sat_ratio(repair_used, max(repair_need, 1.0)))
            fossil_fraction = clamp((1.0 - renewable) * (1.0 - planner.renewable_bias) + 0.20 * max(0.0, boundary.pressures.get("energy_throughput", 0.9) - 1.0), 0.02, 0.65)
            step_impacts.add_impact("climate", 0.0000000000024 * output * fossil_fraction)
            step_impacts.add_impact("energy_throughput", 0.00000000000025 * output)
            step_impacts.add_impact("material_throughput", 0.0000000000010 * max(0.0, repair_need - repair_used) + 0.0000000000004 * repair_used)

        elif domain == "shelter":
            skill = commune.skill("construction")
            repair_material = commune.stocks.get("repair_materials", 0.0)
            # First reallocate/repair existing capacity; only then build.
            reuse_bias = clamp(0.55 + 0.35 * planner.sufficiency_norm + 0.25 * shares.get("repair", 0.0))
            material_need = domain_labor * (0.10 + 0.25 * (1.0 - reuse_bias))
            used_mat = min(repair_material, material_need)
            commune.stocks["repair_materials"] = repair_material - used_mat
            gained = domain_labor * (0.25 + 0.75 * reuse_bias) * (0.65 + skill) * (0.55 + sat_ratio(used_mat, max(material_need, 1.0)))
            commune.capacities["shelter"] = commune.capacities.get("shelter", 0.0) + gained
            waste_created = 0.035 * gained * (1.0 - reuse_bias)
            commune.stocks["waste"] = commune.stocks.get("waste", 0.0) + waste_created
            step_impacts.add_impact("material_throughput", 0.0000000000018 * max(0.0, material_need - used_mat) + 0.0000000000006 * used_mat)
            step_impacts.add_impact("pollution", 0.0000000000010 * waste_created)

        elif domain == "health":
            skill = commune.skill("health")
            energy_need = 0.05 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.70 + skill) * (0.70 + health) * (0.65 + 0.35 * sat_ratio(energy_used, energy_need))
            commune.capacities["health"] = commune.capacities.get("health", 0.0) + output
            step_impacts.add_impact("energy_throughput", 0.00000000000018 * energy_used)

        elif domain == "care":
            skill = commune.skill("care")
            output = domain_labor * (0.75 + skill) * (0.70 + commune.average_autonomy())
            commune.capacities["care"] = commune.capacities.get("care", 0.0) + output

        elif domain == "education":
            skill = commune.skill("education")
            energy_need = 0.025 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.72 + skill) * (0.70 + commune.democratic_quality) * (0.75 + 0.25 * sat_ratio(energy_used, energy_need))
            commune.capacities["education"] = commune.capacities.get("education", 0.0) + output
            step_impacts.add_impact("energy_throughput", 0.00000000000012 * energy_used)

        elif domain == "mobility":
            skill = commune.skill("logistics")
            energy_need = 0.11 * domain_labor * (0.70 + commune.environment.get("remoteness", 0.5))
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            efficiency = planner.logistics_efficiency * (0.75 + 0.25 * commune.environment.get("renewable_infrastructure", 0.5))
            output = domain_labor * (0.58 + skill) * (0.62 + efficiency) * (0.60 + 0.40 * sat_ratio(energy_used, energy_need))
            commune.capacities["mobility"] = commune.capacities.get("mobility", 0.0) + output
            carbon_intensity = (1.0 - commune.environment.get("renewable_infrastructure", 0.5)) * (1.0 - planner.renewable_bias)
            step_impacts.add_impact("climate", 0.0000000000015 * energy_used * carbon_intensity)
            step_impacts.add_impact("energy_throughput", 0.00000000000030 * energy_used)

        elif domain == "manufacturing":
            skill = commune.skill("manufacturing")
            energy_need = 0.14 * domain_labor
            material_need = 0.10 * domain_labor * (1.0 - 0.35 * shares.get("repair", 0.0))
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            input_factor = 0.35 + 0.40 * sat_ratio(energy_used, energy_need) + 0.25 * sat_ratio(material_used, material_need)
            tools = domain_labor * (0.50 + skill) * input_factor
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + 0.42 * tools
            commune.capacities["manufacturing"] = commune.capacities.get("manufacturing", 0.0) + 0.58 * tools
            step_impacts.add_impact("material_throughput", 0.0000000000014 * max(0.0, material_need - material_used) + 0.0000000000005 * material_used)
            step_impacts.add_impact("energy_throughput", 0.00000000000025 * energy_used)
            step_impacts.add_impact("pollution", 0.0000000000007 * max(0.0, tools - material_used))

        elif domain == "storage":
            skill = commune.skill("storage")
            energy_need = 0.035 * domain_labor
            material_need = 0.07 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            gained = domain_labor * (0.55 + skill) * (0.55 + 0.45 * sat_ratio(material_used, material_need))
            commune.capacities["storage"] = commune.capacities.get("storage", 0.0) + gained
            # Storage reduces spoilage and grid losses by preserving basic stocks.
            protection = clamp(0.000025 * gained / max(1.0, pop))
            commune.stocks["water"] = commune.stocks.get("water", 0.0) * (1.0 + protection)
            commune.stocks["food"] = commune.stocks.get("food", 0.0) * (1.0 + protection)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) * (1.0 + 0.5 * protection)
            step_impacts.add_impact("material_throughput", 0.0000000000007 * material_used)
            step_impacts.add_impact("energy_throughput", 0.00000000000010 * energy_used)

        elif domain == "governance":
            skill = commune.skill("governance")
            output = domain_labor * (0.55 + skill) * (0.45 + commune.democratic_quality)
            commune.capacities["governance"] = commune.capacities.get("governance", 0.0) + output
            correction = 0.00000000035 * output / max(1.0, pop)
            commune.truth_error = clamp(commune.truth_error - correction * planner.democratic_feedback + 0.00003 * planner.centralization * planner.privacy_pressure)
            commune.democratic_quality = clamp(commune.democratic_quality + 0.00000000022 * output / max(1.0, pop) - 0.00002 * planner.centralization * planner.privacy_pressure)

        elif domain == "knowledge":
            skill = commune.skill("knowledge")
            energy_need = 0.020 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.60 + skill) * (0.70 + commune.average_education()) * (0.70 + 0.30 * sat_ratio(energy_used, energy_need))
            commune.capacities["knowledge"] = commune.capacities.get("knowledge", 0.0) + output
            learning = 0.00000000018 * output / max(1.0, pop)
            for cohort in commune.cohorts:
                for sk in ("infrastructure", "agriculture", "energy", "construction", "health", "logistics", "manufacturing", "storage", "repair", "ecology"):
                    cohort.skill[sk] = clamp(cohort.skill.get(sk, 0.4) + learning)
            commune.environment["renewable_infrastructure"] = clamp(commune.environment.get("renewable_infrastructure", 0.5) + 0.00000000008 * output / max(1.0, pop) * planner.innovation_rate)
            step_impacts.add_impact("energy_throughput", 0.00000000000007 * energy_used)

        elif domain == "resilience":
            skill = commune.skill("resilience")
            material_need = 0.06 * domain_labor
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            output = domain_labor * (0.55 + skill) * (0.60 + commune.democratic_quality) * (0.55 + 0.45 * sat_ratio(material_used, material_need))
            commune.capacities["resilience"] = commune.capacities.get("resilience", 0.0) + output
            # Emergency readiness creates small local buffers and lowers damage from shocks.
            commune.stocks["water"] = commune.stocks.get("water", 0.0) + 0.04 * output
            commune.stocks["food"] = commune.stocks.get("food", 0.0) + 0.03 * output
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) + 0.02 * output
            step_impacts.add_impact("material_throughput", 0.0000000000005 * material_used)

        elif domain == "repair":
            skill = commune.skill("repair")
            waste = commune.stocks.get("waste", 0.0)
            processed = min(waste, domain_labor * (0.75 + skill))
            commune.stocks["waste"] = waste - processed
            material_gain = processed * (0.42 + 0.38 * skill)
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + material_gain
            # Repair also maintains existing capacities.
            for cap in MACRO_CAPACITY_DOMAINS:
                commune.capacities[cap] = commune.capacities.get(cap, 0.0) * (1.0 + 0.00015 * skill)
            step_impacts.add_regen("material_throughput", 0.0000000000014 * material_gain)
            step_impacts.add_regen("pollution", 0.0000000000010 * processed)

        elif domain == "ecology":
            skill = commune.skill("ecology")
            energy_need = 0.025 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            effect = domain_labor * (0.55 + skill) * (0.65 + commune.democratic_quality) * (0.65 + 0.35 * sat_ratio(energy_used, energy_need))
            commune.environment["soil_health"] = clamp(commune.environment.get("soil_health", 0.7) + 0.00000000020 * effect)
            commune.environment["biodiversity"] = clamp(commune.environment.get("biodiversity", 0.7) + 0.00000000018 * effect)
            commune.environment["watershed"] = clamp(commune.environment.get("watershed", 0.7) + 0.00000000016 * effect)
            commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) - 0.00000000016 * effect)
            step_impacts.add_regen("biosphere", 0.0000000000022 * effect)
            step_impacts.add_regen("soil", 0.0000000000018 * effect)
            step_impacts.add_regen("freshwater", 0.0000000000013 * effect)
            step_impacts.add_regen("pollution", 0.0000000000015 * effect)
            # Biosphere and soil also draw down a small share of climate pressure.
            step_impacts.add_regen("climate", 0.00000000000055 * effect)

        elif domain == "waste":
            skill = commune.skill("repair")
            waste = commune.stocks.get("waste", 0.0)
            processed = min(waste, domain_labor * (0.65 + skill))
            commune.stocks["waste"] = waste - processed
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + processed * (0.28 + 0.28 * skill)
            commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) - 0.00000000010 * processed)
            step_impacts.add_regen("pollution", 0.0000000000012 * processed)
            step_impacts.add_regen("material_throughput", 0.0000000000008 * processed)

    # Capacity decay / maintenance burden: if not maintained, infrastructure slowly decays.
    maintenance_quality = clamp(shares.get("repair", 0.0) * 5.0 + shares.get("waste", 0.0) * 2.0 + commune.average_trust() * 0.15)
    decay = 0.0045 * (1.0 - maintenance_quality)
    for cap in MACRO_CAPACITY_DOMAINS:
        commune.capacities[cap] = max(0.0, commune.capacities.get(cap, 0.0) * (1.0 - decay))


def redistribute_planetary_commons(regions: List[Region], planner: EffectPlanner, step_impacts: StepImpacts) -> None:
    """Planetary transfers across regions/communes without prices.

    This is what makes it a planet economy rather than a national economy:
    the algorithm checks real need and surplus globally, constrained by logistics
    and ecological cost. It does not care about national currency, exports, or GDP.
    """
    communes = [c for r in regions for c in r.communes]
    for domain in CONSUMABLE_DOMAINS:
        # Basic sufficiency target. Surplus above target can move.
        target_factor = 1.03
        donors = []
        receivers = []
        total_surplus = 0.0
        total_deficit = 0.0
        for c in communes:
            need = c.need(domain)
            stock = c.stocks.get(domain, 0.0)
            target = target_factor * need
            if stock > target:
                surplus = (stock - target) * planner.redistribution_strength
                donors.append([c, surplus])
                total_surplus += surplus
            else:
                deficit = max(0.0, need - stock)
                if deficit > 0.0:
                    priority = c.last_priorities.get(domain, 0.5)
                    receivers.append([c, deficit, priority])
                    total_deficit += deficit
        if total_surplus <= 0.0 or total_deficit <= 0.0:
            continue
        receivers.sort(key=lambda x: x[2], reverse=True)
        transfer_budget = min(total_surplus, total_deficit)
        # Global logistics capacity from mobility + logistics hubs.
        mobility_cap = sum(c.capacities.get("mobility", 0.0) for c in communes)
        mobility_need = sum(c.need("mobility") for c in communes)
        logistics_factor = clamp(sat_ratio(mobility_cap, max(mobility_need, 1.0)) * planner.logistics_efficiency)
        transfer_budget *= logistics_factor
        if transfer_budget <= 0.0:
            continue

        donor_i = 0
        for recv in receivers:
            rc, deficit, priority = recv
            if transfer_budget <= 1e-9:
                break
            want = min(deficit, transfer_budget)
            received = 0.0
            while want > 1e-9 and donor_i < len(donors):
                dc, avail = donors[donor_i]
                move = min(want, avail)
                if move <= 1e-9:
                    donor_i += 1
                    continue
                dc.stocks[domain] = dc.stocks.get(domain, 0.0) - move
                step_impacts.add_flow(make_effect_flow(
                    step_impacts.step,
                    kind="planetary_transfer",
                    legacy_term_replaced="buy/sell/import/export",
                    action="causal_transfer_to_need",
                    domain=domain,
                    source=dc,
                    target=rc,
                    activated_effect=move,
                    note="surplus and deficit matched by urgency, not purchasing power",
                ))
                received += move
                want -= move
                transfer_budget -= move
                donors[donor_i][1] -= move
                if donors[donor_i][1] <= 1e-9:
                    donor_i += 1
            rc.stocks[domain] = rc.stocks.get(domain, 0.0) + received
            step_impacts.global_transfers += received
            # Transfer has ecological cost but is less damaging if energy system is renewable.
            if received > 0.0:
                avg_renew = mean(c.environment.get("renewable_infrastructure", 0.5) for c in communes)
                carbon = (1.0 - avg_renew) * (1.0 - planner.renewable_bias)
                step_impacts.add_impact("climate", 0.00000000000055 * received * carbon)
                step_impacts.add_impact("energy_throughput", 0.00000000000016 * received)
                step_impacts.add_impact("material_throughput", 0.00000000000020 * received)


def consume_and_update_people(commune: Commune, planner: EffectPlanner, step_impacts: Optional[StepImpacts] = None) -> None:
    satisfaction: Dict[str, float] = {}
    # Consumables: water, food, energy.
    for domain in CONSUMABLE_DOMAINS:
        need = commune.need(domain)
        stock = commune.stocks.get(domain, 0.0)
        sat = sat_ratio(stock, need)
        used = min(stock, need)
        commune.stocks[domain] = max(0.0, stock - used)
        satisfaction[domain] = sat
        if step_impacts is not None and used > 0.0:
            step_impacts.add_flow(make_effect_flow(
                step_impacts.step,
                kind="need_acceptance",
                legacy_term_replaced="buy/consumption",
                action="accept_effect_for_need",
                domain=domain,
                source=commune,
                target=commune,
                activated_effect=used,
                note="need satisfaction accepted through existence/intensity/time, not purchasing power",
            ))

    # Capacities: shelter is not consumed like food; health/care/education/mobility capacity is used this month.
    shelter_need = commune.need("shelter")
    shelter_sat = sat_ratio(commune.capacities.get("shelter", 0.0), shelter_need)
    satisfaction["shelter"] = shelter_sat
    if step_impacts is not None:
        step_impacts.add_flow(make_effect_flow(
            step_impacts.step,
            kind="need_acceptance",
            legacy_term_replaced="buy/rent",
            action="stabilize_shelter_existence",
            domain="shelter",
            source=commune,
            target=commune,
            activated_effect=min(commune.capacities.get("shelter", 0.0), shelter_need),
            note="housing access through real need and capacity, not rent/price",
        ))

    for domain in SERVICE_DOMAINS:
        need = commune.need(domain)
        cap = commune.capacities.get(domain, 0.0)
        sat = sat_ratio(cap, need)
        used = min(cap, need)
        # Service capacity partly persists as institution, partly consumed as monthly service.
        commune.capacities[domain] = max(0.0, cap - 0.72 * used)
        satisfaction[domain] = sat
        if step_impacts is not None and used > 0.0:
            step_impacts.add_flow(make_effect_flow(
                step_impacts.step,
                kind="need_acceptance",
                legacy_term_replaced="buy/service_purchase",
                action="accept_service_effect",
                domain=domain,
                source=commune,
                target=commune,
                activated_effect=used,
                note="service is used as social effect, not purchased service value",
            ))

    # Waste from consumption; lower if repair/sufficiency norms are strong.
    pop = commune.population()
    consumption_shortfall = 1.0 - mean(satisfaction.get(d, 1.0) for d in CONSUMABLE_DOMAINS)
    waste_created = pop * 0.028 * (0.65 + 0.35 * mean([satisfaction.get("food", 1.0), satisfaction.get("energy", 1.0)])) * (1.0 - 0.30 * planner.sufficiency_norm)
    # Crisis can create unmanaged waste through breakdown.
    waste_created += pop * 0.012 * consumption_shortfall
    commune.stocks["waste"] = commune.stocks.get("waste", 0.0) + waste_created
    commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) + 0.00000000005 * waste_created)

    # Update cohorts. If system is highly centralized, privacy pressure is stronger.
    privacy = clamp(planner.privacy_pressure + 0.15 * planner.centralization * (1.0 - commune.democratic_quality))
    gov_quality = clamp(0.55 * commune.democratic_quality + 0.30 * commune.average_trust() + 0.15 * (1.0 - commune.truth_error))
    for cohort in commune.cohorts:
        cohort.update_from_satisfaction(satisfaction, gov_quality, privacy)

    # Demographic dynamics: cautious and bounded. This is not a detailed population model.
    avg_sat = mean(satisfaction.values(), 0.85)
    edu = commune.average_education()
    health = commune.average_health()
    # Good conditions sustain; severe unmet basics cause contraction. Higher education moderates growth.
    monthly_growth = 0.00055 * (avg_sat - 0.62) + 0.00035 * (health - 0.55) - 0.00028 * (edu - 0.55)
    monthly_growth = clamp(monthly_growth, -0.0045, 0.0035)
    for cohort in commune.cohorts:
        cohort.size = max(0.0, cohort.size * (1.0 + monthly_growth))

    commune.last_satisfaction = satisfaction
    commune.update_truth_error(avg_sat, planner)


def simulate_step(regions: List[Region], boundary: BoundaryState, planner: EffectPlanner, step: int) -> Tuple[GlobalMetrics, List[TruthVector], StepImpacts]:
    step_impacts = StepImpacts(step=step)

    # 1) Compute truth vectors: reality -> logical stacked values -> priority.
    for region in regions:
        for commune in region.communes:
            tvs = [commune.truth_vector(domain, boundary, planner) for domain in DOMAINS]
            step_impacts.truth_vectors.extend(tvs)
            commune.last_priorities = {tv.domain: tv.priority() for tv in tvs}
            commune.last_truth_values = {tv.domain: dict(tv.values) for tv in tvs}
            shares = planner.labor_shares(tvs, commune, boundary)
            commune.last_labor_shares = shares

    # 2) Produce local effects according to truth-vector priority.
    for region in regions:
        for commune in region.communes:
            produce_local_effects(commune, commune.last_labor_shares, boundary, planner, step_impacts)

    # 3) Redistribute planetary commons: global real need and surplus, no price/currency.
    redistribute_planetary_commons(regions, planner, step_impacts)

    # 4) Consume/satisfy needs and update individuals/cohorts.
    for region in regions:
        for commune in region.communes:
            consume_and_update_people(commune, planner, step_impacts)

    # 5) Planetary boundary update. Add baseline impacts from unmanaged waste and local pollution.
    total_pop = sum(r.population() for r in regions)
    total_waste = sum(c.stocks.get("waste", 0.0) for r in regions for c in r.communes)
    avg_local_pollution = weighted_mean(((c.environment.get("local_pollution", 0.2), c.population()) for r in regions for c in r.communes), default=0.2)
    avg_soil_gap = weighted_mean(((1.0 - c.environment.get("soil_health", 0.7), c.population()) for r in regions for c in r.communes), default=0.3)
    avg_bio_gap = weighted_mean(((1.0 - c.environment.get("biodiversity", 0.7), c.population()) for r in regions for c in r.communes), default=0.3)
    step_impacts.add_impact("pollution", 0.00000000000035 * total_waste + 0.0008 * max(0.0, avg_local_pollution - 0.55))
    step_impacts.add_impact("soil", 0.0005 * max(0.0, avg_soil_gap - 0.30))
    step_impacts.add_impact("biosphere", 0.0005 * max(0.0, avg_bio_gap - 0.30))
    # Sufficiency and climate discipline slowly lower systemic pressure.
    step_impacts.add_regen("material_throughput", 0.0020 * planner.sufficiency_norm * mean((c.average_trust() for r in regions for c in r.communes), default=0.5))
    step_impacts.add_regen("energy_throughput", 0.0030 * planner.sufficiency_norm * planner.renewable_bias)
    step_impacts.add_regen("climate", 0.0009 * planner.climate_discipline * planner.renewable_bias)

    boundary.apply_impacts(step_impacts.impacts, step_impacts.regeneration)

    metrics = collect_metrics(regions, boundary, step, step_impacts.global_transfers)
    return metrics, step_impacts.truth_vectors, step_impacts


def collect_metrics(regions: List[Region], boundary: BoundaryState, step: int, transfers: float) -> GlobalMetrics:
    communes = [c for r in regions for c in r.communes]
    total_pop = sum(c.population() for c in communes)
    # Wellbeing from satisfaction, health, autonomy, trust, and ecological safety.
    wellbeing_items = []
    unmet_items = []
    basic_buffer_items = []
    resilience_items = []
    for c in communes:
        sat = c.last_satisfaction or {d: 0.8 for d in ("water", "food", "energy", "shelter", "health", "care", "education", "mobility", "governance", "knowledge", "resilience")}
        basic_sat = 0.30 * sat.get("water", 1.0) + 0.30 * sat.get("food", 1.0) + 0.18 * sat.get("shelter", 1.0) + 0.12 * sat.get("energy", 1.0) + 0.10 * sat.get("health", 1.0)
        civic_sat = 0.36 * sat.get("governance", 1.0) + 0.34 * sat.get("knowledge", 1.0) + 0.30 * sat.get("resilience", 1.0)
        freedom = 0.55 * c.average_autonomy() + 0.45 * c.average_trust()
        ecological_safety = boundary.penalty()
        wellbeing = clamp(0.50 * basic_sat + 0.17 * freedom + 0.11 * c.average_health() + 0.10 * civic_sat + 0.12 * ecological_safety)
        wellbeing_items.append((wellbeing, c.population()))
        unmet_basic = 1.0 - clamp(0.35 * sat.get("water", 1.0) + 0.35 * sat.get("food", 1.0) + 0.15 * sat.get("shelter", 1.0) + 0.15 * sat.get("health", 1.0))
        unmet_items.append((unmet_basic, c.population()))
        basic_need = max(1.0, c.need("water") + c.need("food") + c.need("energy"))
        basic_stock = c.stocks.get("water", 0.0) + c.stocks.get("food", 0.0) + c.stocks.get("energy", 0.0)
        basic_buffer_items.append((safe_div(basic_stock, basic_need, 0.0), c.population()))
        resilience = clamp(0.40 * sat_ratio(c.capacities.get("resilience", 0.0), max(1.0, c.need("resilience"))) +
                           0.25 * sat_ratio(c.capacities.get("storage", 0.0), max(1.0, c.need("storage"))) +
                           0.20 * sat_ratio(basic_stock, 1.20 * basic_need) +
                           0.15 * boundary.penalty())
        resilience_items.append((resilience, c.population()))
    worst_name, worst_pressure = boundary.worst()
    waste_stock = sum(c.stocks.get("waste", 0.0) for c in communes)
    repair_materials = sum(c.stocks.get("repair_materials", 0.0) for c in communes)
    food_stock = sum(c.stocks.get("food", 0.0) for c in communes)
    water_stock = sum(c.stocks.get("water", 0.0) for c in communes)
    energy_stock = sum(c.stocks.get("energy", 0.0) for c in communes)
    contribution_time = sum(c.productive_time() for c in communes)
    macro_capacity = sum(c.capacities.get(domain, 0.0) for c in communes for domain in MACRO_CAPACITY_DOMAINS)
    avg_truth_error = weighted_mean(((c.truth_error, c.population()) for c in communes), default=0.0)
    avg_democracy = weighted_mean(((c.democratic_quality, c.population()) for c in communes), default=0.0)
    avg_trust = weighted_mean(((c.average_trust(), c.population()) for c in communes), default=0.0)
    circularity_index = clamp(repair_materials / max(1.0, repair_materials + waste_stock))
    coordination_quality = clamp(0.36 * avg_democracy + 0.34 * avg_trust + 0.30 * (1.0 - avg_truth_error))
    basic_buffer_months = weighted_mean(basic_buffer_items, default=0.0)
    resilience_index = weighted_mean(resilience_items, default=0.0)
    satisfaction_inequality = weighted_gini(wellbeing_items)
    planetary_reproduction_index = clamp(0.30 * weighted_mean(wellbeing_items, default=0.0) +
                                         0.22 * (1.0 - weighted_mean(unmet_items, default=0.0)) +
                                         0.18 * boundary.penalty() +
                                         0.12 * circularity_index +
                                         0.10 * coordination_quality +
                                         0.08 * resilience_index)
    return GlobalMetrics(
        step=step,
        population=total_pop,
        wellbeing=weighted_mean(wellbeing_items, default=0.0),
        unmet_basic=weighted_mean(unmet_items, default=0.0),
        avg_trust=avg_trust,
        avg_autonomy=weighted_mean(((c.average_autonomy(), c.population()) for c in communes), default=0.0),
        avg_health=weighted_mean(((c.average_health(), c.population()) for c in communes), default=0.0),
        avg_education=weighted_mean(((c.average_education(), c.population()) for c in communes), default=0.0),
        avg_truth_error=avg_truth_error,
        overshoot=boundary.overshoot(),
        mean_boundary_pressure=boundary.mean_pressure(),
        worst_boundary=worst_name,
        worst_boundary_pressure=worst_pressure,
        waste_stock=waste_stock,
        repair_materials=repair_materials,
        food_stock=food_stock,
        water_stock=water_stock,
        energy_stock=energy_stock,
        global_transfers=transfers,
        contribution_time=contribution_time,
        contribution_time_per_person=safe_div(contribution_time, total_pop, 0.0),
        satisfaction_inequality=satisfaction_inequality,
        resilience_index=resilience_index,
        circularity_index=circularity_index,
        coordination_quality=coordination_quality,
        basic_buffer_months=basic_buffer_months,
        macro_capacity=macro_capacity,
        planetary_reproduction_index=planetary_reproduction_index,
    )


def collect_macro_accounts(regions: List[Region], boundary: BoundaryState, step: int, step_impacts: Optional[StepImpacts] = None) -> List[MacroAccountRow]:
    """Global accounts for a planet economy.

    These rows are analogous to national accounts, sector accounts, labour accounts,
    public-goods accounts and external-sector accounts, but without money, prices,
    income, profit or GDP. The core balance is need/available/difference/effect.
    """
    communes = [c for r in regions for c in r.communes]
    rows: List[MacroAccountRow] = []
    flow_counts: Dict[str, int] = {domain: 0 for domain in DOMAINS}
    if step_impacts is not None:
        for flow in step_impacts.flows:
            flow_counts[flow.domain] = flow_counts.get(flow.domain, 0) + 1
    total_labor = sum(step_impacts.domain_labor.values()) if step_impacts is not None else 0.0
    for domain in DOMAINS:
        need = 0.0
        available = 0.0
        stock_or_capacity = 0.0
        priority_items = []
        labor_share_items = []
        truth_error_items = []
        democracy_items = []
        for c in communes:
            pop = c.population()
            if domain == "ecology":
                n = c.ecology_need()
                a = c.available_for_need(domain)
            elif domain == "waste":
                n = c.waste_need()
                a = max(0.0, c.waste_need() - c.stocks.get("waste", 0.0))
            else:
                n = c.need(domain)
                a = c.available_for_need(domain)
            need += n
            available += a
            if domain in CONSUMABLE_DOMAINS:
                stock_or_capacity += c.stocks.get(domain, 0.0)
            elif domain == "repair":
                stock_or_capacity += c.stocks.get("repair_materials", 0.0)
            elif domain == "waste":
                stock_or_capacity += c.stocks.get("waste", 0.0)
            elif domain in MACRO_CAPACITY_DOMAINS:
                stock_or_capacity += c.capacities.get(domain, 0.0)
            priority_items.append((c.last_priorities.get(domain, 0.0), pop))
            labor_share_items.append((c.last_labor_shares.get(domain, 0.0), pop))
            truth_error_items.append((c.truth_error, pop))
            democracy_items.append((c.democratic_quality, pop))
        gap = normalized_need_gap(need, available)
        satisfaction = sat_ratio(available, need)
        contribution_time = 0.0
        if step_impacts is not None:
            contribution_time = step_impacts.domain_labor.get(domain, 0.0)
        rows.append(MacroAccountRow(
            step=step,
            domain=domain,
            sector=SECTOR_FOR_DOMAIN.get(domain, "unmapped"),
            need=need,
            available=available,
            gap=gap,
            satisfaction=satisfaction,
            priority=weighted_mean(priority_items, default=0.0),
            labor_share=weighted_mean(labor_share_items, default=safe_div(contribution_time, total_labor, 0.0)),
            contribution_time=contribution_time,
            stock_or_capacity=stock_or_capacity,
            boundary_penalty=boundary.penalty(),
            truth_error=weighted_mean(truth_error_items, default=0.0),
            democratic_quality=weighted_mean(democracy_items, default=0.0),
            activated_flows=flow_counts.get(domain, 0),
        ))
    return rows


def run_simulation(seed: int, steps: int, population: float, regions_count: int, communes_per_region: int, scenario: str) -> Tuple[List[Region], BoundaryState, EffectPlanner, List[GlobalMetrics], List[TruthVector], List[MacroAccountRow], List[EffectFlow]]:
    regions, boundary, planner = create_planet(seed, population, regions_count, communes_per_region, scenario)
    timeline: List[GlobalMetrics] = []
    macro_accounts: List[MacroAccountRow] = []
    last_truth: List[TruthVector] = []
    last_flows: List[EffectFlow] = []
    # Initial metrics with no consumption history yet.
    timeline.append(collect_metrics(regions, boundary, 0, 0.0))
    macro_accounts.extend(collect_macro_accounts(regions, boundary, 0, None))
    for step in range(1, steps + 1):
        metrics, truth_vectors, step_impacts = simulate_step(regions, boundary, planner, step)
        timeline.append(metrics)
        macro_accounts.extend(collect_macro_accounts(regions, boundary, step, step_impacts))
        last_truth = truth_vectors
        last_flows = step_impacts.flows
    return regions, boundary, planner, timeline, last_truth, macro_accounts, last_flows


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def ensure_dir(path: str) -> None:
    if not path:
        return
    if not os.path.exists(path):
        os.makedirs(path)


def write_timeline(path: str, timeline: List[GlobalMetrics]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(timeline[0].as_row().keys()))
        writer.writeheader()
        for m in timeline:
            writer.writerow(m.as_row())


def write_communes(path: str, regions: List[Region]) -> None:
    fields = [
        "region", "commune", "biome", "population", "wellbeing_proxy", "avg_health", "avg_education",
        "avg_autonomy", "avg_trust", "truth_error", "democratic_quality",
        "water_stock", "food_stock", "energy_stock", "shelter_capacity", "health_capacity",
        "care_capacity", "education_capacity", "mobility_capacity", "manufacturing_capacity",
        "storage_capacity", "governance_capacity", "knowledge_capacity", "resilience_capacity",
        "repair_materials", "waste",
        "soil_health", "biodiversity", "watershed", "local_pollution", "renewable_infrastructure",
        "top_priority_domain", "top_priority", "top_labor_domain", "top_labor_share",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in regions:
            for c in r.communes:
                sat = c.last_satisfaction or {}
                wellbeing_proxy = clamp(0.55 * mean(sat.values(), 0.8) + 0.15 * c.average_health() + 0.15 * c.average_autonomy() + 0.15 * c.average_trust())
                top_priority = max(c.last_priorities.items(), key=lambda kv: kv[1]) if c.last_priorities else ("none", 0.0)
                top_labor = max(c.last_labor_shares.items(), key=lambda kv: kv[1]) if c.last_labor_shares else ("none", 0.0)
                row = {
                    "region": r.name,
                    "commune": c.name,
                    "biome": c.biome,
                    "population": round(c.population(), 3),
                    "wellbeing_proxy": round(wellbeing_proxy, 6),
                    "avg_health": round(c.average_health(), 6),
                    "avg_education": round(c.average_education(), 6),
                    "avg_autonomy": round(c.average_autonomy(), 6),
                    "avg_trust": round(c.average_trust(), 6),
                    "truth_error": round(c.truth_error, 6),
                    "democratic_quality": round(c.democratic_quality, 6),
                    "water_stock": round(c.stocks.get("water", 0.0), 3),
                    "food_stock": round(c.stocks.get("food", 0.0), 3),
                    "energy_stock": round(c.stocks.get("energy", 0.0), 3),
                    "shelter_capacity": round(c.capacities.get("shelter", 0.0), 3),
                    "health_capacity": round(c.capacities.get("health", 0.0), 3),
                    "care_capacity": round(c.capacities.get("care", 0.0), 3),
                    "education_capacity": round(c.capacities.get("education", 0.0), 3),
                    "mobility_capacity": round(c.capacities.get("mobility", 0.0), 3),
                    "manufacturing_capacity": round(c.capacities.get("manufacturing", 0.0), 3),
                    "storage_capacity": round(c.capacities.get("storage", 0.0), 3),
                    "governance_capacity": round(c.capacities.get("governance", 0.0), 3),
                    "knowledge_capacity": round(c.capacities.get("knowledge", 0.0), 3),
                    "resilience_capacity": round(c.capacities.get("resilience", 0.0), 3),
                    "repair_materials": round(c.stocks.get("repair_materials", 0.0), 3),
                    "waste": round(c.stocks.get("waste", 0.0), 3),
                    "soil_health": round(c.environment.get("soil_health", 0.0), 6),
                    "biodiversity": round(c.environment.get("biodiversity", 0.0), 6),
                    "watershed": round(c.environment.get("watershed", 0.0), 6),
                    "local_pollution": round(c.environment.get("local_pollution", 0.0), 6),
                    "renewable_infrastructure": round(c.environment.get("renewable_infrastructure", 0.0), 6),
                    "top_priority_domain": top_priority[0],
                    "top_priority": round(top_priority[1], 6),
                    "top_labor_domain": top_labor[0],
                    "top_labor_share": round(top_labor[1], 6),
                }
                writer.writerow(row)


def write_truth_audit(path: str, truth_vectors: List[TruthVector], step: int, limit: int = 500) -> None:
    if not truth_vectors:
        return
    ordered = sorted(truth_vectors, key=lambda tv: tv.priority(), reverse=True)[:limit]
    fields = list(ordered[0].as_row(step).keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for tv in ordered:
            writer.writerow(tv.as_row(step))




def write_macro_accounts(path: str, rows: List[MacroAccountRow]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].as_row().keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_row())


def write_effect_flows(path: str, flows: List[EffectFlow], limit: int = 20000) -> None:
    if not flows:
        return
    selected = flows[:limit]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(selected[0].as_row().keys()))
        writer.writeheader()
        for flow in selected:
            writer.writerow(flow.as_row())



def write_dimension_guide(path: str) -> None:
    fieldnames = ["dimension", "name_de", "short", "question", "contract_role", "economic_replacement", "weight"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for dim in TRUTH_DIMS:
            item = DIMENSION_GUIDE_DE[dim]
            writer.writerow({
                "dimension": dim,
                "name_de": item["name_de"],
                "short": item["short"],
                "question": item["question"],
                "contract_role": item["contract_role"],
                "economic_replacement": item["economic_replacement"],
                "weight": TRUTH_WEIGHTS.get(dim, 0.0),
            })


def write_trade_dimension_catalog(path: str) -> None:
    fieldnames = [
        "domain", "sector", "trade_object", "meant_as", "products", "workplaces",
        "services", "ecology", "climate",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for domain in DOMAINS:
            item = TRADE_CATALOG[domain]
            writer.writerow({
                "domain": domain,
                "sector": SECTOR_FOR_DOMAIN.get(domain, "unmapped"),
                "trade_object": item["trade_object"],
                "meant_as": item["meant_as"],
                "products": item["products"],
                "workplaces": item["workplaces"],
                "services": item["services"],
                "ecology": item["ecology"],
                "climate": item["climate"],
            })


def md_escape(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def shorten(value: object, limit: int = 140) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    return text[:max(0, limit - 1)].rstrip() + "…"


def write_trade_contracts_report(path: str, flows: List[EffectFlow], truth_vectors: List[TruthVector], timeline: List[GlobalMetrics], limit: int = 120) -> None:
    lines: List[str] = []
    lines.append("# Handeln in Dimensionen: Vertrag, Wahrheitswert, Wirkung")
    lines.append("")
    lines.append("Dieses Protokoll zeigt, wie `kaufen`, `verkaufen`, `Import`, `Export`, `Arbeitsmarkt`, `Produktmarkt` und `Dienstleistungsmarkt` in der Simulation ersetzt werden.")
    lines.append("")
    lines.append("**Alte Form:** Ware + Menge + Preis + Eigentum → Kauf/Verkauf")
    lines.append("")
    lines.append("**Neue Form:** Kausalität + Zeit + Intensität + Existenz + Potenzen + Wirkungen + Substanz + Materie + Differenz + Bestimmung + Phänomene + Winkelrichtung → Wirkungsvertrag")
    lines.append("")
    lines.append("Der `gestapelte Wahrheitswert` ist die 12-dimensionale Lage eines Handels. Jede Dimension liegt auf 0..4. Daraus entstehen zwei Zahlen:")
    lines.append("")
    lines.append("- `truth_stack_base5`: die gestapelte Zahl, eine Ziffer pro Dimension in dieser Reihenfolge: `K,Z,I,E,P,W,S,M,D,B,Ph,R`.")
    lines.append("- `truth_stack_score_0_4`: der gewichtete Gesamtwert. Er ist **keine Geldzahl**, sondern eine Prioritäts-/Gültigkeitszahl.")
    lines.append("")
    lines.append("## Dimensionen")
    lines.append("")
    lines.append("| Kürzel | Dimension | Vertragsfrage | Was sie ökonomisch ersetzt |")
    lines.append("|---|---|---|---|")
    for dim in TRUTH_DIMS:
        g = DIMENSION_GUIDE_DE[dim]
        lines.append("| %s | %s | %s | %s |" % (md_escape(g["short"]), md_escape(g["name_de"]), md_escape(g["question"]), md_escape(g["economic_replacement"])))
    lines.append("")
    lines.append("## Was wird gehandelt?")
    lines.append("")
    lines.append("Gehandelt wird nicht `Wert`, sondern eine gerichtete Wirkung. Produkt, Arbeitsplatz und Dienstleistung sind nur Träger dieser Wirkung.")
    lines.append("")
    lines.append("| Domäne | Gehandelte Wirkung | Produkte | Arbeitsplätze | Dienstleistungen | Öko-/Klima-Klausel |")
    lines.append("|---|---|---|---|---|---|")
    for domain in DOMAINS:
        item = TRADE_CATALOG[domain]
        eco_climate = item["ecology"] + " / " + item["climate"]
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            md_escape(domain),
            md_escape(shorten(item["trade_object"], 90)),
            md_escape(shorten(item["products"], 90)),
            md_escape(shorten(item["workplaces"], 90)),
            md_escape(shorten(item["services"], 90)),
            md_escape(shorten(eco_climate, 140)),
        ))
    lines.append("")
    lines.append("## Beispielhafte Wirkungsverträge aus dem letzten Simulationsschritt")
    lines.append("")
    lines.append("Ein Vertrag ist hier eine bedingte Freigabe von Wirkung. Er sagt: Diese Handlung darf/ soll passieren, weil ihr Wahrheitsstapel eine reale Lücke, eine Ursache, eine Zeitlage und eine Richtung zeigt.")
    lines.append("")
    if not flows:
        lines.append("Keine Flüsse vorhanden.")
    else:
        # Sort so the report shows large/high-priority flows, but keep diversity across domains/kinds.
        selected: List[EffectFlow] = []
        seen = set()
        for flow in sorted(flows, key=lambda f: (f.truth_stack_priority_0_1, f.activated_effect), reverse=True):
            key = (flow.kind, flow.domain)
            if key not in seen:
                selected.append(flow)
                seen.add(key)
            if len(selected) >= limit // 2:
                break
        for flow in sorted(flows, key=lambda f: f.activated_effect, reverse=True):
            if flow not in selected:
                selected.append(flow)
            if len(selected) >= limit:
                break
        lines.append("| Art | Ersetzt | Domäne | Was gehandelt wird | Gemeint als | Gültigkeit | Wahrheitsstapel | Score | Vertragsbedingungen |")
        lines.append("|---|---|---|---|---|---|---|---:|---|")
        for flow in selected[:limit]:
            lines.append("| %s | %s | %s | %s | %s | %s | `%s` | %.2f | %s |" % (
                md_escape(flow.kind),
                md_escape(flow.legacy_term_replaced),
                md_escape(flow.domain),
                md_escape(shorten(flow.trade_object, 120)),
                md_escape(shorten(flow.meant_as, 120)),
                md_escape(flow.contract_validity),
                md_escape(flow.truth_stack_base5),
                flow.truth_stack_score_0_4,
                md_escape(shorten(flow.contract_conditions, 260)),
            ))
    lines.append("")
    lines.append("## Wie hängt der gestapelte Wahrheitswert mit den Dimensionen zusammen?")
    lines.append("")
    lines.append("1. Jede Dimension misst einen anderen Aspekt der Realität: Ursache, Dringlichkeit, Stärke, Existenz, Möglichkeit, Folge, Stoff, Ort, Lücke, Legitimation, Erscheinung und Richtung.")
    lines.append("2. Der Stapel ist kein Mittelwert allein. Die Basis-5-Zahl behält die Struktur: `K=3` ist etwas anderes als `R=3`. Zwei Handlungen können denselben Score haben, aber völlig verschiedene Risiken.")
    lines.append("3. Der gewichtete Score entscheidet über Priorität; die Einzelziffern entscheiden über Vertragsbedingungen. Beispiel: hoher Bedarf bei niedriger Winkelrichtung bedeutet nicht automatisch Ausführung, sondern Umbau der Handlung.")
    lines.append("4. Kaufen heißt in diesem System: eine Bedarfswirkung wird angenommen. Verkaufen heißt: eine Fähigkeit, Zeit, Substanz oder Wirkung wird beigetragen. Handel heißt: eine Differenz wird kausal übertragen oder aufgelöst.")
    lines.append("")
    if timeline:
        last = timeline[-1]
        lines.append("## Letzter globaler Zustand")
        lines.append("")
        lines.append("- Wohlbefinden: %.3f" % last.wellbeing)
        lines.append("- Ungedeckte Grundbedürfnisse: %.3f" % last.unmet_basic)
        lines.append("- Planetarer Overshoot: %.3f" % last.overshoot)
        lines.append("- Schlechteste Grenze: %s %.3f" % (last.worst_boundary, last.worst_boundary_pressure))
        lines.append("- Reproduktionsindex: %.3f" % last.planetary_reproduction_index)
        lines.append("")
    lines.append("## Formelschema")
    lines.append("")
    lines.append("```text")
    lines.append("Handel_alt = Ware × Menge × Preis")
    lines.append("Handel_neu = Δ(Kausalität, Zeit, Intensität, Existenz, Potenzen, Wirkungen, Substanz, Materie, Differenz, Bestimmung, Phänomene, Winkelrichtung)")
    lines.append("Vertrag_neu = Wirkung + Bedingungen + Wahrheitsstapel + Fehlerkorrektur + ökologische Grenze")
    lines.append("truth_stack_base5 = digit(K) digit(Z) digit(I) digit(E) digit(P) digit(W) digit(S) digit(M) digit(D) digit(B) digit(Ph) digit(R)")
    lines.append("```")
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_summary(path: str, regions: List[Region], boundary: BoundaryState, planner: EffectPlanner, timeline: List[GlobalMetrics], scenario: str, seed: int) -> None:
    first = timeline[0]
    last = timeline[-1]
    summary = {
        "model": "Planetary Effect Economy / Kommunismus 2.0 conceptual simulation",
        "scenario": scenario,
        "seed": seed,
        "steps": len(timeline) - 1,
        "regions": len(regions),
        "communes": sum(len(r.communes) for r in regions),
        "initial": first.as_row(),
        "final": last.as_row(),
        "delta": {
            "wellbeing": round(last.wellbeing - first.wellbeing, 6),
            "unmet_basic": round(last.unmet_basic - first.unmet_basic, 6),
            "overshoot": round(last.overshoot - first.overshoot, 6),
            "avg_trust": round(last.avg_trust - first.avg_trust, 6),
            "avg_autonomy": round(last.avg_autonomy - first.avg_autonomy, 6),
            "avg_truth_error": round(last.avg_truth_error - first.avg_truth_error, 6),
            "satisfaction_inequality": round(last.satisfaction_inequality - first.satisfaction_inequality, 6),
            "resilience_index": round(last.resilience_index - first.resilience_index, 6),
            "circularity_index": round(last.circularity_index - first.circularity_index, 6),
            "coordination_quality": round(last.coordination_quality - first.coordination_quality, 6),
            "planetary_reproduction_index": round(last.planetary_reproduction_index - first.planetary_reproduction_index, 6),
        },
        "planetary_boundaries_final": {k: round(v, 6) for k, v in boundary.pressures.items()},
        "planner": {
            "democratic_feedback": planner.democratic_feedback,
            "centralization": planner.centralization,
            "privacy_pressure": planner.privacy_pressure,
            "cooperation": planner.cooperation,
            "sufficiency_norm": planner.sufficiency_norm,
            "climate_discipline": planner.climate_discipline,
            "redistribution_strength": planner.redistribution_strength,
            "innovation_rate": planner.innovation_rate,
            "logistics_efficiency": planner.logistics_efficiency,
            "renewable_bias": planner.renewable_bias,
        },
        "interpretation": interpretation(first, last),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def interpretation(first: GlobalMetrics, last: GlobalMetrics) -> str:
    parts = []
    if last.wellbeing > first.wellbeing + 0.02:
        parts.append("general_improvement")
    elif last.wellbeing < first.wellbeing - 0.02:
        parts.append("general_deterioration")
    else:
        parts.append("mixed_or_stable")
    if last.overshoot < first.overshoot - 0.02:
        parts.append("planetary_overshoot_reduced")
    elif last.overshoot > first.overshoot + 0.02:
        parts.append("planetary_overshoot_increased")
    else:
        parts.append("planetary_boundaries_roughly_stable")
    if last.avg_truth_error < first.avg_truth_error:
        parts.append("truth_feedback_improved")
    else:
        parts.append("truth_feedback_not_improved")
    if last.avg_autonomy < first.avg_autonomy - 0.02:
        parts.append("freedom_warning")
    return ", ".join(parts)


def write_manifest(path: str, timeline: List[GlobalMetrics], boundary: BoundaryState, scenario: str) -> None:
    first = timeline[0]
    last = timeline[-1]
    lines = []
    lines.append("# Planetenwirtschaft-Simulation: erweiterte Wirkungswirtschaft")
    lines.append("")
    lines.append("Diese Simulation modelliert keine nationale Wirtschaft mit Geld, Preisen, BIP, Löhnen, Profit, Miete oder Außenhandelswerten.")
    lines.append("Sie modelliert eine planetare Wirkungswirtschaft: Bedürfnisse, Stoffe, Potenzen, ökologische Grenzen, Zeitbeiträge, Kapazitäten, Sektoren und soziale Rückkopplung.")
    lines.append("")
    lines.append("## Kernprinzip")
    lines.append("")
    lines.append("Eine wirtschaftliche Handlung ist hier keine Kauf-/Verkauf-Transaktion, sondern eine Zustandsänderung:")
    lines.append("")
    lines.append("```text")
    lines.append("Phänomen + Kausalität + Zeit + Intensität + Existenz + Potenzen + Wirkungen")
    lines.append("+ Substanz + Materie + Differenz + Bestimmung + Winkelrichtung")
    lines.append("→ Beitrag / Annahme / Transfer → neue Wirklichkeit")
    lines.append("```")
    lines.append("")
    lines.append("## Erweiterung gegenüber der Grundversion")
    lines.append("")
    lines.append("- `manufacturing`: Grundindustrie, Werkzeuge, Ersatzteile, materielle Transformation.")
    lines.append("- `storage`: Lager, Puffer, Stromspeicher, Vorratssicherheit.")
    lines.append("- `governance`: demokratische Koordination, Konfliktlösung, Wahrheitskorrektur.")
    lines.append("- `knowledge`: Forschung, offene Pläne, technisches Lernen.")
    lines.append("- `resilience`: Katastrophenschutz, Redundanz, Schockabsorption.")
    lines.append("- `macro_accounts.csv`: planetare Makrokonten ohne Geldlogik.")
    lines.append("- `effect_flow_audit.csv`: Kauf/Verkauf/Handel als Wirkungsfluss-Audit mit Vertragsbedingungen und Wahrheitsstapel.")
    lines.append("- `trade_contracts_report.md`: lesbare Darstellung von Handeln in allen Dimensionen.")
    lines.append("- `trade_dimension_catalog.csv`: Produkte, Arbeitsplätze, Dienstleistungen, Ökologie- und Klimaklauseln je Domäne.")
    lines.append("- `dimension_guide.csv`: Bedeutung jeder Dimension und ihr Verhältnis zu Verträgen.")
    lines.append("")
    lines.append("## Was planetar ist")
    lines.append("")
    lines.append("- Planetare Grenzen wirken auf alle Kommunen, nicht nur auf ein Land.")
    lines.append("- Regionen sind Bioregionen und Versorgungsknoten, keine Nationalstaaten.")
    lines.append("- Überschüsse werden über reale Dringlichkeit und Logistik verteilt, nicht über Kaufkraft.")
    lines.append("- Abfall ist eine ungelöste Materialdifferenz und wird in Reparatur/Stoffkreisläufe zurückgeführt.")
    lines.append("- Natur ist kein externes Rohstofflager, sondern Bedingung der Simulation.")
    lines.append("- Wahrheitswerte sind korrigierbar: Vertrauen, Demokratie und Fehlerprüfung beeinflussen die Steuerung.")
    lines.append("")
    lines.append("## Szenario")
    lines.append("")
    lines.append("`%s`" % scenario)
    lines.append("")
    lines.append("## Anfang → Ende")
    lines.append("")
    lines.append("| Kennzahl | Anfang | Ende | Veränderung |")
    lines.append("|---|---:|---:|---:|")
    lines.append("| Bevölkerung | %s | %s | %s |" % (format_big(first.population), format_big(last.population), format_big(last.population - first.population)))
    lines.append("| Wohlbefinden | %.3f | %.3f | %.3f |" % (first.wellbeing, last.wellbeing, last.wellbeing - first.wellbeing))
    lines.append("| unerfüllte Grundbedürfnisse | %.3f | %.3f | %.3f |" % (first.unmet_basic, last.unmet_basic, last.unmet_basic - first.unmet_basic))
    lines.append("| Vertrauen | %.3f | %.3f | %.3f |" % (first.avg_trust, last.avg_trust, last.avg_trust - first.avg_trust))
    lines.append("| Autonomie | %.3f | %.3f | %.3f |" % (first.avg_autonomy, last.avg_autonomy, last.avg_autonomy - first.avg_autonomy))
    lines.append("| Wahrheitsfehler | %.3f | %.3f | %.3f |" % (first.avg_truth_error, last.avg_truth_error, last.avg_truth_error - first.avg_truth_error))
    lines.append("| Versorgungsungleichheit | %.3f | %.3f | %.3f |" % (first.satisfaction_inequality, last.satisfaction_inequality, last.satisfaction_inequality - first.satisfaction_inequality))
    lines.append("| Resilienzindex | %.3f | %.3f | %.3f |" % (first.resilience_index, last.resilience_index, last.resilience_index - first.resilience_index))
    lines.append("| Zirkularitätsindex | %.3f | %.3f | %.3f |" % (first.circularity_index, last.circularity_index, last.circularity_index - first.circularity_index))
    lines.append("| Koordinationsqualität | %.3f | %.3f | %.3f |" % (first.coordination_quality, last.coordination_quality, last.coordination_quality - first.coordination_quality))
    lines.append("| planetarer Reproduktionsindex | %.3f | %.3f | %.3f |" % (first.planetary_reproduction_index, last.planetary_reproduction_index, last.planetary_reproduction_index - first.planetary_reproduction_index))
    lines.append("| planetare Überschreitung | %.3f | %.3f | %.3f |" % (first.overshoot, last.overshoot, last.overshoot - first.overshoot))
    lines.append("| mittlerer Grenzdruck | %.3f | %.3f | %.3f |" % (first.mean_boundary_pressure, last.mean_boundary_pressure, last.mean_boundary_pressure - first.mean_boundary_pressure))
    lines.append("")
    lines.append("## Endzustand planetarer Grenzen")
    lines.append("")
    for k in BOUNDARY_NAMES:
        lines.append("- `%s`: %.3f%s" % (k, boundary.pressures.get(k, 0.0), "  ⚠️ Überschreitung" if boundary.pressures.get(k, 0.0) > 1.0 else ""))
    lines.append("")
    lines.append("## Lesart")
    lines.append("")
    lines.append("Ein Wert über `1.0` bei planetaren Grenzen bedeutet Überschreitung. Ein sinkender Wahrheitsfehler bedeutet, dass Rückkopplung und demokratische Korrektur besser wurden. Sinkende Autonomie ist ein Warnsignal: Dann kippt die Wirkungswirtschaft in Kontrolle.")
    lines.append("")
    lines.append("## Wichtig")
    lines.append("")
    lines.append("Das Modell ist synthetisch und nicht kalibriert. Es ist ein Baukasten für Simulation, Spielmechanik, Systemdesign und Theorieentwicklung.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Terminal display: visible trade in dimensions
# ---------------------------------------------------------------------------


TERMINAL_COLOR_ENABLED = True


def set_terminal_color_enabled(enabled: bool) -> None:
    global TERMINAL_COLOR_ENABLED
    TERMINAL_COLOR_ENABLED = bool(enabled)


def ansi_wrap(text: object, *codes: str) -> str:
    raw = str(text)
    if not TERMINAL_COLOR_ENABLED or not codes:
        return raw
    return "".join(codes) + raw + "\033[0m"


def ansi_fg(r: int, g: int, b: int) -> str:
    return "\033[38;2;%d;%d;%dm" % (int(r), int(g), int(b))


def ansi_bg(r: int, g: int, b: int) -> str:
    return "\033[48;2;%d;%d;%dm" % (int(r), int(g), int(b))


ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_ITALIC = "\033[3m"
ANSI_UNDERLINE = "\033[4m"


DIMENSION_THEME = {
    "causality": {"fg": (255, 87, 87), "bg": (70, 10, 16), "symbol": "⚙", "glow": (255, 196, 196)},
    "time": {"fg": (255, 166, 0), "bg": (82, 45, 0), "symbol": "⏳", "glow": (255, 220, 150)},
    "intensity": {"fg": (255, 214, 10), "bg": (92, 72, 0), "symbol": "🔥", "glow": (255, 245, 170)},
    "existence": {"fg": (38, 222, 129), "bg": (9, 64, 33), "symbol": "●", "glow": (186, 255, 221)},
    "potencies": {"fg": (161, 108, 255), "bg": (49, 20, 92), "symbol": "✦", "glow": (227, 205, 255)},
    "effects": {"fg": (0, 245, 212), "bg": (0, 64, 58), "symbol": "↺", "glow": (180, 255, 244)},
    "substance": {"fg": (190, 140, 90), "bg": (72, 44, 20), "symbol": "▣", "glow": (240, 210, 180)},
    "matter": {"fg": (120, 185, 255), "bg": (20, 45, 79), "symbol": "⬢", "glow": (205, 231, 255)},
    "difference": {"fg": (255, 46, 138), "bg": (84, 9, 50), "symbol": "Δ", "glow": (255, 195, 224)},
    "determination": {"fg": (58, 134, 255), "bg": (12, 34, 86), "symbol": "⚖", "glow": (198, 224, 255)},
    "phenomena": {"fg": (255, 106, 188), "bg": (76, 11, 53), "symbol": "◉", "glow": (255, 210, 235)},
    "angle_direction": {"fg": (0, 229, 255), "bg": (0, 56, 69), "symbol": "🧭", "glow": (188, 250, 255)},
}


def dim_theme(dim: str) -> Dict[str, object]:
    return DIMENSION_THEME.get(dim, {"fg": (255, 255, 255), "bg": (40, 40, 40), "symbol": "•", "glow": (230, 230, 230)})


def color_text(text: object, fg: Optional[Tuple[int, int, int]] = None, bg: Optional[Tuple[int, int, int]] = None, bold: bool = False, italic: bool = False, underline: bool = False, dimmed: bool = False) -> str:
    codes: List[str] = []
    if bold:
        codes.append(ANSI_BOLD)
    if italic:
        codes.append(ANSI_ITALIC)
    if underline:
        codes.append(ANSI_UNDERLINE)
    if dimmed:
        codes.append(ANSI_DIM)
    if fg is not None:
        codes.append(ansi_fg(*fg))
    if bg is not None:
        codes.append(ansi_bg(*bg))
    return ansi_wrap(text, *codes)


def rainbow_text(text: str) -> str:
    palette = [
        (255, 87, 87), (255, 166, 0), (255, 214, 10), (38, 222, 129),
        (0, 245, 212), (58, 134, 255), (161, 108, 255), (255, 46, 138),
        (0, 229, 255), (255, 106, 188),
    ]
    if not TERMINAL_COLOR_ENABLED:
        return text
    out: List[str] = []
    for i, ch in enumerate(text):
        if ch.isspace():
            out.append(ch)
        else:
            out.append(color_text(ch, fg=palette[i % len(palette)], bold=True))
    return "".join(out)


def styled_badge(text: str, fg: Tuple[int, int, int], bg: Tuple[int, int, int], bold: bool = True) -> str:
    return color_text(" %s " % text, fg=fg, bg=bg, bold=bold)


def color_dim_short(short: str) -> str:
    for dim in TRUTH_DIMS:
        if DIMENSION_GUIDE_DE[dim]["short"] == short:
            theme = dim_theme(dim)
            return styled_badge(short, theme["fg"], theme["bg"])
    return short


def render_dim_meter(value: float, dim: str, width: int = 10) -> str:
    theme = dim_theme(dim)
    ratio = max(0.0, min(1.0, value / 4.0))
    filled = int(round(ratio * width))
    filled = max(0, min(width, filled))
    full = color_text("█" * filled, fg=theme["fg"], bold=True) if filled > 0 else ""
    rest = color_text("░" * (width - filled), fg=(95, 95, 95)) if width - filled > 0 else ""
    return full + rest


def render_truth_stack_badges(values: Dict[str, float]) -> str:
    parts: List[str] = []
    for dim in TRUTH_DIMS:
        guide = DIMENSION_GUIDE_DE[dim]
        theme = dim_theme(dim)
        digit = truth_digit(values.get(dim, 0.0))
        label = "%s%s=%d" % (theme["symbol"], guide["short"], digit)
        parts.append(styled_badge(label, theme["fg"], theme["bg"]))
    return " ".join(parts)


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")
ANSI_RESET = "\033[0m"


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


def terminal_char_width(ch: str) -> int:
    """Small stdlib-only display width estimator for UTF-8 terminal output."""
    if not ch:
        return 0
    code = ord(ch)
    if ch in "\n\r\t":
        return 0 if ch != "\t" else 4
    if unicodedata.combining(ch):
        return 0
    # Emoji blocks are commonly rendered double-width.
    if (
        0x1F000 <= code <= 0x1FAFF
        or 0x2600 <= code <= 0x27BF
    ):
        return 2
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def terminal_visible_width(text: str) -> int:
    clean = strip_ansi(str(text))
    return sum(terminal_char_width(ch) for ch in clean)


def terminal_columns() -> int:
    # shutil honors the real terminal when present and falls back safely in pipes.
    return max(40, shutil.get_terminal_size((118, 24)).columns)


def terminal_content_width(extra_margin: int = 0) -> int:
    return max(30, terminal_columns() - max(0, extra_margin))


def plain_wrap(text: str, width: int) -> List[str]:
    """Word-wrap plain text by terminal display width, without external deps."""
    width = max(8, width)
    words = str(text).replace("\n", " ").split(" ")
    lines: List[str] = []
    line = ""
    for word in words:
        if word == "":
            continue
        if terminal_visible_width(word) > width:
            if line:
                lines.append(line.rstrip())
                line = ""
            chunk = ""
            chunk_w = 0
            for ch in word:
                cw = terminal_char_width(ch)
                if chunk_w + cw > width and chunk:
                    lines.append(chunk)
                    chunk = ""
                    chunk_w = 0
                chunk += ch
                chunk_w += cw
            if chunk:
                line = chunk + " "
            continue
        candidate = (line + word + " ") if line else (word + " ")
        if terminal_visible_width(candidate.rstrip()) <= width:
            line = candidate
        else:
            if line:
                lines.append(line.rstrip())
            line = word + " "
    if line:
        lines.append(line.rstrip())
    return lines or [""]


def _ansi_active_codes_until(text: str) -> List[str]:
    active: List[str] = []
    for seq in ANSI_ESCAPE_RE.findall(text):
        if seq == ANSI_RESET:
            active = []
        else:
            active.append(seq)
    return active


def _last_break_position(text: str) -> Tuple[int, int]:
    """Return (string_index, visible_width_before_index) for the last useful break."""
    last_idx = -1
    last_width = 0
    width = 0
    i = 0
    while i < len(text):
        m = ANSI_ESCAPE_RE.match(text, i)
        if m:
            i = m.end()
            continue
        ch = text[i]
        if ch == " ":
            last_idx = i
            last_width = width
        width += terminal_char_width(ch)
        i += 1
    return last_idx, last_width


def ansi_wrap_line(text: str, width: int) -> List[str]:
    """Wrap one ANSI-colored line without counting escape sequences as width.

    It tries to break on spaces/arrows/separators first, then falls back to a
    hard UTF-8 character break. ANSI style codes are carried across wrapped
    lines so colors do not corrupt the terminal.
    """
    text = str(text)
    width = max(8, width)
    if terminal_visible_width(text) <= width:
        return [text]
    lines: List[str] = []
    current = ""
    current_w = 0
    active_codes: List[str] = []
    i = 0
    while i < len(text):
        m = ANSI_ESCAPE_RE.match(text, i)
        if m:
            seq = m.group(0)
            current += seq
            if seq == ANSI_RESET:
                active_codes = []
            else:
                active_codes.append(seq)
            i = m.end()
            continue
        ch = text[i]
        if ch == "\n":
            if active_codes:
                current += ANSI_RESET
            lines.append(current.rstrip())
            current = "".join(active_codes)
            current_w = 0
            i += 1
            continue
        cw = terminal_char_width(ch)
        if current_w + cw > width and current_w > 0:
            break_idx, break_w = _last_break_position(current)
            if break_idx > 0 and break_w >= max(8, int(width * 0.35)):
                head = current[:break_idx].rstrip()
                tail = current[break_idx + 1:].lstrip()
                if active_codes:
                    head += ANSI_RESET
                lines.append(head)
                active_codes = _ansi_active_codes_until(tail) or active_codes
                current = "".join(active_codes) + tail
                current_w = terminal_visible_width(tail)
            else:
                if active_codes:
                    current += ANSI_RESET
                lines.append(current.rstrip())
                current = "".join(active_codes)
                current_w = 0
            if ch == " " and current_w == 0:
                i += 1
            continue
        if current_w == 0 and ch == " ":
            i += 1
            continue
        current += ch
        current_w += cw
        i += 1
    if current or not lines:
        if active_codes:
            current += ANSI_RESET
        lines.append(current.rstrip())
    return lines


def wrap_ansi_text(text: str, width: Optional[int] = None) -> List[str]:
    width = terminal_content_width() if width is None else max(8, width)
    out: List[str] = []
    for line in str(text).split("\n"):
        out.extend(ansi_wrap_line(line, width))
    return out or [""]


def visible_pad(text: str, width: int) -> str:
    return str(text) + " " * max(0, width - terminal_visible_width(str(text)))


def terminal_print(*objects: object, sep: str = " ", end: str = "\n") -> None:
    """Screen-width-safe print for ANSI/UTF-8 terminal art."""
    text = sep.join(str(obj) for obj in objects)
    for line in wrap_ansi_text(text, terminal_content_width()):
        sys.stdout.write(line)
        sys.stdout.write("\n")
    if end and end != "\n":
        sys.stdout.write(end)


def print_dimension_bars(values: Dict[str, float], indent: str = "  ") -> None:
    for dim in TRUTH_DIMS:
        guide = DIMENSION_GUIDE_DE[dim]
        theme = dim_theme(dim)
        value = float(values.get(dim, 0.0))
        short = guide["short"]
        head = color_text("%s %s %s" % (theme["symbol"], short, guide["name_de"]), fg=theme["fg"], bold=True)
        meter = render_dim_meter(value, dim, width=12)
        value_txt = color_text("%.2f/4" % value, fg=theme["glow"], bold=True)
        role_txt = color_text(guide["contract_role"], fg=theme["glow"], italic=True)
        terminal_print("%s%-24s %s %s" % (indent, head, meter, value_txt))
        terminal_print("%s    %s" % (indent, role_txt))


def domain_color(domain: str) -> Tuple[int, int, int]:
    idx = list(DOMAINS).index(domain) if domain in DOMAINS else 0
    palette = [
        (0, 229, 255), (38, 222, 129), (255, 166, 0), (255, 106, 188),
        (58, 134, 255), (255, 214, 10), (161, 108, 255), (255, 87, 87),
        (190, 140, 90), (120, 185, 255), (255, 46, 138), (0, 245, 212),
        (255, 125, 0), (155, 225, 93), (0, 200, 140), (180, 180, 180),
    ]
    return palette[idx % len(palette)]


def domain_badge(domain: str) -> str:
    fg = domain_color(domain)
    bg = tuple(max(0, min(255, int(c * 0.22))) for c in fg)
    return styled_badge(domain.upper(), fg, bg)


def pretty_key_value(label: str, value: str, label_fg: Tuple[int, int, int] = (180, 220, 255), value_fg: Tuple[int, int, int] = (255, 255, 255)) -> None:
    label_text = label.ljust(18)
    available = max(12, terminal_content_width() - terminal_visible_width(label_text) - 1)
    wrapped = plain_wrap(value, available)
    for idx, line in enumerate(wrapped):
        if idx == 0:
            terminal_print("%s %s" % (color_text(label_text, fg=label_fg, bold=True), color_text(line, fg=value_fg)))
        else:
            terminal_print("%s %s" % (" " * terminal_visible_width(label_text), color_text(line, fg=value_fg)))


def colorful_bullet(text: str, fg: Tuple[int, int, int]) -> str:
    return color_text("▸", fg=fg, bold=True) + " " + color_text(text, fg=(245, 245, 245))


def terminal_header(title: str, subtitle: str = "") -> None:
    terminal_rule()
    header = "✦ " + title + " ✦"
    for line in plain_wrap(header, terminal_content_width()):
        terminal_print(color_text(line, fg=(255, 255, 255), bg=(35, 35, 35), bold=True))
    if subtitle:
        for line in plain_wrap(subtitle, terminal_content_width()):
            terminal_print(rainbow_text(line))
    terminal_rule()


def terminal_shorten(value: object, limit: int = 118) -> str:
    text = str(value).replace("\n", " ").strip()
    # Limit by visible width, not Python character count. This prevents wide UTF-8
    # symbols from pushing lines over the terminal edge. Long text is later wrapped
    # by terminal_print; this function only keeps huge fields readable.
    limit = max(10, min(limit, terminal_content_width() * 2))
    if terminal_visible_width(text) <= limit:
        return text
    out = ""
    used = 0
    for ch in text:
        cw = terminal_char_width(ch)
        if used + cw >= limit:
            break
        out += ch
        used += cw
    return out.rstrip() + "…"


def terminal_rule(title: str = "", width: Optional[int] = None) -> None:
    screen = terminal_content_width() if width is None else min(max(30, width), terminal_content_width())
    if title:
        label = "❖ " + title.strip() + " ❖"
        label_w = terminal_visible_width(label) + 2
        if label_w >= screen:
            terminal_print(rainbow_text("═" * screen))
            for line in plain_wrap(label, screen):
                terminal_print(rainbow_text(line))
            terminal_print(rainbow_text("═" * screen))
            return
        fill = max(0, screen - label_w)
        left = "═" * (fill // 2)
        right = "═" * (fill - (fill // 2))
        terminal_print(rainbow_text(left + " " + label + " " + right))
    else:
        terminal_print(rainbow_text("═" * screen))


def sentence_items(text: str) -> List[str]:
    """Split long German condition text into readable terminal bullets."""
    parts: List[str] = []
    current = ""
    for chunk in text.split(". "):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.endswith("."):
            chunk = chunk + "."
        if len(chunk) > 230:
            # Keep very long ecology/climate clauses readable without external wrapping libs.
            words = chunk.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > 170:
                    if line:
                        parts.append(line.rstrip())
                    line = word + " "
                else:
                    line += word + " "
            if line:
                parts.append(line.rstrip())
        else:
            parts.append(chunk)
    return parts


def select_visible_flows(flows: List[EffectFlow], limit: int) -> List[EffectFlow]:
    """Pick diverse, visible flows across domains and trade kinds."""
    if limit <= 0 or not flows:
        return []
    selected: List[EffectFlow] = []
    seen = set()
    # First pass: one high-priority flow per kind/domain.
    for flow in sorted(flows, key=lambda f: (f.truth_stack_priority_0_1, f.activated_effect), reverse=True):
        key = (flow.kind, flow.domain)
        if key in seen:
            continue
        selected.append(flow)
        seen.add(key)
        if len(selected) >= limit:
            return selected
    # Second pass: fill by largest activated effect.
    used_ids = set(id(f) for f in selected)
    for flow in sorted(flows, key=lambda f: f.activated_effect, reverse=True):
        if id(flow) not in used_ids:
            selected.append(flow)
            used_ids.add(id(flow))
        if len(selected) >= limit:
            break
    return selected


def print_dimension_guide_terminal() -> None:
    terminal_header("DIMENSIONEN DES HANDELNS", "Jede Wahrheitsdimension hat ihre eigene Farbe, ihr eigenes Symbol und ihre eigene Vertragsrolle.")
    terminal_print(color_text("Skala:", fg=(255, 214, 10), bold=True), color_text("0 = nicht vorhanden/falsch | 1 = schwach/latent | 2 = teilweise | 3 = stark | 4 = kritisch/hoch real", fg=(240, 240, 240)))
    terminal_print(color_text("Stapel-Reihenfolge:", fg=(0, 229, 255), bold=True), render_truth_stack_badges({dim: 4.0 for dim in TRUTH_DIMS}))
    terminal_print(color_text("Der Stapel ist keine Geldzahl. Er ist die Vertrags- und Zustands-Signatur eines Wirkungsflusses.", fg=(255, 255, 255), italic=True))
    terminal_print("")
    for dim in TRUTH_DIMS:
        g = DIMENSION_GUIDE_DE[dim]
        theme = dim_theme(dim)
        head = styled_badge("%s %s %s" % (theme["symbol"], g["short"], g["name_de"]), theme["fg"], theme["bg"])
        terminal_print(head)
        terminal_print("  " + color_text("Frage:   ", fg=theme["glow"], bold=True) + color_text(g["question"], fg=(245, 245, 245)))
        terminal_print("  " + color_text("Vertrag: ", fg=theme["glow"], bold=True) + color_text(g["contract_role"], fg=(245, 245, 245), italic=True))
        terminal_print("  " + color_text("Ersetzt: ", fg=theme["glow"], bold=True) + color_text(g["economic_replacement"], fg=(245, 245, 245)))
        sample = {d: 0.0 for d in TRUTH_DIMS}
        sample[dim] = 4.0
        terminal_print("  " + color_text("Vollausprägung:", fg=theme["glow"], bold=True) + " " + render_truth_stack_badges(sample))
        terminal_print("")


def print_trade_catalog_terminal(limit: int = 0) -> None:
    terminal_header("WAS GEHANDELT WIRD", "Produkte, Arbeitsplätze, Dienstleistungen sowie Ökologie- und Klimaklauseln werden als Wirkungen sichtbar.")
    domains = list(DOMAINS)
    if limit and limit > 0:
        domains = domains[:limit]
    for domain in domains:
        item = TRADE_CATALOG[domain]
        fg = domain_color(domain)
        terminal_print(domain_badge(domain))
        pretty_key_value("Gehandelte Wirkung", terminal_shorten(item["trade_object"], 170), label_fg=fg)
        pretty_key_value("Gemeint als", terminal_shorten(item["meant_as"], 170), label_fg=fg)
        pretty_key_value("Produkte", terminal_shorten(item["products"], 170), label_fg=fg)
        pretty_key_value("Arbeitsplätze", terminal_shorten(item["workplaces"], 170), label_fg=fg)
        pretty_key_value("Dienstleistungen", terminal_shorten(item["services"], 170), label_fg=fg)
        pretty_key_value("Ökologie", terminal_shorten(item["ecology"], 170), label_fg=fg)
        pretty_key_value("Klima", terminal_shorten(item["climate"], 170), label_fg=fg)
        terminal_print(color_text("─" * terminal_content_width(), fg=fg))
    terminal_print("")


def print_visible_trade_contracts(flows: List[EffectFlow], limit: int = 16, detail: bool = False) -> None:
    selected = select_visible_flows(flows, limit)
    terminal_header("SICHTBARES HANDELN IN DIMENSIONEN", "Extrem bunte Vertragsanzeige: jede Dimension hat ihre eigene Farbe und einen sichtbaren Wahrheitsbalken.")
    if not selected:
        terminal_print(color_text("Keine Wirkungsflüsse vorhanden. Erhöhe --steps oder setze --show-trades auf einen Wert > 0.", fg=(255, 120, 120), bold=True))
        terminal_print("")
        return
    terminal_print(color_text("Alte Form:", fg=(255, 106, 188), bold=True), color_text("Ware + Menge + Preis + Eigentum → kaufen/verkaufen/importieren/exportieren", fg=(240, 240, 240)))
    terminal_print(color_text("Neue Form:", fg=(0, 229, 255), bold=True), color_text("Kausalität + Zeit + Intensität + Existenz + Potenzen + Wirkungen + Substanz + Materie + Differenz + Bestimmung + Phänomene + Winkelrichtung → Wirkungsvertrag", fg=(240, 240, 240)))
    terminal_print(color_text("Anzeige:", fg=(255, 214, 10), bold=True), color_text("Jeder Eintrag ist ein realer Wirkungsfluss, keine Geldtransaktion. activated_effect ist Wirkungseinheit, nicht Wert.", fg=(240, 240, 240), italic=True))
    terminal_print("")
    for idx, flow in enumerate(selected, 1):
        validity_de = CONTRACT_VALIDITY_LABELS.get(flow.contract_validity, flow.contract_validity)
        head = "VERTRAG %03d" % idx
        title = "%s  %s  %s" % (head, flow.domain.upper(), validity_de.upper())
        terminal_rule(title, width=118)
        dom_fg = domain_color(flow.domain)
        terminal_print(domain_badge(flow.domain), color_text(validity_de.upper(), fg=dom_fg, bold=True), color_text("•", fg=(255,255,255)), color_text(flow.kind, fg=(220,220,220), italic=True))
        pretty_key_value("Art", flow.kind, label_fg=dom_fg)
        pretty_key_value("Ersetzt früher", flow.legacy_term_replaced, label_fg=dom_fg)
        pretty_key_value("Handlung", flow.action, label_fg=dom_fg)
        pretty_key_value("Von → Zu", "%s/%s → %s/%s" % (flow.from_region, flow.from_commune, flow.to_region, flow.to_commune), label_fg=dom_fg)
        pretty_key_value("Sektor", flow.sector, label_fg=dom_fg)
        pretty_key_value("Aktivierte Wirkung", "%.3f" % flow.activated_effect, label_fg=dom_fg, value_fg=(255, 240, 170))
        pretty_key_value("Kausale Kette", terminal_shorten(flow.causal_link, 170), label_fg=dom_fg)
        pretty_key_value("Winkelrichtung", terminal_shorten(flow.direction_vector, 170), label_fg=dom_fg)
        terminal_print(color_text("Wahrheitsstapel", fg=(255,255,255), bold=True) + ":  " + render_truth_stack_badges(flow.values))
        pretty_key_value("Base5-Stapel", flow.truth_stack_base5, label_fg=(255, 214, 10), value_fg=(255,255,255))
        pretty_key_value("Score / Priorität", "%.3f / %.3f" % (flow.truth_stack_score_0_4, flow.truth_stack_priority_0_1), label_fg=(0, 229, 255), value_fg=(255,255,255))
        pretty_key_value("Deutung", terminal_shorten(flow.dimension_meaning, 220), label_fg=(255, 106, 188))
        pretty_key_value("Was gehandelt", terminal_shorten(flow.trade_object, 190), label_fg=(38, 222, 129))
        pretty_key_value("Gemeint als", terminal_shorten(flow.meant_as, 190), label_fg=(161, 108, 255))
        terminal_print(color_text("Dimensionen im Detail", fg=(255,255,255), bold=True, underline=True))
        print_dimension_bars(flow.values, indent="  ")
        if detail:
            pretty_key_value("Produkte", terminal_shorten(flow.product_examples, 210), label_fg=(255, 214, 10))
            pretty_key_value("Arbeitsplätze", terminal_shorten(flow.workplace_examples, 210), label_fg=(255, 166, 0))
            pretty_key_value("Dienstleistungen", terminal_shorten(flow.service_examples, 210), label_fg=(58, 134, 255))
            pretty_key_value("Ökologiebedingung", terminal_shorten(flow.ecological_clause, 210), label_fg=(38, 222, 129))
            pretty_key_value("Klimabedingung", terminal_shorten(flow.climate_clause, 210), label_fg=(0, 229, 255))
            terminal_print(color_text("Vertragsbedingungen", fg=(255,255,255), bold=True, underline=True))
            cond_color_cycle = [(255,87,87), (255,166,0), (255,214,10), (38,222,129), (58,134,255), (161,108,255), (255,46,138), (0,229,255)]
            for i, cond in enumerate(sentence_items(flow.contract_conditions)[:12]):
                fg = cond_color_cycle[i % len(cond_color_cycle)]
                terminal_print("  " + colorful_bullet(terminal_shorten(cond, 210), fg))
        else:
            pretty_key_value("Bedingungen", terminal_shorten(flow.contract_conditions, 260), label_fg=(255, 106, 188))
        terminal_print(color_text("┄" * 116, fg=dom_fg))
        terminal_print("")


def print_truth_stack_explanation_terminal() -> None:
    terminal_header("GESTAPELTER WAHRHEITSWERT", "Der Stack ist eine farbige Vertrags- und Zustands-Signatur, keine Geldzahl.")
    sample = {
        "causality": 3.0, "time": 3.0, "intensity": 4.0, "existence": 4.0,
        "potencies": 3.0, "effects": 4.0, "substance": 2.0, "matter": 3.0,
        "difference": 4.0, "determination": 3.0, "phenomena": 4.0, "angle_direction": 3.0,
    }
    terminal_print(color_text("Beispiel-Base5:", fg=(255, 214, 10), bold=True), color_text("334434234343", fg=(255,255,255), bold=True))
    terminal_print(color_text("Farbstapel:", fg=(0, 229, 255), bold=True), render_truth_stack_badges(sample))
    terminal_print(color_text("Dimensionale Auslesung:", fg=(255,255,255), bold=True, underline=True))
    print_dimension_bars(sample, indent="  ")
    terminal_print(color_text("Bedeutung", fg=(255,255,255), bold=True, underline=True))
    terminal_print("  " + colorful_bullet("Kausalität=3: Ursache ist gut getroffen.", dim_theme("causality")["fg"]))
    terminal_print("  " + colorful_bullet("Zeit=3: dringlich.", dim_theme("time")["fg"]))
    terminal_print("  " + colorful_bullet("Intensität=4: sehr starkes Phänomen.", dim_theme("intensity")["fg"]))
    terminal_print("  " + colorful_bullet("Existenz=4: real vorhanden, nicht nur behauptet.", dim_theme("existence")["fg"]))
    terminal_print("  " + colorful_bullet("Potenzen=3: Lösungsmöglichkeiten existieren.", dim_theme("potencies")["fg"]))
    terminal_print("  " + colorful_bullet("Wirkungen=4: hoher positiver Systemeffekt.", dim_theme("effects")["fg"]))
    terminal_print("  " + colorful_bullet("Substanz=2: Stoffe/Energie/Wissen sind nur teilweise verfügbar.", dim_theme("substance")["fg"]))
    terminal_print("  " + colorful_bullet("Materie=3: Ort/Infrastruktur sind ausreichend erreichbar.", dim_theme("matter")["fg"]))
    terminal_print("  " + colorful_bullet("Differenz=4: Bedarfslücke ist maximal sichtbar.", dim_theme("difference")["fg"]))
    terminal_print("  " + colorful_bullet("Bestimmung=3: sozial/demokratisch gut bestimmt.", dim_theme("determination")["fg"]))
    terminal_print("  " + colorful_bullet("Phänomene=4: stark sichtbar/gemeldet/gemessen.", dim_theme("phenomena")["fg"]))
    terminal_print("  " + colorful_bullet("Winkelrichtung=3: Handlung wirkt eher regenerativ/freiheitlich.", dim_theme("angle_direction")["fg"]))
    terminal_print("")
    terminal_print(color_text("Wichtig:", fg=(255, 106, 188), bold=True), color_text("Der Stapel wird zwar als Zahl gespeichert, aber nicht als Wert/Preis benutzt.", fg=(245,245,245)))
    terminal_print(color_text("Der Score sortiert Prioritäten; die Einzelziffern erzeugen Vertragsbedingungen.", fg=(245,245,245), italic=True))
    terminal_print(color_text("Hohe Differenz bei niedriger Winkelrichtung heißt: Bedarf real, aber Handlung umbauen oder blockieren.", fg=(245,245,245)))
    terminal_print("")


# ---------------------------------------------------------------------------
# Extreme UTF-8 / ANSI art gallery for visible planetary economy diagrams
# ---------------------------------------------------------------------------


def art_palette() -> List[Tuple[int, int, int]]:
    return [
        (255, 87, 87), (255, 166, 0), (255, 214, 10), (38, 222, 129),
        (0, 245, 212), (58, 134, 255), (161, 108, 255), (255, 46, 138),
        (0, 229, 255), (255, 106, 188), (190, 140, 90), (155, 225, 93),
    ]


def art_color(index: int) -> Tuple[int, int, int]:
    palette = art_palette()
    return palette[index % len(palette)]


def art_dim_line(dim: str, value: float, width: int = 36) -> str:
    theme = dim_theme(dim)
    guide = DIMENSION_GUIDE_DE[dim]
    available = terminal_content_width() - 34
    width = max(4, min(width, available))
    fill = max(0, min(width, int(round((clamp(value, 0.0, 4.0) / 4.0) * width))))
    meter = color_text("█" * fill, fg=theme["fg"], bold=True) + color_text("░" * (width - fill), fg=(70, 70, 70))
    return "%s %s %s %s" % (
        styled_badge("%s%s" % (theme["symbol"], guide["short"]), theme["fg"], theme["bg"]),
        meter,
        color_text("%4.2f" % value, fg=theme["glow"], bold=True),
        color_text(guide["name_de"], fg=theme["fg"], bold=True),
    )


def art_box_line(text: str, fg: Tuple[int, int, int], width: int = 100) -> str:
    box_width = min(max(30, width), terminal_content_width())
    inner = max(10, box_width - 2)
    wrapped = plain_wrap(str(text), max(8, inner - 2))
    lines: List[str] = []
    for raw in wrapped:
        body = visible_pad(" " + raw, inner - 1) + " "
        lines.append(color_text("┃", fg=fg, bold=True) + color_text(body, fg=(245, 245, 245)) + color_text("┃", fg=fg, bold=True))
    return "\n".join(lines)


def art_panel(title: str, number: int, subtitle: str = "") -> None:
    fg = art_color(number)
    box_width = terminal_content_width()
    inner = max(10, box_width - 2)
    terminal_print("")
    terminal_print(color_text("╔" + "═" * inner + "╗", fg=fg, bold=True))
    title_lines = plain_wrap("  %02d  %s" % (number, title), inner)
    for line in title_lines:
        terminal_print(color_text("║", fg=fg, bold=True) + color_text(visible_pad(line, inner), fg=fg, bold=True) + color_text("║", fg=fg, bold=True))
    if subtitle:
        for line in plain_wrap("  " + subtitle, inner):
            terminal_print(color_text("║", fg=fg, bold=True) + color_text(visible_pad(line, inner), fg=(255, 255, 255), italic=True) + color_text("║", fg=fg, bold=True))
    terminal_print(color_text("╚" + "═" * inner + "╝", fg=fg, bold=True))


def art_ratio_bar(label: str, ratio: float, fg: Tuple[int, int, int], width: int = 50) -> str:
    ratio = clamp(ratio, 0.0, 1.0)
    label_width = min(24, max(10, terminal_content_width() // 3))
    percent_width = 7
    width = max(3, min(width, terminal_content_width() - label_width - percent_width - 3))
    label_clean = str(label)
    if terminal_visible_width(label_clean) > label_width:
        label_clean = plain_wrap(label_clean, label_width)[0]
    fill = int(round(ratio * width))
    return "%s %s %s" % (
        color_text(visible_pad(label_clean, label_width), fg=fg, bold=True),
        color_text("█" * fill, fg=fg, bold=True) + color_text("░" * (width - fill), fg=(72, 72, 72)),
        color_text("%5.1f%%" % (ratio * 100.0), fg=(255, 255, 255), bold=True),
    )


def art_spark(values: List[float], fg: Tuple[int, int, int], width: int = 60) -> str:
    chars = "▁▂▃▄▅▆▇█"
    width = max(6, min(width, terminal_content_width() - 18))
    if not values:
        return ""
    if len(values) > width:
        step = float(len(values)) / float(width)
        sampled = []
        for i in range(width):
            sampled.append(values[int(i * step)])
    else:
        sampled = list(values)
    mn = min(sampled)
    mx = max(sampled)
    span = mx - mn
    out = []
    for value in sampled:
        if span <= 1e-9:
            idx = 3
        else:
            idx = int(round(((value - mn) / span) * (len(chars) - 1)))
        out.append(color_text(chars[max(0, min(len(chars) - 1, idx))], fg=fg, bold=True))
    return "".join(out)


def top_flows_for_art(flows: List[EffectFlow], limit: int = 8) -> List[EffectFlow]:
    return sorted(flows, key=lambda f: (f.truth_stack_priority_0_1, f.activated_effect), reverse=True)[:limit]


def top_truth_for_art(truth_vectors: List[TruthVector], limit: int = 6) -> List[TruthVector]:
    return sorted(truth_vectors, key=lambda tv: tv.priority(), reverse=True)[:limit]


def macro_by_domain(macro_accounts: List[MacroAccountRow]) -> Dict[str, MacroAccountRow]:
    result: Dict[str, MacroAccountRow] = {}
    for row in macro_accounts:
        result[row.domain] = row
    return result


def art_planet_layer_stack(last: GlobalMetrics) -> None:
    art_panel("PLANETEN-SCHICHTEN STATT VOLKSWIRTSCHAFT", 1, "Planet → Länder/Großräume → Kommunen → Gruppen → Einzelpersonen")
    layers = [
        ("🌍 PLANET", "Grenzen: Klima, Wasser, Boden, Biodiversität, Material", (0, 229, 255), last.mean_boundary_pressure),
        ("▰ LÄNDER / GROSSRÄUME", "Infrastruktur, Recht, Ausgleich, Krisenschutz", (58, 134, 255), last.coordination_quality),
        ("◈ KOMMUNEN", "Wohnung, Wasser, Nahrung, Pflege, Energie vor Ort", (38, 222, 129), last.wellbeing),
        ("✦ GRUPPEN", "Fähigkeiten: Bau, Pflege, Forschung, Reparatur, Ökologie", (255, 214, 10), last.macro_capacity),
        ("● EINZELPERSONEN", "Bedürfnis, Fähigkeit, Freiheit, Widerspruchsrecht", (255, 106, 188), last.avg_autonomy),
    ]
    for name, desc, fg, ratio in layers:
        terminal_print(art_ratio_bar(name, clamp(ratio), fg, width=44))
        terminal_print("   " + color_text("╰─ ", fg=fg) + color_text(desc, fg=(245, 245, 245)))
    terminal_print(color_text("        ╰──────────────────────────────────────────────────────────────────────╯", fg=(161,108,255)))
    terminal_print(color_text("        Wirtschaft = Wirklichkeitsänderung innerhalb planetarer Grenzen", fg=(255,255,255), bold=True))


def art_truth_stack_totem(flow: Optional[EffectFlow]) -> None:
    art_panel("GESTAPELTER WAHRHEITSWERT ALS TOTEM", 2, "Die Ziffern sind Dimensionen, nicht Preis und nicht Geld.")
    values = flow.values if flow is not None else {dim: 3.0 for dim in TRUTH_DIMS}
    stack = truth_stack_base5(values)
    terminal_print(color_text("BASE5-STACK: ", fg=(255,214,10), bold=True) + render_truth_stack_badges(values))
    terminal_print(color_text("Zahlensignatur: ", fg=(0,229,255), bold=True) + color_text(stack, fg=(255,255,255), bold=True))
    terminal_print("")
    for dim in TRUTH_DIMS:
        terminal_print("      " + art_dim_line(dim, values.get(dim, 0.0), width=32))
    terminal_print(color_text("      │", fg=(255,255,255)))
    terminal_print(color_text("      ▼", fg=(255,255,255), bold=True))
    terminal_print(color_text("  Vertragsgültigkeit + Priorität + Bedingungen", fg=(255,106,188), bold=True))


def art_causal_pipeline(flow: Optional[EffectFlow]) -> None:
    art_panel("KAUSALKETTE: HANDEL ALS WIRKUNGSFLUSS", 3, "Nicht Ware → Preis, sondern Ursache → Wirkung → neue Wirklichkeit.")
    fg = (0, 245, 212)
    parts = ["BEDARF", "DIFFERENZ", "URSACHE", "POTENZ", "SUBSTANZ", "HANDLUNG", "WIRKUNG", "AUDIT"]
    line = ""
    for i, part in enumerate(parts):
        line += styled_badge(part, art_color(i), tuple(int(c * 0.20) for c in art_color(i)))
        if i < len(parts) - 1:
            line += color_text("━━▶", fg=art_color(i + 1), bold=True)
    terminal_print(line)
    if flow is not None:
        terminal_print(art_box_line("Beispiel: %s" % flow.causal_link, fg, width=110))
        terminal_print(art_box_line("Aktivierte Wirkung: %.3f | Domain: %s | Art: %s" % (flow.activated_effect, flow.domain, flow.kind), fg, width=110))
    terminal_print(color_text("          ╭──────────── Rückkopplung: Phänomene + Wahrheitfehler + Betroffenenberichte ────────────╮", fg=(255,106,188)))
    terminal_print(color_text("          ╰──────────────────────────────────────◀──────────────────────────────────────────────────╯", fg=(255,106,188)))


def art_buy_sell_replacement() -> None:
    art_panel("KAUFEN / VERKAUFEN WIRD UMGEBAUT", 4, "Die alten Marktwörter bleiben nur als Übersetzungshilfe.")
    rows = [
        ("KAUFEN", "Bedarfswirkung annehmen", "need_acceptance", (255, 106, 188)),
        ("VERKAUFEN", "Fähigkeit/Zeit/Substanz beitragen", "contribution_offer", (255, 214, 10)),
        ("IMPORT", "Wirkung von außen in Mangellage übertragen", "planetary_transfer", (0, 229, 255)),
        ("EXPORT", "Überschuss in reale Differenz geben", "planetary_transfer", (38, 222, 129)),
    ]
    for old, new, kind, fg in rows:
        terminal_print(styled_badge(old, fg, tuple(int(c*0.22) for c in fg)) + color_text("  ─────╮", fg=fg, bold=True))
        terminal_print(color_text("              ├──▶ ", fg=fg, bold=True) + color_text(new, fg=(255,255,255), bold=True) + "  " + color_text("[%s]" % kind, fg=fg))
        terminal_print(color_text("              ╰──▶ Wahrheit: K/Z/I/E/P/W/S/M/D/B/Ph/R", fg=fg))


def art_boundary_dashboard(last: GlobalMetrics) -> None:
    art_panel("PLANETARE GRENZEN ALS DASHBOARD", 5, "Über 100% heißt Overshoot; darunter liegt tragfähiger Betriebsraum.")
    # We do not store every boundary in GlobalMetrics, so use visible metrics plus worst boundary.
    proxies = [
        ("climate", last.worst_boundary_pressure if last.worst_boundary == "climate" else min(1.0, last.mean_boundary_pressure * 1.05)),
        ("biosphere", min(1.0, last.mean_boundary_pressure * 0.97 + 0.03)),
        ("freshwater", min(1.0, last.mean_boundary_pressure * 0.93 + 0.04)),
        ("soil", min(1.0, last.mean_boundary_pressure * 0.90 + 0.06)),
        ("pollution", min(1.0, last.mean_boundary_pressure * 0.95 + 0.05)),
        ("material", min(1.0, last.mean_boundary_pressure * 0.88 + 0.02)),
        ("energy", min(1.0, last.mean_boundary_pressure * 0.92 + 0.03)),
    ]
    for i, (name, pressure) in enumerate(proxies):
        fg = art_color(i + 2)
        danger = pressure > 1.0
        label = ("⚠ " if danger else "✓ ") + name
        terminal_print(art_ratio_bar(label, min(pressure, 1.35) / 1.35, fg, width=54) + "  " + color_text("%.3f" % pressure, fg=(255, 255, 255), bold=True))
    terminal_print(color_text("Overshoot gesamt: %.4f | schlimmste Grenze: %s %.3f" % (last.overshoot, last.worst_boundary, last.worst_boundary_pressure), fg=(255, 87, 87), bold=True))


def art_climate_contract_shield(last: GlobalMetrics) -> None:
    art_panel("KLIMAVERTRAG ALS SCHUTZSCHILD", 6, "Jede Wirkung trägt eine Klimarichtung: regenerativ, neutral, riskant oder zerstörend.")
    fg1, fg2, fg3 = (0, 229, 255), (255, 214, 10), (255, 87, 87)
    terminal_print(color_text("                 ╭────────────────────────────╮", fg=fg1, bold=True))
    terminal_print(color_text("             ╭───┤   KLIMA-RELEVANZ-PRÜFUNG  ├───╮", fg=fg1, bold=True))
    terminal_print(color_text("             │   ╰────────────────────────────╯   │", fg=fg1, bold=True))
    terminal_print(color_text("        CO₂  │   Energie  Material  Transport     │  Hitze", fg=fg2, bold=True))
    terminal_print(color_text("             │        ╲      │      ╱             │", fg=fg2, bold=True))
    terminal_print(color_text("             │         ╲     ▼     ╱              │", fg=fg2, bold=True))
    terminal_print(color_text("             │       WINKELRICHTUNG R             │", fg=fg3, bold=True))
    terminal_print(color_text("             ╰──────────────┬─────────────────────╯", fg=fg1, bold=True))
    terminal_print(color_text("                            ▼", fg=fg1, bold=True))
    terminal_print(color_text("                  Vertrag: gültig / bedingt / blockiert", fg=(255,255,255), bold=True))
    terminal_print(art_ratio_bar("Klimadruck Proxy", clamp(last.worst_boundary_pressure / 1.4), fg3, width=50))


def art_material_cycle(last: GlobalMetrics) -> None:
    art_panel("MATERIALKREISLAUF: SUBSTANZ UND MATERIE", 7, "Abfall ist ungelöste Differenz; Reparatur ist positive Wirkung.")
    fg = (38, 222, 129)
    terminal_print(color_text("        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐", fg=fg, bold=True))
    terminal_print(color_text("        │  SUBSTANZ S  │ ───▶ │  PRODUKTION  │ ───▶ │  NUTZUNG     │", fg=fg, bold=True))
    terminal_print(color_text("        └──────┬───────┘      └──────┬───────┘      └──────┬───────┘", fg=fg, bold=True))
    terminal_print(color_text("               │                     │                     │", fg=fg, bold=True))
    terminal_print(color_text("               ▼                     ▼                     ▼", fg=fg, bold=True))
    terminal_print(color_text("        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐", fg=(255,214,10), bold=True))
    terminal_print(color_text("        │  REPARATUR   │ ◀─── │  ABFALL Δ    │ ◀─── │  VERSCHLEISS │", fg=(255,214,10), bold=True))
    terminal_print(color_text("        └──────────────┘      └──────────────┘      └──────────────┘", fg=(255,214,10), bold=True))
    terminal_print(art_ratio_bar("circularity_index", last.circularity_index, (0,245,212), width=46))
    terminal_print(art_ratio_bar("repair_materials", clamp(last.repair_materials / max(1.0, last.repair_materials + last.waste_stock)), (255,106,188), width=46))


def art_commune_network(flows: List[EffectFlow]) -> None:
    art_panel("KOMMUNEN-NETZ: WIRKUNGEN STATT MÄRKTE", 8, "Pfeile bedeuten kausale Wirkung, nicht Kaufpreis.")
    selected = top_flows_for_art(flows, 6)
    nodes = ["◉", "◎", "●", "◌", "◍", "◐"]
    for i, flow in enumerate(selected):
        fg = domain_color(flow.domain)
        left = "%s %s/%s" % (nodes[i % len(nodes)], flow.from_region, flow.from_commune)
        right = "%s/%s %s" % (flow.to_region, flow.to_commune, nodes[(i + 2) % len(nodes)])
        arrow = "═" * (8 + (i % 5)) + "▶"
        terminal_print(color_text(left.ljust(34), fg=fg, bold=True) + color_text(arrow, fg=fg, bold=True) + color_text(right, fg=(255,255,255), bold=True))
        terminal_print("    " + domain_badge(flow.domain) + " " + color_text(flow.kind, fg=fg) + " " + color_text("%.2f Wirkungseinheiten" % flow.activated_effect, fg=(255,240,170), bold=True))
    if not selected:
        terminal_print(color_text("Keine Flows vorhanden.", fg=(255,87,87), bold=True))


def art_products_jobs_services_map() -> None:
    art_panel("PRODUKTE + ARBEITSPLÄTZE + DIENSTLEISTUNGEN", 9, "Alles bleibt sichtbar, aber nicht als Wertträger, sondern als Wirkungsträger.")
    trio = [
        ("PRODUKTE", "Werkzeuge • Nahrung • Wasser • Wohnraum • Medizin • Batterien", (255,214,10)),
        ("ARBEITSPLÄTZE", "Pflege • Reparatur • Landwirtschaft • Forschung • Bau • Energie", (255,106,188)),
        ("DIENSTLEISTUNGEN", "Heilung • Bildung • Transport • Audit • Verteilung • Betreuung", (0,229,255)),
        ("ÖKOLOGIE", "Boden • Wasserhaushalt • Kühlung • Biodiversität • Lebensraum", (38,222,129)),
    ]
    terminal_print(color_text("                 ╭──────────── WIRKUNGSVERTRAG ────────────╮", fg=(255,255,255), bold=True))
    for name, desc, fg in trio:
        terminal_print(color_text("    ", fg=fg) + styled_badge(name, fg, tuple(int(c*0.20) for c in fg)) + color_text(" ───▶ ", fg=fg, bold=True) + color_text(desc, fg=(245,245,245)))
    terminal_print(color_text("                 ╰────── Wahrheit + Bedingungen + Audit ───╯", fg=(255,255,255), bold=True))


def art_service_constellation() -> None:
    art_panel("DIENSTLEISTUNGS-KONSTELLATION", 10, "Sorge, Bildung, Gesundheit und Mobilität sind Reproduktionswirkungen.")
    center = color_text("       ✦ REPRODUKTION ✦", fg=(255,255,255), bg=(50,20,90), bold=True)
    terminal_print(color_text("             health", fg=domain_color("health"), bold=True) + "        " + color_text("care", fg=domain_color("care"), bold=True))
    terminal_print(color_text("                ╲         ╱", fg=(255,106,188), bold=True))
    terminal_print(color_text("                 ╲       ╱", fg=(255,106,188), bold=True))
    terminal_print("                  " + center)
    terminal_print(color_text("                 ╱   │   ╲", fg=(0,229,255), bold=True))
    terminal_print(color_text("        education    │    mobility", fg=(0,229,255), bold=True))
    terminal_print(color_text("                     governance", fg=domain_color("governance"), bold=True))
    terminal_print(color_text("Jede Kante ist ein Wirkungsfluss: Zeit, Vertrauen, Pflege, Wissen, Zugang.", fg=(245,245,245)))


def art_angle_compass(flow: Optional[EffectFlow]) -> None:
    art_panel("WINKELRICHTUNG: ÖKONOMISCHER KOMPASS", 11, "Richtung zählt genauso wie Intensität.")
    r = flow.values.get("angle_direction", 3.0) if flow is not None else 3.0
    fg = dim_theme("angle_direction")["fg"]
    terminal_print(color_text("                         ↑ regenerativ / freiheitlich", fg=(38,222,129), bold=True))
    terminal_print(color_text("                         │", fg=fg, bold=True))
    terminal_print(color_text("        lokal passend ◀──┼──▶ planetar passend", fg=fg, bold=True))
    terminal_print(color_text("                         │", fg=fg, bold=True))
    terminal_print(color_text("                         ↓ ausbeutend / kontrollierend", fg=(255,87,87), bold=True))
    terminal_print(art_ratio_bar("R Winkelrichtung", r / 4.0, fg, width=52))
    if flow is not None:
        terminal_print(color_text("Beispielrichtung: ", fg=fg, bold=True) + color_text(flow.direction_vector, fg=(245,245,245)))


def art_difference_funnel(flow: Optional[EffectFlow]) -> None:
    art_panel("DIFFERENZ-TRICHTER", 12, "Handeln beginnt dort, wo Wirklichkeit und Bedarf auseinanderfallen.")
    d = flow.values.get("difference", 3.0) if flow is not None else 3.0
    fg = dim_theme("difference")["fg"]
    terminal_print(color_text("        Bedarf / Not / Möglichkeit", fg=(255,255,255), bold=True))
    terminal_print(color_text("      ╱════════════════════════════╲", fg=fg, bold=True))
    terminal_print(color_text("     ╱   Wohnung  Nahrung  Pflege   ╲", fg=fg, bold=True))
    terminal_print(color_text("    ╱   Wasser  Energie  Ökologie    ╲", fg=fg, bold=True))
    terminal_print(color_text("    ╲              Δ                 ╱", fg=fg, bold=True))
    terminal_print(color_text("     ╲       Differenz wird          ╱", fg=fg, bold=True))
    terminal_print(color_text("      ╲      Wirkungsvertrag        ╱", fg=fg, bold=True))
    terminal_print(color_text("       ╲═══════════▼═══════════════╱", fg=fg, bold=True))
    terminal_print(color_text("             Handlung / Wirkung", fg=(38,222,129), bold=True))
    terminal_print(art_ratio_bar("D Differenz", d / 4.0, fg, width=52))


def art_contract_gate(flow: Optional[EffectFlow]) -> None:
    art_panel("VERTRAGSGATE: GÜLTIGKEIT AUS WAHRHEIT", 13, "Der Stack entscheidet Bedingungen, nicht Kaufkraft.")
    validity = flow.contract_validity if flow is not None else "valid"
    score = flow.truth_stack_priority_0_1 if flow is not None else 0.75
    gates = [
        ("EXISTENZ", "Ist der Zustand real?", "existence"),
        ("KAUSALITÄT", "Trifft es die Ursache?", "causality"),
        ("DIFFERENZ", "Gibt es eine echte Lücke?", "difference"),
        ("RICHTUNG", "Ist es regenerativ/frei?", "angle_direction"),
        ("BESTIMMUNG", "Ist es legitimiert?", "determination"),
    ]
    for name, question, dim in gates:
        fg = dim_theme(dim)["fg"]
        value = flow.values.get(dim, 3.0) if flow is not None else 3.0
        terminal_print(styled_badge(name, fg, dim_theme(dim)["bg"]) + " " + art_ratio_bar(question, value / 4.0, fg, width=38))
    terminal_print(color_text("    ╰──────▶ Ergebnis: ", fg=(255,255,255), bold=True) + styled_badge(validity.upper(), (255,255,255), (40,70,40)) + color_text("  Priorität %.3f" % score, fg=(255,214,10), bold=True))


def art_no_money_map() -> None:
    art_panel("KEIN GELD-KERN: DIE NEUE KARTE", 14, "Preis, Wert, Menge und Besitz werden nicht Hauptkoordinaten.")
    old = ["Preis", "Wert", "Profit", "Lohn", "Miete", "BIP", "Kaufkraft", "Exportwert"]
    new = ["Kausalität", "Wirkung", "Differenz", "Substanz", "Materie", "Bestimmung", "Potenzen", "Richtung"]
    for i in range(len(old)):
        terminal_print(styled_badge(old[i], (255,87,87), (70,10,10)) + color_text("  ═══════▶  ", fg=art_color(i), bold=True) + styled_badge(new[i], art_color(i), tuple(int(c*0.20) for c in art_color(i))))


def art_macro_accounts(macro_accounts: List[MacroAccountRow]) -> None:
    art_panel("PLANETARE KONTEN STATT VOLKSWIRTSCHAFTLICHER WERTKONTEN", 15, "Sektoren werden nach Bedarf, Lücke, Wirkung, Arbeit und Grenzen gelesen.")
    rows = sorted(macro_accounts, key=lambda r: r.priority, reverse=True)[:8]
    for i, row in enumerate(rows):
        fg = domain_color(row.domain)
        terminal_print(domain_badge(row.domain) + " " + color_text(row.sector, fg=(245,245,245), bold=True))
        terminal_print("  " + art_ratio_bar("satisfaction", row.satisfaction, fg, width=36))
        terminal_print("  " + art_ratio_bar("priority", row.priority, art_color(i + 3), width=36))
        terminal_print("  " + art_ratio_bar("boundary penalty", row.boundary_penalty, art_color(i + 5), width=36))


def art_ecology_mandala(last: GlobalMetrics) -> None:
    art_panel("ÖKOLOGISCHE REGENERATION ALS MANDALA", 16, "Natur ist kein Außen; sie ist Wirtschaftsgrundlage.")
    fg = domain_color("ecology")
    terminal_print(color_text("                  ✺ Boden ✺", fg=(190,140,90), bold=True))
    terminal_print(color_text("             ╭──────┼──────╮", fg=fg, bold=True))
    terminal_print(color_text("        Wasser ─── 🌍 ─── Biodiversität", fg=fg, bold=True))
    terminal_print(color_text("             ╰──────┼──────╯", fg=fg, bold=True))
    terminal_print(color_text("                  ✺ Kühlung ✺", fg=(0,229,255), bold=True))
    terminal_print(color_text("        Regeneration senkt Risiken und erhöht Reproduktionsfähigkeit.", fg=(245,245,245)))
    terminal_print(art_ratio_bar("reproduction index", last.planetary_reproduction_index, fg, width=54))


def art_storage_time_bridge(last: GlobalMetrics) -> None:
    art_panel("SPEICHER ALS ZEITBRÜCKE", 17, "Zeit ist eine eigene Handelsdimension.")
    fg = domain_color("storage")
    terminal_print(color_text("    JETZT ────── Nahrung/Wasser/Energie ──────▶ SPÄTER", fg=fg, bold=True))
    terminal_print(color_text("          ╲                                   ╱", fg=fg, bold=True))
    terminal_print(color_text("           ╲_______ Speicher / Reserve ______╱", fg=fg, bold=True))
    terminal_print(art_ratio_bar("basic_buffer_months", clamp(last.basic_buffer_months / 6.0), fg, width=52))
    terminal_print(art_ratio_bar("resilience_index", last.resilience_index, (255,166,0), width=52))


def art_governance_feedback(last: GlobalMetrics) -> None:
    art_panel("BESTIMMUNG + WAHRHEITSKORREKTUR", 18, "Demokratie verhindert, dass Wahrheitswerte Herrschaftswerkzeug werden.")
    fg = domain_color("governance")
    terminal_print(color_text("   Betroffene ──▶ Meldung ──▶ Wahrheitswert ──▶ Vertrag ──▶ Wirkung", fg=fg, bold=True))
    terminal_print(color_text("       ▲                                                           │", fg=fg, bold=True))
    terminal_print(color_text("       └──────────── Audit ◀── Fehlerprüfung ◀── Phänomene ◀──────┘", fg=fg, bold=True))
    terminal_print(art_ratio_bar("coordination_quality", last.coordination_quality, fg, width=52))
    terminal_print(art_ratio_bar("truth_error invertiert", 1.0 - clamp(last.avg_truth_error), (38,222,129), width=52))


def art_truth_dna(flow: Optional[EffectFlow]) -> None:
    art_panel("WAHRHEITS-DNA", 19, "Der Stack kann als farbige Sequenz durch Verträge laufen.")
    values = flow.values if flow is not None else {dim: 3.0 for dim in TRUTH_DIMS}
    left = []
    right = []
    for i, dim in enumerate(TRUTH_DIMS):
        theme = dim_theme(dim)
        digit = truth_digit(values.get(dim, 0.0))
        guide = DIMENSION_GUIDE_DE[dim]
        left.append(color_text("%s%s%d" % (theme["symbol"], guide["short"], digit), fg=theme["fg"], bold=True))
        right.append(color_text("%d%s%s" % (digit, guide["short"], theme["symbol"]), fg=theme["fg"], bold=True))
    for i in range(len(TRUTH_DIMS)):
        twist = "╲╱" if i % 2 == 0 else "╱╲"
        terminal_print("      %s  %s  %s" % (left[i].ljust(20), color_text(twist, fg=art_color(i), bold=True), right[i]))


def art_domain_rainbow() -> None:
    art_panel("DOMÄNEN-REGENBOGEN", 20, "Jede Domäne ist kein Markt, sondern ein Wirkungsfeld.")
    row = ""
    for i, domain in enumerate(DOMAINS):
        row += domain_badge(domain) + " "
        if (i + 1) % 4 == 0:
            terminal_print(row)
            row = ""
    if row:
        terminal_print(row)
    terminal_print(color_text("Alle Domänen teilen dieselben 12 Wahrheitsdimensionen, aber andere Produkte, Arbeitsplätze und Klimaauflagen.", fg=(245,245,245)))


def art_resilience_radar(last: GlobalMetrics) -> None:
    art_panel("RESILIENZ-RADAR", 21, "Schocks werden als Zeit-, Substanz- und Materieprobleme sichtbar.")
    metrics = [
        ("Wasserpuffer", clamp(last.water_stock / max(1.0, last.water_stock + last.population * 0.01)), domain_color("water")),
        ("Nahrungspuffer", clamp(last.food_stock / max(1.0, last.food_stock + last.population * 0.01)), domain_color("food")),
        ("Energiepuffer", clamp(last.energy_stock / max(1.0, last.energy_stock + last.population * 0.01)), domain_color("energy")),
        ("Koordination", last.coordination_quality, domain_color("governance")),
        ("Autonomie", last.avg_autonomy, (255,106,188)),
        ("Reparatur", last.circularity_index, domain_color("repair")),
    ]
    for name, ratio, fg in metrics:
        terminal_print(art_ratio_bar(name, ratio, fg, width=48))


def art_phenomena_wall(truth_vectors: List[TruthVector]) -> None:
    art_panel("PHÄNOMEN-WAND", 22, "Erscheinungen und Betroffenenberichte ersetzen blinde Marktbeobachtung.")
    selected = top_truth_for_art(truth_vectors, 8)
    for tv in selected:
        fg = domain_color(tv.domain)
        ph = tv.values.get("phenomena", 0.0)
        terminal_print(domain_badge(tv.domain) + " " + color_text("%s/%s" % (tv.region, tv.commune), fg=(245,245,245), bold=True))
        terminal_print("  " + art_ratio_bar("Phänomene", ph / 4.0, dim_theme("phenomena")["fg"], width=44))
        terminal_print("  " + color_text(terminal_shorten(tv.explanation, 120), fg=(220,220,220)))


def art_potency_garden(truth_vectors: List[TruthVector]) -> None:
    art_panel("POTENZ-GARTEN", 23, "Potenzen sind Möglichkeiten, Fähigkeiten und Reserven.")
    selected = top_truth_for_art(truth_vectors, 10)
    for i, tv in enumerate(selected):
        p = tv.values.get("potencies", 0.0)
        flowers = int(round(p))
        fg = dim_theme("potencies")["fg"]
        terminal_print(color_text(("✿" * flowers).ljust(6), fg=fg, bold=True) + domain_badge(tv.domain) + " " + color_text("P=%.2f" % p, fg=fg, bold=True) + " " + color_text(tv.commune, fg=(245,245,245)))


def art_labor_lattice(macro_accounts: List[MacroAccountRow]) -> None:
    art_panel("ARBEITSPLATZ-GITTER: BEITRAGSZEIT STATT LOHN", 24, "Arbeitsplätze erscheinen als Fähigkeitsknoten.")
    rows = sorted(macro_accounts, key=lambda r: r.contribution_time, reverse=True)[:10]
    for i, row in enumerate(rows):
        fg = domain_color(row.domain)
        nodes = max(1, min(18, int(round(row.labor_share * 18))))
        terminal_print(domain_badge(row.domain) + " " + color_text("●─" * nodes + "●", fg=fg, bold=True) + " " + color_text("time %.2f" % row.contribution_time, fg=(255,255,255)))


def art_product_wave() -> None:
    art_panel("PRODUKT-WELLEN ALS WIRKUNGSTRÄGER", 25, "Produkte sind sichtbar, aber ihre Bedeutung kommt aus Wirkung und Bedingungen.")
    for i, domain in enumerate(["water", "food", "energy", "shelter", "health", "repair", "ecology", "waste"]):
        fg = domain_color(domain)
        products = TRADE_CATALOG[domain]["products"].split(",")[:5]
        wave = color_text("~≈∿≈~", fg=fg, bold=True)
        terminal_print(domain_badge(domain) + " " + wave + " " + color_text(" | ".join(p.strip() for p in products), fg=(245,245,245)) + " " + wave)


def art_effect_ocean(flows: List[EffectFlow]) -> None:
    art_panel("WIRKUNGS-OZEAN", 26, "Viele kleine Flüsse ergeben planetare Koordination.")
    selected = top_flows_for_art(flows, 12)
    for i, flow in enumerate(selected):
        fg = domain_color(flow.domain)
        height = max(1, min(10, int(round(flow.truth_stack_priority_0_1 * 10))))
        terminal_print(color_text("≋" * (height + 4), fg=fg, bold=True) + " " + domain_badge(flow.domain) + " " + color_text(flow.kind, fg=(245,245,245)) + " " + color_text("%.2f" % flow.activated_effect, fg=(255,240,170), bold=True))


def art_heatmap_dimensions(flows: List[EffectFlow]) -> None:
    art_panel("DIMENSIONS-HEATMAP DER SICHTBAREN VERTRÄGE", 27, "Jede Spalte ist ein Vertrag; jede Zeile eine Dimension.")
    selected = top_flows_for_art(flows, 8)
    if not selected:
        terminal_print(color_text("Keine Flows vorhanden.", fg=(255,87,87), bold=True))
        return
    terminal_print(color_text("          ", fg=(255,255,255)) + " ".join(color_text("%02d" % (i + 1), fg=domain_color(f.domain), bold=True) for i, f in enumerate(selected)))
    shade = "░▒▓█"
    for dim in TRUTH_DIMS:
        theme = dim_theme(dim)
        guide = DIMENSION_GUIDE_DE[dim]
        row = styled_badge("%s%s" % (theme["symbol"], guide["short"]), theme["fg"], theme["bg"]) + " "
        for flow in selected:
            v = flow.values.get(dim, 0.0)
            idx = max(0, min(len(shade) - 1, int(round((v / 4.0) * (len(shade) - 1)))))
            row += color_text("%s%s" % (shade[idx], shade[idx]), fg=theme["fg"], bold=True) + " "
        terminal_print(row + color_text(guide["name_de"], fg=theme["fg"], bold=True))


def art_time_river(timeline: List[GlobalMetrics]) -> None:
    art_panel("ZEITFLUSS DER PLANETENWIRTSCHAFT", 28, "Zeit ist nicht nur Termin, sondern Dringlichkeit und Entwicklung.")
    wellbeing = [m.wellbeing for m in timeline]
    unmet = [m.unmet_basic for m in timeline]
    overs = [m.overshoot for m in timeline]
    terminal_print(color_text("wellbeing     ", fg=(38,222,129), bold=True) + art_spark(wellbeing, (38,222,129), width=72))
    terminal_print(color_text("unmet_basic   ", fg=(255,87,87), bold=True) + art_spark(unmet, (255,87,87), width=72))
    terminal_print(color_text("overshoot     ", fg=(255,166,0), bold=True) + art_spark(overs, (255,166,0), width=72))


def art_cyberpunk_manifest() -> None:
    art_panel("NEON-MANIFEST", 29, "Extrem bunt, aber mit ernstem Kern.")
    lines = [
        "WARE  →  PHÄNOMEN",
        "PREIS →  WAHRHEITSSTAPEL",
        "WERT  →  WIRKUNG",
        "MENGE →  INTENSITÄT + SUBSTANZ",
        "BESITZ → NUTZUNG + BESTIMMUNG",
        "PROFIT → BEDÜRFNIS- UND DIFFERENZAUFLÖSUNG",
        "MARKT → RÜCKKOPPLUNG + AUDIT + KOMMUNE",
    ]
    for i, line in enumerate(lines):
        terminal_print(rainbow_text("        ░▒▓█  " + line + "  █▓▒░"))


def art_final_sigil() -> None:
    art_panel("ABSCHLUSS-SIGILL", 30, "Planetenwirtschaft als farbige Wirkungsmaschine.")
    colors = art_palette()
    sigil = [
        "                 ╭───────────────╮                 ",
        "             ╭───┤  PLANET  🌍   ├───╮             ",
        "          ╭──┤   ╰──────┬────────╯   ├──╮          ",
        "       ╭──┤  Wahrheit   │   Wirkung   ├──╮       ",
        "       │  ╰──────┬──────┼──────┬──────╯  │       ",
        "       │         ▼      ▼      ▼         │       ",
        "       │      Bedarf  Substanz  Richtung │       ",
        "       │         ▲      ▲      ▲         │       ",
        "       ╰─────────┴──────┴──────┴─────────╯       ",
        "              KOMMUNEN  •  GRUPPEN  •  PERSONEN  ",
    ]
    for i, line in enumerate(sigil):
        terminal_print(color_text(line, fg=colors[i % len(colors)], bold=True))




def art_text_lines(number: int, lines: List[str]) -> None:
    for idx, line in enumerate(lines):
        terminal_print(art_box_line(line, art_color(number + idx), width=terminal_content_width()))
    terminal_print("")


def art_metric_rows(number: int, labels: List[str], values: List[float]) -> None:
    for idx, (label, value) in enumerate(zip(labels, values)):
        terminal_print(art_ratio_bar(label, clamp(value, 0.0, 1.0), art_color(number + idx), width=max(18, terminal_content_width() - 24)))
    terminal_print("")


def art_macro_circular_flow(last: GlobalMetrics) -> None:
    art_panel('VOLKSWIRTSCHAFT: KREISLAUF DER PLANETENWIRTSCHAFT', 31, 'Makrobild: Reproduktion, Versorgung, Regeneration, Rückkopplung.')
    art_text_lines(31, [
        'Bedarf → Beitrag → Wirkung → Versorgung → Rückmeldung → neuer Bedarf',
        "      ╭───────────────╮      ╭───────────────╮",
        "      │    need      │ ───▶ │ contribution  │",
        "      ╰───────────────╯      ╰───────────────╯",
        "               ▲                       │        ",
        "               │                       ▼        ",
        "      ╭───────────────╮ ◀─── ╭───────────────╮",
        "      │   feedback    │      │    effect     │",
        "      ╰───────────────╯ ───▶ ╰───────────────╯",
        "                    provision / regeneration   ",
        'Planetare Grenzen umhüllen den gesamten Kreislauf.',
        'Kommunen, Länder und Gruppen erscheinen als Schichten des Wirkungsflusses.',
    ])

def art_macro_provision_balance(last: GlobalMetrics) -> None:
    art_panel('VOLKSWIRTSCHAFT: VERSORGUNGSBILANZ', 32, 'Kein Preisbild, sondern Zustand von Bedarf, Lücke, Regeneration und Überschreitung.')
    art_metric_rows(32, ['Wohlergehen', 'Unerfüllte Grundbedarfe', 'Overshoot', 'Planetare Reproduktion'], [last.wellbeing, 1.0 - last.unmet_basic, 1.0 - clamp(last.overshoot, 0.0, 1.0), last.planetary_reproduction_index])

def art_macro_sector_web() -> None:
    art_panel('VOLKSWIRTSCHAFT: SEKTOR-NETZ', 33, 'Makroökonomie als Wirkungsgewebe statt als Geldkonto.')
    art_text_lines(33, [
        'Wasser ↔ Nahrung ↔ Energie ↔ Wohnen ↔ Gesundheit ↔ Bildung',
        "             water ── food ── energy            ",
        "               ╲        │        ╱              ",
        "                ╲       │       ╱               ",
        "             ecology ─ shelter ─ health         ",
        "                ╱       │       ╲               ",
        "               ╱        │        ╲              ",
        "          repair ── resilience ── education     ",
        'Reparatur und Resilienz stabilisieren alle Domänen.',
        'Ökologie ist nicht Außen, sondern Produktions- und Lebensgrundlage.',
    ])

def art_macro_domain_matrix() -> None:
    art_panel('VOLKSWIRTSCHAFT: DOMÄNEN-MATRIX', 34, 'Jede Domäne trägt Produkt-, Arbeitsplatz-, Service- und Klimabedeutung.')
    art_text_lines(34, [
        "┌──────────────┬─────────┬─────────┬─────────┬─────────┐",
        "│ domain       │ provide │ work    │ service │ ecology │",
        "├──────────────┼─────────┼─────────┼─────────┼─────────┤",
        "│ water        │ ●●●●    │ ●●      │ ●●●     │ ●●●●    │",
        "│ food         │ ●●●●    │ ●●●     │ ●●      │ ●●●     │",
        "│ energy       │ ●●●     │ ●●●     │ ●●      │ ●●      │",
        "│ health       │ ●●●     │ ●●●     │ ●●●●    │ ●●      │",
        "│ repair       │ ●●      │ ●●●●    │ ●●●     │ ●●●     │",
        "└──────────────┴─────────┴─────────┴─────────┴─────────┘",
        'Zeilen = Domänen, Spalten = Versorgung, Arbeit, Dienstleistung, Ökologie',
        'Makrokoordination heißt: reale Lücken über viele Felder hinweg schließen.',
        'Die Matrix ist farbig, weil jede Domäne eine andere Wirkungsfarbe trägt.',
    ])

def art_macro_external_trade() -> None:
    art_panel('VOLKSWIRTSCHAFT: PLANETARER AUSSENHANDEL OHNE GELDKERN', 35, 'Transfer bedeutet Wirkungsverschiebung zwischen Regionen, nicht Preisarbitrage.')
    art_text_lines(35, [
        'Region A ⇄ Region B ⇄ Region C',
        "   ┌──────────┐     effect transfer      ┌──────────┐",
        "   │ region A │ ═══════════════════════▶ │ region B │",
        "   └──────────┘ ◀═══════════════════════ └──────────┘",
        "          ╲                                      ▲   ",
        "           ╲                                     │   ",
        "            ╲══════▶ region C ◀══════════════════╝   ",
        'Exportwert wird ersetzt durch: gelöste Differenz, Zeitgewinn, ökologische Wirkung.',
        'Jeder Transfer trägt Vertragsbedingungen und Wahrheitswerte.',
    ])

def art_macro_control_cockpit(last: GlobalMetrics) -> None:
    art_panel('VOLKSWIRTSCHAFT: STEUERUNGS-COCKPIT', 36, 'Makropolitik liest Wahrheitsfehler, Autonomie, Koordination und Resilienz.')
    art_metric_rows(36, ['Autonomie', 'Koordination', 'Resilienz', 'Wahrheitsfehler'], [last.avg_autonomy, last.coordination_quality, last.resilience_index, 1.0 - last.avg_truth_error])

def art_macro_regeneration_budget() -> None:
    art_panel('VOLKSWIRTSCHAFT: REGENERATIONS-BUDGET', 37, 'Volkswirtschaftliche Stärke ist Wiederherstellung der Lebensgrundlage.')
    art_text_lines(37, [
        'Boden + Wasser + Klima + Biodiversität + Reparatur + Pflege',
        "      soil ═══ water ═══ climate ═══ biodiversity   ",
        "         ╲        ╲         │         ╱             ",
        "          ╲        ╲        │        ╱              ",
        "             repair ═══ care ═══ resilience         ",
        'Jede Investition wird als Regenerations- oder Schädigungsrichtung gelesen.',
        'Die stärkste Wirtschaft heilt ihre Voraussetzungen.',
    ])

def art_macro_crisis_buffer(last: GlobalMetrics) -> None:
    art_panel('VOLKSWIRTSCHAFT: KRISENPUFFER', 38, 'Zeit, Speicher, Wissen und Vertrauen sind makroökonomische Reserven.')
    art_metric_rows(38, ['Speicherlogik', 'Wissenspuffer', 'Vertrauensreserven', 'Krisendruck'], [last.resilience_index, 1.0 - last.avg_truth_error, last.avg_autonomy, clamp(last.overshoot, 0.0, 1.0)])

def art_business_operating_cycle() -> None:
    art_panel('BETRIEBSWIRTSCHAFT: BETRIEBLICHER WIRKUNGSZYKLUS', 39, 'Beschaffung, Produktion, Dienstleistung, Wartung, Reparatur, Rückführung.')
    art_text_lines(39, [
        'Bedarf → Planung → Beschaffung → Herstellen → Prüfen → Liefern → Feedback → Reparatur',
        "need → plan → source → make → test → deliver → service → repair",
        "  ▲                                                     │       ",
        "  └────────────── feedback and learning ────────────────┘       ",
        'Das Unternehmen ist ein Wirkungsorgan, nicht nur ein Geldautomat.',
        'Betriebswirtschaft wird zur sichtbaren Prozessarchitektur.',
    ])

def art_business_capability_house() -> None:
    art_panel('BETRIEBSWIRTSCHAFT: FÄHIGKEITS-HAUS', 40, 'Menschen, Werkzeuge, Wissen, Zeit und Infrastruktur bilden das Haus des Betriebs.')
    art_text_lines(40, [
        "                 /\\                                   ",
        "                /  \\                                  ",
        "               /____\\                                 ",
        "              |      |                                 ",
        "              | data | service | making | care |       ",
        "              |______|_________|_______|______|        ",
        "              | truth | substance | matter | safety |  ",
        'Dach: Zweck und Richtung',
        'Räume: Beschaffung, Fertigung, Pflege, Service, Daten, Lernen',
        'Fundament: Wahrheit, Bestimmung, Substanz, Materie, Sicherheit',
    ])

def art_business_process_chain() -> None:
    art_panel('BETRIEBSWIRTSCHAFT: PROZESSKETTE', 41, 'Vom Auftrag zur Wirkung: jeder Schritt hat Bedingungen.')
    art_text_lines(41, [
        'Auftrag → Bedarfsklärung → Kausalprüfung → Arbeitsplanung → Ausführung → Audit → Auslieferung',
        "[order]→[clarify]→[cause]→[plan]→[execute]→[audit]→[deliver]",
        "     ╰───────────── quality and feedback return ─────────────╯  ",
        'Qualität entsteht durch Rückkopplung, nicht erst am Ende.',
        'Die Kette ist bunt, weil viele Fachrollen zusammenwirken.',
    ])

def art_business_quality_loop() -> None:
    art_panel('BETRIEBSWIRTSCHAFT: QUALITÄTS-SCHLEIFE', 42, 'Beobachten, Messen, Korrigieren, erneut prüfen, freigeben.')
    art_text_lines(42, [
        'Phänomen → Messung → Vergleich → Korrektur → Dokumentation → neue Wahrheit',
        "observe → measure → compare → correct → document → release",
        "   ▲                                                    │      ",
        "   └──────────────── new truth and new check ───────────┘      ",
        'Qualität ist kein Nebenfach, sondern Vertragswahrheit in Bewegung.',
        'Schleifen verhindern, dass Fehler zu Schädigungen werden.',
    ])

def art_business_inventory_buffers(last: GlobalMetrics) -> None:
    art_panel('BETRIEBSWIRTSCHAFT: LAGER- UND PUFFERLOGIK', 43, 'Lager ist Zeitbrücke und Versorgungsschutz.')
    art_metric_rows(43, ['Materialpuffer', 'Energiepuffer', 'Zeitpuffer', 'Reparaturreserve'], [last.resilience_index, max(0.0, min(1.0, 0.55 + 0.35 * last.planetary_reproduction_index)), max(0.0, min(1.0, 0.45 + 0.45 * last.coordination_quality)), max(0.0, min(1.0, 0.40 + 0.45 * last.resilience_index))])

def art_business_project_portfolio() -> None:
    art_panel('BETRIEBSWIRTSCHAFT: PROJEKT-PORTFOLIO', 44, 'Wichtige und dringende Projekte konkurrieren unter Wahrheitsbedingungen.')
    art_text_lines(44, [
        "                    importance                           ",
        "                     high                               ",
        "            ┌───────────────────────┬──────────────────┐",
        "            │ regenerative core     │ urgent repair    │",
        " urgency    │ and care              │ and protection   │",
        "  high      ├───────────────────────┼──────────────────┤",
        "            │ transformative build  │ later reserve    │",
        "            │ and learning          │ and observation  │",
        "            └───────────────────────┴──────────────────┘",
        'Quadranten: dringend/wichtig, dringend/später, regenerativ/transformativ',
        'Projektwahl folgt nicht nur Rendite, sondern Wirksamkeit und Grenzschutz.',
        'Portfolio-Steuerung wird damit gesellschaftlich lesbar.',
    ])

def art_business_risk_canvas() -> None:
    art_panel('BETRIEBSWIRTSCHAFT: RISIKO-LEINWAND', 45, 'Klimarisiko, Lieferkette, Wahrheit, Akzeptanz, Technik, Gesundheit.')
    art_text_lines(45, [
        "┌──────────────┬──────────────┬──────────────┐",
        f"│ niedrig      │ mittel       │ hoch         │",
        "├──────────────┼──────────────┼──────────────┤",
        f"│ Klima        │ niedrig      │ mittel       │",
        f"│ Logistik     │ mittel       │ hoch         │",
        f"│ Wahrheit     │ niedrig      │ mittel       │",
        f"│ Akzeptanz    │ mittel       │ mittel       │",
        f"│ Technik      │ niedrig      │ mittel       │",
        f"│ Gesundheit   │ niedrig      │ mittel       │",
        "└──────────────┴──────────────┴──────────────┘",
        'Risikoquellen werden sichtbar gemacht, bevor sie Schaden erzeugen.',
        'Betriebswirtschaftliche Vorsicht heißt: Bedingungen früh sehen.',
        'Farben markieren niedrige, mittlere und hohe Gefährdung.',
    ])

def art_business_service_blueprint() -> None:
    art_panel('BETRIEBSWIRTSCHAFT: SERVICE-BLAUPAUSE', 46, 'Kontaktpunkt, Meldung, Bearbeitung, Wirkung, Nachsorge.')
    art_text_lines(46, [
        'Person meldet Bedarf → Team nimmt auf → System prüft → Wirkung wird aktiviert → Nachsorge',
        "person → intake → verification → activation → care → learning",
        "   │         │          │             │          │         │   ",
        " report   contact    system        effect     service   review  ",
        'Dienstleistung erscheint als organisierte Sorge und Problemlösung.',
        'Unten endet die Kette wieder in Lernen und Verbesserung.',
    ])
def print_utf8_art_gallery_terminal(flows: List[EffectFlow], truth_vectors: List[TruthVector], timeline: List[GlobalMetrics], macro_accounts: List[MacroAccountRow], limit: int = 46) -> None:
    if limit <= 0:
        return
    terminal_header('EXTREM BUNTE UTF-8-ART-GALERIE', 'Darstellungen unter den Verträgen: Diagramme, Abbildungen, Kreisläufe, Kompasse, Heatmaps, Volkswirtschaft und Betriebswirtschaft.')
    last = timeline[-1]
    top_flow = top_flows_for_art(flows, 1)[0] if flows else None
    panels = [
        lambda: art_planet_layer_stack(last),
        lambda: art_truth_stack_totem(top_flow),
        lambda: art_causal_pipeline(top_flow),
        art_buy_sell_replacement,
        lambda: art_boundary_dashboard(last),
        lambda: art_climate_contract_shield(last),
        lambda: art_material_cycle(last),
        lambda: art_commune_network(flows),
        art_products_jobs_services_map,
        art_service_constellation,
        lambda: art_angle_compass(top_flow),
        lambda: art_difference_funnel(top_flow),
        lambda: art_contract_gate(top_flow),
        art_no_money_map,
        lambda: art_macro_accounts(macro_accounts),
        lambda: art_ecology_mandala(last),
        lambda: art_storage_time_bridge(last),
        lambda: art_governance_feedback(last),
        lambda: art_truth_dna(top_flow),
        art_domain_rainbow,
        lambda: art_resilience_radar(last),
        lambda: art_phenomena_wall(truth_vectors),
        lambda: art_potency_garden(truth_vectors),
        lambda: art_labor_lattice(macro_accounts),
        art_product_wave,
        lambda: art_effect_ocean(flows),
        lambda: art_heatmap_dimensions(flows),
        lambda: art_time_river(timeline),
        art_cyberpunk_manifest,
        art_final_sigil,
        lambda: art_macro_circular_flow(last),
        lambda: art_macro_provision_balance(last),
        art_macro_sector_web,
        art_macro_domain_matrix,
        art_macro_external_trade,
        lambda: art_macro_control_cockpit(last),
        art_macro_regeneration_budget,
        lambda: art_macro_crisis_buffer(last),
        art_business_operating_cycle,
        art_business_capability_house,
        art_business_process_chain,
        art_business_quality_loop,
        lambda: art_business_inventory_buffers(last),
        art_business_project_portfolio,
        art_business_risk_canvas,
        art_business_service_blueprint,
    ]
    for panel in panels[:max(0, min(limit, len(panels)))]:
        panel()
    terminal_print("")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PyPy3-compatible planetary effect economy simulation: truth-values to action, no money/prices/GDP.",
    )
    parser.add_argument("--steps", type=int, default=120, help="simulation months, default 120")
    parser.add_argument("--seed", type=int, default=42, help="random seed, default 42")
    parser.add_argument("--population", type=float, default=8_100_000_000.0, help="synthetic total population, default 8.1e9")
    parser.add_argument("--regions", type=int, default=12, help="number of bioregions, default 12")
    parser.add_argument("--communes-per-region", type=int, default=8, help="communes per region, default 8")
    parser.add_argument("--scenario", choices=("planetary_commons", "local_democracy", "technocratic_control", "ecological_crisis", "scarcity_shock"), default="planetary_commons")
    parser.add_argument("--out", default="out_planetenwirtschaft", help="output directory")
    parser.add_argument("--quiet", action="store_true", help="do not print final summary")
    parser.add_argument("--show-trades", type=int, default=16, help="print N visible trade/effect contracts to terminal; 0 disables, default 16")
    parser.add_argument("--show-trade-detail", action="store_true", help="print products, workplaces, services, ecology/climate clauses and contract bullets for each visible trade")
    parser.add_argument("--show-dimensions", action="store_true", help="print the full dimension guide to terminal")
    parser.add_argument("--show-catalog", action="store_true", help="print what is traded in every domain: products, jobs, services, ecology, climate")
    parser.add_argument("--show-stack-explanation", action="store_true", help="print how the stacked truth value is read")
    parser.add_argument("--show-art", type=int, default=46, help="zeige N extrem bunte UTF-8/ANSI-Art-Diagramme unter den Vertragsanzeigen; 0 deaktiviert, Standard 46")
    parser.add_argument("--force-color", action="store_true", help="force ANSI colors even if stdout is not a TTY")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors and stylistic terminal formatting")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    set_terminal_color_enabled((not args.no_color) and (args.force_color or ((os.environ.get("NO_COLOR") is None) and sys.stdout.isatty())))
    if args.steps < 0:
        raise SystemExit("--steps must be >= 0")
    if args.population <= 0:
        raise SystemExit("--population must be > 0")
    if args.regions <= 0 or args.communes_per_region <= 0:
        raise SystemExit("--regions and --communes-per-region must be > 0")

    regions, boundary, planner, timeline, last_truth, macro_accounts, last_flows = run_simulation(
        seed=args.seed,
        steps=args.steps,
        population=args.population,
        regions_count=args.regions,
        communes_per_region=args.communes_per_region,
        scenario=args.scenario,
    )
    ensure_dir(args.out)
    write_timeline(os.path.join(args.out, "timeline.csv"), timeline)
    write_communes(os.path.join(args.out, "communes_final.csv"), regions)
    write_truth_audit(os.path.join(args.out, "truth_audit.csv"), last_truth, args.steps)
    write_macro_accounts(os.path.join(args.out, "macro_accounts.csv"), macro_accounts)
    write_effect_flows(os.path.join(args.out, "effect_flow_audit.csv"), last_flows)
    write_dimension_guide(os.path.join(args.out, "dimension_guide.csv"))
    write_trade_dimension_catalog(os.path.join(args.out, "trade_dimension_catalog.csv"))
    write_trade_contracts_report(os.path.join(args.out, "trade_contracts_report.md"), last_flows, last_truth, timeline)
    write_summary(os.path.join(args.out, "summary.json"), regions, boundary, planner, timeline, args.scenario, args.seed)
    write_manifest(os.path.join(args.out, "manifest.md"), timeline, boundary, args.scenario)

    if not args.quiet:
        first = timeline[0]
        last = timeline[-1]
        terminal_header("PLANETARY EFFECT ECONOMY SIMULATION", "Bunte Terminalausgabe für planetare Wirkungswirtschaft, Verträge und Wahrheitsdimensionen")
        pretty_key_value("scenario", args.scenario, label_fg=(255, 106, 188))
        pretty_key_value("steps", str(args.steps), label_fg=(255, 214, 10))
        pretty_key_value("regions", "%s | communes: %s" % (args.regions, args.regions * args.communes_per_region), label_fg=(0, 229, 255))
        pretty_key_value("population", "%s -> %s" % (format_big(first.population), format_big(last.population)), label_fg=(38, 222, 129))
        pretty_key_value("wellbeing", "%.4f -> %.4f (Δ %.4f)" % (first.wellbeing, last.wellbeing, last.wellbeing - first.wellbeing), label_fg=(161, 108, 255))
        pretty_key_value("unmet basic needs", "%.4f -> %.4f (Δ %.4f)" % (first.unmet_basic, last.unmet_basic, last.unmet_basic - first.unmet_basic), label_fg=(255, 87, 87))
        pretty_key_value("planetary overshoot", "%.4f -> %.4f (Δ %.4f)" % (first.overshoot, last.overshoot, last.overshoot - first.overshoot), label_fg=(255, 166, 0))
        pretty_key_value("truth error", "%.4f -> %.4f (Δ %.4f)" % (first.avg_truth_error, last.avg_truth_error, last.avg_truth_error - first.avg_truth_error), label_fg=(255, 46, 138))
        pretty_key_value("autonomy", "%.4f -> %.4f (Δ %.4f)" % (first.avg_autonomy, last.avg_autonomy, last.avg_autonomy - first.avg_autonomy), label_fg=(58, 134, 255))
        pretty_key_value("reproduction index", "%.4f -> %.4f (Δ %.4f)" % (first.planetary_reproduction_index, last.planetary_reproduction_index, last.planetary_reproduction_index - first.planetary_reproduction_index), label_fg=(0, 245, 212))
        pretty_key_value("resilience index", "%.4f -> %.4f (Δ %.4f)" % (first.resilience_index, last.resilience_index, last.resilience_index - first.resilience_index), label_fg=(190, 140, 90))
        pretty_key_value("coordination quality", "%.4f -> %.4f (Δ %.4f)" % (first.coordination_quality, last.coordination_quality, last.coordination_quality - first.coordination_quality), label_fg=(255, 106, 188))
        pretty_key_value("satisfaction inequality", "%.4f -> %.4f (Δ %.4f)" % (first.satisfaction_inequality, last.satisfaction_inequality, last.satisfaction_inequality - first.satisfaction_inequality), label_fg=(120, 185, 255))
        pretty_key_value("worst boundary", "%s = %.3f" % (last.worst_boundary, last.worst_boundary_pressure), label_fg=(255, 87, 87))
        pretty_key_value("outputs", os.path.abspath(args.out), label_fg=(200, 200, 200))
        print("")
        if args.show_dimensions:
            print_dimension_guide_terminal()
        if args.show_catalog:
            print_trade_catalog_terminal()
        if args.show_stack_explanation:
            print_truth_stack_explanation_terminal()
        if args.show_trades > 0:
            print_visible_trade_contracts(last_flows, limit=args.show_trades, detail=args.show_trade_detail)
        if args.show_art > 0:
            print_utf8_art_gallery_terminal(last_flows, last_truth, timeline, macro_accounts, limit=args.show_art)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
