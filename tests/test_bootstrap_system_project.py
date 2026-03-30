from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "bootstrap_system_project.py"


class BootstrapSystemProjectTests(unittest.TestCase):
    def test_systems_profile_bootstrap_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target_repo = Path(tempdir) / "system-project"
            target_repo.mkdir()

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--target-repo",
                    str(target_repo),
                    "--profile",
                    "systems",
                ],
                check=True,
                cwd=REPO_ROOT,
            )

            research_root = target_repo / "research" / "autoresearch"
            manifest_path = research_root / "manifest.json"
            experiments_path = research_root / "experiments.tsv"
            claim_ledger_path = research_root / "claim_ledger.md"
            runbook_path = research_root / "runbook.md"
            artifacts_dir = research_root / "artifacts"

            self.assertTrue(manifest_path.exists())
            self.assertTrue(experiments_path.exists())
            self.assertTrue(claim_ledger_path.exists())
            self.assertTrue(runbook_path.exists())
            self.assertTrue(artifacts_dir.exists())

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["profile"], "systems")
            self.assertEqual(manifest["project_name"], "system-project")
            self.assertEqual(manifest["primary_metric"]["name"], "primary_metric")
            self.assertEqual(manifest["primary_metric"]["direction"], "minimize")
            self.assertEqual(manifest["validation_commands"], ["pytest -q"])
            self.assertEqual(manifest["benchmark_commands"], [])

            header = experiments_path.read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(
                header,
                "timestamp\tcommit\tstatus\tprimary_metric\tprimary_value\tdelta_vs_best_pct\ttests\tartifact_dir\tdescription",
            )


if __name__ == "__main__":
    unittest.main()
