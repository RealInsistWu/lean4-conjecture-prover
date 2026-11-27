#!/usr/bin/env python3
"""Build and audit named Lean declarations in a trusted existing Lake project.

This is a conservative evidence collector, not a security sandbox, statement
equivalence checker, or proof of novelty. Requires Python 3.9+ and Lake.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ALLOWED_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)*")
SORRY_WARNING = re.compile(r"declaration uses ['‘`]sorry['’`]", re.I)


class CheckError(Exception):
    pass


def identifier(value):
    if not IDENT.fullmatch(value) or value.startswith("_root_."):
        raise argparse.ArgumentTypeError(
            "use an ordinary ASCII dotted, fully qualified Lean identifier"
        )
    return value


def run(command, project, timeout):
    try:
        result = subprocess.run(
            command, cwd=project, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired as exc:
        raise CheckError(f"timed out after {timeout}s: {' '.join(command)}") from exc
    except OSError as exc:
        raise CheckError(f"could not execute {command[0]}: {exc}") from exc
    output = result.stdout + "\n" + result.stderr
    if result.returncode:
        raise CheckError(
            f"exit {result.returncode}: {' '.join(command)}\n{output[-8000:]}"
        )
    return output


def parse_axioms(output, theorem):
    quoted = re.escape("'" + theorem + "'")
    pattern = (
        r"(?m)^[ \t]*" + quoted +
        r"(?:[ \t]+does not depend on any axioms[ \t]*$|"
        r"[ \t]+depends on axioms:[ \t\r\n]*\[([^\]]*)\][ \t]*$)"
    )
    matches = list(re.finditer(pattern, output))
    if len(matches) != 1:
        raise CheckError(f"missing or ambiguous axiom report for {theorem}")
    raw = matches[0].group(1)
    axioms = [] if raw is None or not raw.strip() else [
        item.strip() for item in raw.split(",")
    ]
    unexpected = sorted(set(axioms) - ALLOWED_AXIOMS)
    if unexpected:
        raise CheckError(f"{theorem} depends on disallowed axioms: {unexpected}")
    return axioms


def verify(project, module, theorems, timeout):
    report = {
        "status": "FAILED",
        "statement_review": "REQUIRED",
        "project": str(project),
        "module": module,
        "theorems": theorems,
        "allowed_axioms": sorted(ALLOWED_AXIOMS),
        "checks": {},
    }
    try:
        if not project.is_dir() or not any(
            (project / f).is_file() for f in ("lakefile.lean", "lakefile.toml")
        ):
            raise CheckError("project must be an existing Lake project")
        lake = shutil.which("lake")
        if not lake:
            raise CheckError("Lake not found on PATH; no formal check performed")
        report["lean_version"] = run(
            [lake, "env", "lean", "--version"], project, timeout
        ).strip()
        # +Module explicitly requests the Lean module target rather than a
        # potentially identically named package target.
        build = run([lake, "build", "+" + module], project, timeout)
        if SORRY_WARNING.search(build):
            raise CheckError("build emitted a sorry warning")
        # Use a temporary valid module path inside the project root so that
        # Lean can infer a module name; never edit the candidate proof.
        with tempfile.TemporaryDirectory(prefix="Lean4Audit_", dir=project) as directory:
            audit = Path(directory) / "Audit.lean"
            lines = [f"import {module}", ""]
            for theorem in theorems:
                lines.extend([f"#check @{theorem}", f"#print axioms {theorem}"])
            audit.write_text("\n".join(lines) + "\n", encoding="utf-8")
            relative = str(audit.relative_to(project))
            output = run([lake, "env", "lean", relative], project, timeout)
        report["audit_output"] = output.strip()
        if SORRY_WARNING.search(output):
            raise CheckError("audit emitted a sorry warning")
        for theorem in theorems:
            report["checks"][theorem] = {"axioms": parse_axioms(output, theorem)}
        report["status"] = "MECHANICAL_PASS"
    except (CheckError, OSError) as exc:
        report["error"] = str(exc)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--module", type=identifier, required=True)
    parser.add_argument("--theorem", type=identifier, action="append", required=True)
    parser.add_argument("--timeout", type=int, default=600,
                        help="maximum seconds per subprocess (default: 600)")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    if len(set(args.theorem)) != len(args.theorem):
        parser.error("duplicate --theorem values")
    report = verify(args.project.resolve(), args.module, args.theorem, args.timeout)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "MECHANICAL_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
