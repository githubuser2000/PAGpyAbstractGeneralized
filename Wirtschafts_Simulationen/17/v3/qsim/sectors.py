# -*- coding: utf-8 -*-
"""Güter, Sektoren, Arbeitstypen und Produktionsrezepte.

Das Modell bildet nicht nur Intelligenzarbeit ab, sondern eine ganze Volks-
wirtschaft: Nahrung, Rohstoffe, Energie, Industrie, Bau, Gesundheit, Bildung,
Logistik, Handel, Pflege, Kultur, Sicherheit, Umwelt, öffentliche Dienste,
Finanzwesen, Software/KI/Forschung und Wartung.
"""

from __future__ import print_function

from dataclasses import dataclass, field
from .utils import normalize_weights
from .money import Q_VALUES, vector_from_value


@dataclass
class LaborType:
    key: str
    label: str
    base_wage: float
    q_wage_distribution: dict
    description: str

    def wage_vector(self, wage_zw):
        return vector_from_value(wage_zw, self.q_wage_distribution)


LABOR_TYPES = {
    "manual_basic": LaborType("manual_basic", "Einfache körperliche Arbeit", 1.15, {1: 0.55, 2: 0.30, 7: 0.15}, "Tragen, Reinigen, einfache Dienste, Hilfstätigkeiten"),
    "agriculture": LaborType("agriculture", "Landwirtschaft", 1.35, {1: 0.35, 2: 0.35, 10: 0.15, 16: 0.15}, "Nahrung, Boden, Pflanzen, Tiere, Ernte"),
    "mining": LaborType("mining", "Rohstoffarbeit", 1.70, {2: 0.45, 4: 0.20, 10: 0.15, 16: 0.20}, "Bergbau, Rohstoffgewinnung, Gewinnung harter Grundlagen"),
    "energy": LaborType("energy", "Energiearbeit", 2.15, {10: 0.25, 16: 0.35, 18: 0.25, 20: 0.15}, "Kraftwerke, Netze, Energieanlagen, Versorgung"),
    "industrial": LaborType("industrial", "Industriearbeit", 2.05, {4: 0.20, 5: 0.35, 10: 0.20, 20: 0.25}, "Fabrikation, Maschinenbedienung, Serienarbeit"),
    "craft": LaborType("craft", "Handwerk", 1.95, {2: 0.25, 4: 0.30, 10: 0.20, 15: 0.25}, "Reparatur, Bauhandwerk, lokale Fertigung"),
    "construction": LaborType("construction", "Bauarbeit", 2.25, {4: 0.20, 10: 0.25, 18: 0.35, 20: 0.20}, "Gebäude, Infrastruktur, physische Konstruktion"),
    "logistics": LaborType("logistics", "Logistik", 1.75, {7: 0.35, 11: 0.20, 14: 0.15, 16: 0.30}, "Transport, Lager, Verteilung, Routen"),
    "retail": LaborType("retail", "Handel", 1.40, {7: 0.20, 11: 0.45, 13: 0.15, 15: 0.20}, "Verkauf, Kundenkontakt, Verteilung am Markt"),
    "hospitality": LaborType("hospitality", "Gastgewerbe", 1.35, {11: 0.35, 15: 0.40, 16: 0.10, 7: 0.15}, "Gastronomie, Unterkunft, Alltagserholung"),
    "care": LaborType("care", "Pflege", 1.85, {11: 0.40, 13: 0.25, 14: 0.10, 16: 0.25}, "Pflege, Betreuung, Hilfe im Alltag"),
    "health": LaborType("health", "Gesundheit", 2.75, {11: 0.25, 12: 0.15, 13: 0.30, 16: 0.30}, "Medizinische Versorgung, Diagnostik, Therapie"),
    "teaching": LaborType("teaching", "Bildung", 2.10, {3: 0.20, 6: 0.15, 12: 0.45, 14: 0.20}, "Lehre, Ausbildung, Didaktik, Wissensvermittlung"),
    "research": LaborType("research", "Forschung", 3.10, {1: 0.15, 3: 0.30, 12: 0.20, 17: 0.15, 19: 0.20}, "Neue Fragen, Theorien, Werkzeuge, Generierungsprinzipien"),
    "software": LaborType("software", "Software/KI/Automatisierung", 2.90, {5: 0.25, 6: 0.15, 8: 0.15, 13: 0.20, 19: 0.25}, "Programmierung, Automatisierung, KI-Dienste"),
    "engineering": LaborType("engineering", "Ingenieurwesen", 3.00, {10: 0.25, 11: 0.15, 17: 0.15, 18: 0.30, 20: 0.15}, "Technische Konstruktion, Anlagen, Design"),
    "maintenance": LaborType("maintenance", "Wartung", 1.95, {10: 0.20, 16: 0.40, 17: 0.25, 20: 0.15}, "Instandhaltung, Reparatur, Betriebssicherung"),
    "finance": LaborType("finance", "Finanzwesen", 2.45, {9: 0.20, 10: 0.25, 12: 0.15, 13: 0.20, 18: 0.20}, "Banken, Risiko, Kredit, Zahlungsströme"),
    "legal": LaborType("legal", "Recht/Verträge", 2.35, {6: 0.15, 10: 0.45, 11: 0.20, 14: 0.20}, "Verträge, Regeln, Haftung, Konfliktklärung"),
    "creative": LaborType("creative", "Kreative Arbeit", 1.85, {1: 0.15, 3: 0.30, 15: 0.35, 17: 0.20}, "Kunst, Medien, Design, Kultur"),
    "public_service": LaborType("public_service", "Öffentlicher Dienst", 2.05, {10: 0.25, 11: 0.20, 14: 0.25, 16: 0.30}, "Verwaltung, Infrastruktur, öffentliche Ordnung"),
    "security": LaborType("security", "Sicherheit", 1.95, {10: 0.35, 11: 0.15, 14: 0.15, 16: 0.35}, "Schutz, Resilienz, Gefahrenabwehr"),
    "environmental": LaborType("environmental", "Umweltarbeit", 2.15, {1: 0.10, 10: 0.25, 12: 0.15, 17: 0.25, 18: 0.25}, "Ressourcenpflege, Ökologie, Klimaanpassung"),
    "management": LaborType("management", "Management/Organisation", 3.00, {7: 0.15, 10: 0.20, 14: 0.35, 18: 0.30}, "Koordination, Planung, Verantwortung, Meisterung"),
}


