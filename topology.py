from __future__ import annotations

from itertools import combinations
from typing import Iterable, Hashable, FrozenSet, Set


Element = Hashable
Menge = FrozenSet[Element]


class Topologie:
    """
    Modell einer endlichen Topologie auf einer Grundmenge X.

    Eine Topologie T auf X ist eine Menge offener Teilmengen von X mit:
    1. ∅ in T
    2. X in T
    3. beliebige Vereinigungen aus T liegen wieder in T
    4. endliche Schnitte aus T liegen wieder in T

    Diese Klasse ist auf endliche Grundmengen ausgelegt.
    """

    def __init__(
        self,
        grundmenge: Iterable[Element],
        offene_mengen: Iterable[Iterable[Element]] | None = None,
        *,
        validieren: bool = True,
    ) -> None:
        self._grundmenge: Menge = frozenset(grundmenge)
        self._offene_mengen: Set[Menge] = set()

        if offene_mengen is None:
            self._offene_mengen = {
                frozenset(),
                self._grundmenge,
            }
        else:
            self._offene_mengen = {frozenset(m) for m in offene_mengen}

        if validieren:
            self._validiere_und_normalisiere()

    def __repr__(self) -> str:
        offene_sortiert = sorted(
            (self._sortierte_darstellung(m) for m in self._offene_mengen),
            key=lambda x: (len(x), x),
        )
        return (
            f"Topologie(grundmenge={self._sortierte_darstellung(self._grundmenge)}, "
            f"offene_mengen={offene_sortiert})"
        )

    @staticmethod
    def _sortierte_darstellung(menge: Menge) -> list:
        return sorted(menge, key=repr)

    def _validiere_und_normalisiere(self) -> None:
        for o in self._offene_mengen:
            if not o.issubset(self._grundmenge):
                diff = o - self._grundmenge
                raise ValueError(
                    f"Offene Menge {o} enthält Elemente außerhalb der Grundmenge: {diff}"
                )

        if frozenset() not in self._offene_mengen:
            raise ValueError("∅ muss offen sein.")

        if self._grundmenge not in self._offene_mengen:
            raise ValueError("Die Grundmenge X muss offen sein.")

        offene_liste = list(self._offene_mengen)

        for a in offene_liste:
            for b in offene_liste:
                schnitt = a & b
                if schnitt not in self._offene_mengen:
                    raise ValueError(
                        f"Nicht abgeschlossen unter endlichen Schnitten: {a} ∩ {b} = {schnitt} ist nicht offen."
                    )

        # Für endliche Topologien genügt Abschluss unter allen Vereinigungen der vorhandenen offenen Mengen.
        for familie in self._potenzmenge(offene_liste):
            vereinigung = frozenset().union(*familie) if familie else frozenset()
            if vereinigung not in self._offene_mengen:
                raise ValueError(
                    f"Nicht abgeschlossen unter Vereinigungen: {vereinigung} ist nicht offen."
                )

    @staticmethod
    def _potenzmenge(iterable: list[Menge]) -> Iterable[tuple[Menge, ...]]:
        n = len(iterable)
        for r in range(n + 1):
            yield from combinations(iterable, r)

    @property
    def grundmenge(self) -> Menge:
        return self._grundmenge

    @property
    def offene_mengen(self) -> FrozenSet[Menge]:
        return frozenset(self._offene_mengen)

    def ist_offen(self, menge: Iterable[Element]) -> bool:
        return frozenset(menge) in self._offene_mengen

    def ist_abgeschlossen(self, menge: Iterable[Element]) -> bool:
        m = frozenset(menge)
        return (self._grundmenge - m) in self._offene_mengen

    def add_offene_menge(self, menge: Iterable[Element], *, automatisch_erweitern: bool = False) -> None:
        """
        Fügt eine offene Menge hinzu.

        automatisch_erweitern=False:
            prüft streng, ob die resultierende Struktur noch eine Topologie ist.

        automatisch_erweitern=True:
            erzeugt die kleinste Topologie, die die neue Menge zusätzlich enthält.
        """
        m = frozenset(menge)
        if not m.issubset(self._grundmenge):
            raise ValueError("Die neue Menge ist keine Teilmenge der Grundmenge.")

        if automatisch_erweitern:
            self._erzeuge_kleinste_topologie_mit(m)
        else:
            alte = set(self._offene_mengen)
            self._offene_mengen.add(m)
            try:
                self._validiere_und_normalisiere()
            except Exception:
                self._offene_mengen = alte
                raise

    def remove_offene_menge(self, menge: Iterable[Element]) -> None:
        """
        Entfernt eine offene Menge, sofern die verbleibende Struktur noch eine Topologie ist.
        ∅ und X dürfen nicht entfernt werden.
        """
        m = frozenset(menge)
        if m == frozenset() or m == self._grundmenge:
            raise ValueError("∅ und X dürfen nicht entfernt werden.")

        if m not in self._offene_mengen:
            return

        alte = set(self._offene_mengen)
        self._offene_mengen.remove(m)
        try:
            self._validiere_und_normalisiere()
        except Exception:
            self._offene_mengen = alte
            raise

    def _erzeuge_kleinste_topologie_mit(self, menge: Menge) -> None:
        """
        Erzeugt die kleinste Topologie, die die bisherigen offenen Mengen und 'menge' enthält.
        Für endliche Grundmengen per Abschluss unter endlichen Schnitten und Vereinigungen.
        """
        offene = set(self._offene_mengen)
        offene.add(menge)
        offene.add(frozenset())
        offene.add(self._grundmenge)

        changed = True
        while changed:
            changed = False
            aktuelle = list(offene)

            # Endliche Schnitte: bei endlicher Menge iterativ paarweise ausreichend
            for a in aktuelle:
                for b in aktuelle:
                    s = a & b
                    if s not in offene:
                        offene.add(s)
                        changed = True

            # Vereinigungen
            aktuelle = list(offene)
            for a in aktuelle:
                for b in aktuelle:
                    v = a | b
                    if v not in offene:
                        offene.add(v)
                        changed = True

        self._offene_mengen = offene
        self._validiere_und_normalisiere()

    def inneres(self, menge: Iterable[Element]) -> Menge:
        """
        Größte offene Teilmenge von menge.
        """
        m = frozenset(menge)
        kandidaten = [o for o in self._offene_mengen if o.issubset(m)]
        return frozenset().union(*kandidaten) if kandidaten else frozenset()

    def abschluss(self, menge: Iterable[Element]) -> Menge:
        """
        Kleinste abgeschlossene Obermenge von menge.
        closure(A) = X \ interior(X \ A)
        """
        m = frozenset(menge)
        return self._grundmenge - self.inneres(self._grundmenge - m)

    def rand(self, menge: Iterable[Element]) -> Menge:
        """
        Rand(A) = closure(A) \ interior(A)
        """
        m = frozenset(menge)
        return self.abschluss(m) - self.inneres(m)

    def aeusseres(self, menge: Iterable[Element]) -> Menge:
        """
        Äußeres(A) = interior(X \ A)
        """
        m = frozenset(menge)
        return self.inneres(self._grundmenge - m)

    def umgebungen(self, punkt: Element) -> FrozenSet[Menge]:
        """
        Alle offenen Mengen, die den Punkt enthalten.
        """
        if punkt not in self._grundmenge:
            raise ValueError(f"{punkt!r} liegt nicht in der Grundmenge.")
        return frozenset(o for o in self._offene_mengen if punkt in o)

    def ist_umgebung(self, punkt: Element, menge: Iterable[Element]) -> bool:
        """
        'menge' ist Umgebung von punkt, wenn es eine offene Menge O gibt mit punkt in O ⊆ menge.
        """
        m = frozenset(menge)
        if punkt not in self._grundmenge:
            raise ValueError(f"{punkt!r} liegt nicht in der Grundmenge.")
        if not m.issubset(self._grundmenge):
            raise ValueError("Die geprüfte Menge liegt nicht in der Grundmenge.")

        for o in self._offene_mengen:
            if punkt in o and o.issubset(m):
                return True
        return False

    def ist_diskret(self) -> bool:
        return self._offene_mengen == set(self._alle_teilmengen(self._grundmenge))

    def ist_indiskret(self) -> bool:
        return self._offene_mengen == {frozenset(), self._grundmenge}

    @staticmethod
    def _alle_teilmengen(menge: Menge) -> Iterable[Menge]:
        liste = list(menge)
        for r in range(len(liste) + 1):
            for teil in combinations(liste, r):
                yield frozenset(teil)

    @classmethod
    def diskrete_topologie(cls, grundmenge: Iterable[Element]) -> "Topologie":
        g = frozenset(grundmenge)
        return cls(g, cls._alle_teilmengen(g), validieren=True)

    @classmethod
    def indiskrete_topologie(cls, grundmenge: Iterable[Element]) -> "Topologie":
        g = frozenset(grundmenge)
        return cls(g, [frozenset(), g], validieren=True)

    @classmethod
    def aus_basis(
        cls,
        grundmenge: Iterable[Element],
        basis: Iterable[Iterable[Element]],
    ) -> "Topologie":
        """
        Erzeugt die von einer Basis erzeugte Topologie.
        Für endliche Grundmengen genügt iterativer Abschluss unter Vereinigungen
        der durch Schnitte erzeugten Basismengen.
        """
        g = frozenset(grundmenge)
        basis_mengen = {frozenset(b) for b in basis}

        for b in basis_mengen:
            if not b.issubset(g):
                raise ValueError(f"Basismenge {b} ist keine Teilmenge der Grundmenge.")

        # Basiseigenschaft 1: jedes x in X liegt in mindestens einer Basismenge
        for x in g:
            if not any(x in b for b in basis_mengen):
                raise ValueError(f"Für {x!r} gibt es keine Basismenge, die x enthält.")

        # Basiseigenschaft 2: bei x in B1 ∩ B2 gibt es B3 mit x in B3 ⊆ B1 ∩ B2
        for b1 in basis_mengen:
            for b2 in basis_mengen:
                schnitt = b1 & b2
                for x in schnitt:
                    if not any(x in b3 and b3.issubset(schnitt) for b3 in basis_mengen):
                        raise ValueError(
                            f"Basiseigenschaft verletzt bei {b1} und {b2} für Punkt {x!r}."
                        )

        offene = {frozenset(), g}
        basis_liste = list(basis_mengen)

        for familie in cls._potenzmenge(basis_liste):
            vereinigung = frozenset().union(*familie) if familie else frozenset()
            offene.add(vereinigung)

        return cls(g, offene, validieren=True)
