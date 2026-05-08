# -*- coding: utf-8 -*-
"""Q-Währung: Münzen, Werte, Wallets und Schuldenlogik.

Die Münznummer ist die semantische Prägung. Der Münzwert ist die Zeilenhöhe.
Negative Bestände sind Schulden. Inverse Operationen wie 1/Q17 sind keine
Schulden, sondern werden als semantische Gegenoperationen dokumentiert.
"""

from __future__ import print_function

from collections import defaultdict
from .utils import EPS, clamp, normalize_weights

Q_META = {
    1:  {"name": "Schwierigkeit", "value": 1.0, "layer": "Grundmünze", "meaning": "Aufgabe, Schwierigkeit, Knoten, Problemkern"},
    2:  {"name": "Komplexität", "value": 1.0, "layer": "Grundmünze", "meaning": "Teil, Kompliziertheit, Molekülelement, Teilstruktur"},
    3:  {"name": "Abstraktion", "value": 1.0, "layer": "Grundmünze", "meaning": "Theorie, Modell, lockerer/fester Zwischenzustand"},
    4:  {"name": "Kristallisation", "value": 1.0, "layer": "Grundmünze", "meaning": "formales Objekt, Faden, mathematische Gestalt"},
    5:  {"name": "Kodierung", "value": 2.0, "layer": "Operationsmünze", "meaning": "Enkodieren, Befehl, Kommando, imperatives Programmieren"},
    6:  {"name": "Deklaration", "value": 2.0, "layer": "Operationsmünze", "meaning": "declarative Beschreibung, Regel, Faden statt Befehl"},
    7:  {"name": "Delegation", "value": 2.0, "layer": "Operationsmünze", "meaning": "Delegieren, Referenzieren, Verantwortungsübertragung"},
    8:  {"name": "Bibliothek", "value": 2.0, "layer": "Operationsmünze", "meaning": "wiederverwendbarer Stein, Wabe, Bausteinsammlung"},
    9:  {"name": "Framework", "value": 2.0, "layer": "Operationsmünze", "meaning": "Rahmen, Organisches, allgemeine Intelligenzstruktur"},
    10: {"name": "Constraint", "value": 3.0, "layer": "Systemmünze", "meaning": "Beschränkung, Struktur, Strick, Möglichkeitsraum"},
    11: {"name": "Schnittstelle", "value": 3.0, "layer": "Systemmünze", "meaning": "Eingriff, Interface, Gedankeneinsatz"},
    12: {"name": "Toolbox", "value": 3.0, "layer": "Systemmünze", "meaning": "Werkzeugkoffer, Mathematik, Methoden"},
    13: {"name": "Programm/Dienst", "value": 3.0, "layer": "Systemmünze", "meaning": "Programm, Service, Paradigma, Dienst, Gedankenansatz"},
    14: {"name": "Orchestrierung", "value": 3.0, "layer": "Systemmünze", "meaning": "Komposition, Choreographie, Dirigieren, Meisterung"},
    15: {"name": "Anwendung", "value": 3.0, "layer": "Systemmünze", "meaning": "Applikation, Werk, Opus"},
    16: {"name": "Betrieb", "value": 3.0, "layer": "Systemmünze", "meaning": "Menü, Kernel, Betriebssystem, Ausführung"},
    17: {"name": "Kompression", "value": 4.0, "layer": "Kapitalmünze", "meaning": "Kompression; 1/Q17 = Dekompression"},
    18: {"name": "Architektur", "value": 4.0, "layer": "Kapitalmünze", "meaning": "Architektur, Konstruktion"},
    19: {"name": "Generierung", "value": 4.0, "layer": "Kapitalmünze", "meaning": "Generierung; 1/Q19 = Degenerierung"},
    20: {"name": "Modul/Maschine", "value": 4.0, "layer": "Kapitalmünze", "meaning": "Modul, Maschine, Gerät, fertige Entwicklung"},
}

Q_VALUES = dict((i, Q_META[i]["value"]) for i in Q_META)
Q_LABELS = dict((i, "Q%d" % i) for i in Q_META)

