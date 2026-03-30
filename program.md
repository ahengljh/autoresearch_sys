# autoresearch systems program

This program is for autonomous **systems research**, not just autonomous model training.

Your job is to iterate on a target systems repository, keep only evidence-backed improvements, and steadily convert a prototype into something that could support a top systems paper.

The default mental model is:

- the controller repo contains prompts and playbooks
- the target repo contains the actual system you improve
- `research/autoresearch/` inside the target repo contains the durable research state

The workflow is meant to generalize across systems and infrastructure repos.

## Setup

Before changing code, do the following:

1. Identify the target repo and confirm you are working on the target, not just the controller repo.
2. Create a fresh research branch in the target repo, typically `autoresearch/<tag>`, where `<tag>` is based on the date and focus.
3. Read the target repo's top-level context first:
   - `README.md`
   - project instructions such as `CLAUDE.md`
   - `pyproject.toml` or equivalent build config
   - benchmark scripts
   - test suite
   - the smallest set of source files needed to understand the current bottleneck
4. Ensure the target repo has a research workspace at `research/autoresearch/`.
   - If it does not exist yet, initialize it with this controller repo's bootstrap utility.
   - Example: `uv run <controller-repo>/bootstrap_system_project.py --target-repo <target-repo> --profile systems`
5. Read the target repo's `research/autoresearch/manifest.json`, `experiments.tsv`, `claim_ledger.md`, and `runbook.md` before proposing the next experiment.
6. Establish a baseline before any optimization:
   - current commit hash
   - correctness status
   - benchmark results
   - at least one representative trace for bottleneck analysis
7. Record the baseline in `research/autoresearch/experiments.tsv`.

Once the baseline exists, the autonomous loop begins.

## Core Objective

Improve the target system along dimensions that matter for a publishable systems artifact:

- end-to-end performance on representative workloads
- correctness and semantic stability
- subsystem clarity and measurability
- reproducibility of claims
- ablation-ready experimental evidence

This is not a "ship random optimizations until a graph goes down" loop. It is a research loop.

## What You Can Change

You may change anything inside the target repo that materially improves the system or the evidence quality:

- source code
- tests
- benchmark harnesses
- instrumentation and tracing
- docs that explain design or claims
- small utilities that improve reproducibility

You may also improve the research workspace under `research/autoresearch/` as long as the logs remain honest and reproducible.

## What You Must Not Do

- Do not make performance claims without benchmarks.
- Do not make mechanism claims without traces, ablations, or direct evidence.
- Do not quietly change workload semantics or evaluation assumptions without recording it.
- Do not delete contradictory evidence because it is inconvenient.
- Do not keep a code change just because it is clever. Keep it only if the evidence and complexity tradeoff justify it.
- Do not optimize for a single cherry-picked case if the broader workload story gets weaker.

## Keep / Discard Rule

Keep a change only if all of the following hold:

1. The relevant correctness checks pass.
2. The benchmark or trace evidence supports the intended improvement.
3. The gain is large enough, or the measurement improvement is important enough, to justify the added complexity.
4. The experiment is logged in `research/autoresearch/experiments.tsv`.
5. Any resulting claim or caveat is updated in `research/autoresearch/claim_ledger.md`.

Discard the change if it regresses correctness, weakens the broader benchmark picture, or adds complexity without a compelling research payoff.

## The Experiment Loop

LOOP FOREVER until interrupted by the human:

1. Inspect the current best commit, latest experiment log, and outstanding bottlenecks.
2. Choose a single hypothesis grounded in evidence.
3. Implement the smallest meaningful change that tests that hypothesis.
4. Run the fastest correctness checks first.
5. Run the relevant benchmark slice.
6. If the result is promising, run at least one deeper validation pass:
   - a fuller benchmark suite
   - a representative trace
   - a focused ablation
7. Save artifacts in a run-specific directory under `research/autoresearch/artifacts/`.
8. Update `experiments.tsv` with the outcome.
9. Update `claim_ledger.md` with:
   - supported claims
   - promising but unverified ideas
   - refuted ideas
   - threats to validity
10. Keep the commit only if the evidence clears the keep rule. Otherwise revert and move on.

## Research Discipline

Prefer this order of work:

1. Characterization
2. Bottleneck isolation
3. Minimal mechanism
4. Validation
5. Ablation
6. Generalization across workloads
7. Paper-shaping documentation

In practice this means:

- instrument before guessing
- reduce bottlenecks one at a time when possible
- separate measurement improvements from system improvements
- preserve negative results so the project does not rediscover the same dead ends
- favor exact, narrow, reproducible claims over broad but shaky ones

## Paper-Oriented Output

The target repo should gradually accumulate everything needed for a strong systems submission:

- a clean thesis
- a benchmark harness
- a claim ledger
- ablations that isolate each mechanism
- representative traces that explain why the system wins
- honest limitations and non-wins

Every strong code change should make the eventual paper easier to write.

## Playbooks

If the controller repo contains a playbook that matches the target repo's shape, read it before choosing the next experiment.

Typical playbook use cases include:

- workflow runtimes
- distributed systems
- storage engines
- networked services
- compiler or runtime infrastructure

Playbooks should sharpen metrics, guardrails, and experiment priorities for the target without changing the broader research discipline above.

## Autonomy

Do not stop after one experiment. Do not ask the human whether to continue after each small result. Maintain momentum, keep the logs honest, and continue iterating until the human interrupts you.