@dataclass
class Good:
    key: str
    label: str
    base_price: float
    essential: float
    durability: float
    household_weight: float
    description: str


GOODS = {
    "food": Good("food", "Nahrung", 1.0, 1.00, 0.05, 1.00, "Lebensmittel und Grundversorgung"),
    "raw_materials": Good("raw_materials", "Rohstoffe", 1.4, 0.35, 0.80, 0.05, "Metalle, Mineralien, Grundstoffe"),
    "energy": Good("energy", "Energie", 1.6, 0.95, 0.00, 0.70, "Strom, Wärme, Treibstoffe"),
    "manufactured_goods": Good("manufactured_goods", "Industriegüter", 2.5, 0.45, 0.65, 0.35, "Geräte, Werkzeuge, Konsumgüter"),
    "housing": Good("housing", "Wohnraum/Bau", 4.0, 0.95, 0.95, 0.80, "Wohnraum und Bauleistung"),
    "health_service": Good("health_service", "Gesundheitsleistung", 3.2, 0.90, 0.00, 0.55, "Medizin und Pflege"),
    "education_service": Good("education_service", "Bildungsleistung", 2.8, 0.65, 0.15, 0.35, "Ausbildung, Schule, Weiterbildung"),
    "transport_service": Good("transport_service", "Transport/Logistik", 1.8, 0.65, 0.00, 0.45, "Mobilität und Verteilung"),
    "retail_service": Good("retail_service", "Handelsleistung", 1.5, 0.40, 0.00, 0.30, "Distribution und Kundenservice"),
    "finance_service": Good("finance_service", "Finanzdienst", 2.2, 0.25, 0.00, 0.10, "Kredit, Versicherung, Zahlungswesen"),
    "public_service": Good("public_service", "Öffentliche Leistung", 2.5, 0.75, 0.05, 0.50, "Verwaltung, Sicherheit, Gemeingüter"),
    "culture_service": Good("culture_service", "Kultur/Kreativität", 1.9, 0.25, 0.10, 0.35, "Medien, Kunst, Unterhaltung"),
    "hospitality_service": Good("hospitality_service", "Gastgewerbe", 1.7, 0.20, 0.00, 0.25, "Gastronomie, Unterkunft, Tourismus"),
    "maintenance_service": Good("maintenance_service", "Wartung", 2.0, 0.55, 0.00, 0.25, "Reparatur, Instandhaltung, Betriebspflege"),
    "automation_service": Good("automation_service", "Software/KI/Automatisierung", 3.5, 0.35, 0.25, 0.15, "Software, KI, Automatisierung, Daten"),
    "knowledge": Good("knowledge", "Forschung/Wissen", 3.8, 0.30, 0.50, 0.10, "Forschung, neue Theorien, Prototypen"),
    "environment_service": Good("environment_service", "Umwelt/Resilienz", 2.6, 0.60, 0.20, 0.25, "Ökologische Reparatur, Ressourcenpflege"),
    "security_service": Good("security_service", "Sicherheit", 2.1, 0.70, 0.00, 0.30, "Schutz, Resilienz, Gefahrenabwehr"),
}