INVERSE_OPERATIONS = {
    5: "Dekodieren",
    7: "Referenzieren",
    10: "Entwicklungsmöglichkeit",
    17: "Dekompression",
    19: "Degenerierung/Dekadenz",
}

# Ersatznähe: Eine Typenschuld Qk kann teilweise durch ähnliche Münzen gedeckt werden.
# Werte sind semantische Anrechnungsfaktoren. 1.0 = gleiche Münze.
SUBSTITUTION = defaultdict(dict)
for q in Q_META:
    SUBSTITUTION[q][q] = 1.0
# ausgewählte Nähebeziehungen
SUBSTITUTION[5].update({6: 0.55, 8: 0.45, 13: 0.50})
SUBSTITUTION[6].update({5: 0.45, 10: 0.55, 12: 0.40})
SUBSTITUTION[8].update({5: 0.35, 9: 0.70, 12: 0.55, 17: 0.45})
SUBSTITUTION[9].update({8: 0.70, 10: 0.50, 11: 0.45, 13: 0.50})
SUBSTITUTION[10].update({6: 0.55, 11: 0.55, 12: 0.45, 18: 0.60})
SUBSTITUTION[11].update({10: 0.55, 13: 0.50, 16: 0.45, 18: 0.45})
SUBSTITUTION[12].update({3: 0.35, 8: 0.55, 10: 0.40, 17: 0.45})
SUBSTITUTION[13].update({5: 0.45, 11: 0.50, 15: 0.55, 16: 0.40})
SUBSTITUTION[14].update({7: 0.45, 11: 0.45, 16: 0.50, 18: 0.45})
SUBSTITUTION[15].update({13: 0.60, 16: 0.50, 20: 0.50})
SUBSTITUTION[16].update({11: 0.45, 13: 0.35, 14: 0.50, 18: 0.40, 20: 0.45})
SUBSTITUTION[17].update({3: 0.35, 8: 0.40, 12: 0.45, 18: 0.55})
SUBSTITUTION[18].update({10: 0.60, 11: 0.45, 14: 0.50, 17: 0.55, 20: 0.55})
SUBSTITUTION[19].update({8: 0.40, 9: 0.55, 13: 0.50, 17: 0.50, 18: 0.60, 20: 0.60})
SUBSTITUTION[20].update({13: 0.40, 15: 0.55, 16: 0.60, 18: 0.60, 19: 0.65})


def coin_value(q):
    return Q_VALUES[int(q)]


def q_name(q):
    return Q_META[int(q)]["name"]


def vector_value(vec):
    total = 0.0
    for q, qty in vec.items():
        total += Q_VALUES[int(q)] * qty
    return total


def vector_from_value(amount_zw, distribution, min_coin=1):
    """Wandelt einen ZW-Betrag in einen Q-Vektor anhand von Wertanteilen um.

    distribution: dict Q -> Wertanteil, nicht Mengenanteil.
    """
    if amount_zw <= EPS:
        return {}
    dist = normalize_weights(distribution)
    out = {}
    for q, share in dist.items():
        q = int(q)
        out[q] = (amount_zw * share) / Q_VALUES[q]
    return out


