# Lean 4 verification

Load before formalizing or claiming machine verification.

1. Use an existing trusted Lean/Lake project if possible; respect its `lean-toolchain`, Lake configuration, mathlib version, and manifest. Do not silently install dependencies, modify user projects, or download large caches. Ask before costly setup if authorization is unclear. If Lean is absent, preserve the mathematical result and label formalization NOT RUN.
2. Freeze the original informal contract. Formalize its exact domain, quantifiers, definitions, and conclusion (or exact logical negation). Have a separate reviewer compare the elaborated statement and any custom definitions against the contract. Preserve this statement while editing proofs. Reject vacuous assumptions, weaker statements, circular restatements, restricted domains, and hidden target hypotheses.
3. Use Lean for high-risk lemmas when helpful; do not force full formalization of every exploratory branch. For the final theorem, prefer explicit structure and available standard lemmas. Source-mode restrictions still apply to mathlib searches. Check the mathematical meaning of imported results.
4. Build in the pinned environment. No `sorry`, `admit`, `sorryAx`, custom axioms, or opaque computational trust assumptions may discharge an obligation. Ordinary kernel-checked classical proofs may use `propext`, `Classical.choice`, and `Quot.sound`. The strict checker rejects every other transitive axiom, including native-computation trust axioms. Use kernel-checkable alternatives when possible.
5. Run the bundled checker against the final module and fully qualified theorem names:

   ```sh
   python3 <skill-dir>/scripts/verify_lean.py --project /path/to/lean-project \
     --module MyProject.Proof --theorem MyProject.result
   ```

   The checker builds the module, imports it in a fresh audit file, prints the theorem type, and audits transitive axioms. It exits nonzero on missing tools, build errors, missing or ambiguous axiom output, unexpected axioms, or timeout. Repeat `--theorem` for additional claims. Save its JSON output if a reproducible record is needed.

   If the script cannot run but Lean is available, manually use `lake build +MyProject.Proof` and run a separate file importing the module with `#check @MyProject.result` and `#print axioms MyProject.result` via `lake env lean Audit.lean`. Inspect the result rather than relying on an editor screenshot or exit code alone.

6. Review the printed type, definitions, imports, and exact statement independently. The script checks the compiled declaration and its reported axioms, not whether it expresses the user's conjecture. Use a clean trusted build and inspect sources if provenance is uncertain. Re-run after relevant edits. Do not execute untrusted Lean or Lake code outside a suitable sandbox; build scripts, tactics, macros, imports, and native code may execute arbitrary code.

Report `PASS` only after a successful mechanical check and statement review. Otherwise use `STATEMENT NOT VALIDATED`, `FAILED`, or `NOT RUN` as appropriate, even if the informal proof looks sound. State the Lean version, module, theorem, command, axiom list, and any remaining gap. If Lean was mandatory and unavailable or failed, the requested formal proof is incomplete.

Reference: https://lean-lang.org/doc/reference/latest/ValidatingProofs/
