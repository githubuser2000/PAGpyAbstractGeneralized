# CHANGELOG V2

Gegenüber der ersten Version wurden vor allem folgende Blöcke ergänzt:

## Neue Akteurstypen und Datenstrukturen

- `InvestmentFund`: Investment-/Pensionsfonds mit AUM, Mandatswinkel, Bonds und Equity-Holdings
- `CorporateGroup`: explizite Konzern-/Holdingstruktur mit Parent, Tochterfirmen, Tax Haven und Opazität
- `PropertyAsset`: Immobilien, Eigenheime, Mietobjekte, Zustand, Wert, Miete, Hypothek
- `InsurancePolicy`: Versicherungen mit Prämien, Coverage, Claims
- `Bond`: Sovereign und Corporate Bonds mit Coupon, Laufzeit, Default
- `EquityListing`: Aktienlisting mit Shares, Free Float, Preis, Winkel, Konfidenz
- `RatingAgency`: alternative Orakel mit Accuracy, Bias, Corruption, Influence
- `PoliticalParty`: Parteien mit Ideologie, Wirtschaftspolitik, Autoritarismus, Support, Spendern
- `TradeAgreement`: Handelsabkommen mit Tarifdiscount und Winkelangleichung
- `InfrastructureAsset`: Infrastruktur nach Sektor, Kapazität und Zustand

## Neue Mechaniken

- FX-/Kapitalfluss-Orderbookapproximation
- Reserveinterventionen durch Zentralbanken
- Reservewährungsstatus
- Bondemissionen und Bonddefaults
- Equity Issuance und Mark-to-Market-Aktienpreise
- Dividendenzahlungen
- Konzerninternes Transfer Pricing und Steuervermeidung
- Immobilienmarkt, Mieten, Hypotheken, Landpreisindex
- Versicherungsprämien und Schadensfälle
- R&D, Patente, Technologie-Spillovers
- Ratingagenturen als nichtstaatliche Bewertungsorakel
- politische Parteien, Lobbying-Spenden, ideologischer Einfluss
- Verfassungs-/Gerichts-Overrides gegen willkürliche Sanktionen
- Minderheitenschutz und Minority-Harm-Index
- zivilgesellschaftliche Untersuchungen
- Vertragsstreitigkeiten und Gerichtslösung
- Infrastrukturwartung und Produktivitätswirkung
- Carbon Stock, Biodiversity, Health Burden, Crime Index, Data Privacy Damage
- Human Capital, Gesundheit, Alterung, Renteneintritt, Sterblichkeit, Migration
- Handelsabkommen mit langsamer Winkelangleichung

## Neue Metriken

- `fx_orderbook_volume`
- `capital_flow_volume`
- `reserve_intervention`
- `bond_issuance`
- `bond_defaults`
- `equity_issuance`
- `equity_trading_volume`
- `dividends`
- `transfer_pricing_volume`
- `tax_avoided`
- `real_estate_rents`
- `mortgages_issued`
- `insurance_premiums`
- `insurance_claims`
- `r_and_d_spend`
- `patent_events`
- `rating_actions`
- `constitutional_overrides`
- `minority_harm_index`
- `migration_count`
- `infrastructure_spending`
- `privacy_damage`
- `health_damage`
- `biodiversity_loss`
- `crime_delta`
- `contract_disputes`

## Teststatus

- `python3 -m py_compile vector_currency_sim.py` erfolgreich.
- Demo-Lauf mit `--steps 60 --countries 3 --households 600 --firms 120 --banks 9 --seed 42` erfolgreich.
- `pypy3` war in der Erstellungsumgebung nicht installiert; der Code ist reine Standardbibliothek und PyPy3-kompatibel geschrieben.
