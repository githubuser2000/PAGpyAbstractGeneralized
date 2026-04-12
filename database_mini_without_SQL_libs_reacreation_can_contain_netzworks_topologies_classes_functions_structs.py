
# mini_database_extended_structures.py
from __future__ import annotations

import copy
import csv
import json
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union


# =============================================================================
# Fehler
# =============================================================================

class MiniDatabaseError(Exception):
    pass


class TableExistsError(MiniDatabaseError):
    pass


class TableNotFoundError(MiniDatabaseError):
    pass


class SchemaError(MiniDatabaseError):
    pass


class ConstraintError(MiniDatabaseError):
    pass


class RowNotFoundError(MiniDatabaseError):
    pass


class StructureError(MiniDatabaseError):
    pass


# =============================================================================
# Struktur-Typen
# =============================================================================

class ValueKind(Enum):
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto()
    DICT = auto()
    LIST = auto()
    ANY = auto()

    STRUCT = auto()
    FUNCTION = auto()
    CLASS = auto()
    NETWORK = auto()
    TOPOLOGY = auto()
    MATH_CATEGORY = auto()


@dataclass
class StructValue:
    name: str
    fields: Dict[str, Any]

    def project(self, field_names: Sequence[str]) -> "StructValue":
        return StructValue(
            name=f"{self.name}_projection",
            fields={k: self.fields[k] for k in field_names if k in self.fields},
        )

    def rename_fields(self, mapping: Dict[str, str]) -> "StructValue":
        new_fields = {}
        for key, value in self.fields.items():
            new_fields[mapping.get(key, key)] = value
        return StructValue(name=f"{self.name}_renamed", fields=new_fields)

    def merge(self, other: "StructValue", *, name: Optional[str] = None) -> "StructValue":
        merged = dict(self.fields)
        for k, v in other.fields.items():
            if k in merged:
                raise StructureError(f"Feldkonflikt beim Merge: {k!r}")
            merged[k] = v
        return StructValue(name=name or f"{self.name}_{other.name}_merged", fields=merged)


@dataclass
class FunctionValue:
    name: str
    domain_name: str
    codomain_name: str
    impl: Optional[Callable[[Any], Any]] = None
    pure: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def __call__(self, value: Any) -> Any:
        if self.impl is None:
            raise StructureError(f"Funktion {self.name!r} ist nicht ausführbar.")
        return self.impl(value)

    def compose(self, other: "FunctionValue", *, name: Optional[str] = None) -> "FunctionValue":
        if other.codomain_name != self.domain_name:
            raise StructureError(
                f"Nicht komponierbar: {other.codomain_name!r} != {self.domain_name!r}"
            )
        if self.impl is None or other.impl is None:
            impl = None
        else:
            impl = lambda x, f=self.impl, g=other.impl: f(g(x))
        return FunctionValue(
            name=name or f"{self.name}_o_{other.name}",
            domain_name=other.domain_name,
            codomain_name=self.codomain_name,
            impl=impl,
            pure=self.pure and other.pure,
            metadata={"composed_of": (self.name, other.name)},
        )


@dataclass
class ClassValue:
    name: str
    fields: List[str]
    methods: List[str]
    base_classes: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.base_classes is None:
            self.base_classes = []
        if self.metadata is None:
            self.metadata = {}

    def inherits_from(self, other: "ClassValue") -> bool:
        return set(other.fields).issubset(set(self.fields)) and set(other.methods).issubset(set(self.methods))

    def project(self, field_subset: Sequence[str], *, name: Optional[str] = None) -> "ClassValue":
        subset = [f for f in self.fields if f in set(field_subset)]
        return ClassValue(
            name=name or f"{self.name}_projection",
            fields=subset,
            methods=list(self.methods),
            base_classes=list(self.base_classes),
            metadata=dict(self.metadata),
        )


@dataclass
class NetworkValue:
    name: str
    nodes: List[Any]
    edges: List[Tuple[Any, Any]]
    directed: bool = True
    protocols: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.protocols is None:
            self.protocols = []
        if self.metadata is None:
            self.metadata = {}

    def validate(self) -> bool:
        node_set = set(self.nodes)
        return all(u in node_set and v in node_set for u, v in self.edges)

    def induced_subnetwork(self, node_subset: Sequence[Any], *, name: Optional[str] = None) -> "NetworkValue":
        subset = set(node_subset)
        return NetworkValue(
            name=name or f"{self.name}_subnetwork",
            nodes=[n for n in self.nodes if n in subset],
            edges=[(u, v) for (u, v) in self.edges if u in subset and v in subset],
            directed=self.directed,
            protocols=list(self.protocols),
            metadata=dict(self.metadata),
        )

    def map_nodes(self, mapping: Dict[Any, Any], *, name: Optional[str] = None) -> "NetworkValue":
        new_nodes = [mapping.get(n, n) for n in self.nodes]
        new_edges = [(mapping.get(u, u), mapping.get(v, v)) for (u, v) in self.edges]
        return NetworkValue(
            name=name or f"{self.name}_mapped",
            nodes=new_nodes,
            edges=new_edges,
            directed=self.directed,
            protocols=list(self.protocols),
            metadata=dict(self.metadata),
        )


