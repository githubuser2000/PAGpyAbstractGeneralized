from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple, Union


# =============================================================================
# Fehler
# =============================================================================

class CategoryError(Exception):
    pass


class ObjectAlreadyExists(CategoryError):
    pass


class ObjectNotFound(CategoryError):
    pass


class MorphismAlreadyExists(CategoryError):
    pass


class MorphismNotFound(CategoryError):
    pass


class CompositionError(CategoryError):
    pass


class IdentityError(CategoryError):
    pass


class DomainCompatibilityError(CategoryError):
    pass


# =============================================================================
# Domänen-Arten
# =============================================================================

class DomainKind(Enum):
    GENERIC = auto()
    TOPOLOGY = auto()
    NETWORK = auto()
    CLASS = auto()
    FUNCTION = auto()
    STRUCT = auto()


class MorphismKind(Enum):
    GENERIC = auto()

    # Topologie
    CONTINUOUS_MAP = auto()
    OPEN_MAP = auto()
    CLOSED_MAP = auto()
    HOMEOMORPHISM = auto()

    # Netzwerk
    NETWORK_HOMOMORPHISM = auto()
    GRAPH_EMBEDDING = auto()
    FLOW_TRANSFORMATION = auto()
    PROTOCOL_MAP = auto()

    # Klasse
    CLASS_INHERITANCE = auto()
    CLASS_INSTANCE_MAP = auto()
    CLASS_EMBEDDING = auto()
    CLASS_PROJECTION = auto()

    # Funktion
    FUNCTION_MAP = auto()
    FUNCTION_COMPOSITION = auto()
    EVALUATION = auto()
    CURRYING = auto()

    # Struct
    STRUCT_PROJECTION = auto()
    STRUCT_EMBEDDING = auto()
    STRUCT_ISOMORPHISM = auto()
    FIELD_RENAMING = auto()

    # gemischt / allgemein
    INTERPRETATION = auto()
    REALIZATION = auto()
    ABSTRACTION = auto()
    TRANSLATION = auto()


# =============================================================================
# Domänen-Payloads
# =============================================================================

@dataclass(frozen=True)
class TopologyData:
    """
    Endliche symbolische Topologie.
    carrier: Grundmenge
    opens: Menge offener Mengen
    """
    carrier: FrozenSet[Any]
    opens: FrozenSet[FrozenSet[Any]]

    def is_valid(self) -> bool:
        # sehr einfache Prüfung für endliche Topologien
        if frozenset() not in self.opens:
            return False
        if self.carrier not in self.opens:
            return False

        # endliche Schnitte
        opens_list = list(self.opens)
        for a in opens_list:
            for b in opens_list:
                if a.intersection(b) not in self.opens:
                    return False

        # endliche Vereinigungen
        for a in opens_list:
            for b in opens_list:
                if a.union(b) not in self.opens:
                    return False

        return True


@dataclass(frozen=True)
class NetworkData:
    """
    Allgemeines Netzwerk / Graph.
    nodes: Knoten
    edges: Kanten als Tupel (u, v)
    directed: gerichtet oder ungerichtet
    protocols: optionale Protokollnamen
    """
    nodes: FrozenSet[Any]
    edges: FrozenSet[Tuple[Any, Any]]
    directed: bool = True
    protocols: FrozenSet[str] = field(default_factory=frozenset)

    def is_valid(self) -> bool:
        for u, v in self.edges:
            if u not in self.nodes or v not in self.nodes:
                return False
        return True


