# -*- coding: utf-8 -*-
"""Hilfsfunktionen für die Q-Wirtschaftssimulation.

Dieses Modul verwendet nur die Python-Standardbibliothek und läuft dadurch auch
unter PyPy3. Es enthält bewusst keine I/O-lastigen oder externen Abhängigkeiten.
"""

from __future__ import print_function

import math
import random
import statistics
from collections import defaultdict

EPS = 1e-9


def clamp(x, lo, hi):
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def safe_div(a, b, default=0.0):
    if abs(b) <= EPS:
        return default
    return a / b


def weighted_choice(rng, items):
    """items: Liste von (objekt, gewicht)."""
    total = sum(max(0.0, w) for _, w in items)
    if total <= EPS:
        return items[0][0] if items else None
    r = rng.random() * total
    acc = 0.0
    for item, weight in items:
        acc += max(0.0, weight)
        if r <= acc:
            return item
    return items[-1][0]


def mean(values, default=0.0):
    values = list(values)
    if not values:
        return default
    return sum(values) / float(len(values))


def gini(values):
    """Gini-Koeffizient für nichtnegative und gemischte Vermögen.

    Negative Werte werden durch Verschiebung behandelt, weil in Simulationen
    Schuldner auftauchen können. Der Koeffizient bleibt damit interpretierbar
    als Konzentrationsmaß, nicht als exakte wohlfahrtstheoretische Aussage.
    """
    values = list(values)
    if not values:
        return 0.0
    mn = min(values)
    if mn < 0:
        values = [v - mn for v in values]
    total = sum(values)
    n = len(values)
    if total <= EPS or n <= 1:
        return 0.0
    values.sort()
    cum = 0.0
    for i, v in enumerate(values, start=1):
        cum += i * v
    return (2.0 * cum) / (n * total) - (n + 1.0) / n


def percentile(values, pct, default=0.0):
    values = sorted(values)
    if not values:
        return default
    if pct <= 0:
        return values[0]
    if pct >= 100:
        return values[-1]
    k = (len(values) - 1) * pct / 100.0
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return values[f]
    return values[f] * (c - k) + values[c] * (k - f)


def normalize_weights(weights):
    total = sum(max(0.0, v) for v in weights.values())
    if total <= EPS:
        if not weights:
            return {}
        equal = 1.0 / float(len(weights))
        return dict((k, equal) for k in weights)
    return dict((k, max(0.0, v) / total) for k, v in weights.items())


def add_dict(a, b, scale=1.0):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0.0) + v * scale
    return out


def multiply_dict(d, scale):
    return dict((k, v * scale) for k, v in d.items())


def stable_hash(s):
    """Ein stabiler kleiner Hash, unabhängig von PYTHONHASHSEED."""
    h = 2166136261
    for ch in str(s):
        h ^= ord(ch)
        h = (h * 16777619) & 0xffffffff
    return h


class IdGenerator(object):
    def __init__(self):
        self.next_id = 1

    def new(self, prefix):
        i = self.next_id
        self.next_id += 1
        return "%s%05d" % (prefix, i)


class EventLog(object):
    """Kleines Ereignisprotokoll für Berichte."""

    def __init__(self, max_items=1000):
        self.max_items = max_items
        self.items = []

    def add(self, period, kind, message, data=None):
        self.items.append({
            "period": int(period),
            "kind": str(kind),
            "message": str(message),
            "data": data or {},
        })
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items:]

    def recent(self, n=20):
        return self.items[-n:]


class RunningStat(object):
    """Online-Mittelwert/Varianz. Praktisch für lange Läufe."""

    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0

    def push(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.m2 += delta * delta2

    @property
    def variance(self):
        if self.n < 2:
            return 0.0
        return self.m2 / (self.n - 1)

    @property
    def stdev(self):
        return math.sqrt(self.variance)
