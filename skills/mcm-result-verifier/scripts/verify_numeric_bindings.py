#!/usr/bin/env python3
"""Compare a numeric binding registry with real CSV/JSON files, using stdlib only.

CSV row indexes count data rows from zero. JSON keys are strings or nonnegative
array indexes. Source paths (including symlink targets) must remain under --root.
Exit 0 only when every binding passes; malformed input produces an ERROR report.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
from decimal import Decimal, DecimalException, InvalidOperation, localcontext
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import stat
import tempfile
from typing import Any


REQUIRED = {"id", "file", "selector", "expected", "abs_tol", "rel_tol", "unit"}
COMPARISON_RULE = (
    "abs(actual-expected) <= max(abs_tol, "
    "rel_tol * max(abs(actual), abs(expected)))"
)
MAX_COMPARISON_DIGITS = 1_100_000


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def finite_json(value):
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError("JSON numbers must be finite")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("JSON numbers must be finite")
    if isinstance(value, dict):
        for item in value.values():
            finite_json(item)
    elif isinstance(value, list):
        for item in value:
            finite_json(item)


def load_decimal_json(text):
    return json.loads(text, parse_float=Decimal, parse_constant=Decimal,
                      object_pairs_hook=unique_object)


def finite_number(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError(f"{name} must be a finite JSON number")
    number = value if isinstance(value, Decimal) else Decimal(str(value))
    if not number.is_finite():
        raise ValueError(f"{name} must be finite")
    return number


def within_root(root: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("referenced file resolves outside the project root") from exc
    if not resolved.is_file():
        raise ValueError("referenced file does not exist or is not a regular file")
    return resolved


def read_source(root: Path, file: str, selector: Any, result: dict) -> Decimal:
    path = within_root(root, file)
    data = path.read_bytes()
    source_sha256 = hashlib.sha256(data).hexdigest()
    result.update({"source_path": str(path.relative_to(root)),
                   "source_sha256": source_sha256})
    if not isinstance(selector, dict):
        raise ValueError("selector must be an object")
    if path.suffix.lower() == ".csv":
        if set(selector) != {"row", "column"}:
            raise ValueError("CSV selector must contain only row and column")
        row, column = selector["row"], selector["column"]
        if isinstance(row, bool) or not isinstance(row, int) or row < 0:
            raise ValueError("CSV row must be a nonnegative data-row index")
        if not isinstance(column, str) or not column:
            raise ValueError("CSV column must be a nonempty header name")
        reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""), strict=True)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError("CSV headers must be unique")
        if headers.count(column) != 1:
            raise ValueError("CSV column must exist exactly once in the header")
        selected = None
        for index, record in enumerate(reader):
            if None in record or any(value is None for value in record.values()):
                raise ValueError("CSV record width does not match the header")
            if index == row:
                selected = record[column]
        if selected is None:
            raise ValueError("CSV row is absent or selected cell is missing")
        try:
            actual = Decimal(selected.strip())
        except InvalidOperation as exc:
            raise ValueError("selected CSV cell is not numeric") from exc
        if not actual.is_finite():
            raise ValueError("selected CSV cell must be finite")
    elif path.suffix.lower() == ".json":
        if set(selector) != {"keys"} or not isinstance(selector["keys"], list):
            raise ValueError("JSON selector must contain only a keys array")
        selected = load_decimal_json(data.decode("utf-8-sig"))
        finite_json(selected)
        for key in selector["keys"]:
            if isinstance(key, str):
                if not isinstance(selected, dict):
                    raise ValueError("JSON string key requires an object")
                if key not in selected:
                    raise ValueError(f"JSON key is absent: {key}")
                selected = selected[key]
            elif isinstance(key, int) and not isinstance(key, bool) and key >= 0:
                if not isinstance(selected, list) or key >= len(selected):
                    raise ValueError("JSON array index is absent or not an array")
                selected = selected[key]
            else:
                raise ValueError("JSON keys must be strings or nonnegative indexes")
        actual = finite_number(selected, "selected JSON value")
    else:
        raise ValueError("only .csv and .json source files are supported")
    return actual


def report_number(value: Decimal) -> int | float | str:
    """Use ordinary JSON numbers when safe, with a string for extreme magnitudes."""
    numeric = float(value)
    if not math.isfinite(numeric) or (numeric == 0 and value != 0):
        return str(value)
    if value == value.to_integral_value() and value.adjusted() <= 308:
        return int(value)
    return numeric if Decimal(str(numeric)) == value else str(value)


def json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return report_number(value) if value.is_finite() else str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    return value


def verify_binding(root: Path, binding: Any, duplicates: set[str], index: int) -> dict:
    result: dict[str, Any] = {"index": index, "status": "ERROR"}
    if not isinstance(binding, dict):
        result["message"] = "binding must be an object"
        return result
    for name in ("id", "file", "selector", "expected", "abs_tol", "rel_tol", "unit"):
        result[name] = json_safe(binding.get(name))
    result["source_sha256"] = None
    try:
        missing = sorted(REQUIRED - set(binding))
        if missing:
            raise ValueError(f"missing required fields: {', '.join(missing)}")
        identifier = binding["id"]
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("id must be a nonempty string")
        if identifier in duplicates:
            raise ValueError(f"duplicate binding id: {identifier}")
        if not isinstance(binding["file"], str) or not binding["file"].strip():
            raise ValueError("file must be a nonempty path string")
        if not isinstance(binding["unit"], str):
            raise ValueError("unit must be a string (empty is allowed for dimensionless)")
        actual = read_source(root, binding["file"], binding["selector"], result)
        result.update({"actual": report_number(actual), "actual_decimal": str(actual)})
        expected = finite_number(binding["expected"], "expected")
        abs_tol = finite_number(binding["abs_tol"], "abs_tol")
        rel_tol = finite_number(binding["rel_tol"], "rel_tol")
        if abs_tol < 0 or rel_tol < 0:
            raise ValueError("tolerances must be nonnegative")
        with localcontext() as context:
            # Subtraction needs the exponent span, not only coefficient length.
            # Extend exponent limits too, so tiny finite values never become zero.
            values = (actual, expected, abs_tol, rel_tol)
            operands = [value for value in (actual, expected) if value != 0]
            exponent_span = (max(value.adjusted() for value in operands)
                             - min(value.as_tuple().exponent for value in operands)
                             + 1) if operands else 1
            product_digits = len(rel_tol.as_tuple().digits) + max(
                len(actual.as_tuple().digits), len(expected.as_tuple().digits)
            )
            precision = max(50, exponent_span, product_digits,
                            *(len(value.as_tuple().digits) for value in values)) + 2
            if precision > MAX_COMPARISON_DIGITS:
                raise ValueError("exact comparison exceeds the precision resource budget")
            context.prec = precision
            magnitude = max(actual.copy_abs(), expected.copy_abs())
            context.Emin = min(context.Emin, *(value.as_tuple().exponent for value in values),
                               rel_tol.as_tuple().exponent + magnitude.as_tuple().exponent)
            context.Emax = max(context.Emax, *(value.adjusted() for value in values),
                               rel_tol.adjusted() + magnitude.adjusted() + 2)
            difference = abs(actual - expected)
            tolerance = max(abs_tol, rel_tol * magnitude)
            passed = difference <= tolerance
        result.update({"absolute_difference": report_number(difference),
                       "allowed_difference": report_number(tolerance),
                       "status": "PASS" if passed else "FAIL",
                       "message": "within tolerance" if passed else "outside tolerance"})
    except (ValueError, TypeError, RuntimeError, OSError, UnicodeError, csv.Error,
            DecimalException, RecursionError) as exc:
        result["message"] = str(exc)
    return result


def verify(root: Path, registry_path: Path) -> dict:
    report: dict[str, Any] = {
        "schema_version": 1,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "bindings_path": str(registry_path),
        "comparison_rule": COMPARISON_RULE,
        "registry_sha256": None,
        "status": "ERROR",
        "errors": [],
        "results": [],
    }
    try:
        if not root.is_dir():
            raise ValueError("project root does not exist or is not a directory")
        registry_path = within_root(root, str(registry_path))
        registry_data = registry_path.read_bytes()
        report["registry_sha256"] = hashlib.sha256(registry_data).hexdigest()
        registry = load_decimal_json(registry_data.decode("utf-8-sig"))
        if not isinstance(registry, dict):
            raise ValueError("registry must be an object with a bindings array")
        bindings = registry.get("bindings")
        if not isinstance(bindings, list) or not bindings:
            raise ValueError("bindings must be a nonempty array")
        if "schema_version" in registry and (type(registry["schema_version"]) is not int
                                             or registry["schema_version"] != 1):
            raise ValueError("schema_version must be integer 1 when declared")
        for field in ("freeze_id", "run_id"):
            if field in registry:
                if not isinstance(registry[field], str) or not registry[field].strip():
                    raise ValueError(f"{field} must be a nonempty string when declared")
                report[field] = json_safe(registry[field])
        counts = Counter(item["id"] for item in bindings
                         if isinstance(item, dict) and isinstance(item.get("id"), str))
        duplicates = {identifier for identifier, count in counts.items() if count > 1}
        report["results"] = [verify_binding(root, item, duplicates, index)
                             for index, item in enumerate(bindings)]
        finite_json(registry)
        statuses = {item["status"] for item in report["results"]}
        report["status"] = "ERROR" if "ERROR" in statuses else (
            "FAIL" if "FAIL" in statuses else "PASS"
        )
    except (ValueError, TypeError, RuntimeError, OSError, UnicodeError, RecursionError) as exc:
        report["status"] = "ERROR"
        report["errors"].append(str(exc))
    report["summary"] = {state: sum(item["status"] == state for item in report["results"])
                         for state in ("PASS", "FAIL", "ERROR")}
    report["summary"]["total"] = len(report["results"])
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="project root")
    parser.add_argument("--bindings", required=True, type=Path,
                        help="registry path, relative to project root if not absolute")
    parser.add_argument("--output", required=True, type=Path,
                        help="report path, relative to project root if not absolute")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"Cannot resolve project root: {exc}", file=sys.stderr)
        return 2
    bindings_path = args.bindings if args.bindings.is_absolute() else root / args.bindings
    output = args.output if args.output.is_absolute() else root / args.output
    report = verify(root, bindings_path)
    try:
        resolved_output = output.resolve()
        try:
            resolved_output.relative_to(root)
        except ValueError as exc:
            raise ValueError("output resolves outside the project root") from exc
        sources = set()
        for item in report["results"]:
            if isinstance(item.get("file"), str):
                source = Path(item["file"])
                try:
                    sources.add((source if source.is_absolute() else root / source).resolve())
                except (ValueError, RuntimeError, OSError):
                    # Invalid source paths have already produced an ERROR item.
                    continue
        protected = sources | {bindings_path.resolve()}
        same_file = (output.exists() and any(path.exists() and output.samefile(path)
                                            for path in protected))
        if resolved_output in protected or same_file:
            raise ValueError("output must not overwrite the registry or a source file")
        if resolved_output.is_relative_to(root / "inputs"):
            raise ValueError("output cannot modify the read-only input area")
        for component in (output, *output.parents):
            if component.resolve() == root:
                break
            if component.is_symlink():
                raise ValueError("output cannot use a symlinked project path")
        previous = None
        if output.exists():
            info = output.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not info.st_mode & 0o222:
                raise ValueError("output cannot replace an alias, directory or read-only artifact")
            prior = load_decimal_json(output.read_text(encoding="utf-8-sig"))
            finite_json(prior)
            if (not isinstance(prior, dict) or type(prior.get("schema_version")) is not int
                    or prior["schema_version"] != 1 or prior.get("comparison_rule") != COMPARISON_RULE
                    or prior.get("status") not in ["PASS", "FAIL", "ERROR"]
                    or not isinstance(prior.get("results"), list)
                    or not isinstance(prior.get("summary"), dict)):
                raise ValueError("output cannot replace an unrelated existing artifact")
            previous = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        output.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                             prefix=".numeric-review-", delete=False) as handle:
                temp_path = Path(handle.name)
                handle.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
                             + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            if previous is None:
                os.link(temp_path, output)
            else:
                info = output.stat()
                current = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
                if current != previous or info.st_nlink != 1:
                    raise ValueError("output changed during preparation; refusing replacement")
                os.replace(temp_path, output)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
    except (ValueError, TypeError, RuntimeError, OSError, RecursionError) as exc:
        print(f"Cannot write report: {exc}", file=sys.stderr)
        return 2
    print(f"{report['status']}: {report['summary']['total']} bindings; report={output}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
