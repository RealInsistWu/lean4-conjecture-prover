# Lean4 Conjecture Prover

A compact Codex / Agent Skills workflow for difficult mathematical conjectures:
adaptive independent discovery, adversarial proof auditing, and Lean 4 verification.

Derived from [conjecture-prover](https://github.com/RealInsistWu/conjecture-prover).
The core prompt is deliberately small. Detailed instructions are loaded only
when needed; deterministic checks are delegated to a script.

## What it does

- Preserves the exact conjecture, its logical negation, and its acceptance criteria.
- Searches independent mathematical mechanisms and dynamically reallocates agents
  when supported by the runtime.
- Rejects circular reasoning, unproved target-strength reductions, invalid
  counterexamples, and empirical evidence presented as proof.
- Supports isolated, literature-assisted, and hybrid research.
- Checks named Lean declarations and their transitive axiom dependencies.
- Records material progress for long-running research without replaying every transcript.

This is a skill, not a standalone theorem-proving model or autonomous agent server.
Actual agent concurrency, tools, permissions, compute, and context limits are
determined by the host. The 64-agent ceiling is not a promised capability.

## Install

Extract the ZIP. Copy the entire `lean4-conjecture-prover/` directory into
your Codex user skills directory, typically `~/.agents/skills/`, or the
repository's `.agents/skills/` directory.

```sh
mkdir -p ~/.agents/skills
cp -R ./lean4-conjecture-prover ~/.agents/skills/
```

If you later publish this repository under the intended name, you can also clone
your published repository directly into that directory. Restart or open a new
Codex session if the skill is not immediately discovered.

For Codex skill setup, see the [official skill guide](https://learn.chatgpt.com/docs/build-skills).
The ZIP also follows the single-top-level-folder layout used by the
[OpenAI Skills API](https://developers.openai.com/api/docs/guides/tools-skills).

## Use

```text
Use $lean4-conjecture-prover to prove or disprove the following conjecture.
Work in isolated mode. Verify a surviving result in Lean 4 if available.
[Exact statement]
```

```text
Use $lean4-conjecture-prover in research mode.
Search relevant literature, explore independent mechanisms,
and produce a rigorously audited proof with a Lean 4 formalization.
[Exact statement]
```

```text
Use $lean4-conjecture-prover to audit this proof.
Require a machine-checked Lean 4 proof of the exact conclusion.
[Statement and candidate proof]
```

### Source modes

| Mode | Behavior |
| --- | --- |
| `isolated` (default) | Background mathematics only; no target answers or status lookup. |
| `research` (opt-in) | Relevant literature and existing results are permitted and cited. |
| `hybrid` (opt-in) | Start isolated; switch at an agreed checkpoint and record the transition. |

Isolation is a research protocol, not a guarantee that a pretrained model has
never encountered the problem. The user may impose stricter search boundaries.

### Lean 4

Use an existing trusted Lean/Lake project with a pinned `lean-toolchain`.
For mathlib proofs, use that project's compatible mathlib version. The skill does
not install Lean or download mathlib automatically.

Requirements for the helper: Python 3.9+ and Lake on `PATH`.

For a theorem named `MyProject.result` in `MyProject.Proof`:

```sh
python3 /path/to/lean4-conjecture-prover/scripts/verify_lean.py \
  --project /path/to/lean-project \
  --module MyProject.Proof \
  --theorem MyProject.result
```

For a quick smoke test, copy `examples/Demo.lean` into a library module in your
own Lake project, then pass the corresponding module name and
`--theorem ConjectureDemo.add_comm`.

The script builds the module, imports it in a fresh temporary audit file, prints
the declaration's type and checks the reported transitive axioms. Its strict
allowlist is `propext`, `Classical.choice`, and `Quot.sound`. It rejects unknown
axioms, missing/ambiguous reports, `sorry` warnings, build errors and timeouts.
Use `--theorem` repeatedly to check multiple declarations, and `--timeout` to
adjust the per-command limit. Identifiers supplied to this helper must use
ordinary ASCII dotted Lean names; for other names, audit manually.

Exit code 0 and `MECHANICAL_PASS` are **not** a statement-equivalence verdict:
the exact elaborated theorem, its definitions, and its scope still need review.
Only then may the skill report formalization `PASS`. A clean build of the wrong
theorem does not prove the conjecture.

Run Lean and Lake only on trusted code or in a suitable sandbox. The helper is
not a security boundary, does not independently validate arbitrary compiler
artifacts, and cannot establish novelty. Use a trusted toolchain and clean
build when provenance is uncertain. The strict allowlist may reject otherwise
acceptable native-computation proofs; see
[Lean's proof validation guide](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## Repository layout

```text
lean4-conjecture-prover/
├── SKILL.md                  # Small, always-loaded skill body after invocation
├── README.md                 # Installation and usage
├── agents/openai.yaml        # Codex UI metadata
├── references/
│   ├── search.md             # Adaptive multi-agent search and adversarial audit
│   ├── sources.md            # Source boundaries and provenance
│   └── lean.md               # Formalization and verification protocol
├── assets/checkpoint.md      # Optional persistent research template
├── scripts/verify_lean.py     # Lake build + axiom audit, standard library only
├── examples/Demo.lean         # Minimal demonstration theorem
├── tests/test_verify_lean.py  # Python unit tests (mocked Lean workflow)
├── .github/workflows/tests.yml
└── .gitignore
```

## Prompt budget and design choices

The initial `SKILL.md` contains about 550 whitespace-separated English words
(roughly 4 KB). Actual token count depends on the model tokenizer. The metadata
is used for discovery; the body is loaded on invocation. Detailed references
are not intended to be read automatically.

Simple conjectures should be solved directly; substantial ones warrant
independent search and a sparse dependency ledger. Update the checkpoint only
when material mathematical progress occurs or before handoff. Agent packets
should contain the contract and relevant evidence, not the entire conversation.
This reduces context overhead without promising a fixed inference-token cost.

The default isolated policy and 64-agent ceiling are retained from the original
project. Literature-assisted search is opt-in. Lean verification is attempted
when feasible; a rigorous informal result and its machine verification status
are reported separately unless the user requires formalization.

## Tests

```sh
python -m unittest discover -s tests -v
```

The packaged tests cover accepted standard axioms, forbidden axioms, missing or
ambiguous audit output, invalid identifiers, missing Lake, build failures,
`sorry` warnings, and the simulated build/audit workflow. They passed in the
packaging environment. Lean/Lake was not installed there, so end-to-end real
Lean compilation has not yet been tested. The example is provided for that
purpose. No head-to-head mathematical benchmark or token-usage evaluation has
been performed.

## 中文快速说明

新版保留原版证明契约、动态搜索、方法去重及独立审查，新增可选文献模式、
Lean 4 公理审计和研究断点模板。默认 `isolated`，不会主动检索目标猜想的
答案。复杂研究才加载相应参考文件，不要求每次都执行全部管理流程。

使用 `$lean4-conjecture-prover` 并给出完整数学命题即可。若需要文献辅助，
明确指定 `research` 或 `hybrid`；若要求最终必须通过 Lean 4，明确写出该要求。
没有真正运行 Lean 时，不会声称机器验证成功。

本仓库未擅自指定开源许可证；发布者可根据原项目权利与意愿选择许可证。
