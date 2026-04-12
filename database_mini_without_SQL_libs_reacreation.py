
# mini_database.py
from __future__ import annotations

import copy
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple


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


@dataclass
class _Condition:
    column: str
    op: str
    value: Any


class MiniDatabase:
    """
    Eine minimalistische relationale Datenbank ohne SQL und ohne externe Datenbank-Bibliotheken.

    Merkmale:
    - mehrere Tabellen
    - Schema pro Tabelle
    - Datentyp-Prüfung
    - Primärschlüssel
    - Unique / Not Null / Default
    - Fremdschlüssel
    - CRUD-Operationen
    - Filtern, Sortieren, Limit, Projektion
    - Inner / Left Join
    - Add / Drop / Rename Column
    - Transaktionen (einfaches Snapshot-Modell)
    - JSON persistieren / laden
    - CSV Import / Export
    - Indexe für exakte Werte
    """

    SUPPORTED_TYPES = {"int", "float", "str", "bool", "dict", "list", "any"}

    def __init__(self, name: str = "database") -> None:
        self.name = name
        self.tables: Dict[str, Dict[str, Any]] = {}
        self._transaction_stack: List[Dict[str, Dict[str, Any]]] = []

    # ---------------------------------------------------------------------
    # Hilfsmethoden: Schema / Typen
    # ---------------------------------------------------------------------

    def _ensure_table(self, table: str) -> Dict[str, Any]:
        if table not in self.tables:
            raise TableNotFoundError(f"Tabelle {table!r} existiert nicht.")
        return self.tables[table]

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
                "foreign_key": config.get("foreign_key"),  # ("table", "column")
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
        return False

    def _copy_state(self) -> Dict[str, Dict[str, Any]]:
        return copy.deepcopy(self.tables)

    def _primary_key_column(self, table: str) -> Optional[str]:
        t = self._ensure_table(table)
        for col, cfg in t["schema"].items():
            if cfg["primary_key"]:
                return col
        return None

    # ---------------------------------------------------------------------
    # Tabellenverwaltung
    # ---------------------------------------------------------------------

    def create_table(self, table: str, schema: Dict[str, Dict[str, Any]]) -> None:
        if table in self.tables:
            raise TableExistsError(f"Tabelle {table!r} existiert bereits.")

        normalized_schema = self._normalize_schema(schema)

        self.tables[table] = {
            "schema": normalized_schema,
            "rows": [],
            "indexes": {},   # column -> {value -> [row_ids]}
            "meta": {
                "row_id_counter": 1,
            },
        }

    def drop_table(self, table: str) -> None:
        self._ensure_table(table)
        del self.tables[table]

    def rename_table(self, old_name: str, new_name: str) -> None:
        if old_name not in self.tables:
            raise TableNotFoundError(f"Tabelle {old_name!r} existiert nicht.")
        if new_name in self.tables:
            raise TableExistsError(f"Tabelle {new_name!r} existiert bereits.")

        self.tables[new_name] = self.tables.pop(old_name)

        # Fremdschlüssel-Verweise anderer Tabellen aktualisieren
        for t in self.tables.values():
            for col, cfg in t["schema"].items():
                fk = cfg.get("foreign_key")
                if fk and fk[0] == old_name:
                    cfg["foreign_key"] = (new_name, fk[1])

    def list_tables(self) -> List[str]:
        return sorted(self.tables.keys())

    def table_schema(self, table: str) -> Dict[str, Dict[str, Any]]:
        t = self._ensure_table(table)
        return copy.deepcopy(t["schema"])

    def add_column(self, table: str, column: str, config: Dict[str, Any]) -> None:
        t = self._ensure_table(table)
        if column in t["schema"]:
            raise SchemaError(f"Spalte {column!r} existiert bereits in {table!r}.")

        normalized = self._normalize_schema({column: config})[column]
        if normalized["primary_key"]:
            raise SchemaError("Primärschlüssel nachträglich hinzufügen wird hier nicht unterstützt.")

        t["schema"][column] = normalized

        default = normalized.get("default", None)
        nullable = normalized.get("nullable", True)

        for row in t["rows"]:
            if default is None and not nullable:
                raise SchemaError(
                    f"Neue Spalte {column!r} ist nicht nullable und hat keinen Default."
                )
            row["data"][column] = copy.deepcopy(default)

        self._rebuild_indexes(table)

    def drop_column(self, table: str, column: str) -> None:
        t = self._ensure_table(table)
        if column not in t["schema"]:
            raise SchemaError(f"Spalte {column!r} existiert nicht.")

        if t["schema"][column]["primary_key"]:
            raise SchemaError("Primärschlüsselspalte kann nicht gelöscht werden.")

        del t["schema"][column]
        t["indexes"].pop(column, None)

        for row in t["rows"]:
            row["data"].pop(column, None)

        # Fremdschlüssel, die auf diese Spalte zeigen, verhindern
        for other_name, other_table in self.tables.items():
            for other_col, other_cfg in other_table["schema"].items():
                fk = other_cfg.get("foreign_key")
                if fk == (table, column):
                    raise SchemaError(
                        f"Spalte {table}.{column} wird noch als Fremdschlüssel von "
                        f"{other_name}.{other_col} referenziert."
                    )

    def rename_column(self, table: str, old_name: str, new_name: str) -> None:
        t = self._ensure_table(table)
        if old_name not in t["schema"]:
            raise SchemaError(f"Spalte {old_name!r} existiert nicht.")
        if new_name in t["schema"]:
            raise SchemaError(f"Spalte {new_name!r} existiert bereits.")

        t["schema"][new_name] = t["schema"].pop(old_name)
        if old_name in t["indexes"]:
            t["indexes"][new_name] = t["indexes"].pop(old_name)

        for row in t["rows"]:
            row["data"][new_name] = row["data"].pop(old_name)

        for other_table in self.tables.values():
            for other_col, cfg in other_table["schema"].items():
                fk = cfg.get("foreign_key")
                if fk == (table, old_name):
                    cfg["foreign_key"] = (table, new_name)

        self._rebuild_indexes(table)

    # ---------------------------------------------------------------------
    # Indexe
    # ---------------------------------------------------------------------

    def create_index(self, table: str, column: str) -> None:
        t = self._ensure_table(table)
        if column not in t["schema"]:
            raise SchemaError(f"Spalte {column!r} existiert nicht.")

        index: Dict[Any, List[int]] = {}
        for row in t["rows"]:
            value = row["data"].get(column)
            index.setdefault(self._freeze_value(value), []).append(row["_id"])
        t["indexes"][column] = index

    def drop_index(self, table: str, column: str) -> None:
        t = self._ensure_table(table)
        t["indexes"].pop(column, None)

    def _freeze_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return tuple(sorted((k, self._freeze_value(v)) for k, v in value.items()))
        if isinstance(value, list):
            return tuple(self._freeze_value(v) for v in value)
        return value

    def _rebuild_indexes(self, table: str) -> None:
        t = self._ensure_table(table)
        existing = list(t["indexes"].keys())
        t["indexes"] = {}
        for col in existing:
            self.create_index(table, col)

    def _update_indexes_for_insert(self, table: str, row: Dict[str, Any], row_id: int) -> None:
        t = self._ensure_table(table)
        for col, idx in t["indexes"].items():
            value = self._freeze_value(row.get(col))
            idx.setdefault(value, []).append(row_id)

    # ---------------------------------------------------------------------
    # Constraints
    # ---------------------------------------------------------------------

    def _build_row(self, table: str, values: Dict[str, Any]) -> Dict[str, Any]:
        t = self._ensure_table(table)
        row: Dict[str, Any] = {}

        for column, cfg in t["schema"].items():
            if column in values:
                val = values[column]
            else:
                val = copy.deepcopy(cfg["default"])

            if val is None and not cfg["nullable"]:
                raise ConstraintError(
                    f"Spalte {table}.{column} darf nicht NULL sein."
                )

            if val is not None and not self._check_type(cfg["type"], val):
                raise ConstraintError(
                    f"Falscher Typ für {table}.{column}: {val!r} passt nicht zu {cfg['type']!r}."
                )

            row[column] = val

        extra_columns = set(values.keys()) - set(t["schema"].keys())
        if extra_columns:
            raise SchemaError(
                f"Unbekannte Spalten für Tabelle {table!r}: {sorted(extra_columns)}"
            )

        return row

    def _check_unique_constraints(
        self,
        table: str,
        row: Dict[str, Any],
        *,
        ignore_row_id: Optional[int] = None,
    ) -> None:
        t = self._ensure_table(table)

        for col, cfg in t["schema"].items():
            if not cfg["unique"]:
                continue

            value = row.get(col)
            for existing in t["rows"]:
                if ignore_row_id is not None and existing["_id"] == ignore_row_id:
                    continue
                if existing["data"].get(col) == value:
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

            if ref_col not in rt["schema"]:
                raise ConstraintError(
                    f"Fremdschlüsselziel {ref_table}.{ref_col} existiert nicht."
                )

            found = False
            for existing in rt["rows"]:
                if existing["data"].get(ref_col) == value:
                    found = True
                    break

            if not found:
                raise ConstraintError(
                    f"Fremdschlüssel verletzt: {table}.{col}={value!r} verweist auf "
                    f"nicht vorhandenes {ref_table}.{ref_col}."
                )

    def _check_delete_references(self, table: str, rows_to_delete: List[Dict[str, Any]]) -> None:
        pk_col = self._primary_key_column(table)
        if pk_col is None:
            return

        values_to_delete = {row["data"][pk_col] for row in rows_to_delete}

        for other_name, other in self.tables.items():
            for col, cfg in other["schema"].items():
                fk = cfg.get("foreign_key")
                if fk == (table, pk_col):
                    for existing in other["rows"]:
                        if existing["data"].get(col) in values_to_delete:
                            raise ConstraintError(
                                f"Löschen verhindert: {other_name}.{col} referenziert noch "
                                f"{table}.{pk_col}."
                            )

    # ---------------------------------------------------------------------
    # Filter / Bedingungen
    # ---------------------------------------------------------------------

    def where(self, column: str, op: str, value: Any) -> Dict[str, Any]:
        return {"column": column, "op": op, "value": value}

    def _match_condition(self, current: Any, op: str, expected: Any) -> bool:
        if op == "==":
            return current == expected
        if op == "!=":
            return current != expected
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
                col = cond["column"]
                op = cond["op"]
                value = cond["value"]
                if not self._match_condition(row.get(col), op, value):
                    return False

        if predicate and not predicate(row):
            return False

        return True

    # ---------------------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------------------

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
        inserted = []
        for row in rows:
            inserted.append(self.insert(table, row))
        return inserted

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
            for col in order_cols:
                if col not in t["schema"]:
                    raise SchemaError(f"Sortierspalte {col!r} existiert nicht.")

            rows.sort(
                key=lambda r: tuple(r.get(col) for col in order_cols),
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

    def count(
        self,
        table: str,
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> int:
        t = self._ensure_table(table)
        return sum(
            1 for r in t["rows"]
            if self._row_matches(r["data"], conditions, predicate)
        )

    def exists(
        self,
        table: str,
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> bool:
        return self.count(table, conditions=conditions, predicate=predicate) > 0

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

    def truncate(self, table: str) -> None:
        t = self._ensure_table(table)
        self._check_delete_references(table, t["rows"])
        t["rows"] = []
        self._rebuild_indexes(table)

    # ---------------------------------------------------------------------
    # Lookup per Index / PK
    # ---------------------------------------------------------------------

    def get_by_primary_key(self, table: str, value: Any) -> Dict[str, Any]:
        pk = self._primary_key_column(table)
        if pk is None:
            raise SchemaError(f"Tabelle {table!r} hat keinen Primärschlüssel.")
        return self.select_one(table, conditions=[self.where(pk, "==", value)])

    def find_by_index(self, table: str, column: str, value: Any) -> List[Dict[str, Any]]:
        t = self._ensure_table(table)
        if column not in t["indexes"]:
            raise MiniDatabaseError(
                f"Für {table}.{column} existiert kein Index."
            )

        row_ids = t["indexes"][column].get(self._freeze_value(value), [])
        id_set = set(row_ids)
        return [
            copy.deepcopy(r["data"])
            for r in t["rows"]
            if r["_id"] in id_set
        ]

    # ---------------------------------------------------------------------
    # Joins
    # ---------------------------------------------------------------------

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

        if left_on not in lt["schema"]:
            raise SchemaError(f"Spalte {left_table}.{left_on} existiert nicht.")
        if right_on not in rt["schema"]:
            raise SchemaError(f"Spalte {right_table}.{right_on} existiert nicht.")

        left_rows = self.select(left_table, conditions=left_conditions)
        right_rows = self.select(right_table, conditions=right_conditions)

        if select_left is None:
            select_left = list(lt["schema"].keys())
        if select_right is None:
            select_right = list(rt["schema"].keys())

        result = []
        right_lookup: Dict[Any, List[Dict[str, Any]]] = {}
        for row in right_rows:
            right_lookup.setdefault(row.get(right_on), []).append(row)

        for lrow in left_rows:
            matches = right_lookup.get(lrow.get(left_on), [])
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

    # ---------------------------------------------------------------------
    # Aggregation
    # ---------------------------------------------------------------------

    def aggregate(
        self,
        table: str,
        column: str,
        func: str,
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> Any:
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

    def group_by(
        self,
        table: str,
        by: str,
        aggregations: Dict[str, Tuple[str, str]],
        *,
        conditions: Optional[Sequence[Dict[str, Any]]] = None,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[Dict[str, Any]]:
        rows = self.select(table, conditions=conditions, predicate=predicate)
        groups: Dict[Any, List[Dict[str, Any]]] = {}

        for row in rows:
            groups.setdefault(row.get(by), []).append(row)

        result = []
        for group_value, members in groups.items():
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

    # ---------------------------------------------------------------------
    # Transaktionen
    # ---------------------------------------------------------------------

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

    # ---------------------------------------------------------------------
    # Persistenz
    # ---------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tables": copy.deepcopy(self.tables),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MiniDatabase":
        db = cls(name=data.get("name", "database"))
        db.tables = copy.deepcopy(data.get("tables", {}))
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

    # ---------------------------------------------------------------------
    # CSV Import / Export
    # ---------------------------------------------------------------------

    def export_csv(self, table: str, path: Union[str, Path]) -> None:
        t = self._ensure_table(table)
        path = Path(path)

        fieldnames = list(t["schema"].keys())
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in t["rows"]:
                writer.writerow(row["data"])

    def import_csv(
        self,
        table: str,
        path: Union[str, Path],
        *,
        cast: bool = True,
    ) -> int:
        t = self._ensure_table(table)
        path = Path(path)
        inserted = 0

        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for raw_row in reader:
                row = {}
                for col, value in raw_row.items():
                    cfg = t["schema"][col]
                    if value == "":
                        row[col] = None
                    elif not cast:
                        row[col] = value
                    else:
                        row[col] = self._cast_from_string(value, cfg["type"])
                self.insert(table, row)
                inserted += 1

        return inserted

    def _cast_from_string(self, value: str, type_name: str) -> Any:
        if type_name == "str" or type_name == "any":
            return value
        if type_name == "int":
            return int(value)
        if type_name == "float":
            return float(value)
        if type_name == "bool":
            low = value.strip().lower()
            if low in {"true", "1", "yes", "ja"}:
                return True
            if low in {"false", "0", "no", "nein"}:
                return False
            raise MiniDatabaseError(f"Kann {value!r} nicht als bool lesen.")
        if type_name in {"dict", "list"}:
            return json.loads(value)
        return value

    # ---------------------------------------------------------------------
    # Meta / Diagnose
    # ---------------------------------------------------------------------

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
    db = MiniDatabase("demo")

    db.create_table(
        "users",
        {
            "id": {"type": "int", "primary_key": True},
            "name": {"type": "str", "nullable": False},
            "email": {"type": "str", "unique": True, "nullable": False},
            "age": {"type": "int", "default": 0},
        },
    )

    db.create_table(
        "posts",
        {
            "id": {"type": "int", "primary_key": True},
            "user_id": {"type": "int", "foreign_key": ("users", "id"), "nullable": False},
            "title": {"type": "str", "nullable": False},
            "likes": {"type": "int", "default": 0},
        },
    )

    db.insert("users", {"id": 1, "name": "Ada", "email": "ada@example.org", "age": 36})
    db.insert("users", {"id": 2, "name": "Linus", "email": "linus@example.org", "age": 30})

    db.insert("posts", {"id": 10, "user_id": 1, "title": "First post", "likes": 5})
    db.insert("posts", {"id": 11, "user_id": 1, "title": "Second post", "likes": 2})
    db.insert("posts", {"id": 12, "user_id": 2, "title": "Kernel notes", "likes": 9})

    print(db.select("users", order_by="age"))
    print(db.join("users", "posts", left_on="id", right_on="user_id", left_prefix="user_", right_prefix="post_"))
    print(db.group_by("posts", "user_id", {"post_count": ("count", "id"), "like_sum": ("sum", "likes")}))
