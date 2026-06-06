# Coverage der V2-Simulation

Die V2 ergänzt möglichst viele der zuvor genannten fehlenden Bausteine. Sie ist kein perfektes Weltmodell, aber ein großes lauffähiges Gerüst.

| Bereich | V2-Umsetzung |
|---|---|
| Vektorwährung | `VectorMoney(amount, theta, confidence, origin, history)` |
| Betrag als Winkelgewicht | `VectorMoney.merge_with()` gewichtet Winkel nach `amount * confidence` |
| Kauf-/Verkaufswinkel | `buy_angle` und `sell_angle` in `ActorBase` |
| Gut/Böse-Orakel | `government_moral_score()`, `government_oracles_and_policy()` |
| Beliebt/Unbeliebt-Orakel | `people_popularity_score()` aus Völkergruppen, Preis, Qualität, Werbung, Jobs, Skandalen |
| Mehrere Länder | `Country` mit Währung, Wechselkurs, Tarifen, Medienfreiheit, Recht, Infrastruktur, Umwelt, Ressourcen |
| Winkelübersetzung | `translate_angle()` und `Country.angle_translation` |
| Regierungen | `Government` mit Kompetenz, Korruption, Ideologie, Macht, Propaganda, Steuern, Sanktionen |
| Völkergruppen | `PeopleGroup` mit Einkommen, Ideologie, Aktivismus, Moralstrenge, Medienanfälligkeit |
| Haushalte | Einkommen, Arbeit, Konsum, Sparen, Gesundheit, Alter, Human Capital, Migration, Hypothek, Pension, Versicherung |
| Firmen | Sektor, Preis, Inventar, Technologie, Produktivität, Löhne, Betrug, Lobbying, Werbung, Lieferkettenwinkel |
| Konzerne/Holdings | `CorporateGroup` mit Parent, Tochterfirmen, Tax Haven, Opazität, konsolidiertem Winkel |
| Transfer Pricing | `corporate_transfer_pricing()` mit Steuervermeidung und Laundering-Effekt |
| Dividenden | `corporate_governance_and_dividends()` |
| Aktienmarkt | `EquityListing`, Share Price, Equity Issuance, Mark-to-Market, institutionelle Holdings |
| Bondmarkt | `Bond`, Sovereign Bonds, Corporate Bonds, Coupons, Defaults, Issuance |
| Banken | Kapital, Reserven, Kredite, Hypotheken, Bond-/Equitybestände, Schattenexposure |
| Zentralbanken | Zinsen, Geldemission, FX-Reserven, Reservewährungsstatus, Lender of Last Resort |
| Fonds/Pensionen | `InvestmentFund` mit AUM, Mandatswinkel, Aktien- und Bondbeständen |
| Ratingagenturen | `RatingAgency` als alternative Orakel mit Accuracy, Bias, Corruption, Influence |
| FX/Kapitalflüsse | `fx_orderbook_and_capital_flows()` mit Orderbook-Approximation, Kapitalflüssen, Reserveinterventionen |
| Trade Agreements | `TradeAgreement`, Tarifsenkung und langsame Winkelangleichung |
| Immobilien | `PropertyAsset`, Mietmarkt, Eigenheim, Landpreisindex |
| Hypotheken | Haushaltshypotheken, Bank-Hypothekenbuch, Tilgung |
| Versicherung | `InsurancePolicy`, Prämien, Claims bei Gesundheit, Cyber, Property, Political Risk, Liability |
| Infrastruktur | `InfrastructureAsset`, Wartung, Infrastrukturqualität, Produktivitätswirkung |
| Produktmärkte | `product_and_service_markets()` |
| Dienstleistungsmärkte | über `GoodSpec.service=True` |
| Arbeitsmarkt | `labor_market()` und `pay_wages()` |
| Kreditmarkt | `credit_market()` und `loan_servicing()` |
| Winkelmarkt | `angle_market()` mit Rotation, Kosten, Konfidenzverlust, Laundering Index |
| Steuern/Subventionen | Konsum-, Einkommen-, Profitsteuer, Sozialleistungen, Subventionen, Procurement |
| Lieferketten | `production_and_supply_chains()` mit sektoralen Inputsektoren und Lieferkettenwinkel |
| Medien/Propaganda/Werbung | `update_media_and_sentiment()` plus Medienfirmen, Media Power, Propaganda Budget |
| Recht/Gerichte | `legal_system_and_audits()`, `contracts_and_disputes()` |
| Verfassungsschutz | `political_parties_constitution_and_civil_society()` mit Court Overrides |
| Parteien | `PoliticalParty`, Unterstützung, Spender, ideologischer Zug auf Regierung |
| Minderheitenschutz | `minority_harm_index`, Civil Rights, Minority Protection |
| Zivilgesellschaft | Investigations gegen Betrug bei hoher Medienfreiheit/Civil Rights |
| Umwelt | Pollution, Carbon, Biodiversity, Health Burden, Ressourcenverbrauch |
| Datenschutz | `data_privacy_damage`, Privacy Enforcement |
| Kriminalität | `crime_index`, Reaktion auf Arbeitslosigkeit, Proteste, Schwarzmarkt, Legitimität |
| Human Capital | Bildung/Innovation, Gesundheit, Alterung, Renteneintritt |
| Migration | Haushalte können bei besseren Ländern und offenen Grenzen migrieren |
| Innovation | R&D Spend, Patente, Technologiefrontier, Spillover |
| Krisen/Schocks | Energiekrise, Naturkatastrophe, Cyberattacke, Kriegsschreck, Boykott, Bank Run, Skandale |
| Metriken | klassische Makrogrößen plus Winkel-, Finanz-, Politik-, Umwelt- und Gesellschaftsmetriken |

