"""Master Verification Script for Day 14 AI Evaluation Lab.

This script executes all validation, testing, benchmarking, and analysis
scripts across Checkpoints 1 through 5 and Bonus Exercises 3.4 & 3.5,
producing a consolidated readiness report.

Usage:
    python verify_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_step(step_name: str, command: list[str]) -> bool:
    print(f"\n[{'='*30} STEP: {step_name} {'='*30}]")
    print(f"Command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False, text=True)
    if result.returncode == 0:
        print(f"--> [SUCCESS] {step_name} passed.")
        return True
    else:
        print(f"--> [FAILED] {step_name} exited with code {result.returncode}.")
        return False


def main() -> int:
    print("=" * 80)
    print("DAY 14 AI EVALUATION LAB — MASTER VERIFICATION PIPELINE")
    print("=" * 80)

    steps: list[tuple[str, list[str]]] = [
        ("CP1-CP3: Core Unit Tests (pytest)", [sys.executable, "-m", "pytest", "tests/", "-q"]),
        ("CP4: Golden Dataset Validation", [sys.executable, "validate_golden_dataset.py"]),
        ("CP4: Benchmark Answers Evaluation (Ex 3.2)", [sys.executable, "evaluate_answers.py"]),
        ("CP5: Failure Analysis & Reflection (Ex 3.2/CP5)", [sys.executable, "run_failure_analysis.py"]),
        ("Task 3 & Ex 3.3: LLM Judge & Rubric Demo", [sys.executable, "run_llm_judge_demo.py"]),
        ("Bonus Ex 3.4: Framework Comparison Demo", [sys.executable, "run_framework_comparison_demo.py"]),
        ("Bonus Ex 3.5: Retrieval Reranking Experiment", [sys.executable, "run_rerank_experiment.py"]),
    ]

    all_passed = True
    results_summary: list[tuple[str, bool]] = []

    for name, cmd in steps:
        success = run_step(name, cmd)
        results_summary.append((name, success))
        if not success:
            all_passed = False

    print("\n" + "=" * 80)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    for name, success in results_summary:
        status_str = "PASS [✓]" if success else "FAIL [✗]"
        print(f"{name:<55} : {status_str}")

    print("=" * 80)
    if all_passed:
        print("ALL VERIFICATIONS PASSED! Repository is 100% reproducible and complete.")
        return 0
    else:
        print("SOME VERIFICATIONS FAILED. Please review the failed step output above.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
