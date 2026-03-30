"""Initialize a systems-research workspace inside a target repository.

Usage:
    uv run bootstrap_system_project.py --target-repo ../target-system --profile systems
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


DEFAULT_GUARDRAILS = [
    "Keep correctness checks green before making performance claims.",
    "Prefer narrow, exact mechanisms over broad, unverifiable optimizations.",
    "Record negative results instead of rediscovering them later.",
    "Keep only changes that improve the target metric or substantially improve measurement quality.",
]

DEFAULT_RESEARCH_QUESTIONS = [
    "Which bottlenecks dominate end-to-end latency today?",
    "Which mechanism is the smallest credible change that addresses the top bottleneck?",
    "Which workloads improve, and which workloads do not?",
]


@dataclass(frozen=True)
class Profile:
    name: str
    project_name: str
    research_goal: str
    metric_name: str
    metric_direction: str
    validation_commands: tuple[str, ...]
    benchmark_commands: tuple[str, ...]
    characterization_commands: tuple[str, ...]
    guardrails: tuple[str, ...]
    research_questions: tuple[str, ...]


PROFILES = {
    "systems": Profile(
        name="systems",
        project_name="SystemsProject",
        research_goal=(
            "Improve end-to-end behavior for a target systems project while "
            "preserving correctness and strengthening artifact-grade evidence."
        ),
        metric_name="primary_metric",
        metric_direction="minimize",
        validation_commands=("pytest -q",),
        benchmark_commands=(),
        characterization_commands=(),
        guardrails=(
            "Keep correctness checks green before making performance claims.",
            "Prefer narrow, exact mechanisms over broad, unverifiable optimizations.",
            "Optimize for the target system metric, not a cherry-picked microbenchmark.",
            "Prefer reproducible evidence over intuition.",
        ),
        research_questions=(
            "Which bottlenecks dominate end-to-end behavior today?",
            "Which mechanism is the smallest credible change that addresses the top bottleneck?",
            "Which workloads improve, and which workloads do not?",
        ),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a systems-research workspace")
    parser.add_argument("--target-repo", required=True, help="Path to the target repository")
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        help="Optional repo profile with prefilled commands and research goals",
    )
    parser.add_argument("--project-name", help="Human-readable project name")
    parser.add_argument("--goal", help="Primary research goal")
    parser.add_argument("--metric-name", help="Primary metric name")
    parser.add_argument(
        "--direction",
        choices=["minimize", "maximize"],
        help="Whether the primary metric should go down or up",
    )
    parser.add_argument(
        "--validation-command",
        action="append",
        help="Validation command to store in the manifest; may be passed multiple times",
    )
    parser.add_argument(
        "--benchmark-command",
        action="append",
        help="Benchmark command to store in the manifest; may be passed multiple times",
    )
    parser.add_argument(
        "--characterization-command",
        action="append",
        help="Trace or characterization command to store in the manifest; may be passed multiple times",
    )
    parser.add_argument(
        "--research-dir",
        default="research/autoresearch",
        help="Research workspace path relative to the target repo",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite generated files if they already exist",
    )
    return parser.parse_args()


def choose_profile(args: argparse.Namespace) -> Profile | None:
    if not args.profile:
        return None
    return PROFILES[args.profile]


def coalesce_list(overrides: list[str] | None, defaults: tuple[str, ...]) -> list[str]:
    if overrides:
        return overrides
    return list(defaults)


def build_manifest(
    args: argparse.Namespace,
    target_repo: Path,
    research_root: Path,
    profile: Profile | None,
) -> dict[str, object]:
    project_name = args.project_name or target_repo.name
    research_goal = args.goal or (
        profile.research_goal if profile else "Improve the target systems project with reproducible, publishable evidence."
    )
    metric_name = args.metric_name or (profile.metric_name if profile else "primary_metric")
    metric_direction = args.direction or (profile.metric_direction if profile else "minimize")
    validation_defaults = profile.validation_commands if profile else ("pytest",)
    benchmark_defaults = profile.benchmark_commands if profile else ()
    characterization_defaults = profile.characterization_commands if profile else ()
    guardrails = list(profile.guardrails) if profile else list(DEFAULT_GUARDRAILS)
    research_questions = list(profile.research_questions) if profile else list(DEFAULT_RESEARCH_QUESTIONS)
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    return {
        "schema_version": 1,
        "profile": profile.name if profile else "generic",
        "project_name": project_name,
        "target_repo": str(target_repo),
        "research_dir": str(research_root.relative_to(target_repo)),
        "created_at_utc": created_at,
        "research_goal": research_goal,
        "paper_goal": (
            "Accumulate benchmarked, reproducible evidence that can support a "
            "systems paper rather than a one-off local optimization."
        ),
        "primary_metric": {
            "name": metric_name,
            "direction": metric_direction,
        },
        "validation_commands": coalesce_list(args.validation_command, validation_defaults),
        "benchmark_commands": coalesce_list(args.benchmark_command, benchmark_defaults),
        "characterization_commands": coalesce_list(
            args.characterization_command,
            characterization_defaults,
        ),
        "guardrails": guardrails,
        "research_questions": research_questions,
        "iteration_contract": [
            "Establish and log a baseline before optimizing.",
            "Change one mechanism at a time whenever possible.",
            "Keep only evidence-backed wins or measurement improvements.",
            "Update the experiment log and claim ledger after every iteration.",
        ],
    }


def render_experiments_header() -> str:
    return (
        "timestamp\tcommit\tstatus\tprimary_metric\tprimary_value\t"
        "delta_vs_best_pct\ttests\tartifact_dir\tdescription\n"
    )


def render_claim_ledger(manifest: dict[str, object]) -> str:
    project_name = str(manifest["project_name"])
    metric = str(manifest["primary_metric"]["name"])  # type: ignore[index]
    return dedent(
        f"""\
        # Claim ledger for {project_name}

        Use this file to separate what is supported from what is only promising.

        ## Supported claims

        - Claim:
          Evidence:
          Scope:
          Caveats:

        ## Promising but unverified

        - Hypothesis:
          Missing evidence:
          Next step:

        ## Refuted or discarded

        - Idea:
          Why it failed:
          Artifact:

        ## Threats to validity

        - Metric focus: `{metric}`
        - Workload coverage:
        - Measurement limitations:
        """
    )


def render_runbook(manifest: dict[str, object]) -> str:
    project_name = str(manifest["project_name"])
    validation_commands = manifest["validation_commands"]
    benchmark_commands = manifest["benchmark_commands"]
    characterization_commands = manifest["characterization_commands"]
    guardrails = manifest["guardrails"]
    research_questions = manifest["research_questions"]

    def format_block(lines: object) -> str:
        values = list(lines) if isinstance(lines, list) else list(lines or [])  # type: ignore[arg-type]
        if not values:
            return "- Fill this in before the first autonomous run."
        return "\n".join(f"- `{line}`" for line in values)

    return dedent(
        f"""\
        # Runbook for {project_name}

        ## Baseline checklist

        - Record the current commit.
        - Run the validation commands.
        - Run the benchmark commands.
        - Collect at least one trace or characterization artifact.
        - Log the baseline in `experiments.tsv`.

        ## Validation commands

        {format_block(validation_commands)}

        ## Benchmark commands

        {format_block(benchmark_commands)}

        ## Characterization commands

        {format_block(characterization_commands)}

        ## Keep rule

        - Tests must pass before a performance claim is trusted.
        - Keep only changes with evidence-backed metric improvement or major measurement value.
        - Save every promising run under `artifacts/`.
        - Update `claim_ledger.md` after each experiment.

        ## Research questions

        {format_block(research_questions)}

        ## Guardrails

        {format_block(guardrails)}
        """
    )


def write_text(path: Path, content: str, force: bool) -> str:
    existed_before = path.exists()
    if existed_before and not force:
        return "skipped"
    path.write_text(content, encoding="utf-8")
    return "updated" if existed_before else "created"


def main() -> None:
    args = parse_args()
    target_repo = Path(args.target_repo).expanduser().resolve()
    if not target_repo.exists() or not target_repo.is_dir():
        raise SystemExit(f"Target repository does not exist or is not a directory: {target_repo}")

    research_dir = Path(args.research_dir)
    if research_dir.is_absolute():
        raise SystemExit("--research-dir must be relative to the target repository")

    research_root = target_repo / research_dir
    artifacts_dir = research_root / "artifacts"
    research_root.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    profile = choose_profile(args)
    manifest = build_manifest(args, target_repo, research_root, profile)

    files = {
        research_root / "manifest.json": json.dumps(manifest, indent=2) + "\n",
        research_root / "experiments.tsv": render_experiments_header(),
        research_root / "claim_ledger.md": render_claim_ledger(manifest),
        research_root / "runbook.md": render_runbook(manifest),
    }

    for path, content in files.items():
        status = write_text(path, content, force=args.force)
        print(f"{status:>7} {path}")

    print(f"{'ready':>7} {artifacts_dir}")


if __name__ == "__main__":
    main()