@dataclass
class SectorRecipe:
    key: str
    label: str
    output_good: str
    base_productivity: float
    input_goods: dict
    labor_mix: dict
    q_distribution: dict
    q_intensity: float
    capital_intensity: float
    public_share: float = 0.0
    export_share: float = 0.0
    critical_q: tuple = field(default_factory=tuple)
    description: str = ""

    def q_mint_for_output_value(self, output_value, quality):
        amount = max(0.0, float(output_value)) * self.q_intensity * max(0.0, quality)
        return vector_from_value(amount, self.q_distribution)

    def normalized_labor_mix(self):
        return normalize_weights(self.labor_mix)


SECTOR_RECIPES = {
    "agriculture": SectorRecipe(
        "agriculture", "Landwirtschaft", "food", 5.5,
        {"energy": 0.08, "manufactured_goods": 0.03, "environment_service": 0.02},
        {"agriculture": 0.55, "manual_basic": 0.20, "logistics": 0.10, "maintenance": 0.10, "management": 0.05},
        {1: 0.35, 2: 0.25, 10: 0.15, 16: 0.15, 18: 0.10}, 0.10, 0.35, export_share=0.08, critical_q=(10, 16),
        description="Erzeugt Nahrung aus Natur, Energie, Maschinen und Arbeit."),
    "mining": SectorRecipe(
        "mining", "Rohstoffe", "raw_materials", 4.0,
        {"energy": 0.16, "maintenance_service": 0.03},
        {"mining": 0.45, "industrial": 0.20, "energy": 0.10, "maintenance": 0.15, "management": 0.10},
        {2: 0.35, 4: 0.15, 10: 0.20, 16: 0.15, 18: 0.15}, 0.11, 0.65, export_share=0.18, critical_q=(10, 16, 18),
        description="Gewinnt Rohstoffe und erzeugt ökologische Nebenrisiken."),
    "energy": SectorRecipe(
        "energy", "Energie", "energy", 4.8,
        {"raw_materials": 0.10, "manufactured_goods": 0.05, "maintenance_service": 0.04},
        {"energy": 0.35, "engineering": 0.20, "maintenance": 0.20, "industrial": 0.10, "management": 0.15},
        {10: 0.20, 16: 0.35, 18: 0.30, 20: 0.15}, 0.15, 0.85, public_share=0.10, export_share=0.10, critical_q=(16, 18, 20),
        description="Erzeugt Strom/Wärme/Treibstoffe; zentrale Produktionsbedingung."),
    "manufacturing": SectorRecipe(
        "manufacturing", "Industrie", "manufactured_goods", 4.2,
        {"raw_materials": 0.30, "energy": 0.16, "automation_service": 0.03, "maintenance_service": 0.05},
        {"industrial": 0.38, "engineering": 0.18, "maintenance": 0.12, "logistics": 0.10, "software": 0.08, "management": 0.14},
        {4: 0.10, 5: 0.20, 10: 0.20, 16: 0.15, 18: 0.20, 20: 0.15}, 0.18, 0.80, export_share=0.20, critical_q=(10, 16, 18, 20),
        description="Verwandelt Rohstoffe und Energie in Geräte und Konsumgüter."),
    "construction": SectorRecipe(
        "construction", "Bau", "housing", 2.4,
        {"raw_materials": 0.30, "manufactured_goods": 0.18, "energy": 0.10, "maintenance_service": 0.02},
        {"construction": 0.42, "craft": 0.16, "engineering": 0.16, "manual_basic": 0.10, "logistics": 0.06, "management": 0.10},
        {4: 0.10, 10: 0.20, 11: 0.10, 18: 0.40, 20: 0.20}, 0.20, 0.95, public_share=0.15, critical_q=(10, 18, 20),
        description="Baut Wohnungen, Anlagen und Infrastruktur."),
    "healthcare": SectorRecipe(
        "healthcare", "Gesundheit", "health_service", 3.1,
        {"energy": 0.05, "manufactured_goods": 0.08, "automation_service": 0.02},
        {"health": 0.42, "care": 0.25, "administrative": 0.0, "software": 0.05, "logistics": 0.05, "management": 0.10, "maintenance": 0.08, "public_service": 0.05},
        {11: 0.20, 12: 0.15, 13: 0.25, 14: 0.10, 16: 0.30}, 0.16, 0.45, public_share=0.45, critical_q=(11, 13, 16),
        description="Heilt, pflegt und stabilisiert menschliche Arbeitsfähigkeit."),
    "education": SectorRecipe(
        "education", "Bildung", "education_service", 3.0,
        {"energy": 0.03, "automation_service": 0.04, "public_service": 0.02},
        {"teaching": 0.52, "research": 0.10, "software": 0.08, "public_service": 0.10, "management": 0.10, "creative": 0.10},
        {1: 0.10, 3: 0.20, 6: 0.15, 12: 0.40, 14: 0.15}, 0.18, 0.30, public_share=0.55, critical_q=(3, 12, 14),
        description="Erhöht Fähigkeiten und senkt zukünftige Knappheit."),
    "logistics": SectorRecipe(
        "logistics", "Logistik", "transport_service", 4.5,
        {"energy": 0.22, "manufactured_goods": 0.03, "maintenance_service": 0.04},
        {"logistics": 0.50, "manual_basic": 0.10, "software": 0.08, "maintenance": 0.12, "management": 0.12, "security": 0.08},
        {7: 0.25, 11: 0.15, 14: 0.15, 16: 0.30, 18: 0.15}, 0.12, 0.55, export_share=0.10, critical_q=(7, 16, 18),
        description="Bewegt Güter, Menschen und Versorgungsströme."),
    "retail": SectorRecipe(
        "retail", "Handel", "retail_service", 4.0,
        {"transport_service": 0.12, "energy": 0.04, "automation_service": 0.02},
        {"retail": 0.45, "logistics": 0.15, "software": 0.08, "hospitality": 0.05, "management": 0.15, "security": 0.07, "creative": 0.05},
        {7: 0.15, 11: 0.35, 13: 0.20, 15: 0.20, 16: 0.10}, 0.10, 0.30, critical_q=(11, 13, 16),
        description="Organisiert Marktzugang und Kundenversorgung."),
    "finance": SectorRecipe(
        "finance", "Finanzwesen", "finance_service", 3.2,
        {"automation_service": 0.05, "public_service": 0.02, "energy": 0.02},
        {"finance": 0.42, "legal": 0.16, "software": 0.12, "management": 0.20, "public_service": 0.05, "research": 0.05},
        {9: 0.20, 10: 0.25, 12: 0.10, 13: 0.20, 18: 0.25}, 0.14, 0.25, critical_q=(10, 13, 18),
        description="Allokiert Kredit, Risiko und Zahlungsfähigkeit."),
    "public": SectorRecipe(
        "public", "Öffentlicher Dienst", "public_service", 3.0,
        {"energy": 0.04, "automation_service": 0.04, "finance_service": 0.02},
        {"public_service": 0.42, "legal": 0.14, "security": 0.12, "teaching": 0.08, "management": 0.18, "software": 0.06},
        {10: 0.25, 11: 0.15, 14: 0.25, 16: 0.35}, 0.15, 0.35, public_share=0.90, critical_q=(10, 14, 16),
        description="Schafft Ordnung, Regeln, Gemeingüter und Verwaltung."),
    "creative": SectorRecipe(
        "creative", "Kreativwirtschaft", "culture_service", 3.0,
        {"energy": 0.02, "automation_service": 0.03, "retail_service": 0.03},
        {"creative": 0.55, "software": 0.10, "retail": 0.10, "management": 0.10, "research": 0.05, "hospitality": 0.10},
        {1: 0.10, 3: 0.30, 15: 0.35, 17: 0.25}, 0.11, 0.20, export_share=0.08, critical_q=(3, 15, 17),
        description="Erzeugt Kultur, Design, Erzählungen und Aufmerksamkeit."),
    "hospitality": SectorRecipe(
        "hospitality", "Gastgewerbe", "hospitality_service", 3.5,
        {"food": 0.18, "energy": 0.05, "retail_service": 0.03},
        {"hospitality": 0.50, "retail": 0.12, "manual_basic": 0.12, "logistics": 0.08, "management": 0.12, "creative": 0.06},
        {11: 0.25, 15: 0.40, 16: 0.20, 7: 0.15}, 0.10, 0.25, export_share=0.08, critical_q=(11, 15, 16),
        description="Erzeugt Gastronomie, Tourismus, Unterkunft und Alltagsdienst."),
    "maintenance": SectorRecipe(
        "maintenance", "Wartung", "maintenance_service", 3.6,
        {"manufactured_goods": 0.08, "energy": 0.04, "raw_materials": 0.03},
        {"maintenance": 0.45, "craft": 0.18, "engineering": 0.12, "software": 0.08, "manual_basic": 0.07, "management": 0.10},
        {10: 0.20, 16: 0.35, 17: 0.25, 20: 0.20}, 0.16, 0.45, critical_q=(10, 16, 17, 20),
        description="Senkt Abschreibung, hält Systeme lebendig und verhindert Krise."),
    "software_ai": SectorRecipe(
        "software_ai", "Software/KI/Automatisierung", "automation_service", 3.6,
        {"energy": 0.08, "education_service": 0.03, "knowledge": 0.04},
        {"software": 0.48, "research": 0.14, "engineering": 0.10, "teaching": 0.05, "management": 0.13, "legal": 0.05, "creative": 0.05},
        {5: 0.18, 6: 0.12, 8: 0.13, 9: 0.10, 10: 0.10, 13: 0.15, 17: 0.08, 19: 0.24}, 0.24, 0.45, export_share=0.25, critical_q=(6, 10, 13, 16, 18, 19),
        description="Programmiert, automatisiert und erzeugt datenbasierte Produktionsmittel."),
    "research": SectorRecipe(
        "research", "Forschung", "knowledge", 2.2,
        {"education_service": 0.08, "automation_service": 0.06, "energy": 0.03, "public_service": 0.02},
        {"research": 0.48, "teaching": 0.12, "software": 0.12, "engineering": 0.12, "creative": 0.06, "management": 0.06, "legal": 0.04},
        {1: 0.16, 3: 0.26, 4: 0.08, 12: 0.18, 17: 0.12, 19: 0.20}, 0.28, 0.35, public_share=0.40, export_share=0.12, critical_q=(1, 3, 12, 17, 19),
        description="Findet neue Aufgaben, Modelle, Werkzeuge und Generierungsprinzipien."),
    "environment": SectorRecipe(
        "environment", "Umwelt/Resilienz", "environment_service", 2.8,
        {"energy": 0.04, "manufactured_goods": 0.04, "knowledge": 0.03},
        {"environmental": 0.42, "engineering": 0.18, "manual_basic": 0.10, "research": 0.10, "public_service": 0.10, "management": 0.10},
        {1: 0.10, 10: 0.25, 12: 0.15, 17: 0.25, 18: 0.25}, 0.17, 0.40, public_share=0.55, critical_q=(10, 17, 18),
        description="Repariert ökologische Schäden und stärkt Langzeitresilienz."),
    "security": SectorRecipe(
        "security", "Sicherheit", "security_service", 3.3,
        {"energy": 0.03, "automation_service": 0.04, "public_service": 0.03},
        {"security": 0.48, "public_service": 0.14, "software": 0.12, "legal": 0.08, "management": 0.12, "logistics": 0.06},
        {10: 0.30, 11: 0.15, 14: 0.15, 16: 0.30, 18: 0.10}, 0.13, 0.35, public_share=0.45, critical_q=(10, 16, 18),
        description="Schützt Infrastruktur, Menschen, Netze und Vertragsordnung."),
}

