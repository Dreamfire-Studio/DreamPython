from __future__ import annotations
from typing import Any, Dict, Optional, Callable, Mapping, Iterable, Tuple
import json
import pathlib
import tempfile
import os
import sys

Json = Dict[str, Any]
SchemaRule = Tuple[type | tuple[type, ...], Optional[Callable[[Any], bool]]]
Schema = Mapping[str, SchemaRule]

def load_json(path: pathlib.Path, default: Optional[Any] = None) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception as e:
        print(f"[JsonController] Failed to parse {path}: {e}", file=sys.stderr)
        return default

def save_json(path: pathlib.Path, data: Any, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tmp:
        json.dump(data, tmp, indent=indent, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name
    os.replace(tmp_name, path)

def deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = {k: v for k, v in base.items()}
        for k, v in override.items():
            if k in merged:
                merged[k] = deep_merge(merged[k], v)
            else:
                merged[k] = v
        return merged
    return override

def load_and_merge(path: pathlib.Path, defaults: Optional[Any] = None, create_if_missing: bool = False) -> Any:
    data = load_json(path, default=None)
    if data is None:
        result = defaults if defaults is not None else {}
        if create_if_missing:
            try:
                save_json(path, result)
            except Exception as e:
                print(f"[JsonController] Failed to create {path}: {e}", file=sys.stderr)
        return result
    return deep_merge(defaults if defaults is not None else {}, data)

def get_in(data: Any, path: str, default: Any = None) -> Any:
    if not path:
        return data
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict):
            if part in cur:
                cur = cur[part]
            else:
                return default
        elif isinstance(cur, list):
            try:
                idx = int(part)
            except ValueError:
                return default
            if 0 <= idx < len(cur):
                cur = cur[idx]
            else:
                return default
        else:
            return default
    return cur

def set_in(data: Any, path: str, value: Any, create_missing: bool = True) -> bool:
    if not path:
        return False
    parts = path.split(".")
    cur = data
    for i, part in enumerate(parts[:-1]):
        nxt = parts[i + 1]
        if isinstance(cur, dict):
            if part not in cur:
                if not create_missing:
                    return False
                cur[part] = [] if nxt.isdigit() else {}
            cur = cur[part]
        elif isinstance(cur, list):
            if not part.isdigit():
                return False
            idx = int(part)
            if idx < 0:
                return False
            while len(cur) <= idx:
                cur.append({} if not nxt.isdigit() else [])
            cur = cur[idx]
        else:
            return False

    last = parts[-1]
    if isinstance(cur, dict):
        cur[last] = value
        return True
    if isinstance(cur, list) and last.isdigit():
        idx = int(last)
        if idx < 0:
            return False
        while len(cur) <= idx:
            cur.append(None)
        cur[idx] = value
        return True
    return False

def validate(data: Any, schema: Schema) -> bool:
    ok = True
    for path, rule in schema.items():
        expected, predicate = rule
        val = get_in(data, path, default=None)
        if not isinstance(val, expected):
            print(f"[JsonController] Validation failed at '{path}': expected {expected}, got {type(val).__name__}",
                  file=sys.stderr)
            ok = False
            continue
        if predicate and not predicate(val):
            print(f"[JsonController] Validation predicate failed at '{path}' (value: {val})", file=sys.stderr)
            ok = False
    return ok