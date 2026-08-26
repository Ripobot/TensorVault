#!/usr/bin/env python3
"""
Simple prompt linter for TensorVault prompt files.

Checks:
- File parses as YAML or JSON.
- Required top-level metadata fields exist.
- recommended_parameters contains temperature and top_p in expected ranges.
- Prompt text doesn't contain obvious secrets or disallowed keywords (basic heuristics).
- Warns on probable PII (emails, phone numbers) found in the prompt body.

Usage:
  python3 scripts/prompt_lint.py prompts/system/**/*.yaml
  python3 scripts/prompt_lint.py prompts/system/openai/example-prompt.yaml

Dependencies:
  pip install PyYAML
"""
from pathlib import Path
import sys
import argparse
import yaml
import json
import re

REQUIRED_FIELDS = {"id", "title", "purpose", "model_family", "prompt", "recommended_parameters", "safety_notes"}
PII_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PII_PHONE_RE = re.compile(r"\+?\d[\d\-\s]{7,}\d")
SECRET_KEYWORDS = ["api_key", "apikey", "password", "secret", "private_key", "ssh-rsa"]

def load_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".json"}:
            return json.loads(text)
        else:
            return yaml.safe_load(text)
    except Exception as e:
        raise RuntimeError(f"Failed to parse {path}: {e}")

def check_required_fields(data, path):
    if not isinstance(data, dict):
        return [f"<root>: Document must be a mapping/object (found {type(data).__name__})"]
    missing = REQUIRED_FIELDS - set(data.keys())
    errors = []
    if missing:
        errors.append(f"Missing required fields: {sorted(list(missing))}")
    return errors

def check_recommended_parameters(data):
    errors = []
    rp = data.get("recommended_parameters", {})
    if not isinstance(rp, dict):
        return ["recommended_parameters must be an object"]
    # temperature
    temp = rp.get("temperature")
    if temp is None:
        errors.append("recommended_parameters.temperature is required")
    else:
        try:
            t = float(temp)
            if not (0.0 <= t <= 2.0):
                errors.append(f"temperature {t} out of typical range [0.0, 2.0]")
        except Exception:
            errors.append("temperature must be a number")
    top_p = rp.get("top_p")
    if top_p is None:
        errors.append("recommended_parameters.top_p is required")
    else:
        try:
            p = float(top_p)
            if not (0.0 <= p <= 1.0):
                errors.append(f"top_p {p} out of range [0.0, 1.0]")
        except Exception:
            errors.append("top_p must be a number")
    # optional max_tokens
    if "max_tokens" in rp:
        try:
            m = int(rp["max_tokens"])
            if m < 0:
                errors.append("max_tokens must be >= 0")
        except Exception:
            errors.append("max_tokens must be an integer")
    return errors

def check_prompt_content(data):
    errors = []
    warnings = []
    prompt_field = data.get("prompt")
    if prompt_field is None:
        return errors, warnings
    # Prompt can be string or list
    if isinstance(prompt_field, list):
        text = "\n".join(str(x) for x in prompt_field)
    else:
        text = str(prompt_field)

    # Check for secret-looking keywords
    lowered = text.lower()
    for kw in SECRET_KEYWORDS:
        if kw in lowered:
            errors.append(f"Potential secret keyword found in prompt text: '{kw}'")

    # Basic PII checks (warn)
    if PII_EMAIL_RE.search(text):
        warnings.append("Potential email address found in prompt text (remove real emails).")
    if PII_PHONE_RE.search(text):
        warnings.append("Potential phone number found in prompt text (remove real phone numbers).")

    # Very basic credit-card-like detection (warn)
    cc_like = re.search(r"\b(?:\d[ -]*?){13,19}\b", text)
    if cc_like:
        warnings.append("Long numeric sequence found (possible credit card number). Remove or redact.")

    return errors, warnings

def lint_path(path: Path):
    results = {"path": str(path), "ok": True, "errors": [], "warnings": []}
    try:
        data = load_file(path)
    except Exception as e:
        results["ok"] = False
        results["errors"].append(str(e))
        return results

    # Required fields
    results["errors"].extend(check_required_fields(data, path))
    # recommended_parameters checks
    results["errors"].extend(check_recommended_parameters(data))
    # prompt content checks
    p_errs, p_warns = check_prompt_content(data)
    results["errors"].extend(p_errs)
    results["warnings"].extend(p_warns)

    if results["errors"]:
        results["ok"] = False
    return results

def main(argv):
    p = argparse.ArgumentParser(description="Lint prompt YAML/JSON files for basic metadata & safety checks")
    p.add_argument("files", nargs="+", help="File path(s) or glob pattern(s) to lint")
    args = p.parse_args(argv)

    any_failed = False
    from glob import glob
    paths = []
    for pattern in args.files:
        if any(ch in pattern for ch in ["*", "?", "["]):
            paths.extend(sorted([Path(p) for p in glob(pattern, recursive=True)]))
        else:
            paths.append(Path(pattern))

    if not paths:
        print("No files found for given patterns.", file=sys.stderr)
        return 2

    for path in paths:
        if not path.exists():
            print(f"[MISSING] {path}")
            any_failed = True
            continue
        res = lint_path(path)
        if res["ok"]:
            print(f"[OK]     {res['path']}")
        else:
            any_failed = True
            print(f"[FAIL]   {res['path']}")
            for e in res["errors"]:
                print(f"         - ERROR: {e}")
            for w in res["warnings"]:
                print(f"         - WARN:  {w}")

    return (2 if any_failed else 0)

if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