class Wallet(object):
    """Vektor-Wallet mit Q1..Q20. Negative Werte sind Schulden."""

    def __init__(self, balances=None):
        self.balances = dict((i, 0.0) for i in range(1, 21))
        if balances:
            for q, qty in balances.items():
                self.balances[int(q)] = float(qty)

    def copy(self):
        return Wallet(self.balances)

    def add_coin(self, q, qty):
        q = int(q)
        self.balances[q] = self.balances.get(q, 0.0) + float(qty)
        if abs(self.balances[q]) < EPS:
            self.balances[q] = 0.0

    def add_vector(self, vec, scale=1.0):
        for q, qty in vec.items():
            self.add_coin(q, float(qty) * scale)

    def positive_qty(self, q):
        return max(0.0, self.balances.get(int(q), 0.0))

    def debt_qty(self, q):
        return max(0.0, -self.balances.get(int(q), 0.0))

    def total_value(self):
        return sum(Q_VALUES[q] * qty for q, qty in self.balances.items())

    def positive_value(self):
        return sum(Q_VALUES[q] * max(0.0, qty) for q, qty in self.balances.items())

    def debt_value(self):
        return sum(Q_VALUES[q] * max(0.0, -qty) for q, qty in self.balances.items())

    def q_value(self, q):
        q = int(q)
        return Q_VALUES[q] * self.balances.get(q, 0.0)

    def debt_vector(self):
        return dict((q, -qty) for q, qty in self.balances.items() if qty < -EPS)

    def asset_vector(self):
        return dict((q, qty) for q, qty in self.balances.items() if qty > EPS)

    def as_dict(self, precision=6):
        return dict(("Q%d" % q, round(qty, precision)) for q, qty in self.balances.items() if abs(qty) > EPS)

    def extract_value(self, amount_zw, preferred_order=None, debt_q=1, allow_debt=True):
        """Entnimmt beliebige positive Münzen bis amount_zw.

        Rückgabe: Q-Vektor der abgegebenen Münzen. Falls allow_debt=True und
        das Wallet nicht reicht, wird der Rest als negative Position in debt_q
        gebucht und zugleich als ausgegebener Vektor zurückgegeben. So entsteht
        private Schuld: Zahler negativ, Empfänger positiv.
        """
        amount_zw = float(amount_zw)
        if amount_zw <= EPS:
            return {}
        remaining = amount_zw
        out = {}
        if preferred_order is None:
            preferred_order = list(range(20, 0, -1))
        used = set()
        # Erst bevorzugte Reihenfolge.
        for q in preferred_order:
            q = int(q)
            used.add(q)
            qty = self.positive_qty(q)
            if qty <= EPS or remaining <= EPS:
                continue
            qv = Q_VALUES[q]
            take_qty = min(qty, remaining / qv)
            if take_qty > EPS:
                self.add_coin(q, -take_qty)
                out[q] = out.get(q, 0.0) + take_qty
                remaining -= take_qty * qv
        # Dann alle übrigen.
        if remaining > EPS:
            for q in range(1, 21):
                if q in used:
                    continue
                qty = self.positive_qty(q)
                if qty <= EPS or remaining <= EPS:
                    continue
                qv = Q_VALUES[q]
                take_qty = min(qty, remaining / qv)
                if take_qty > EPS:
                    self.add_coin(q, -take_qty)
                    out[q] = out.get(q, 0.0) + take_qty
                    remaining -= take_qty * qv
        if remaining > EPS and allow_debt:
            debt_q = int(debt_q)
            debt_qty = remaining / Q_VALUES[debt_q]
            self.add_coin(debt_q, -debt_qty)
            out[debt_q] = out.get(debt_q, 0.0) + debt_qty
            remaining = 0.0
        return out

    def pay_value_to(self, recipient_wallet, amount_zw, preferred_order=None, debt_q=1, allow_debt=True):
        vec = self.extract_value(amount_zw, preferred_order=preferred_order, debt_q=debt_q, allow_debt=allow_debt)
        recipient_wallet.add_vector(vec)
        return vector_value(vec)

    def transfer_vector_to(self, recipient_wallet, vec, allow_debt=True):
        """Überträgt eine konkrete Q-Signatur. Bei Mangel entsteht Typenschuld."""
        transferred = {}
        for q, qty in vec.items():
            q = int(q)
            qty = float(qty)
            if qty <= EPS:
                continue
            have = self.positive_qty(q)
            take = min(have, qty)
            if take > EPS:
                self.add_coin(q, -take)
                recipient_wallet.add_coin(q, take)
                transferred[q] = transferred.get(q, 0.0) + take
            missing = qty - take
            if missing > EPS and allow_debt:
                # Zahler bucht negative Q-Schuld, Empfänger bekommt Forderung in derselben Münze.
                self.add_coin(q, -missing)
                recipient_wallet.add_coin(q, missing)
                transferred[q] = transferred.get(q, 0.0) + missing
        return transferred

    def semantic_solvenz(self, required_q):
        """Deckungsgrad für eine Typenschuld an Q required_q.

        Positive Bestände ähnlicher Münzen werden mit Haircut angerechnet.
        """
        required_q = int(required_q)
        needed = self.debt_qty(required_q) * Q_VALUES[required_q]
        if needed <= EPS:
            return 1.0
        coverage = 0.0
        for q, qty in self.asset_vector().items():
            factor = SUBSTITUTION[required_q].get(q, 0.0)
            coverage += qty * Q_VALUES[q] * factor
        return coverage / needed

    def repay_own_debt(self, q, max_value=None):
        """Verwendet positive ähnliche Münzen, um negative Position Qq zu reduzieren.

        Diese interne Tilgung modelliert Coin-Markt/Umwandlung mit Haircuts. Sie
        ist konservativ: Es verschwindet positiver Wert, bis die Schuld teilweise
        gedeckt ist. Rückgabe ist getilgter Schuldwert.
        """
        q = int(q)
        debt_value = self.debt_qty(q) * Q_VALUES[q]
        if debt_value <= EPS:
            return 0.0
        if max_value is not None:
            debt_value = min(debt_value, float(max_value))
        remaining = debt_value
        # Ähnliche Münzen zuerst, dann hoher Wert.
        candidates = []
        for cq, factor in SUBSTITUTION[q].items():
            if factor > 0 and self.positive_qty(cq) > EPS:
                candidates.append((cq, factor))
        candidates.sort(key=lambda x: (-x[1], -Q_VALUES[x[0]]))
        paid_debt_value = 0.0
        for cq, factor in candidates:
            if remaining <= EPS:
                break
            avail_qty = self.positive_qty(cq)
            avail_value_as_q = avail_qty * Q_VALUES[cq] * factor
            use_as_q = min(avail_value_as_q, remaining)
            qty_to_burn = use_as_q / (Q_VALUES[cq] * factor)
            self.add_coin(cq, -qty_to_burn)
            debt_qty_reduction = use_as_q / Q_VALUES[q]
            self.add_coin(q, debt_qty_reduction)
            remaining -= use_as_q
            paid_debt_value += use_as_q
        return paid_debt_value

    def clean_small(self):
        for q in range(1, 21):
            if abs(self.balances[q]) < EPS:
                self.balances[q] = 0.0

    def __repr__(self):
        return "Wallet(%s)" % self.as_dict()