@dataclass(frozen=True)
class ClassData:
    """
    Symbolische Klassenbeschreibung.
    """
    name: str
    fields: FrozenSet[str] = field(default_factory=frozenset)
    methods: FrozenSet[str] = field(default_factory=frozenset)
    base_classes: FrozenSet[str] = field(default_factory=frozenset)
    metadata: Tuple[Tuple[str, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FunctionData:
    """
    Symbolische Beschreibung eines Funktionsobjekts oder Funktionsraums.
    """
    name: str
    domain_name: str
    codomain_name: str
    arity: int = 1
    pure: bool = True
    metadata: Tuple[Tuple[str, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StructData:
    """
    Struct / Record-Typ.
    fields: Feldname -> Typname (symbolisch)
    """
    name: str
    fields: Tuple[Tuple[str, str], ...]
    packed: bool = False
    metadata: Tuple[Tuple[str, Any], ...] = field(default_factory=tuple)

    def field_names(self) -> Set[str]:
        return {name for name, _ in self.fields}


# =============================================================================
# Kategorielle Grundtypen
# =============================================================================

@dataclass(frozen=True, eq=True)
class CatObject:
    name: str
    kind: DomainKind = DomainKind.GENERIC
    payload: Any = None
    tags: FrozenSet[str] = field(default_factory=frozenset)

    def __str__(self) -> str:
        return f"{self.name}<{self.kind.name}>"


@dataclass
class Morphism:
    name: str
    source: CatObject
    target: CatObject
    kind: MorphismKind = MorphismKind.GENERIC
    fn: Optional[Callable[[Any], Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __call__(self, x: Any) -> Any:
        if self.fn is None:
            raise TypeError(f"Morphismus {self.name!r} ist symbolisch und nicht ausführbar.")
        return self.fn(x)

    def is_symbolic(self) -> bool:
        return self.fn is None

    def __str__(self) -> str:
        return (
            f"{self.name}: {self.source.name}<{self.source.kind.name}>"
            f" -> {self.target.name}<{self.target.kind.name}>"
            f" [{self.kind.name}]"
        )


# =============================================================================
# Die erweiterte allgemeine Kategorie
# =============================================================================

class MathematicalCategory:
    def __init__(
        self,
        name: str,
        *,
        auto_register_identities: bool = True,
        auto_register_composites: bool = True,
    ) -> None:
        self.name = name
        self.auto_register_identities = auto_register_identities
        self.auto_register_composites = auto_register_composites

        self.objects: Dict[str, CatObject] = {}
        self.morphisms: Dict[str, Morphism] = {}
        self._identities: Dict[str, str] = {}
        self._composition_cache: Dict[Tuple[str, str], str] = {}

    # -------------------------------------------------------------------------
    # Objektverwaltung
    # -------------------------------------------------------------------------

    def add_object(
        self,
        name: str,
        *,
        kind: DomainKind = DomainKind.GENERIC,
        payload: Any = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        if name in self.objects:
            raise ObjectAlreadyExists(f"Objekt {name!r} existiert bereits.")
        obj = CatObject(
            name=name,
            kind=kind,
            payload=payload,
            tags=frozenset(tags or ()),
        )
        self._validate_object_payload(obj)
        self.objects[name] = obj
        if self.auto_register_identities:
            self._create_identity_for_object(obj)
        return obj

    def get_object(self, name: str) -> CatObject:
        if name not in self.objects:
            raise ObjectNotFound(f"Objekt {name!r} existiert nicht.")
        return self.objects[name]

    def ensure_object(
        self,
        name: str,
        *,
        kind: DomainKind = DomainKind.GENERIC,
        payload: Any = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        if name in self.objects:
            return self.objects[name]
        return self.add_object(name, kind=kind, payload=payload, tags=tags)

    # -------------------------------------------------------------------------
    # Objekt-Validierung
    # -------------------------------------------------------------------------

    def _validate_object_payload(self, obj: CatObject) -> None:
        if obj.kind == DomainKind.TOPOLOGY:
            if not isinstance(obj.payload, TopologyData):
                raise DomainCompatibilityError(
                    f"Objekt {obj.name!r} vom Typ TOPOLOGY braucht TopologyData."
                )
            if not obj.payload.is_valid():
                raise DomainCompatibilityError(
                    f"Topologie-Payload von {obj.name!r} ist ungültig."
                )

        elif obj.kind == DomainKind.NETWORK:
            if not isinstance(obj.payload, NetworkData):
                raise DomainCompatibilityError(
                    f"Objekt {obj.name!r} vom Typ NETWORK braucht NetworkData."
                )
            if not obj.payload.is_valid():
                raise DomainCompatibilityError(
                    f"Netzwerk-Payload von {obj.name!r} ist ungültig."
                )

        elif obj.kind == DomainKind.CLASS:
            if not isinstance(obj.payload, ClassData):
                raise DomainCompatibilityError(
                    f"Objekt {obj.name!r} vom Typ CLASS braucht ClassData."
                )

        elif obj.kind == DomainKind.FUNCTION:
            if not isinstance(obj.payload, FunctionData):
                raise DomainCompatibilityError(
                    f"Objekt {obj.name!r} vom Typ FUNCTION braucht FunctionData."
                )

        elif obj.kind == DomainKind.STRUCT:
            if not isinstance(obj.payload, StructData):
                raise DomainCompatibilityError(
                    f"Objekt {obj.name!r} vom Typ STRUCT braucht StructData."
                )

    # -------------------------------------------------------------------------
    # Morphismusverwaltung
    # -------------------------------------------------------------------------

    def add_morphism(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        *,
        kind: MorphismKind = MorphismKind.GENERIC,
        fn: Optional[Callable[[Any], Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> Morphism:
        src = self.get_object(source) if isinstance(source, str) else source
        tgt = self.get_object(target) if isinstance(target, str) else target

        if name in self.morphisms and not overwrite:
            raise MorphismAlreadyExists(f"Morphismus {name!r} existiert bereits.")

        morph = Morphism(
            name=name,
            source=src,
            target=tgt,
            kind=kind,
            fn=fn,
            metadata=dict(metadata or {}),
        )

        self._validate_morphism_kind_compatibility(morph)

        self.morphisms[name] = morph
        self._composition_cache.clear()
        return morph

    def get_morphism(self, name: str) -> Morphism:
        if name not in self.morphisms:
            raise MorphismNotFound(f"Morphismus {name!r} existiert nicht.")
        return self.morphisms[name]

    def hom(self, source: Union[str, CatObject], target: Union[str, CatObject]) -> List[Morphism]:
        src = self.get_object(source) if isinstance(source, str) else source
        tgt = self.get_object(target) if isinstance(target, str) else target
        return [m for m in self.morphisms.values() if m.source == src and m.target == tgt]

    # -------------------------------------------------------------------------
    # Typ-Verträglichkeit für Morphismen
    # -------------------------------------------------------------------------

    def _validate_morphism_kind_compatibility(self, morph: Morphism) -> None:
        s = morph.source.kind
        t = morph.target.kind
        k = morph.kind

        # allgemein immer erlaubt
        if k == MorphismKind.GENERIC:
            return

        # Topologie
        if k in {
            MorphismKind.CONTINUOUS_MAP,
            MorphismKind.OPEN_MAP,
            MorphismKind.CLOSED_MAP,
            MorphismKind.HOMEOMORPHISM,
        }:
            if s != DomainKind.TOPOLOGY or t != DomainKind.TOPOLOGY:
                raise DomainCompatibilityError(
                    f"{k.name} verlangt TOPOLOGY -> TOPOLOGY, nicht {s.name} -> {t.name}."
                )

        # Netzwerk
        elif k in {
            MorphismKind.NETWORK_HOMOMORPHISM,
            MorphismKind.GRAPH_EMBEDDING,
            MorphismKind.FLOW_TRANSFORMATION,
            MorphismKind.PROTOCOL_MAP,
        }:
            if s != DomainKind.NETWORK or t != DomainKind.NETWORK:
                raise DomainCompatibilityError(
                    f"{k.name} verlangt NETWORK -> NETWORK, nicht {s.name} -> {t.name}."
                )

        # Klasse
        elif k in {
            MorphismKind.CLASS_INHERITANCE,
            MorphismKind.CLASS_INSTANCE_MAP,
            MorphismKind.CLASS_EMBEDDING,
            MorphismKind.CLASS_PROJECTION,
        }:
            if s != DomainKind.CLASS or t != DomainKind.CLASS:
                raise DomainCompatibilityError(
                    f"{k.name} verlangt CLASS -> CLASS, nicht {s.name} -> {t.name}."
                )

        # Funktion
        elif k in {
            MorphismKind.FUNCTION_MAP,
            MorphismKind.FUNCTION_COMPOSITION,
            MorphismKind.EVALUATION,
            MorphismKind.CURRYING,
        }:
            if s != DomainKind.FUNCTION or t != DomainKind.FUNCTION:
                raise DomainCompatibilityError(
                    f"{k.name} verlangt FUNCTION -> FUNCTION, nicht {s.name} -> {t.name}."
                )

        # Struct
        elif k in {
            MorphismKind.STRUCT_PROJECTION,
            MorphismKind.STRUCT_EMBEDDING,
            MorphismKind.STRUCT_ISOMORPHISM,
            MorphismKind.FIELD_RENAMING,
        }:
            if s != DomainKind.STRUCT or t != DomainKind.STRUCT:
                raise DomainCompatibilityError(
                    f"{k.name} verlangt STRUCT -> STRUCT, nicht {s.name} -> {t.name}."
                )

        # gemischte
        elif k in {
            MorphismKind.INTERPRETATION,
            MorphismKind.REALIZATION,
            MorphismKind.ABSTRACTION,
            MorphismKind.TRANSLATION,
        }:
            return

        self._validate_payload_level_constraints(morph)

    def _validate_payload_level_constraints(self, morph: Morphism) -> None:
        k = morph.kind

        # Homeomorphismus: topologisch, hier nur symbolisch schwach geprüft
        if k == MorphismKind.HOMEOMORPHISM:
            if morph.source.kind != DomainKind.TOPOLOGY or morph.target.kind != DomainKind.TOPOLOGY:
                raise DomainCompatibilityError("HOMEOMORPHISM braucht Topologien.")

        # Class inheritance: Felder/Methoden der Oberklasse sollten Teilmenge sein
        elif k == MorphismKind.CLASS_INHERITANCE:
            src = morph.source.payload
            tgt = morph.target.payload
            if isinstance(src, ClassData) and isinstance(tgt, ClassData):
                # src -> tgt lesen wir hier als "src erbt/ist eingebettet in tgt"
                if not tgt.fields.issubset(src.fields):
                    raise DomainCompatibilityError(
                        f"CLASS_INHERITANCE verletzt Feldstruktur: "
                        f"{tgt.name}.fields ist nicht Teilmenge von {src.name}.fields"
                    )
                if not tgt.methods.issubset(src.methods):
                    raise DomainCompatibilityError(
                        f"CLASS_INHERITANCE verletzt Methodenstruktur: "
                        f"{tgt.name}.methods ist nicht Teilmenge von {src.name}.methods"
                    )

        # Struct projection: Ziel-Felder müssen Teilmenge der Quell-Felder sein
        elif k == MorphismKind.STRUCT_PROJECTION:
            src = morph.source.payload
            tgt = morph.target.payload
            if isinstance(src, StructData) and isinstance(tgt, StructData):
                src_fields = src.field_names()
                tgt_fields = tgt.field_names()
                if not tgt_fields.issubset(src_fields):
                    raise DomainCompatibilityError(
                        f"STRUCT_PROJECTION {morph.name!r}: Ziel-Felder {tgt_fields} "
                        f"sind keine Teilmenge von Quell-Feldern {src_fields}."
                    )

        # Struct isomorphism: gleiche Feldnamenmenge
        elif k == MorphismKind.STRUCT_ISOMORPHISM:
            src = morph.source.payload
            tgt = morph.target.payload
            if isinstance(src, StructData) and isinstance(tgt, StructData):
                if src.field_names() != tgt.field_names():
                    raise DomainCompatibilityError(
                        f"STRUCT_ISOMORPHISM {morph.name!r}: Feldmengen stimmen nicht überein."
                    )

        # Network homomorphism: symbolisch erstmal nur Netzwerke; tiefer nur mit Metadata/Funktion
        elif k == MorphismKind.NETWORK_HOMOMORPHISM:
            pass

        # Continuous map: symbolisch erstmal nur Topologien; echte Stetigkeit nur mit Testfunktion
        elif k == MorphismKind.CONTINUOUS_MAP:
            pass

    # -------------------------------------------------------------------------
    # Bequeme Objektkonstruktoren
    # -------------------------------------------------------------------------

    def add_topology(
        self,
        name: str,
        *,
        carrier: Iterable[Any],
        opens: Iterable[Iterable[Any]],
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        payload = TopologyData(
            carrier=frozenset(carrier),
            opens=frozenset(frozenset(o) for o in opens),
        )
        return self.add_object(name, kind=DomainKind.TOPOLOGY, payload=payload, tags=tags)

    def add_network(
        self,
        name: str,
        *,
        nodes: Iterable[Any],
        edges: Iterable[Tuple[Any, Any]],
        directed: bool = True,
        protocols: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        payload = NetworkData(
            nodes=frozenset(nodes),
            edges=frozenset(edges),
            directed=directed,
            protocols=frozenset(protocols or ()),
        )
        return self.add_object(name, kind=DomainKind.NETWORK, payload=payload, tags=tags)

    def add_class_object(
        self,
        name: str,
        *,
        fields: Optional[Iterable[str]] = None,
        methods: Optional[Iterable[str]] = None,
        base_classes: Optional[Iterable[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        payload = ClassData(
            name=name,
            fields=frozenset(fields or ()),
            methods=frozenset(methods or ()),
            base_classes=frozenset(base_classes or ()),
            metadata=tuple(sorted((metadata or {}).items())),
        )
        return self.add_object(name, kind=DomainKind.CLASS, payload=payload, tags=tags)

    def add_function_object(
        self,
        name: str,
        *,
        domain_name: str,
        codomain_name: str,
        arity: int = 1,
        pure: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        payload = FunctionData(
            name=name,
            domain_name=domain_name,
            codomain_name=codomain_name,
            arity=arity,
            pure=pure,
            metadata=tuple(sorted((metadata or {}).items())),
        )
        return self.add_object(name, kind=DomainKind.FUNCTION, payload=payload, tags=tags)

    def add_struct_object(
        self,
        name: str,
        *,
        fields: Dict[str, str],
        packed: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        payload = StructData(
            name=name,
            fields=tuple(sorted(fields.items())),
            packed=packed,
            metadata=tuple(sorted((metadata or {}).items())),
        )
        return self.add_object(name, kind=DomainKind.STRUCT, payload=payload, tags=tags)

    # -------------------------------------------------------------------------
    # Identitäten
    # -------------------------------------------------------------------------

    def _create_identity_for_object(self, obj: CatObject) -> Morphism:
        name = f"id_{obj.name}"
        if name in self.morphisms:
            existing = self.morphisms[name]
            if existing.source != obj or existing.target != obj:
                raise IdentityError(
                    f"Vorhandener Morphismus {name!r} kollidiert mit Identität."
                )
            self._identities[obj.name] = name
            return existing

        kind = MorphismKind.GENERIC
        if obj.kind == DomainKind.TOPOLOGY:
            kind = MorphismKind.HOMEOMORPHISM
        elif obj.kind == DomainKind.NETWORK:
            kind = MorphismKind.NETWORK_HOMOMORPHISM
        elif obj.kind == DomainKind.CLASS:
            kind = MorphismKind.CLASS_EMBEDDING
        elif obj.kind == DomainKind.FUNCTION:
            kind = MorphismKind.FUNCTION_MAP
        elif obj.kind == DomainKind.STRUCT:
            kind = MorphismKind.STRUCT_ISOMORPHISM

        morph = Morphism(
            name=name,
            source=obj,
            target=obj,
            kind=kind,
            fn=lambda x: x,
            metadata={"identity": True},
        )
        self.morphisms[name] = morph
        self._identities[obj.name] = name
        return morph

    def identity(self, obj: Union[str, CatObject]) -> Morphism:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        if o.name not in self._identities:
            return self._create_identity_for_object(o)
        return self.get_morphism(self._identities[o.name])

    # -------------------------------------------------------------------------
    # Komposition
    # -------------------------------------------------------------------------

    def can_compose(self, g: Union[str, Morphism], f: Union[str, Morphism]) -> bool:
        gm = self.get_morphism(g) if isinstance(g, str) else g
        fm = self.get_morphism(f) if isinstance(f, str) else f
        return fm.target == gm.source

    def compose(
        self,
        g: Union[str, Morphism],
        f: Union[str, Morphism],
        *,
        name: Optional[str] = None,
        register: Optional[bool] = None,
    ) -> Morphism:
        gm = self.get_morphism(g) if isinstance(g, str) else g
        fm = self.get_morphism(f) if isinstance(f, str) else f

        if fm.target != gm.source:
            raise CompositionError(
                f"Nicht komponierbar: {fm.name}: {fm.source.name}->{fm.target.name}, "
                f"{gm.name}: {gm.source.name}->{gm.target.name}"
            )

        key = (gm.name, fm.name)
        if key in self._composition_cache:
            return self.get_morphism(self._composition_cache[key])

        result_kind = self._compose_morphism_kinds(gm, fm)

        composed_fn: Optional[Callable[[Any], Any]]
        if gm.fn is not None and fm.fn is not None:
            composed_fn = lambda x, _g=gm.fn, _f=fm.fn: _g(_f(x))
        else:
            composed_fn = None

        result_name = name or f"{gm.name}_o_{fm.name}"
        result = Morphism(
            name=result_name,
            source=fm.source,
            target=gm.target,
            kind=result_kind,
            fn=composed_fn,
            metadata={"composite_of": (gm.name, fm.name)},
        )

        self._validate_morphism_kind_compatibility(result)

        do_register = self.auto_register_composites if register is None else register
        if do_register:
            if result_name in self.morphisms:
                existing = self.morphisms[result_name]
                if existing.source != result.source or existing.target != result.target:
                    raise CompositionError(
                        f"Kompositionsname {result_name!r} existiert mit anderer Signatur."
                    )
                result = existing
            else:
                self.morphisms[result_name] = result
            self._composition_cache[key] = result.name

        return result

    def _compose_morphism_kinds(self, g: Morphism, f: Morphism) -> MorphismKind:
        # gleiche Art bleibt möglichst erhalten
        if g.kind == f.kind:
            return g.kind

        # Identitätsähnliche generische Fälle
        if g.metadata.get("identity"):
            return f.kind
        if f.metadata.get("identity"):
            return g.kind

        # Domänengleiche allgemeine Schließung
        if g.source.kind == g.target.kind == f.source.kind == f.target.kind:
            domain = g.source.kind

            if domain == DomainKind.TOPOLOGY:
                # HOMEOMORPHISM ist spezieller als CONTINUOUS_MAP;
                # Mischung fällt konservativ auf CONTINUOUS_MAP zurück
                topo_kinds = {
                    MorphismKind.CONTINUOUS_MAP,
                    MorphismKind.OPEN_MAP,
                    MorphismKind.CLOSED_MAP,
                    MorphismKind.HOMEOMORPHISM,
                }
                if g.kind in topo_kinds and f.kind in topo_kinds:
                    if g.kind == MorphismKind.HOMEOMORPHISM and f.kind == MorphismKind.HOMEOMORPHISM:
                        return MorphismKind.HOMEOMORPHISM
                    return MorphismKind.CONTINUOUS_MAP

            elif domain == DomainKind.NETWORK:
                net_kinds = {
                    MorphismKind.NETWORK_HOMOMORPHISM,
                    MorphismKind.GRAPH_EMBEDDING,
                    MorphismKind.FLOW_TRANSFORMATION,
                    MorphismKind.PROTOCOL_MAP,
                }
                if g.kind in net_kinds and f.kind in net_kinds:
                    return MorphismKind.NETWORK_HOMOMORPHISM

            elif domain == DomainKind.CLASS:
                class_kinds = {
                    MorphismKind.CLASS_INHERITANCE,
                    MorphismKind.CLASS_INSTANCE_MAP,
                    MorphismKind.CLASS_EMBEDDING,
                    MorphismKind.CLASS_PROJECTION,
                }
                if g.kind in class_kinds and f.kind in class_kinds:
                    return MorphismKind.CLASS_EMBEDDING

            elif domain == DomainKind.FUNCTION:
                fn_kinds = {
                    MorphismKind.FUNCTION_MAP,
                    MorphismKind.FUNCTION_COMPOSITION,
                    MorphismKind.EVALUATION,
                    MorphismKind.CURRYING,
                }
                if g.kind in fn_kinds and f.kind in fn_kinds:
                    return MorphismKind.FUNCTION_COMPOSITION

            elif domain == DomainKind.STRUCT:
                struct_kinds = {
                    MorphismKind.STRUCT_PROJECTION,
                    MorphismKind.STRUCT_EMBEDDING,
                    MorphismKind.STRUCT_ISOMORPHISM,
                    MorphismKind.FIELD_RENAMING,
                }
                if g.kind in struct_kinds and f.kind in struct_kinds:
                    # Projektion nach Projektion bleibt Projektion-artig
                    if (
                        g.kind == MorphismKind.STRUCT_PROJECTION
                        or f.kind == MorphismKind.STRUCT_PROJECTION
                    ):
                        return MorphismKind.STRUCT_PROJECTION
                    return MorphismKind.STRUCT_EMBEDDING

        # gemischte Strukturübersetzungen
        mixed = {
            MorphismKind.INTERPRETATION,
            MorphismKind.REALIZATION,
            MorphismKind.ABSTRACTION,
            MorphismKind.TRANSLATION,
        }
        if g.kind in mixed or f.kind in mixed:
            return MorphismKind.TRANSLATION

        return MorphismKind.GENERIC

    # -------------------------------------------------------------------------
    # Bequeme Morphismus-Konstruktoren
    # -------------------------------------------------------------------------

    def add_continuous_map(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        *,
        fn: Optional[Callable[[Any], Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Morphism:
        return self.add_morphism(
            name,
            source,
            target,
            kind=MorphismKind.CONTINUOUS_MAP,
            fn=fn,
            metadata=metadata,
        )

    def add_network_homomorphism(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        *,
        fn: Optional[Callable[[Any], Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Morphism:
        return self.add_morphism(
            name,
            source,
            target,
            kind=MorphismKind.NETWORK_HOMOMORPHISM,
            fn=fn,
            metadata=metadata,
        )

    def add_class_inheritance(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Morphism:
        return self.add_morphism(
            name,
            source,
            target,
            kind=MorphismKind.CLASS_INHERITANCE,
            fn=None,
            metadata=metadata,
        )

    def add_function_map(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        *,
        fn: Optional[Callable[[Any], Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Morphism:
        return self.add_morphism(
            name,
            source,
            target,
            kind=MorphismKind.FUNCTION_MAP,
            fn=fn,
            metadata=metadata,
        )

    def add_struct_projection(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        *,
        fn: Optional[Callable[[Any], Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Morphism:
        return self.add_morphism(
            name,
            source,
            target,
            kind=MorphismKind.STRUCT_PROJECTION,
            fn=fn,
            metadata=metadata,
        )

    def add_translation(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        *,
        fn: Optional[Callable[[Any], Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Morphism:
        return self.add_morphism(
            name,
            source,
            target,
            kind=MorphismKind.TRANSLATION,
            fn=fn,
            metadata=metadata,
        )

    # -------------------------------------------------------------------------
    # Dekorator-API
    # -------------------------------------------------------------------------

    def Mor(
        self,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        name: Optional[str] = None,
        *,
        kind: MorphismKind = MorphismKind.GENERIC,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ):
        src = self.get_object(source) if isinstance(source, str) else source
        tgt = self.get_object(target) if isinstance(target, str) else target

        def decorator(fn: Callable[[Any], Any]) -> Morphism:
            morph_name = name or fn.__name__
            return self.add_morphism(
                morph_name,
                src,
                tgt,
                kind=kind,
                fn=fn,
                metadata=metadata,
                overwrite=overwrite,
            )
        return decorator

    # -------------------------------------------------------------------------
    # Analyse
    # -------------------------------------------------------------------------

    def objects_of_kind(self, kind: DomainKind) -> List[CatObject]:
        return [o for o in self.objects.values() if o.kind == kind]

    def morphisms_of_kind(self, kind: MorphismKind) -> List[Morphism]:
        return [m for m in self.morphisms.values() if m.kind == kind]

    def describe(self) -> str:
        lines = [
            f"Category({self.name})",
            f"  objects: {len(self.objects)}",
            f"  morphisms: {len(self.morphisms)}",
            "",
            "Objects:",
        ]
        for o in sorted(self.objects.values(), key=lambda x: x.name):
            lines.append(f"  - {o.name}: {o.kind.name}")

        lines.append("")
        lines.append("Morphisms:")
        for m in sorted(self.morphisms.values(), key=lambda x: x.name):
            symbolic = "symbolic" if m.is_symbolic() else "concrete"
            lines.append(
                f"  - {m.name}: {m.source.name}->{m.target.name} "
                f"[{m.kind.name}, {symbolic}]"
            )
        return "\n".join(lines)
