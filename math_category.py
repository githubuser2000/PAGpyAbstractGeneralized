from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Generic,
    Hashable,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)
import itertools
import uuid


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


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


class FunctorError(CategoryError):
    pass


class NaturalTransformationError(CategoryError):
    pass


class UniversalConstructionError(CategoryError):
    pass


@dataclass(frozen=True, eq=True)
class CatObject:
    """
    Ein Objekt einer Kategorie.

    payload:
        Optionales Python-Objekt oder Metadaten.
    """
    name: str
    payload: Any = None
    tags: FrozenSet[str] = field(default_factory=frozenset)

    def __str__(self) -> str:
        return self.name


@dataclass
class Morphism:
    """
    Ein Morphismus einer Kategorie.

    fn:
        Optionale konkrete Python-Funktion, die den Morphismus realisiert.
        Wenn None, ist der Morphismus symbolisch.

    metadata:
        Freie Zusatzinformationen.
    """
    name: str
    source: CatObject
    target: CatObject
    fn: Optional[Callable[[Any], Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __call__(self, x: Any) -> Any:
        if self.fn is None:
            raise TypeError(
                f"Morphismus {self.name!r} ist rein symbolisch und nicht ausführbar."
            )
        return self.fn(x)

    def is_symbolic(self) -> bool:
        return self.fn is None

    def signature(self) -> Tuple[str, str]:
        return (self.source.name, self.target.name)

    def __str__(self) -> str:
        return f"{self.name}: {self.source.name} -> {self.target.name}"


@dataclass
class DiagramPath:
    """
    Ein Pfad aus Morphismen in einem Diagramm.
    """
    morphisms: Tuple[Morphism, ...]

    @property
    def source(self) -> CatObject:
        if not self.morphisms:
            raise ValueError("Leerer Pfad hat keine Quelle.")
        return self.morphisms[0].source

    @property
    def target(self) -> CatObject:
        if not self.morphisms:
            raise ValueError("Leerer Pfad hat kein Ziel.")
        return self.morphisms[-1].target

    def names(self) -> List[str]:
        return [m.name for m in self.morphisms]

    def __str__(self) -> str:
        if not self.morphisms:
            return "<empty path>"
        return " ∘ ".join(m.name for m in reversed(self.morphisms))


@dataclass
class CommutativeConstraint:
    """
    Forderung, dass zwei Pfade denselben zusammengesetzten Morphismus ergeben sollen.
    """
    left: DiagramPath
    right: DiagramPath
    name: str = ""


@dataclass
class Functor:
    """
    Kovarianter Funktor F: C -> D.
    """
    name: str
    source_category: "MathematicalCategory"
    target_category: "MathematicalCategory"
    object_map: Dict[str, str] = field(default_factory=dict)
    morphism_map: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def map_object(self, obj: CatObject) -> CatObject:
        if obj.name not in self.object_map:
            raise FunctorError(
                f"Funktor {self.name!r} hat keine Objektabbildung für {obj.name!r}."
            )
        return self.target_category.get_object(self.object_map[obj.name])

    def map_morphism(self, morph: Morphism) -> Morphism:
        if morph.name not in self.morphism_map:
            raise FunctorError(
                f"Funktor {self.name!r} hat keine Morphismusabbildung für {morph.name!r}."
            )
        return self.target_category.get_morphism(self.morphism_map[morph.name])

    def validate(self) -> None:
        # Identitäten erhalten
        for obj in self.source_category.objects.values():
            src_id = self.source_category.identity(obj.name)
            mapped_obj = self.map_object(obj)
            mapped_id = self.target_category.identity(mapped_obj.name)
            mapped_src_id = self.map_morphism(src_id)
            if mapped_src_id.name != mapped_id.name:
                raise FunctorError(
                    f"Funktor {self.name!r} erhält Identität von {obj.name!r} nicht: "
                    f"F(id_{obj.name}) = {mapped_src_id.name}, erwartet {mapped_id.name}"
                )

        # Komposition erhalten
        for g in self.source_category.morphisms.values():
            for f in self.source_category.morphisms.values():
                if f.target == g.source:
                    comp = self.source_category.compose(g.name, f.name)
                    lhs = self.map_morphism(comp)
                    Fg = self.map_morphism(g)
                    Ff = self.map_morphism(f)
                    rhs = self.target_category.compose(Fg.name, Ff.name)
                    if lhs.name != rhs.name:
                        raise FunctorError(
                            f"Funktor {self.name!r} erhält Komposition nicht für "
                            f"{g.name} ∘ {f.name}: "
                            f"F(g∘f)={lhs.name}, aber F(g)∘F(f)={rhs.name}"
                        )


@dataclass
class NaturalTransformation:
    """
    Natürliche Transformation eta: F => G
    mit Komponenten eta_A: F(A) -> G(A)
    """
    name: str
    source_functor: Functor
    target_functor: Functor
    components: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def component(self, obj_name: str) -> Morphism:
        if obj_name not in self.components:
            raise NaturalTransformationError(
                f"Keine Komponente für Objekt {obj_name!r}."
            )
        cat = self.source_functor.target_category
        return cat.get_morphism(self.components[obj_name])

    def validate(self) -> None:
        F = self.source_functor
        G = self.target_functor

        if F.source_category is not G.source_category:
            raise NaturalTransformationError(
                "Quellfunktoren der natürlichen Transformation haben unterschiedliche Quellkategorien."
            )
        if F.target_category is not G.target_category:
            raise NaturalTransformationError(
                "Quellfunktoren der natürlichen Transformation haben unterschiedliche Zielkategorien."
            )

        C = F.source_category
        D = F.target_category

        # Komponenten müssen den richtigen Typ haben: eta_A: F(A) -> G(A)
        for obj in C.objects.values():
            eta_a = self.component(obj.name)
            expected_src = F.map_object(obj)
            expected_tgt = G.map_object(obj)
            if eta_a.source != expected_src or eta_a.target != expected_tgt:
                raise NaturalTransformationError(
                    f"Komponente {eta_a.name!r} hat falschen Typ. "
                    f"Erwartet {expected_src.name}->{expected_tgt.name}, "
                    f"erhalten {eta_a.source.name}->{eta_a.target.name}"
                )

        # Natürlichkeitsquadrat: G(f) ∘ eta_A = eta_B ∘ F(f)
        for f in C.morphisms.values():
            eta_a = self.component(f.source.name)
            eta_b = self.component(f.target.name)
            Gf = G.map_morphism(f)
            Ff = F.map_morphism(f)

            left = D.compose(Gf.name, eta_a.name)
            right = D.compose(eta_b.name, Ff.name)

            if left.name != right.name:
                raise NaturalTransformationError(
                    f"Natürlichkeit verletzt für {f.name!r}: "
                    f"{Gf.name} ∘ {eta_a.name} != {eta_b.name} ∘ {Ff.name}"
                )


class MathematicalCategory:
    """
    Umfangreiches Grundgerüst einer kleinen Kategorie.

    Hauptfähigkeiten:
    - Objekte und Morphismen registrieren
    - Identitäten verwalten
    - Komposition verwalten und optional automatisch erzeugen
    - symbolische und konkrete Morphismen mischen
    - Kategoriengesetze prüfen
    - Isomorphismen prüfen / registrieren
    - Produkte, Koprodukte, Equalizer, Pullbacks etc. über Registry hinterlegen
    - Funktoren und natürliche Transformationen verwalten
    - Diagramme und Kommutativitätsbedingungen prüfen
    - Opposite Category erzeugen
    - Unterkategorien bilden
    - Hom-Mengen, Endomorphismen, Automorphismen etc. abfragen

    Grenze:
    Diese Klasse ist ein starkes Framework für allgemeine Kategorien,
    aber keine magische Entscheidungsmaschine für alle universellen Konstruktionen
    in jeder denkbaren Kategorie.
    """

    def __init__(
        self,
        name: str,
        *,
        auto_register_composites: bool = True,
        auto_register_identities: bool = True,
        equality_on_morphisms: Optional[Callable[[Morphism, Morphism], bool]] = None,
    ) -> None:
        self.name = name
        self.auto_register_composites = auto_register_composites
        self.auto_register_identities = auto_register_identities

        self.objects: Dict[str, CatObject] = {}
        self.morphisms: Dict[str, Morphism] = {}
        self._identities: Dict[str, str] = {}
        self._composition_cache: Dict[Tuple[str, str], str] = {}

        # Universelle Konstruktionen / Zusatzstruktur
        self.products: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.coproducts: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.equalizers: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.coequalizers: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.pullbacks: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.pushouts: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.exponentials: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.terminal_objects: Set[str] = set()
        self.initial_objects: Set[str] = set()

        self.functors: Dict[str, Functor] = {}
        self.natural_transformations: Dict[str, NaturalTransformation] = {}
        self.diagram_constraints: List[CommutativeConstraint] = []

        if equality_on_morphisms is None:
            self.equality_on_morphisms = lambda a, b: a.name == b.name
        else:
            self.equality_on_morphisms = equality_on_morphisms

    # -------------------------------------------------------------------------
    # Objektverwaltung
    # -------------------------------------------------------------------------

    def add_object(
        self,
        name: str,
        *,
        payload: Any = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        if name in self.objects:
            raise ObjectAlreadyExists(f"Objekt {name!r} existiert bereits.")
        obj = CatObject(name=name, payload=payload, tags=frozenset(tags or ()))
        self.objects[name] = obj
        if self.auto_register_identities:
            self._create_identity_for_object(obj)
        return obj

    def ensure_object(
        self,
        name: str,
        *,
        payload: Any = None,
        tags: Optional[Iterable[str]] = None,
    ) -> CatObject:
        if name in self.objects:
            return self.objects[name]
        return self.add_object(name, payload=payload, tags=tags)

    def get_object(self, name: str) -> CatObject:
        try:
            return self.objects[name]
        except KeyError as exc:
            raise ObjectNotFound(f"Objekt {name!r} existiert nicht.") from exc

    def remove_object(self, name: str, *, cascade: bool = False) -> None:
        if name not in self.objects:
            raise ObjectNotFound(f"Objekt {name!r} existiert nicht.")

        incident = [
            m.name for m in self.morphisms.values()
            if m.source.name == name or m.target.name == name
        ]
        if incident and not cascade:
            raise CategoryError(
                f"Objekt {name!r} hat inzidente Morphismen: {incident}. "
                f"Setze cascade=True zum Entfernen."
            )

        for morph_name in incident:
            self.remove_morphism(morph_name)

        if name in self._identities:
            self._identities.pop(name, None)

        self.objects.pop(name, None)
        self._clear_composition_cache()

    def list_objects(self) -> List[CatObject]:
        return list(self.objects.values())

    # -------------------------------------------------------------------------
    # Morphismusverwaltung
    # -------------------------------------------------------------------------

    def add_morphism(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        fn: Optional[Callable[[Any], Any]] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> Morphism:
        src_obj = self.get_object(source) if isinstance(source, str) else source
        tgt_obj = self.get_object(target) if isinstance(target, str) else target

        if name in self.morphisms and not overwrite:
            raise MorphismAlreadyExists(f"Morphismus {name!r} existiert bereits.")

        morph = Morphism(
            name=name,
            source=src_obj,
            target=tgt_obj,
            fn=fn,
            metadata=dict(metadata or {}),
        )
        self.morphisms[name] = morph
        self._clear_composition_cache()
        self._cache_existing_compositions_involving(name)
        return morph

    def ensure_morphism(
        self,
        name: str,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        fn: Optional[Callable[[Any], Any]] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Morphism:
        if name in self.morphisms:
            return self.morphisms[name]
        return self.add_morphism(name, source, target, fn, metadata=metadata)

    def get_morphism(self, name: str) -> Morphism:
        try:
            return self.morphisms[name]
        except KeyError as exc:
            raise MorphismNotFound(f"Morphismus {name!r} existiert nicht.") from exc

    def remove_morphism(self, name: str) -> None:
        if name not in self.morphisms:
            raise MorphismNotFound(f"Morphismus {name!r} existiert nicht.")

        morph = self.morphisms[name]
        if self._identities.get(morph.source.name) == name and morph.source == morph.target:
            self._identities.pop(morph.source.name, None)

        self.morphisms.pop(name)
        self._clear_composition_cache()

    def list_morphisms(self) -> List[Morphism]:
        return list(self.morphisms.values())

    def hom(self, source: Union[str, CatObject], target: Union[str, CatObject]) -> List[Morphism]:
        src = self.get_object(source) if isinstance(source, str) else source
        tgt = self.get_object(target) if isinstance(target, str) else target
        return [m for m in self.morphisms.values() if m.source == src and m.target == tgt]

    def endomorphisms(self, obj: Union[str, CatObject]) -> List[Morphism]:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        return self.hom(o, o)

    def automorphisms(self, obj: Union[str, CatObject]) -> List[Morphism]:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        autos = []
        for m in self.endomorphisms(o):
            if self.is_isomorphism(m.name):
                autos.append(m)
        return autos

    # -------------------------------------------------------------------------
    # Identitäten
    # -------------------------------------------------------------------------

    def _create_identity_for_object(self, obj: CatObject) -> Morphism:
        name = f"id_{obj.name}"
        if name in self.morphisms:
            morph = self.morphisms[name]
            if morph.source != obj or morph.target != obj:
                raise IdentityError(
                    f"Vorhandener Morphismus {name!r} kollidiert mit Identität auf {obj.name!r}."
                )
            self._identities[obj.name] = name
            return morph

        morph = Morphism(
            name=name,
            source=obj,
            target=obj,
            fn=(lambda x: x),
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

    def is_identity(self, morphism_name: str) -> bool:
        m = self.get_morphism(morphism_name)
        return (
            m.source == m.target
            and self._identities.get(m.source.name) == m.name
        )

    # -------------------------------------------------------------------------
    # Komposition
    # -------------------------------------------------------------------------

    def can_compose(
        self,
        g: Union[str, Morphism],
        f: Union[str, Morphism],
    ) -> bool:
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
        """
        Gibt g ∘ f zurück, also zuerst f, dann g.
        """
        gm = self.get_morphism(g) if isinstance(g, str) else g
        fm = self.get_morphism(f) if isinstance(f, str) else f

        if fm.target != gm.source:
            raise CompositionError(
                f"Nicht komponierbar: {fm.name}: {fm.source.name}->{fm.target.name}, "
                f"{gm.name}: {gm.source.name}->{gm.target.name}"
            )

        cache_key = (gm.name, fm.name)
        if cache_key in self._composition_cache:
            return self.get_morphism(self._composition_cache[cache_key])

        if name is None:
            name = self._canonical_composite_name(gm, fm)

        do_register = self.auto_register_composites if register is None else register

        composed_fn: Optional[Callable[[Any], Any]]
        if gm.fn is not None and fm.fn is not None:
            composed_fn = lambda x, _g=gm.fn, _f=fm.fn: _g(_f(x))
        else:
            composed_fn = None

        metadata = {
            "composite_of": (gm.name, fm.name),
        }

        result = Morphism(
            name=name,
            source=fm.source,
            target=gm.target,
            fn=composed_fn,
            metadata=metadata,
        )

        if do_register:
            if name in self.morphisms:
                existing = self.morphisms[name]
                if existing.source != result.source or existing.target != result.target:
                    raise CompositionError(
                        f"Kompositionsname {name!r} existiert bereits mit anderer Signatur."
                    )
                result = existing
            else:
                self.morphisms[name] = result
            self._composition_cache[cache_key] = result.name

        return result

    def compose_many(
        self,
        *morphisms: Union[str, Morphism],
        name: Optional[str] = None,
        register: Optional[bool] = None,
    ) -> Morphism:
        if len(morphisms) < 2:
            raise CompositionError("Für compose_many werden mindestens zwei Morphismen benötigt.")

        resolved = [
            self.get_morphism(m) if isinstance(m, str) else m
            for m in morphisms
        ]

        current = resolved[0]
        for nxt in resolved[1:]:
            current = self.compose(current, nxt, register=register)
        if name is not None:
            if current.name != name:
                current = self.add_morphism(
                    name,
                    current.source,
                    current.target,
                    current.fn,
                    metadata=dict(current.metadata),
                    overwrite=True,
                )
        return current

    def _canonical_composite_name(self, g: Morphism, f: Morphism) -> str:
        return f"{g.name}_o_{f.name}"

    def _clear_composition_cache(self) -> None:
        self._composition_cache.clear()

    def _cache_existing_compositions_involving(self, morphism_name: str) -> None:
        # Hier bewusst leer/leichtgewichtig. Cache wird bei compose aufgebaut.
        return None

    # -------------------------------------------------------------------------
    # Kategoriengesetze
    # -------------------------------------------------------------------------

    def validate_identities(self) -> None:
        for obj in self.objects.values():
            id_obj = self.identity(obj)
            if id_obj.source != obj or id_obj.target != obj:
                raise IdentityError(f"Identität auf {obj.name!r} hat falschen Typ.")

        for m in self.morphisms.values():
            left = self.compose(m.name, self.identity(m.source).name, register=False)
            right = self.compose(self.identity(m.target).name, m.name, register=False)

            if left.source != m.source or left.target != m.target:
                raise IdentityError(f"Linke Identität passt nicht für {m.name!r}.")
            if right.source != m.source or right.target != m.target:
                raise IdentityError(f"Rechte Identität passt nicht für {m.name!r}.")

    def validate_associativity(self) -> None:
        morphs = list(self.morphisms.values())
        for h in morphs:
            for g in morphs:
                for f in morphs:
                    if f.target == g.source and g.target == h.source:
                        left = self.compose(h, self.compose(g, f, register=False), register=False)
                        right = self.compose(self.compose(h, g, register=False), f, register=False)
                        if left.source != right.source or left.target != right.target:
                            raise CompositionError(
                                f"Assoziativität typmäßig verletzt für "
                                f"{h.name}, {g.name}, {f.name}."
                            )

    def validate(self) -> None:
        self.validate_identities()
        self.validate_associativity()

        for functor in self.functors.values():
            functor.validate()

        for nat in self.natural_transformations.values():
            nat.validate()

        self.validate_diagrams()

    # -------------------------------------------------------------------------
    # Isomorphismen
    # -------------------------------------------------------------------------

    def find_inverse_candidates(self, morphism_name: str) -> List[Morphism]:
        m = self.get_morphism(morphism_name)
        candidates = self.hom(m.target, m.source)
        good = []
        id_src = self.identity(m.source)
        id_tgt = self.identity(m.target)

        for cand in candidates:
            try:
                left = self.compose(cand, m, register=False)
                right = self.compose(m, cand, register=False)
                if (
                    left.source == id_src.source
                    and left.target == id_src.target
                    and right.source == id_tgt.source
                    and right.target == id_tgt.target
                ):
                    good.append(cand)
            except CompositionError:
                continue
        return good

    def is_isomorphism(self, morphism_name: str) -> bool:
        return len(self.find_inverse_candidates(morphism_name)) > 0

    def register_isomorphism_pair(
        self,
        f_name: str,
        g_name: str,
    ) -> None:
        f = self.get_morphism(f_name)
        g = self.get_morphism(g_name)

        if f.source != g.target or f.target != g.source:
            raise CategoryError("Morphismen sind typmäßig keine inversen Kandidaten.")

        fg = self.compose(f, g, register=False)
        gf = self.compose(g, f, register=False)

        id_f_src = self.identity(f.source)
        id_f_tgt = self.identity(f.target)

        if fg.source != id_f_tgt.source or fg.target != id_f_tgt.target:
            raise CategoryError(f"{f_name} ∘ {g_name} passt nicht zur Zielidentität.")
        if gf.source != id_f_src.source or gf.target != id_f_src.target:
            raise CategoryError(f"{g_name} ∘ {f_name} passt nicht zur Quellidentität.")

        self.morphisms[f_name].metadata["inverse"] = g_name
        self.morphisms[g_name].metadata["inverse"] = f_name
        self.morphisms[f_name].metadata["isomorphism"] = True
        self.morphisms[g_name].metadata["isomorphism"] = True

    # -------------------------------------------------------------------------
    # Terminale / initiale Objekte
    # -------------------------------------------------------------------------

    def set_terminal_object(self, obj: Union[str, CatObject]) -> None:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        self.terminal_objects.add(o.name)

    def set_initial_object(self, obj: Union[str, CatObject]) -> None:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        self.initial_objects.add(o.name)

    def is_terminal(self, obj: Union[str, CatObject]) -> bool:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        return o.name in self.terminal_objects

    def is_initial(self, obj: Union[str, CatObject]) -> bool:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        return o.name in self.initial_objects

    # -------------------------------------------------------------------------
    # Produkte / Koprodukte / Universal-Konstruktionen per Registry
    # -------------------------------------------------------------------------

    def register_product(
        self,
        left_obj: Union[str, CatObject],
        right_obj: Union[str, CatObject],
        product_obj: Union[str, CatObject],
        proj_left: Union[str, Morphism],
        proj_right: Union[str, Morphism],
    ) -> None:
        A = self.get_object(left_obj) if isinstance(left_obj, str) else left_obj
        B = self.get_object(right_obj) if isinstance(right_obj, str) else right_obj
        P = self.get_object(product_obj) if isinstance(product_obj, str) else product_obj
        p1 = self.get_morphism(proj_left) if isinstance(proj_left, str) else proj_left
        p2 = self.get_morphism(proj_right) if isinstance(proj_right, str) else proj_right

        if p1.source != P or p1.target != A:
            raise UniversalConstructionError("Erste Projektion hat falschen Typ.")
        if p2.source != P or p2.target != B:
            raise UniversalConstructionError("Zweite Projektion hat falschen Typ.")

        self.products[(A.name, B.name)] = {
            "product": P.name,
            "proj_left": p1.name,
            "proj_right": p2.name,
        }

    def get_product(self, left_obj: Union[str, CatObject], right_obj: Union[str, CatObject]) -> Dict[str, Morphism]:
        A = self.get_object(left_obj) if isinstance(left_obj, str) else left_obj
        B = self.get_object(right_obj) if isinstance(right_obj, str) else right_obj
        key = (A.name, B.name)
        if key not in self.products:
            raise UniversalConstructionError(f"Kein Produkt registriert für {A.name}, {B.name}.")
        data = self.products[key]
        return {
            "product": self.get_morphism(self.identity(data["product"]).name).source,  # Produktobjekt
            "proj_left": self.get_morphism(data["proj_left"]),
            "proj_right": self.get_morphism(data["proj_right"]),
        }

    def pair(
        self,
        f: Union[str, Morphism],
        g: Union[str, Morphism],
        *,
        name: Optional[str] = None,
        fn: Optional[Callable[[Any], Any]] = None,
    ) -> Morphism:
        """
        Universeller Morphismus <f, g>: X -> A×B.
        Muss registriertes Produkt verwenden.
        Die Eindeutigkeit wird hier nicht algorithmisch bewiesen, sondern
        als strukturierte Konstruktion unterstützt.
        """
        fm = self.get_morphism(f) if isinstance(f, str) else f
        gm = self.get_morphism(g) if isinstance(g, str) else g

        if fm.source != gm.source:
            raise UniversalConstructionError("pair benötigt Morphismen mit gleicher Quelle.")

        key = (fm.target.name, gm.target.name)
        if key not in self.products:
            raise UniversalConstructionError(
                f"Kein Produkt für {fm.target.name} und {gm.target.name} registriert."
            )
        prod_info = self.products[key]
        P = self.get_object(prod_info["product"])

        if name is None:
            name = f"pair_{fm.name}_{gm.name}"

        return self.add_morphism(
            name=name,
            source=fm.source,
            target=P,
            fn=fn,
            metadata={
                "pair_of": (fm.name, gm.name),
                "universal_over_product": key,
            },
            overwrite=True,
        )

    def register_coproduct(
        self,
        left_obj: Union[str, CatObject],
        right_obj: Union[str, CatObject],
        coproduct_obj: Union[str, CatObject],
        inj_left: Union[str, Morphism],
        inj_right: Union[str, Morphism],
    ) -> None:
        A = self.get_object(left_obj) if isinstance(left_obj, str) else left_obj
        B = self.get_object(right_obj) if isinstance(right_obj, str) else right_obj
        C = self.get_object(coproduct_obj) if isinstance(coproduct_obj, str) else coproduct_obj
        i1 = self.get_morphism(inj_left) if isinstance(inj_left, str) else inj_left
        i2 = self.get_morphism(inj_right) if isinstance(inj_right, str) else inj_right

        if i1.source != A or i1.target != C:
            raise UniversalConstructionError("Erste Injektion hat falschen Typ.")
        if i2.source != B or i2.target != C:
            raise UniversalConstructionError("Zweite Injektion hat falschen Typ.")

        self.coproducts[(A.name, B.name)] = {
            "coproduct": C.name,
            "inj_left": i1.name,
            "inj_right": i2.name,
        }

    def copair(
        self,
        f: Union[str, Morphism],
        g: Union[str, Morphism],
        *,
        name: Optional[str] = None,
        fn: Optional[Callable[[Any], Any]] = None,
    ) -> Morphism:
        """
        [f, g]: A+B -> X
        """
        fm = self.get_morphism(f) if isinstance(f, str) else f
        gm = self.get_morphism(g) if isinstance(g, str) else g

        if fm.target != gm.target:
            raise UniversalConstructionError("copair benötigt Morphismen mit gleichem Ziel.")

        key = (fm.source.name, gm.source.name)
        if key not in self.coproducts:
            raise UniversalConstructionError(
                f"Kein Koprodukt für {fm.source.name} und {gm.source.name} registriert."
            )

        coproduct_info = self.coproducts[key]
        C = self.get_object(coproduct_info["coproduct"])

        if name is None:
            name = f"copair_{fm.name}_{gm.name}"

        return self.add_morphism(
            name=name,
            source=C,
            target=fm.target,
            fn=fn,
            metadata={
                "copair_of": (fm.name, gm.name),
                "universal_over_coproduct": key,
            },
            overwrite=True,
        )

    def register_equalizer(
        self,
        f: Union[str, Morphism],
        g: Union[str, Morphism],
        equalizer_obj: Union[str, CatObject],
        inclusion: Union[str, Morphism],
    ) -> None:
        fm = self.get_morphism(f) if isinstance(f, str) else f
        gm = self.get_morphism(g) if isinstance(g, str) else g
        E = self.get_object(equalizer_obj) if isinstance(equalizer_obj, str) else equalizer_obj
        e = self.get_morphism(inclusion) if isinstance(inclusion, str) else inclusion

        if fm.source != gm.source or fm.target != gm.target:
            raise UniversalConstructionError("Equalizer braucht parallele Morphismen.")
        if e.source != E or e.target != fm.source:
            raise UniversalConstructionError("Equalizer-Einbettung hat falschen Typ.")

        self.equalizers[(fm.name, gm.name)] = {
            "object": E.name,
            "inclusion": e.name,
        }

    def register_pullback(
        self,
        f: Union[str, Morphism],
        g: Union[str, Morphism],
        pullback_obj: Union[str, CatObject],
        proj_left: Union[str, Morphism],
        proj_right: Union[str, Morphism],
    ) -> None:
        fm = self.get_morphism(f) if isinstance(f, str) else f
        gm = self.get_morphism(g) if isinstance(g, str) else g
        P = self.get_object(pullback_obj) if isinstance(pullback_obj, str) else pullback_obj
        p1 = self.get_morphism(proj_left) if isinstance(proj_left, str) else proj_left
        p2 = self.get_morphism(proj_right) if isinstance(proj_right, str) else proj_right

        if fm.target != gm.target:
            raise UniversalConstructionError("Pullback braucht Morphismen mit gleichem Ziel.")
        if p1.source != P or p1.target != fm.source:
            raise UniversalConstructionError("Linke Pullback-Projektion hat falschen Typ.")
        if p2.source != P or p2.target != gm.source:
            raise UniversalConstructionError("Rechte Pullback-Projektion hat falschen Typ.")

        self.pullbacks[(fm.name, gm.name)] = {
            "object": P.name,
            "proj_left": p1.name,
            "proj_right": p2.name,
        }

    def register_pushout(
        self,
        f: Union[str, Morphism],
        g: Union[str, Morphism],
        pushout_obj: Union[str, CatObject],
        inj_left: Union[str, Morphism],
        inj_right: Union[str, Morphism],
    ) -> None:
        fm = self.get_morphism(f) if isinstance(f, str) else f
        gm = self.get_morphism(g) if isinstance(g, str) else g
        P = self.get_object(pushout_obj) if isinstance(pushout_obj, str) else pushout_obj
        i1 = self.get_morphism(inj_left) if isinstance(inj_left, str) else inj_left
        i2 = self.get_morphism(inj_right) if isinstance(inj_right, str) else inj_right

        if fm.source != gm.source:
            raise UniversalConstructionError("Pushout braucht Morphismen mit gleicher Quelle.")
        if i1.source != fm.target or i1.target != P:
            raise UniversalConstructionError("Linke Pushout-Injektion hat falschen Typ.")
        if i2.source != gm.target or i2.target != P:
            raise UniversalConstructionError("Rechte Pushout-Injektion hat falschen Typ.")

        self.pushouts[(fm.name, gm.name)] = {
            "object": P.name,
            "inj_left": i1.name,
            "inj_right": i2.name,
        }

    def register_exponential(
        self,
        base_obj: Union[str, CatObject],
        exponent_obj: Union[str, CatObject],
        exponential_obj: Union[str, CatObject],
        evaluation: Union[str, Morphism],
    ) -> None:
        A = self.get_object(base_obj) if isinstance(base_obj, str) else base_obj
        B = self.get_object(exponent_obj) if isinstance(exponent_obj, str) else exponent_obj
        E = self.get_object(exponential_obj) if isinstance(exponential_obj, str) else exponential_obj
        ev = self.get_morphism(evaluation) if isinstance(evaluation, str) else evaluation

        self.exponentials[(A.name, B.name)] = {
            "object": E.name,
            "evaluation": ev.name,
        }

    # -------------------------------------------------------------------------
    # Diagramme
    # -------------------------------------------------------------------------

    def make_path(self, morphism_names: Sequence[Union[str, Morphism]]) -> DiagramPath:
        morphs = [
            self.get_morphism(m) if isinstance(m, str) else m
            for m in morphism_names
        ]
        if not morphs:
            raise CategoryError("Ein Pfad darf nicht leer sein.")

        for left, right in zip(morphs[:-1], morphs[1:]):
            # Da Pfad in natürlicher Leserichtung gegeben wird:
            # A -f-> B -g-> C
            # also morphism_names = [f, g]
            if left.target != right.source:
                raise CategoryError(
                    f"Pfad ist nicht verkettbar: {left.name} dann {right.name}."
                )
        return DiagramPath(tuple(morphs))

    def compose_path(self, path: DiagramPath, *, register: bool = False) -> Morphism:
        current = path.morphisms[0]
        for nxt in path.morphisms[1:]:
            current = self.compose(nxt, current, register=register)
        return current

    def add_commutative_constraint(
        self,
        left_path: Sequence[Union[str, Morphism]],
        right_path: Sequence[Union[str, Morphism]],
        *,
        name: str = "",
    ) -> CommutativeConstraint:
        left = self.make_path(left_path)
        right = self.make_path(right_path)

        if left.source != right.source or left.target != right.target:
            raise CategoryError(
                "Kommutativitätsbedingung braucht Pfade mit gleicher Quelle und gleichem Ziel."
            )

        constraint = CommutativeConstraint(left=left, right=right, name=name)
        self.diagram_constraints.append(constraint)
        return constraint

    def validate_diagrams(self) -> None:
        for c in self.diagram_constraints:
            left = self.compose_path(c.left, register=False)
            right = self.compose_path(c.right, register=False)

            if (
                left.source != right.source
                or left.target != right.target
            ):
                raise CategoryError(
                    f"Diagramm-Bedingung {c.name!r} typmäßig verletzt."
                )

            # In voller Allgemeinheit kann man Gleichheit von Morphismen nicht automatisch
            # in jeder Kategorie entscheiden. Deshalb ist Gleichheit injizierbar.
            if not self.equality_on_morphisms(left, right):
                raise CategoryError(
                    f"Diagramm-Bedingung {c.name!r} verletzt: "
                    f"{left.name} != {right.name}"
                )

    # -------------------------------------------------------------------------
    # Funktoren und natürliche Transformationen
    # -------------------------------------------------------------------------

    def add_functor(
        self,
        name: str,
        target_category: "MathematicalCategory",
        *,
        object_map: Dict[str, str],
        morphism_map: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Functor:
        if name in self.functors:
            raise FunctorError(f"Funktor {name!r} existiert bereits.")

        F = Functor(
            name=name,
            source_category=self,
            target_category=target_category,
            object_map=dict(object_map),
            morphism_map=dict(morphism_map),
            metadata=dict(metadata or {}),
        )
        self.functors[name] = F
        return F

    def get_functor(self, name: str) -> Functor:
        if name not in self.functors:
            raise FunctorError(f"Funktor {name!r} existiert nicht.")
        return self.functors[name]

    def add_natural_transformation(
        self,
        name: str,
        source_functor: Union[str, Functor],
        target_functor: Union[str, Functor],
        *,
        components: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NaturalTransformation:
        if name in self.natural_transformations:
            raise NaturalTransformationError(
                f"Natürliche Transformation {name!r} existiert bereits."
            )

        F = self.get_functor(source_functor) if isinstance(source_functor, str) else source_functor
        G = self.get_functor(target_functor) if isinstance(target_functor, str) else target_functor

        eta = NaturalTransformation(
            name=name,
            source_functor=F,
            target_functor=G,
            components=dict(components),
            metadata=dict(metadata or {}),
        )
        self.natural_transformations[name] = eta
        return eta

    def get_natural_transformation(self, name: str) -> NaturalTransformation:
        if name not in self.natural_transformations:
            raise NaturalTransformationError(
                f"Natürliche Transformation {name!r} existiert nicht."
            )
        return self.natural_transformations[name]

    # -------------------------------------------------------------------------
    # Opposite Category, Unterkategorie, Klonen
    # -------------------------------------------------------------------------

    def opposite(self, name: Optional[str] = None) -> "MathematicalCategory":
        op = MathematicalCategory(
            name=name or f"{self.name}^op",
            auto_register_composites=self.auto_register_composites,
            auto_register_identities=self.auto_register_identities,
        )

        for obj in self.objects.values():
            op.add_object(obj.name, payload=obj.payload, tags=obj.tags)

        # zuerst nicht-Identitäten, dann Identitäten sauber überschreiben falls nötig
        for m in self.morphisms.values():
            op.add_morphism(
                name=m.name,
                source=m.target.name,
                target=m.source.name,
                fn=m.fn,
                metadata=dict(m.metadata),
                overwrite=True,
            )

        # Identitätsregister neu aufbauen
        for obj in op.objects.values():
            op._identities[obj.name] = f"id_{obj.name}"
            if f"id_{obj.name}" not in op.morphisms:
                op._create_identity_for_object(obj)

        return op

    def subcategory(
        self,
        name: str,
        *,
        object_names: Iterable[str],
        morphism_names: Iterable[str],
    ) -> "MathematicalCategory":
        sub = MathematicalCategory(
            name=name,
            auto_register_composites=self.auto_register_composites,
            auto_register_identities=self.auto_register_identities,
        )

        object_set = set(object_names)
        morphism_set = set(morphism_names)

        for obj_name in object_set:
            obj = self.get_object(obj_name)
            sub.add_object(obj.name, payload=obj.payload, tags=obj.tags)

        for morph_name in morphism_set:
            m = self.get_morphism(morph_name)
            if m.source.name not in object_set or m.target.name not in object_set:
                raise CategoryError(
                    f"Morphismus {morph_name!r} liegt nicht vollständig in den gewählten Objekten."
                )
            sub.add_morphism(
                m.name,
                m.source.name,
                m.target.name,
                m.fn,
                metadata=dict(m.metadata),
            )

        return sub

    def clone(self, name: Optional[str] = None) -> "MathematicalCategory":
        cloned = MathematicalCategory(
            name=name or f"{self.name}_clone",
            auto_register_composites=self.auto_register_composites,
            auto_register_identities=self.auto_register_identities,
            equality_on_morphisms=self.equality_on_morphisms,
        )

        for obj in self.objects.values():
            cloned.add_object(obj.name, payload=obj.payload, tags=obj.tags)

        for m in self.morphisms.values():
            if cloned.auto_register_identities and m.name == f"id_{m.source.name}" and m.source == m.target:
                continue
            cloned.add_morphism(
                m.name,
                m.source.name,
                m.target.name,
                m.fn,
                metadata=dict(m.metadata),
                overwrite=True,
            )

        cloned.products = {k: dict(v) for k, v in self.products.items()}
        cloned.coproducts = {k: dict(v) for k, v in self.coproducts.items()}
        cloned.equalizers = {k: dict(v) for k, v in self.equalizers.items()}
        cloned.coequalizers = {k: dict(v) for k, v in self.coequalizers.items()}
        cloned.pullbacks = {k: dict(v) for k, v in self.pullbacks.items()}
        cloned.pushouts = {k: dict(v) for k, v in self.pushouts.items()}
        cloned.exponentials = {k: dict(v) for k, v in self.exponentials.items()}
        cloned.terminal_objects = set(self.terminal_objects)
        cloned.initial_objects = set(self.initial_objects)

        return cloned

    # -------------------------------------------------------------------------
    # Ausführung / praktische Hilfen
    # -------------------------------------------------------------------------

    def apply(self, morphism: Union[str, Morphism], value: Any) -> Any:
        m = self.get_morphism(morphism) if isinstance(morphism, str) else morphism
        return m(value)

    def try_apply(self, morphism: Union[str, Morphism], value: Any, default: Any = None) -> Any:
        try:
            return self.apply(morphism, value)
        except Exception:
            return default

    def compose_and_apply(
        self,
        g: Union[str, Morphism],
        f: Union[str, Morphism],
        value: Any,
    ) -> Any:
        return self.compose(g, f)(value)

    # -------------------------------------------------------------------------
    # Suche / Analyse
    # -------------------------------------------------------------------------

    def incoming(self, obj: Union[str, CatObject]) -> List[Morphism]:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        return [m for m in self.morphisms.values() if m.target == o]

    def outgoing(self, obj: Union[str, CatObject]) -> List[Morphism]:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        return [m for m in self.morphisms.values() if m.source == o]

    def parallel_pairs(self) -> List[Tuple[Morphism, Morphism]]:
        result = []
        morphs = list(self.morphisms.values())
        for i, a in enumerate(morphs):
            for b in morphs[i + 1:]:
                if a.source == b.source and a.target == b.target:
                    result.append((a, b))
        return result

    def composable_pairs(self) -> List[Tuple[Morphism, Morphism]]:
        result = []
        for g in self.morphisms.values():
            for f in self.morphisms.values():
                if f.target == g.source:
                    result.append((g, f))
        return result

    def reachability(self, source: Union[str, CatObject], target: Union[str, CatObject]) -> bool:
        src = self.get_object(source) if isinstance(source, str) else source
        tgt = self.get_object(target) if isinstance(target, str) else target

        if src == tgt:
            return True

        visited = set()
        stack = [src]
        while stack:
            current = stack.pop()
            if current.name in visited:
                continue
            visited.add(current.name)
            for m in self.outgoing(current):
                if m.target == tgt:
                    return True
                stack.append(m.target)
        return False

    # -------------------------------------------------------------------------
    # Dekorator-API
    # -------------------------------------------------------------------------

    def Mor(
        self,
        source: Union[str, CatObject],
        target: Union[str, CatObject],
        name: Optional[str] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> Callable[[Callable[[Any], Any]], Morphism]:
        src = self.get_object(source) if isinstance(source, str) else source
        tgt = self.get_object(target) if isinstance(target, str) else target

        def decorator(fn: Callable[[Any], Any]) -> Morphism:
            morph_name = name or fn.__name__
            return self.add_morphism(
                morph_name,
                src,
                tgt,
                fn,
                metadata=metadata,
                overwrite=overwrite,
            )
        return decorator

    def End(
        self,
        obj: Union[str, CatObject],
        name: Optional[str] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> Callable[[Callable[[Any], Any]], Morphism]:
        o = self.get_object(obj) if isinstance(obj, str) else obj
        return self.Mor(o, o, name=name, metadata=metadata, overwrite=overwrite)

    # -------------------------------------------------------------------------
    # Darstellung
    # -------------------------------------------------------------------------

    def summary(self) -> str:
        lines = [
            f"Category({self.name})",
            f"  objects:   {len(self.objects)}",
            f"  morphisms: {len(self.morphisms)}",
            f"  functors:  {len(self.functors)}",
            f"  natural transformations: {len(self.natural_transformations)}",
        ]
        return "\n".join(lines)

    def describe(self) -> str:
        lines = [self.summary(), "", "Objects:"]
        for obj in sorted(self.objects.values(), key=lambda x: x.name):
            lines.append(f"  - {obj.name}")

        lines.append("")
        lines.append("Morphisms:")
        for m in sorted(self.morphisms.values(), key=lambda x: x.name):
            kind = "identity" if self.is_identity(m.name) else "morphism"
            symbolic = "symbolic" if m.is_symbolic() else "concrete"
            lines.append(
                f"  - {m.name}: {m.source.name} -> {m.target.name} [{kind}, {symbolic}]"
            )
        return "\n".join(lines)


# -----------------------------------------------------------------------------
# Beispielverwendung
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    C = MathematicalCategory("Example")

    A = C.add_object("A")
    B = C.add_object("B")
    D = C.add_object("D")

    @C.Mor("A", "B", "f")
    def f(x: int) -> int:
        return x + 1

    @C.Mor("B", "D", "g")
    def g(x: int) -> int:
        return 2 * x

    h = C.compose("g", "f", name="h")
    print(h)               # h: A -> D
    print(h(10))           # 22

    print(C.identity("A")) # id_A: A -> A
    C.validate()

    print()
    print(C.describe())