# Einige Rezepte enthalten administrative Arbeit indirekt; der Typ wird hier auf public_service/management abgebildet.
# Das hält die Arbeitstypenliste klar, ohne eine weitere Kategorie einzuführen.
for recipe in SECTOR_RECIPES.values():
    if "administrative" in recipe.labor_mix:
        val = recipe.labor_mix.pop("administrative")
        recipe.labor_mix["public_service"] = recipe.labor_mix.get("public_service", 0.0) + val * 0.60
        recipe.labor_mix["management"] = recipe.labor_mix.get("management", 0.0) + val * 0.40


HOUSEHOLD_CONSUMPTION_WEIGHTS = dict((k, g.household_weight) for k, g in GOODS.items() if g.household_weight > 0)
ESSENTIAL_GOODS = [k for k, g in GOODS.items() if g.essential >= 0.65]
CAPITAL_GOODS = ["manufactured_goods", "housing", "automation_service", "maintenance_service", "knowledge"]
PUBLIC_GOODS = ["public_service", "education_service", "health_service", "environment_service", "security_service", "housing"]


def sector_for_good(good_key):
    for s, recipe in SECTOR_RECIPES.items():
        if recipe.output_good == good_key:
            return s
    return None


def labor_types_for_sector(sector_key):
    recipe = SECTOR_RECIPES[sector_key]
    return list(recipe.normalized_labor_mix().keys())