@dataclass
class TopologyValue:
    name: str
    carrier: List[Any]
    opens: List[List[Any]]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def validate(self) -> bool:
        carrier_set = set(self.carrier)
        open_sets = {frozenset(o) for o in self.opens}
        if frozenset() not in open_sets:
            return False
        if frozenset(carrier_set) not in open_sets:
            return False
        for a in open_sets:
            for b in open_sets:
                if a.intersection(b) not in open_sets:
                    return False
                if a.union(b) not in open_sets:
                    return False
        return True

    def subspace(self, subset: Sequence[Any], *, name: Optional[str] = None) -> "TopologyValue":
        subset_set = set(subset)
        new_opens = []
        for o in self.opens:
            inter = sorted(list(set(o).intersection(subset_set)))
            if inter not in new_opens:
                new_opens.append(inter)
        return TopologyValue(
            name=name or f"{self.name}_subspace",
            carrier=sorted(list(subset_set)),
            opens=new_opens,
            metadata=dict(self.metadata),
        )


@dataclass
class CategoryObjectValue:
    name: str
    payload: Any = None


@dataclass
class CategoryMorphismValue:
    name: str
    source: str
    target: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MathCategoryValue:
    name: str
    objects: List[CategoryObjectValue]
    morphisms: List[CategoryMorphismValue]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def object_names(self) -> List[str]:
        return [o.name for o in self.objects]

    def morphism_names(self) -> List[str]:
        return [m.name for m in self.morphisms]

    def outgoing(self, object_name: str) -> List[CategoryMorphismValue]:
        return [m for m in self.morphisms if m.source == object_name]

    def incoming(self, object_name: str) -> List[CategoryMorphismValue]:
        return [m for m in self.morphisms if m.target == object_name]

    def compose_symbolic(self, g_name: str, f_name: str, *, name: Optional[str] = None) -> CategoryMorphismValue:
        g = next((m for m in self.morphisms if m.name == g_name), None)
        f = next((m for m in self.morphisms if m.name == f_name), None)
        if g is None or f is None:
            raise StructureError("Morphismen für Komposition nicht gefunden.")
        if f.target != g.source:
            raise StructureError("Morphismen sind nicht komponierbar.")
        return CategoryMorphismValue(
            name=name or f"{g.name}_o_{f.name}",
            source=f.source,
            target=g.target,
            metadata={"composite_of": (g.name, f.name)},
        )


# =============================================================================
# Serialisierung / Deserialisierung strukturierter Werte
# =============================================================================

def _serialize_value(value: Any) -> Any:
    if isinstance(value, StructValue):
        return {"__kind__": "StructValue", "data": {"name": value.name, "fields": value.fields}}
    if isinstance(value, FunctionValue):
        return {
            "__kind__": "FunctionValue",
            "data": {
                "name": value.name,
                "domain_name": value.domain_name,
                "codomain_name": value.codomain_name,
                "pure": value.pure,
                "metadata": value.metadata,
                "has_impl": value.impl is not None,
            },
        }
    if isinstance(value, ClassValue):
        return {
            "__kind__": "ClassValue",
            "data": {
                "name": value.name,
                "fields": value.fields,
                "methods": value.methods,
                "base_classes": value.base_classes,
                "metadata": value.metadata,
            },
        }
    if isinstance(value, NetworkValue):
        return {
            "__kind__": "NetworkValue",
            "data": {
                "name": value.name,
                "nodes": value.nodes,
                "edges": value.edges,
                "directed": value.directed,
                "protocols": value.protocols,
                "metadata": value.metadata,
            },
        }
    if isinstance(value, TopologyValue):
        return {
            "__kind__": "TopologyValue",
            "data": {
                "name": value.name,
                "carrier": value.carrier,
                "opens": value.opens,
                "metadata": value.metadata,
            },
        }
    if isinstance(value, MathCategoryValue):
        return {
            "__kind__": "MathCategoryValue",
            "data": {
                "name": value.name,
                "objects": [asdict(o) for o in value.objects],
                "morphisms": [asdict(m) for m in value.morphisms],
                "metadata": value.metadata,
            },
        }
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    return value


