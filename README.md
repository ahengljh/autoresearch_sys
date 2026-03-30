# autoresearch

![teaser](progress.png)

This repo started as a tiny autonomous pretraining loop. It now also serves as a controller repo for autonomous **systems research**, where the agent iterates on an external project, keeps only evidence-backed wins, and leaves behind paper-grade artifacts instead of just a pile of code diffs.

The original training demo is still here, but the default `program.md` is now aimed at external systems repos: prototypes with benchmarks, traces, workloads, and a real shot at becoming a publishable artifact.

## What Changed

- `program.md` is now a systems-research agent prompt.
- `playbooks/systems.md` is a generic playbook for systems and infrastructure projects.
- `bootstrap_system_project.py` initializes a target repo with a research ledger, claim log, and experiment log.
- `programs/pretraining.md` preserves the original single-file training-loop prompt.
- `prepare.py` and `train.py` remain as the legacy model-training workload that inspired this repo.

## Systems Quick Start

**Requirements:** Python 3.10+, [uv](https://docs.astral.sh/uv/), and a target repo you want the agent to improve.

```bash
# 1. Install dependencies for this controller repo
uv sync

# 2. Bootstrap a research ledger inside the target repo
uv run bootstrap_system_project.py --target-repo ../target-system --profile systems

# 3. Start your coding agent in the target repo and point it at:
#    - this repo's program.md
#    - this repo's playbooks/systems.md
#    - the target repo's research/autoresearch/manifest.json
```

The bootstrap step creates a small research workspace inside the target repo:

```text
research/autoresearch/
  manifest.json
  experiments.tsv
  claim_ledger.md
  runbook.md
  artifacts/
```

That workspace is where the agent records baselines, hypothesis-by-hypothesis experiment results, and paper claims that are actually supported by benchmarks and traces.

## Default Systems Loop

The systems agent in `program.md` follows a tighter loop than the original training-only version:

1. Characterize the target system first.
2. Pick one bottleneck-backed hypothesis.
3. Make the smallest meaningful code change in the target repo.
4. Run correctness checks before performance claims.
5. Run benchmarks and traces.
6. Keep only changes that improve the target metric or meaningfully improve measurement quality.
7. Update the experiment log and claim ledger so the project trends toward a paper, not just a faster local branch.

This is designed for systems work where the real output is not "best checkpoint wins", but a reproducible story:

- what bottleneck existed
- what mechanism addressed it
- how much it helped
- where it did not help
- which ablations support the claim

## Good Fit

This workflow is a strong fit for systems repos that already have some combination of:

- benchmark scripts
- trace or profiling capture
- subsystem decomposition that maps well to hypothesis-driven iteration
- explicit correctness constraints around latency, scheduling, communication, storage, or resource management

The bundled `playbooks/systems.md` turns those ingredients into an operating procedure for an autonomous research agent. You can also add target-specific playbooks as the project matures.

## Legacy Pretraining Mode

The original autonomous pretraining setup is still here if you want it:

```bash
uv run prepare.py
uv run train.py
```

Use `programs/pretraining.md` for the legacy "edit `train.py`, run for five minutes, keep or discard by `val_bpb`" workflow.

## Project Structure

```text
bootstrap_system_project.py  - bootstrap a systems-research ledger in a target repo
program.md                   - default systems-research agent instructions
playbooks/systems.md         - generic systems-research playbook
programs/pretraining.md      - legacy pretraining-only prompt
prepare.py                   - legacy training data prep and evaluation harness
train.py                     - legacy training workload the agent can still modify
pyproject.toml               - dependencies for this controller repo
```

## Design Principles

- **Evidence over vibes.** Systems wins must be supported by tests, benchmarks, and traces.
- **Hypothesis-first iteration.** Every change should have a bottleneck, a mechanism, and a validation plan.
- **Claim discipline.** Keep a ledger of what is truly supported, what is promising, and what was refuted.
- **Composable playbooks.** The controller repo holds reusable prompts and target-specific operating guidance.
- **Legacy example intact.** The original training setup remains available as a small autonomous-research sandbox.

## License

MIT
