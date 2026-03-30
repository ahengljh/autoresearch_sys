# systems playbook

Use this playbook when the target repo is a systems or infrastructure project with benchmarks, traces, workloads, or operational metrics.

## Thesis

The working thesis for a systems target is:

> Targeted, evidence-backed mechanisms can improve end-to-end system behavior without weakening correctness, semantics, or reproducibility.

Every iteration should either strengthen this thesis, sharpen its boundaries, or disprove a weak version of it.

## Primary Metric

Optimize for the project's **headline end-to-end metric**, not an isolated microbenchmark that flatters the mechanism.

Preferred headline metric:

- a benchmark, latency, throughput, utilization, cost, or tail-behavior metric that the target repo already treats as primary

Useful secondary metrics:

- queueing and waiting time from traces or profiles
- bottleneck-local counters
- workload-specific wins and losses instead of a single aggregate score
- resource efficiency alongside latency when relevant

## Required Checks

Run fast correctness checks before performance claims:

```bash
pytest -q
```

Run the benchmark harness for evidence:

```bash
python scripts/run_benchmarks.py --output-dir results/autoresearch
```

Collect representative traces when a change looks promising:

```bash
python scripts/collect_trace.py --output results/autoresearch/trace.json
```

Adapt the exact commands to the target repo's build and evaluation harness.

## Keep Rule

Keep a change only if:

1. The tests pass.
2. The benchmark evidence improves the target workloads or clearly strengthens the measurement story.
3. The trace, profile, or counter evidence explains the win in terms of an actual mechanism.
4. The change does not violate the target repo's correctness constraints.

If a change helps one workload but hurts another, log the tradeoff explicitly. That can still be a valid result if the mechanism is well understood.

## High-Value Experiment Lanes

Prioritize these lanes:

1. **Characterization**
   - quantify queue delay, waiting, resource bottlenecks, and critical-path slack
   - add instrumentation before guessing
2. **Bottleneck isolation**
   - identify the smallest mechanism that could plausibly move the headline metric
   - validate that the suspected bottleneck is really on the critical path
3. **Mechanism design**
   - improve scheduling, placement, communication, storage, caching, or execution policy
   - avoid mixing several causal changes unless the experiment is explicitly an integration pass
4. **Validation**
   - check when an apparent local improvement actually converts into end-to-end wins
   - inspect workload-specific regressions and non-wins
5. **Benchmark realism**
   - strengthen workloads so they expose the mechanism the paper wants to claim
   - expand ablations only when they improve the causal story

## Guardrails

Do not drift away from the repo's core design rules:

- preserve exact semantics and correctness
- prefer one clear mechanism over a pile of confounded tweaks
- make every subsystem benchmarkable or observable in isolation when possible
- record negative results instead of rediscovering them
- avoid overclaiming from a narrow benchmark slice

## Paper Packaging

Treat the repo as if it is slowly becoming the appendix and artifact bundle for a systems submission.

Try to leave behind:

- benchmark tables that isolate each mechanism
- traces that explain why the full system wins
- a clear story for baseline, mechanism-only, and integrated ablations
- honest limitations, especially where a mechanism does not help
- a claim ledger that ties code changes to evidence