def _deserialize_value(value: Any) -> Any:
    if isinstance(value, dict) and "__kind__" in value:
        kind = value["__kind__"]
        data = value["data"]
        if kind == "StructValue":
            return StructValue(**data)
        if kind == "FunctionValue":
            return FunctionValue(
                name=data["name"],
                domain_name=data["domain_name"],
                codomain_name=data["codomain_name"],
                impl=None,
                pure=data.get("pure", True),
                metadata=data.get("metadata") or {},
            )
        if kind == "ClassValue":
            return ClassValue(**data)
        if kind == "NetworkValue":
            return NetworkValue(**data)
        if kind == "TopologyValue":
            return TopologyValue(**data)
        if kind == "MathCategoryValue":
            return MathCategoryValue(
                name=data["name"],
                objects=[CategoryObjectValue(**o) for o in data["objects"]],
                morphisms=[CategoryMorphismValue(**m) for m in data["morphisms"]],
                metadata=data.get("metadata") or {},
            )
    if isinstance(value, dict):
        return {k: _deserialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deserialize_value(v) for v in value]
    return value


# =============================================================================
# Datenbank
# =============================================================================

class MiniDatabase:
    """
    Minimalistische relationale Datenbank ohne SQL und ohne DB-Libs.

    Erweiterung:
    Tabelleninhalte und Operationen können auch enthalten:
    - Structs
    - Funktionen
    - Klassen
    - Netzwerke
    - Topologien
    - mathematische Kategorien
    """

    SUPPORTED_TYPES = {
        "int", "float", "str", "bool", "dict", "list", "any",
        "struct", "function", "class", "network", "topology", "math_category",
    }

    def __init__(self, name: str = "database") -> None:
        self.name = name
        self.tables: Dict[str, Dict[str, Any]] = {}
        self._transaction_stack: List[Dict[str, Dict[str, Any]]] = []

    # -----------------------------------------------------------------
    # Grundlegende Hilfe
    # -----------------------------------------------------------------

    def _ensure_table(self, table: str) -> Dict[str, Any]:
        if table not in self.tables:
            raise TableNotFoundError(f"Tabelle {table!r} existiert nicht.")
        return self.tables[table]

    def _copy_state(self) -> Dict[str, Dict[str, Any]]:
        return copy.deepcopy(self.tables)

    def _primary_key_column(self, table: str) -> Optional[str]:
        t = self._ensure_table(table)
        for col, cfg in t["schema"].items():
            if cfg["primary_key"]:
                return col
        return None

    def _freeze_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return tuple(sorted((k, self._freeze_value(v)) for k, v in value.items()))
        if isinstance(value, list):
            return tuple(self._freeze_value(v) for v in value)
        if isinstance(value, StructValue):
            return ("StructValue", value.name, tuple(sorted((k, self._freeze_value(v)) for k, v in value.fields.items())))
        if isinstance(value, ClassValue):
            return ("ClassValue", value.name, tuple(value.fields), tuple(value.methods), tuple(value.base_classes))
        if isinstance(value, FunctionValue):
            return ("FunctionValue", value.name, value.domain_name, value.codomain_name, value.pure)
        if isinstance(value, NetworkValue):
            return ("NetworkValue", value.name, tuple(value.nodes), tuple(value.edges), value.directed, tuple(value.protocols))
        if isinstance(value, TopologyValue):
            return ("TopologyValue", value.name, tuple(value.carrier), tuple(tuple(x) for x in value.opens))
        if isinstance(value, MathCategoryValue):
            return ("MathCategoryValue", value.name, tuple((o.name, self._freeze_value(o.payload)) for o in value.objects), tuple((m.name, m.source, m.target) for m in value.morphisms))
        return value

    # -----------------------------------------------------------------
    # Typprüfung
    # -----------------------------------------------------------------

    def _check_type(self, type_name: str, value: Any) -> bool:
        if type_name == "any":
            return True
        if type_name == "int":
            return isinstance(value, int) and not isinstance(value, bool)
        if type_name == "float":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if type_name == "str":
            return isinstance(value, str)
        if type_name == "bool":
            return isinstance(value, bool)
        if type_name == "dict":
            return isinstance(value, dict)
        if type_name == "list":
            return isinstance(value, list)
        if type_name == "struct":
            return isinstance(value, StructValue)
        if type_name == "function":
            return isinstance(value, FunctionValue)
        if type_name == "class":
            return isinstance(value, ClassValue)
        if type_name == "network":
            return isinstance(value, NetworkValue)
        if type_name == "topology":
            return isinstance(value, TopologyValue)
        if type_name == "math_category":
            return isinstance(value, MathCategoryValue)
        return False

    def _normalize_schema(self, schema: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        normalized: Dict[str, Dict[str, Any]] = {}
        primary_keys: List[str] = []

        for column, config in schema.items():
            if not isinstance(config, dict):
                raise SchemaError(f"Schema für Spalte {column!r} muss ein Dict sein.")

            col_type = config.get("type", "any")
            if col_type not in self.SUPPORTED_TYPES:
                raise SchemaError(
                    f"Nicht unterstützter Typ {col_type!r} für Spalte {column!r}."
                )

            entry = {
                "type": col_type,
                "nullable": bool(config.get("nullable", True)),
                "unique": bool(config.get("unique", False)),
                "primary_key": bool(config.get("primary_key", False)),
                "default": config.get("default", None),
                "foreign_key": config.get("foreign_key"),
            }

            if entry["primary_key"]:
                primary_keys.append(column)
                entry["nullable"] = False
                entry["unique"] = True

            fk = entry["foreign_key"]
            if fk is not None:
                if (
                    not isinstance(fk, (tuple, list))
                    or len(fk) != 2
                    or not all(isinstance(x, str) for x in fk)
                ):
                    raise SchemaError(
                        f"foreign_key von Spalte {column!r} muss ('tabelle', 'spalte') sein."
                    )
                entry["foreign_key"] = (fk[0], fk[1])

            normalized[column] = entry

        if len(primary_keys) > 1:
            raise SchemaError(
                "Diese Minimal-Datenbank unterstützt genau null oder einen Primärschlüssel pro Tabelle."
            )

        return normalized

    # -----------------------------------------------------------------
    # Tabellen
    # -----------------------------------------------------------------

    def create_table(self, table: str, schema: Dict[str, Dict[str, Any]]) -> None:
        if table in self.tables:
            raise TableExistsError(f"Tabelle {table!r} existiert bereits.")

        normalized_schema = self._normalize_schema(schema)
        self.tables[table] = {
            "schema": normalized_schema,
            "rows": [],
            "indexes": {},
            "meta": {"row_id_counter": 1},
        }

    def drop_table(self, table: str) -> None:
        self._ensure_table(table)
        del self.tables[table]

    def list_tables(self) -> List[str]:
        return sorted(self.tables.keys())

    def table_schema(self, table: str) -> Dict[str, Dict[str, Any]]:
        return copy.deepcopy(self._ensure_table(table)["schema"])

    # -----------------------------------------------------------------
    # Indexe
    # -----------------------------------------------------------------

    def create_index(self, table: str, column: str) -> None:
        t = self._ensure_table(table)
        if column not in t["schema"]:
            raise SchemaError(f"Spalte {column!r} existiert nicht.")
        index: Dict[Any, List[int]] = {}
        for row in t["rows"]:
            value = row["data"].get(column)
            index.setdefault(self._freeze_value(value), []).append(row["_id"])
        t["indexes"][column] = index

    def _rebuild_indexes(self, table: str) -> None:
        t = self._ensure_table(table)
        index_cols = list(t["indexes"].keys())
        t["indexes"] = {}
        for col in index_cols:
            self.create_index(table, col)

    def _update_indexes_for_insert(self, table: str, row: Dict[str, Any], row_id: int) -> None:
        t = self._ensure_table(table)
        for col, idx in t["indexes"].items():
            idx.setdefault(self._freeze_value(row.get(col)), []).append(row_id)

    # -----------------------------------------------------------------
    # Constraints / Rows
    # -----------------------------------------------------------------

    def _validate_structure_semantics(self, table: str, row: Dict[str, Any]) -> None:
        t = self._ensure_table(table)
        for col, cfg in t["schema"].items():
            value = row.get(col)
            if value is None:
                continue
            ty = cfg["type"]

            if ty == "network" and not value.validate():
                raise ConstraintError(f"Ungültiges Netzwerk in {table}.{col}.")
            if ty == "topology" and not value.validate():
                raise ConstraintError(f"Ungültige Topologie in {table}.{col}.")
            if ty == "math_category":
                object_names = value.object_names()
                for m in value.morphisms:
                    if m.source not in object_names or m.target not in object_names:
                        raise ConstraintError(
                            f"Ungültige math_category in {table}.{col}: Morphismus {m.name!r} verweist auf unbekanntes Objekt."
                        )

    def _build_row(self, table: str, values: Dict[str, Any]) -> Dict[str, Any]:
        t = self._ensure_table(table)
        row: Dict[str, Any] = {}

        for column, cfg in t["schema"].items():
            if column in values:
                val = values[column]
            else:
                val = copy.deepcopy(cfg["default"])

            if val is None and not cfg["nullable"]:
                raise ConstraintError(f"Spalte {table}.{column} darf nicht NULL sein.")

            if val is not None and not self._check_type(cfg["type"], val):
                raise ConstraintError(
                    f"Falscher Typ für {table}.{column}: {val!r} passt nicht zu {cfg['type']!r}."
                )

            row[column] = val

        extra_columns = set(values.keys()) - set(t["schema"].keys())
        if extra_columns:
            raise SchemaError(f"Unbekannte Spalten für Tabelle {table!r}: {sorted(extra_columns)}")

        self._validate_structure_semantics(table, row)
        return row

    def _check_unique_constraints(self, table: str, row: Dict[str, Any], *, ignore_row_id: Optional[int] = None) -> None:
        t = self._ensure_table(table)
        for col, cfg in t["schema"].items():
            if not cfg["unique"]:
                continue
            value = row.get(col)
            frozen = self._freeze_value(value)
            for existing in t["rows"]:
                if ignore_row_id is not None and existing["_id"] == ignore_row_id:
                    continue
                if self._freeze_value(existing["data"].get(col)) == frozen:
                    raise ConstraintError(
                        f"Unique-Constraint verletzt in {table}.{col} für Wert {value!r}."
                    )

    def _check_foreign_keys(self, table: str, row: Dict[str, Any]) -> None:
        t = self._ensure_table(table)
        for col, cfg in t["schema"].items():
            fk = cfg.get("foreign_key")
            if not fk:
                continue

            value = row.get(col)
            if value is None:
                continue

            ref_table, ref_col = fk
            rt = self._ensure_table(ref_table)
            found = False
            for existing in rt["rows"]:
                if self._freeze_value(existing["data"].get(ref_col)) == self._freeze_value(value):
                    found = True
                    break

            if not found:
                raise ConstraintError(
                    f"Fremdschlüssel verletzt: {table}.{col} verweist auf nicht vorhandenes {ref_table}.{ref_col}."
                )

    def _check_delete_references(self, table: str, rows_to_delete: List[Dict[str, Any]]) -> None:
        pk_col = self._primary_key_column(table)
        if pk_col is None:
            return

        values_to_delete = {self._freeze_value(row["data"][pk_col]) for row in rows_to_delete}

        for other_name, other in self.tables.items():
            for col, cfg in other["schema"].items():
                fk = cfg.get("foreign_key")
                if fk == (table, pk_col):
                    for existing in other["rows"]:
                        if self._freeze_value(existing["data"].get(col)) in values_to_delete:
                            raise ConstraintError(
                                f"Löschen verhindert: {other_name}.{col} referenziert noch {table}.{pk_col}."
                            )

    # -----------------------------------------------------------------
    # Filter
    # -----------------------------------------------------------------

    def where(self, column: str, op: str, value: Any) -> Dict[str, Any]:
        return {"column": column, "op": op, "value": value}

    def _match_condition(self, current: Any, op: str, expected: Any) -> bool:
        if op == "==":
            return self._freeze_value(current) == self._freeze_value(expected)
        if op == "!=":
            return self._freeze_value(current) != self._freeze_value(expected)
        if op == ">":
            return current is not None and current > expected
        if op == ">=":
            return current is not None and current >= expected
        if op == "<":
            return current is not None and current < expected
        if op == "<=":
            return current is not None and current <= expected
        if op == "in":
            return current in expected
        if op == "contains":
            return expected in current if current is not None else False
        if op == "startswith":
            return isinstance(current, str) and current.startswith(expected)
        if op == "endswith":
            return isinstance(current, str) and current.endswith(expected)
        raise MiniDatabaseError(f"Unbekannter Operator {op!r}.")

    def _row_matches(
        self,
        row: Dict[str, Any],
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> bool:
        if conditions:
            for cond in conditions:
                if not self._match_condition(row.get(cond["column"]), cond["op"], cond["value"]):
                    return False
        if predicate and not predicate(row):
            return False
        return True

    # -----------------------------------------------------------------
    # CRUD
    # -----------------------------------------------------------------

    def insert(self, table: str, values: Dict[str, Any]) -> Dict[str, Any]:
        t = self._ensure_table(table)
        row = self._build_row(table, values)
        self._check_unique_constraints(table, row)
        self._check_foreign_keys(table, row)

        row_id = t["meta"]["row_id_counter"]
        t["meta"]["row_id_counter"] += 1

        internal_row = {"_id": row_id, "data": row}
        t["rows"].append(internal_row)
        self._update_indexes_for_insert(table, row, row_id)
        return copy.deepcopy(row)

    def insert_many(self, table: str, rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for row in rows:
            out.append(self.insert(table, row))
        return out

    def select(
        self,
        table: str,
        *,
        columns: Optional[Sequence[str]] = None,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
        order_by: Optional[Union[str, Sequence[str]]] = None,
        descending: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        t = self._ensure_table(table)

        if columns is not None:
            unknown = set(columns) - set(t["schema"].keys())
            if unknown:
                raise SchemaError(f"Unbekannte Spalten in select: {sorted(unknown)}")

        rows = [
            copy.deepcopy(r["data"])
            for r in t["rows"]
            if self._row_matches(r["data"], conditions, predicate)
        ]

        if order_by is not None:
            order_cols = [order_by] if isinstance(order_by, str) else list(order_by)
            rows.sort(
                key=lambda r: tuple(self._freeze_value(r.get(col)) for col in order_cols),
                reverse=descending,
            )

        if offset:
            rows = rows[offset:]
        if limit is not None:
            rows = rows[:limit]

        if columns is not None:
            rows = [{col: row.get(col) for col in columns} for row in rows]

        return rows

    def select_one(
        self,
        table: str,
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> Dict[str, Any]:
        rows = self.select(table, conditions=conditions, predicate=predicate, limit=1)
        if not rows:
            raise RowNotFoundError(f"Kein Datensatz gefunden in {table!r}.")
        return rows[0]

    def update(
        self,
        table: str,
        values: Dict[str, Any],
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> int:
        t = self._ensure_table(table)
        unknown = set(values.keys()) - set(t["schema"].keys())
        if unknown:
            raise SchemaError(f"Unbekannte Spalten in update: {sorted(unknown)}")

        updated = 0
        for internal_row in t["rows"]:
            current = internal_row["data"]
            if not self._row_matches(current, conditions, predicate):
                continue

            candidate = copy.deepcopy(current)
            for col, val in values.items():
                cfg = t["schema"][col]
                if val is None and not cfg["nullable"]:
                    raise ConstraintError(f"Spalte {table}.{col} darf nicht NULL sein.")
                if val is not None and not self._check_type(cfg["type"], val):
                    raise ConstraintError(
                        f"Falscher Typ für {table}.{col}: {val!r} passt nicht zu {cfg['type']!r}."
                    )
                candidate[col] = val

            self._validate_structure_semantics(table, candidate)
            self._check_unique_constraints(table, candidate, ignore_row_id=internal_row["_id"])
            self._check_foreign_keys(table, candidate)

            internal_row["data"] = candidate
            updated += 1

        if updated:
            self._rebuild_indexes(table)
        return updated

    def delete(
        self,
        table: str,
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> int:
        t = self._ensure_table(table)
        to_delete = [r for r in t["rows"] if self._row_matches(r["data"], conditions, predicate)]
        if not to_delete:
            return 0
        self._check_delete_references(table, to_delete)
        delete_ids = {r["_id"] for r in to_delete}
        t["rows"] = [r for r in t["rows"] if r["_id"] not in delete_ids]
        self._rebuild_indexes(table)
        return len(to_delete)

    # -----------------------------------------------------------------
    # Gewöhnliche DB-Operationen
    # -----------------------------------------------------------------

    def count(self, table: str, *, conditions=None, predicate=None) -> int:
        t = self._ensure_table(table)
        return sum(1 for r in t["rows"] if self._row_matches(r["data"], conditions, predicate))

    def exists(self, table: str, *, conditions=None, predicate=None) -> bool:
        return self.count(table, conditions=conditions, predicate=predicate) > 0

    def get_by_primary_key(self, table: str, value: Any) -> Dict[str, Any]:
        pk = self._primary_key_column(table)
        if pk is None:
            raise SchemaError(f"Tabelle {table!r} hat keinen Primärschlüssel.")
        return self.select_one(table, conditions=[self.where(pk, "==", value)])

    def find_by_index(self, table: str, column: str, value: Any) -> List[Dict[str, Any]]:
        t = self._ensure_table(table)
        if column not in t["indexes"]:
            raise MiniDatabaseError(f"Für {table}.{column} existiert kein Index.")
        row_ids = t["indexes"][column].get(self._freeze_value(value), [])
        id_set = set(row_ids)
        return [copy.deepcopy(r["data"]) for r in t["rows"] if r["_id"] in id_set]

    def join(
        self,
        left_table: str,
        right_table: str,
        *,
        left_on: str,
        right_on: str,
        how: str = "inner",
        select_left: Optional[Sequence[str]] = None,
        select_right: Optional[Sequence[str]] = None,
        left_prefix: str = "",
        right_prefix: str = "",
        right_conditions: Optional[Sequence[Dict[str, Any]]] = None,
        left_conditions: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        if how not in {"inner", "left"}:
            raise MiniDatabaseError("Join-Art muss 'inner' oder 'left' sein.")

        lt = self._ensure_table(left_table)
        rt = self._ensure_table(right_table)

        left_rows = self.select(left_table, conditions=left_conditions)
        right_rows = self.select(right_table, conditions=right_conditions)

        if select_left is None:
            select_left = list(lt["schema"].keys())
        if select_right is None:
            select_right = list(rt["schema"].keys())

        result = []
        right_lookup: Dict[Any, List[Dict[str, Any]]] = {}
        for row in right_rows:
            right_lookup.setdefault(self._freeze_value(row.get(right_on)), []).append(row)

        for lrow in left_rows:
            matches = right_lookup.get(self._freeze_value(lrow.get(left_on)), [])
            if matches:
                for rrow in matches:
                    joined = {}
                    for col in select_left:
                        joined[f"{left_prefix}{col}"] = lrow.get(col)
                    for col in select_right:
                        joined[f"{right_prefix}{col}"] = rrow.get(col)
                    result.append(joined)
            elif how == "left":
                joined = {}
                for col in select_left:
                    joined[f"{left_prefix}{col}"] = lrow.get(col)
                for col in select_right:
                    joined[f"{right_prefix}{col}"] = None
                result.append(joined)

        return result

    def aggregate(self, table: str, column: str, func: str, *, conditions=None, predicate=None) -> Any:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        values = [row.get(column) for row in rows if row.get(column) is not None]
        if func == "count":
            return len(values)
        if func == "sum":
            return sum(values)
        if func == "avg":
            return sum(values) / len(values) if values else None
        if func == "min":
            return min(values) if values else None
        if func == "max":
            return max(values) if values else None
        raise MiniDatabaseError(f"Unbekannte Aggregation {func!r}.")

    def group_by(self, table: str, by: str, aggregations: Dict[str, Tuple[str, str]], *, conditions=None, predicate=None) -> List[Dict[str, Any]]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        groups: Dict[Any, List[Dict[str, Any]]] = {}
        for row in rows:
            groups.setdefault(self._freeze_value(row.get(by)), []).append(row)

        result = []
        for _, members in groups.items():
            group_value = members[0].get(by)
            out = {by: group_value}
            for out_name, (func, column) in aggregations.items():
                values = [r.get(column) for r in members if r.get(column) is not None]
                if func == "count":
                    out[out_name] = len(values)
                elif func == "sum":
                    out[out_name] = sum(values)
                elif func == "avg":
                    out[out_name] = sum(values) / len(values) if values else None
                elif func == "min":
                    out[out_name] = min(values) if values else None
                elif func == "max":
                    out[out_name] = max(values) if values else None
                else:
                    raise MiniDatabaseError(f"Unbekannte Aggregation {func!r}.")
            result.append(out)
        return result

    # -----------------------------------------------------------------
    # Struktur-Operationen auf Tabelleninhalten
    # -----------------------------------------------------------------

    def apply_function_value(
        self,
        table: str,
        function_column: str,
        input_value: Any,
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[Any]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        results = []
        for row in rows:
            f = row.get(function_column)
            if not isinstance(f, FunctionValue):
                raise StructureError(f"{table}.{function_column} enthält keinen FunctionValue.")
            results.append(f(input_value))
        return results

    def compose_function_rows(
        self,
        table: str,
        first_conditions: Sequence[Dict[str, Any]],
        second_conditions: Sequence[Dict[str, Any]],
        *,
        output_name: str,
    ) -> FunctionValue:
        f = self.select_one(table, conditions=first_conditions)
        g = self.select_one(table, conditions=second_conditions)

        fval = f[next(k for k, v in f.items() if isinstance(v, FunctionValue))]
        gval = g[next(k for k, v in g.items() if isinstance(v, FunctionValue))]

        if not isinstance(fval, FunctionValue) or not isinstance(gval, FunctionValue):
            raise StructureError("Zeilen enthalten keine komponierbaren FunctionValue-Objekte.")
        return fval.compose(gval, name=output_name)

    def project_structs(
        self,
        table: str,
        struct_column: str,
        field_names: Sequence[str],
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[StructValue]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        out = []
        for row in rows:
            s = row.get(struct_column)
            if not isinstance(s, StructValue):
                raise StructureError(f"{table}.{struct_column} enthält keinen StructValue.")
            out.append(s.project(field_names))
        return out

    def rename_struct_fields(
        self,
        table: str,
        struct_column: str,
        mapping: Dict[str, str],
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[StructValue]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        out = []
        for row in rows:
            s = row.get(struct_column)
            if not isinstance(s, StructValue):
                raise StructureError(f"{table}.{struct_column} enthält keinen StructValue.")
            out.append(s.rename_fields(mapping))
        return out

    def network_subnetworks(
        self,
        table: str,
        network_column: str,
        node_subset: Sequence[Any],
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[NetworkValue]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        out = []
        for row in rows:
            n = row.get(network_column)
            if not isinstance(n, NetworkValue):
                raise StructureError(f"{table}.{network_column} enthält keinen NetworkValue.")
            out.append(n.induced_subnetwork(node_subset))
        return out

    def topology_subspaces(
        self,
        table: str,
        topology_column: str,
        subset: Sequence[Any],
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[TopologyValue]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        out = []
        for row in rows:
            topo = row.get(topology_column)
            if not isinstance(topo, TopologyValue):
                raise StructureError(f"{table}.{topology_column} enthält keinen TopologyValue.")
            out.append(topo.subspace(subset))
        return out

    def class_inheritance_pairs(
        self,
        table: str,
        class_column: str,
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[Tuple[ClassValue, ClassValue]]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        classes = []
        for row in rows:
            c = row.get(class_column)
            if not isinstance(c, ClassValue):
                raise StructureError(f"{table}.{class_column} enthält keinen ClassValue.")
            classes.append(c)

        out = []
        for a in classes:
            for b in classes:
                if a.name != b.name and a.inherits_from(b):
                    out.append((a, b))
        return out

    def compose_category_morphisms(
        self,
        table: str,
        category_column: str,
        *,
        g_name: str,
        f_name: str,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[CategoryMorphismValue]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        out = []
        for row in rows:
            cat = row.get(category_column)
            if not isinstance(cat, MathCategoryValue):
                raise StructureError(f"{table}.{category_column} enthält keinen MathCategoryValue.")
            out.append(cat.compose_symbolic(g_name, f_name))
        return out

    # -----------------------------------------------------------------
    # Transaktionen
    # -----------------------------------------------------------------

    def begin(self) -> None:
        self._transaction_stack.append(self._copy_state())

    def commit(self) -> None:
        if not self._transaction_stack:
            raise MiniDatabaseError("Keine aktive Transaktion.")
        self._transaction_stack.pop()

    def rollback(self) -> None:
        if not self._transaction_stack:
            raise MiniDatabaseError("Keine aktive Transaktion.")
        self.tables = self._transaction_stack.pop()

    # -----------------------------------------------------------------
    # Persistenz
    # -----------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        serial_tables = copy.deepcopy(self.tables)
        for table_name, table in serial_tables.items():
            for row in table["rows"]:
                row["data"] = {k: _serialize_value(v) for k, v in row["data"].items()}
        return {
            "name": self.name,
            "tables": serial_tables,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MiniDatabase":
        db = cls(name=data.get("name", "database"))
        db.tables = copy.deepcopy(data.get("tables", {}))
        for table_name, table in db.tables.items():
            for row in table["rows"]:
                row["data"] = {k: _deserialize_value(v) for k, v in row["data"].items()}
        return db

    def save_json(self, path: Union[str, Path]) -> None:
        path = Path(path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_json(cls, path: Union[str, Path]) -> "MiniDatabase":
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    # -----------------------------------------------------------------
    # CSV
    # -----------------------------------------------------------------

    def export_csv(self, table: str, path: Union[str, Path]) -> None:
        t = self._ensure_table(table)
        path = Path(path)
        fieldnames = list(t["schema"].keys())
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in t["rows"]:
                serial = {}
                for k, v in row["data"].items():
                    if isinstance(v, (StructValue, FunctionValue, ClassValue, NetworkValue, TopologyValue, MathCategoryValue)):
                        serial[k] = json.dumps(_serialize_value(v), ensure_ascii=False)
                    else:
                        serial[k] = v
                writer.writerow(serial)

    # -----------------------------------------------------------------
    # Meta
    # -----------------------------------------------------------------

    def info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tables": {
                table_name: {
                    "row_count": len(table_data["rows"]),
                    "columns": list(table_data["schema"].keys()),
                    "primary_key": self._primary_key_column(table_name),
                    "indexes": list(table_data["indexes"].keys()),
                }
                for table_name, table_data in self.tables.items()
            },
        }

    def __repr__(self) -> str:
        return f"MiniDatabase(name={self.name!r}, tables={list(self.tables.keys())!r})"


if __name__ == "__main__":
    db = MiniDatabase("extended-demo")

    db.create_table(
        "artifacts",
        {
            "id": {"type": "int", "primary_key": True},
            "kind": {"type": "str", "nullable": False},
            "struct_obj": {"type": "struct", "nullable": True},
            "function_obj": {"type": "function", "nullable": True},
            "class_obj": {"type": "class", "nullable": True},
            "network_obj": {"type": "network", "nullable": True},
            "topology_obj": {"type": "topology", "nullable": True},
            "category_obj": {"type": "math_category", "nullable": True},
        },
    )

    s = StructValue("Person", {"id": 1, "name": "Ada", "email": "ada@example.org"})
    f = FunctionValue("succ", "int", "int", impl=lambda x: x + 1)
    c = ClassValue("User", ["id", "name", "email"], ["save", "login"])
    n = NetworkValue("NetA", ["a", "b", "c"], [("a", "b"), ("b", "c")], True, ["tcp"])
    t = TopologyValue("Discrete2", [1, 2], [[], [1], [2], [1, 2]])
    mc = MathCategoryValue(
        "SmallCat",
        objects=[CategoryObjectValue("A"), CategoryObjectValue("B")],
        morphisms=[CategoryMorphismValue("f", "A", "B")],
    )

    db.insert("artifacts", {"id": 1, "kind": "struct", "struct_obj": s})
    db.insert("artifacts", {"id": 2, "kind": "function", "function_obj": f})
    db.insert("artifacts", {"id": 3, "kind": "class", "class_obj": c})
    db.insert("artifacts", {"id": 4, "kind": "network", "network_obj": n})
    db.insert("artifacts", {"id": 5, "kind": "topology", "topology_obj": t})
    db.insert("artifacts", {"id": 6, "kind": "category", "category_obj": mc})

    print(db.select("artifacts"))
    print(db.project_structs("artifacts", "struct_obj", ["id", "name"], conditions=[db.where("kind", "==", "struct")]))
    print(db.apply_function_value("artifacts", "function_obj", 10, conditions=[db.where("kind", "==", "function")]))
    print(db.network_subnetworks("artifacts", "network_obj", ["a", "b"], conditions=[db.where("kind", "==", "network")]))
    print(db.topology_subspaces("artifacts", "topology_obj", [1], conditions=[db.where("kind", "==", "topology")]))
