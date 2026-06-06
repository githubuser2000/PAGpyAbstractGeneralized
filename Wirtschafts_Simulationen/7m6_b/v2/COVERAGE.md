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
