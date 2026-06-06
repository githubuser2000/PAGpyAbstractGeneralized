# Abdeckung der geforderten Wirtschaftssimulation

Die Simulation bildet die geforderten Bausteine nicht als perfektes Realweltmodell ab, sondern als lauffähiges agentenbasiertes Gerüst. Die wichtigsten Teile sind im Code enthalten:

| Bereich | Umsetzung im Code |
|---|---|
| Mehrere Länder | `Country` mit eigener Währung, Wechselkurs, Medienfreiheit, Rechtssystem, Ressourcen, Pollution, Zoll, Border Openness |
| Mehrere Regierungen | `Government` mit Kompetenz, Korruption, Ideologie, Informationsqualität, Gerichtsunabhängigkeit, Propaganda, Steuern, Sanktionen |
| Gut/Böse-Orakel | `government_moral_score()` und `government_oracles_and_policy()` |
| Mehrere Völker | `PeopleGroup` je Land; Gruppen mit Ideologie, Aktivismus, Medienanfälligkeit, Einkommen, Moralstrenge |
| Beliebt/Unbeliebt-Orakel | `people_popularity_score()` aus Preis, Qualität, Jobs, Werbung, Skandalen, Sektorpräferenzen, Medien |
| Vektorwährung | `VectorMoney(amount, theta, confidence, origin, history)` |
| Winkelhandel | `angle_market()` mit Rotation, Kosten, Spread, Konfidenzverlust und Winkelwäscheindex |
| Kaufwinkel / Verkaufswinkel | `buy_angle` und `sell_angle` in `ActorBase` für Haushalte, Firmen, Banken, Regierungen, Zentralbanken |
| Betrag als Winkelgewicht | Winkelverschmelzung in `VectorMoney.merge_with()` ist nach `amount * confidence` gewichtet |
| Produkte | Sektoren in `GOOD_SPECS`, Produktmarkt in `product_and_service_markets()` |
| Dienstleistungen | Sektoren mit `service=True`, laufen durch denselben Marktmechanismus |
| Arbeitsmarkt | `labor_market()` und `pay_wages()` |
| Firmen / Konzerne | `Firm` mit Markt-/Daten-/Medienmacht, Eigentümerland, Lobbying, Werbung, Patenten, Fraud, Compliance, Supply Chain |
| Banken | `Bank`, Kreditbücher, Kapital, Reserven, Bankausfälle |
| Zentralbanken | `CentralBank`, Zinsregel, Lender-of-last-resort, Geldemission |
| Kreditmarkt | `credit_market()` mit Ausfallrisiko, Winkelrisiko und Zinsaufschlag |
| Kredite | `Loan` mit Betrag, Rate, Laufzeit, Winkel, Konfidenz |
| Steuern | Konsum-, Einkommen- und Profitsteuern |
| Subventionen | `taxes_subsidies_and_public_spending()` |
| Öffentliche Beschaffung | Regierung kauft Güter/Dienstleistungen bei Firmen |
| Internationale Wirtschaft | Cross-country transactions, Wechselkurse, Zölle, Trade Balance, Winkelübersetzung |
| Winkelübersetzung | `translate_angle()` und `Country.angle_translation` |
| Medien | `update_media_and_sentiment()`, Medienfirmen, Werbung, Propaganda, Sentiment |
| Skandale / Leaks | `generate_shocks()` erzeugt Firmenskandale und Korruptionsleaks |
| Gerichte / Audits | `legal_system_and_audits()` mit Fines und Rehabilitation |
| Lieferketten | `production_and_supply_chains()` mit Inputsektoren und Supply-Chain-Winkel |
| Umwelt | Pollution, Ressourcenverbrauch, Umweltfeedback |
| Schocks und Krisen | Energiekrise, Naturkatastrophe, Cyberattacke, Kriegsschreck, Boykottwelle, Bank-Run-Angst |
| Schwarzmarkt | `transaction()` kann Steuern umgehen, Konfidenz senken und Winkel verschlechtern |
| Betrug | `fraud_level`, Skandalwahrscheinlichkeit, Auditrisiko, Legal Fines |
| Macht | Market Power, Lobbying, Media Power, Data Power, Regierungsmacht |
| Zeit und Gedächtnis | Alle Schritte sind Monatsperioden; Sentiment, Moral Memory, Reputation und Preise sind geglättet |
| Kennzahlen | GDP, Inflation, Arbeitslosigkeit, Gini, Winkelverteilung, Winkelspread, Konfidenz, Legitimitätsgap, Laundering Index, Defaults, Protests |

## Bewusste Vereinfachungen

- Konzerne sind als Firmen mit Markt-, Medien-, Datenmacht und Eigentümerland modelliert, aber noch nicht als explizite Holdinggraphen.
- Es gibt nationale Wechselkurse und Winkelübersetzung, aber kein vollständiges FX-Orderbuch.
- Lieferketten sind sektoral, nicht einzelne Produkt-BOMs.
- Haushalte sind Agenten, keine demografischen Familienmodelle.
- Banken haben Kredit- und Kapitalmechanik, aber keine vollständige doppelte Buchführung mit Depositenmatrix.
- Die Parametrisierung ist synthetisch und nicht kalibriert.

## Warum trotzdem nützlich?

Das Modell ist als erste große lauffähige Basis gedacht. Die kritischen Mechanismen sind vorhanden: Betrag, Winkel, Konfidenz, Herkunft, Orakelunsicherheit, Machtmissbrauch, Winkelwäsche, Märkte, Kredit, Arbeit, Staat, Medien, Recht, Umwelt und internationale Konflikte. Dadurch entstehen bereits nichttriviale Dynamiken, die man mit Seeds, Parametern und Metriken experimentell untersuchen kann.