## Was weiterhin bewusst vereinfacht ist

- Die doppelte Buchführung ist stock-flow-artig, aber keine vollständige Depositenmatrix für jede Bank-Haushalt-Beziehung.
- Produkt-BOMs sind sektorale Inputgewichte, keine detaillierten Einzelstücklisten.
- FX ist eine Orderbook-Approximation, kein vollständiges Limit-Orderbuch pro Währungspaar.
- Aktien- und Bondmärkte sind institutionelle Overlays, kein Tick-by-Tick-Markt.
- Demografie ist kompakt modelliert: Alter, Tod, Renten, Migration; keine vollständigen Familienhaushalte.
- Politik ist Mehrparteienlogik, aber kein vollwertiges Parlament mit Koalitionsvertrag.
- Ratingagenturen und Zivilgesellschaft sind modelliert, aber nicht als vollständige Medien-/NGO-Netzwerke.

Diese Vereinfachungen sind bewusst gewählt, damit die Simulation als eine große einzelne PyPy3-Datei lauffähig bleibt.

# V3 Ergänzungen

## Expliziter Dreifachmarkt Wert/Gutartigkeit/Beliebtheit

V3 ergänzt eine eigene Phase `triadic_value_goodness_popularity_market`, die folgende Tauschbeziehungen modelliert und in `metrics.csv` schreibt:

- `value_buy_goodness_volume`: scalarer Wert kauft echte Gutartigkeit über Compliance, Audits, Umweltverbesserung, Arbeitsschutz, Transparenz und Betrugsreduktion.
- `value_buy_popularity_volume`: scalarer Wert kauft Beliebtheit über Werbung, Medien, Service und Community-Effekte.
- `popularity_buy_goodness_volume`: Beliebtheit kauft Gutartigkeit, weil Markenvertrauen und soziale Akzeptanz die Kosten glaubwürdiger Reformen senken.
- `goodness_buy_popularity_volume`: Gutartigkeit kauft Beliebtheit, wenn Medienfreiheit, Gerichte und Zivilgesellschaft gute Handlungen sichtbar machen.
- `value_good_pop_exchange_fees`: Reibung, Gebühren, Korruptionsverlust und Ineffizienz des Dreifachtausches.
- `triadic_exchange_count`: Anzahl dieser Dreifachtauschereignisse pro Schritt.

Der Tausch ist adversarial modelliert: Betrug, geringe Transparenz, schwache Gerichte, geringe Medienfreiheit und Korruption können einen scheinbaren Popularitäts- oder Gutartigkeitserwerb in Konfidenzverlust und Winkelwäsche verwandeln.

## UTF‑8/ANSI-Diagramme als Skriptausgabe

Mit `--art` gibt das Skript viele farbige Terminaldiagramme aus:

- Makro-Cockpit
- Weltgeld-Kompass
- Dreifachhandel Wert/Gutartigkeit/Beliebtheit
- Marktflussdiagramm
- Kreis-Orderbuch für Kaufwinkel und Verkaufswinkel
- Akteurstabelle mit zwei Winkeln je Akteur
- Länder-/Jurisdiktionspanels
- Firmenquadrantenkarte Gutartigkeit × Beliebtheit
- externe Effekte und Sicherheitsventile
- Ereignisband

Die Diagramme funktionieren ohne externe Pakete und können mit `--no-color` als reine UTF‑8-Art ausgegeben werden.

## Buy-/Sell-Winkel sichtbar gemacht

V2 hatte `buy_angle` und `sell_angle` bereits intern. V3 macht sie im Output zentral sichtbar:

```text
Kaufwinkel θ_K       = Akzeptanzrichtung
Verkaufswinkel θ_V   = verlangte Richtung
Spread Δθ            = Distanz auf dem Kreis
Betrag m             = Gewicht der Winkelorder
```

Das Kreis-Orderbuch aggregiert alle Akteure nach Winkelzonen und gewichtet sie mit Cashbetrag und Konfidenz.