class Mint(object):
    """Münzamt: prägt geprüfte Q-Münzen und beobachtet Geldmenge."""

    def __init__(self):
        self.minted_by_q = dict((q, 0.0) for q in range(1, 21))
        self.burned_by_q = dict((q, 0.0) for q in range(1, 21))
        self.rejected_value = 0.0
        self.validation_strictness = 1.0

    def mint_vector(self, agent_wallet, vec, quality=1.0):
        """Prägt Münzen abhängig von Qualität und Strenge."""
        quality = clamp(float(quality), 0.0, 1.5)
        factor = clamp(quality / max(EPS, self.validation_strictness), 0.0, 1.2)
        minted = {}
        for q, qty in vec.items():
            q = int(q)
            mq = max(0.0, float(qty) * factor)
            if mq <= EPS:
                continue
            agent_wallet.add_coin(q, mq)
            self.minted_by_q[q] += mq
            minted[q] = mq
        rejected = max(0.0, vector_value(vec) - vector_value(minted))
        self.rejected_value += rejected
        return minted

    def burn_vector(self, agent_wallet, vec):
        burned = {}
        for q, qty in vec.items():
            q = int(q)
            qty = min(float(qty), agent_wallet.positive_qty(q))
            if qty <= EPS:
                continue
            agent_wallet.add_coin(q, -qty)
            self.burned_by_q[q] += qty
            burned[q] = qty
        return burned

    def money_supply_report(self, agents):
        positive = dict((q, 0.0) for q in range(1, 21))
        debt = dict((q, 0.0) for q in range(1, 21))
        for a in agents:
            for q, qty in a.wallet.balances.items():
                if qty > EPS:
                    positive[q] += qty
                elif qty < -EPS:
                    debt[q] += -qty
        return {"positive_qty": positive, "debt_qty": debt}
