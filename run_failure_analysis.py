"""Checkpoint 5 — Failure Analysis & Reflection Helper Script.

This script reproduces and verifies all quantitative data and root-cause diagnoses
reported in reflection.md:
1. Benchmark summary metrics (Average, Min, Max).
2. Score tier classification (Good, Needs Work, Significant Issues).
3. Failure type distribution.
4. Top 3 worst-performing cases with analyzer.find_root_cause().
5. Failure clustering & Improvement log mapping (F001–F004 to QA IDs).
6. Regression test verification (runner.run_regression).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from evaluate_answers import load_evaluation_inputs
from template import BenchmarkRunner, EvalResult, FailureAnalyzer, RAGASEvaluator


def run_failure_analysis(
    golden_path: str | Path = "golden_dataset.json",
    actual_path: str | Path = "artifacts/actual_answers.json",
    benchmark_path: str | Path = "artifacts/benchmark_results.json",
) -> None:
    golden_file = Path(golden_path).resolve()
    actual_file = Path(actual_path).resolve()
    bench_file = Path(benchmark_path).resolve()

    if not golden_file.is_file() or not actual_file.is_file():
        raise FileNotFoundError("Missing golden_dataset.json or actual_answers.json")

    pairs, answers = load_evaluation_inputs(golden_file, actual_file)
    evaluator = RAGASEvaluator()
    runner = BenchmarkRunner()
    analyzer = FailureAnalyzer()

    # Run evaluation
    results = runner.run(pairs, answers.__getitem__, evaluator)
    report = runner.generate_report(results)

    print("=" * 80)
    print("CHECKPOINT 5: FAILURE ANALYSIS & BENCHMARK VERIFICATION REPORT")
    print("=" * 80)

    # -----------------------------------------------------------------------
    # Section 1: Benchmark Summary Table
    # -----------------------------------------------------------------------
    print("\n--- 1. BENCHMARK SUMMARY (Avg, Min, Max) ---")
    print(f"Overall Pass Rate: {report['pass_rate']:.1%} ({report['passed']}/{report['total']})")

    metrics = [
        ("Context Recall", [r.context_recall for r in results if r.context_recall is not None]),
        ("Context Precision", [r.context_precision for r in results if r.context_precision is not None]),
        ("Faithfulness", [r.faithfulness for r in results]),
        ("Relevance", [r.relevance for r in results]),
        ("Completeness", [r.completeness for r in results]),
        ("Overall Score", [r.overall_score() for r in results]),
    ]

    print(f"{'Metric':<20} | {'Average':<10} | {'Min':<10} | {'Max':<10}")
    print("-" * 58)
    for name, vals in metrics:
        avg_v = sum(vals) / len(vals) if vals else 0.0
        min_v = min(vals) if vals else 0.0
        max_v = max(vals) if vals else 0.0
        print(f"{name:<20} | {avg_v:<10.3f} | {min_v:<10.3f} | {max_v:<10.3f}")

    # Score interpretation tiers
    good_cases = [r.qa_pair.metadata["id"] for r in results if r.overall_score() >= 0.8]
    needs_work_cases = [r.qa_pair.metadata["id"] for r in results if 0.6 <= r.overall_score() < 0.8]
    significant_cases = [r.qa_pair.metadata["id"] for r in results if r.overall_score() < 0.6]

    print("\n--- SCORE INTERPRETATION TIERS ---")
    print(f"- Good (0.8–1.0): {len(good_cases)} cases -> {good_cases}")
    print(f"- Needs Work (0.6–0.8): {len(needs_work_cases)} cases -> {needs_work_cases}")
    print(f"- Significant Issues (<0.6): {len(significant_cases)} cases -> {significant_cases}")

    # Failure types
    print("\n--- FAILURE TYPE DISTRIBUTION ---")
    failure_counts = report["failure_types"]
    for ftype in ["hallucination", "irrelevant", "incomplete", "off_topic", "refusal"]:
        count = failure_counts.get(ftype, 0)
        pct = (count / report["total"]) * 100
        print(f"- {ftype:<14}: {count:>2} ({pct:>5.1f}%)")

    # -----------------------------------------------------------------------
    # Section 2: Top 3 Worst Failures & Root Cause
    # -----------------------------------------------------------------------
    print("\n--- 2. TOP 3 WORST FAILURES (5 Whys Analysis Targets) ---")
    sorted_by_score = sorted(results, key=lambda item: item.overall_score())
    top_3_worst = sorted_by_score[:3]

    for rank, res in enumerate(top_3_worst, start=1):
        case_id = res.qa_pair.metadata.get("id", "UNKNOWN")
        root_cause = analyzer.find_root_cause(res)
        print(f"\n[Failure {rank}] ID: {case_id} | Difficulty: {res.qa_pair.metadata.get('difficulty')}")
        print(f"  Question:         {res.qa_pair.question[:70]}...")
        print(f"  Actual Answer:    {res.actual_answer[:70]}...")
        print(
            f"  Scores:           Recall: {res.context_recall:.3f} | "
            f"Precision: {res.context_precision:.3f} | "
            f"Faithfulness: {res.faithfulness:.3f} | "
            f"Relevance: {res.relevance:.3f} | "
            f"Completeness: {res.completeness:.3f} | "
            f"Overall: {res.overall_score():.3f}"
        )
        print(f"  Failure Type:     {res.failure_type}")
        print(f"  analyzer.find_root_cause(): \"{root_cause}\"")

    # -----------------------------------------------------------------------
    # Section 3: Failure Clustering & Improvement Log
    # -----------------------------------------------------------------------
    print("\n--- 3. FAILURE TAXONOMY & IMPROVEMENT LOG ---")
    failures = runner.identify_failures(results, threshold=0.5)
    suggestions = analyzer.generate_improvement_suggestions(failures)
    log_table = analyzer.generate_improvement_log(failures, suggestions)

    print("Generated Improvement Log Table:")
    print(log_table)

    print("\nFailure ID to QA ID Mapping:")
    for idx, f in enumerate(failures, start=1):
        f_code = f"F{idx:03d}"
        qa_id = f.qa_pair.metadata.get("id")
        print(f"- {f_code} corresponds to QA ID: {qa_id} (Type: {f.failure_type})")

    # -----------------------------------------------------------------------
    # Section 4: Regression Testing Verification
    # -----------------------------------------------------------------------
    print("\n--- 4. REGRESSION TESTING VERIFICATION ---")
    reg_result = runner.run_regression(results, results)
    print(f"Regression against self (baseline): Passed = {reg_result['passed']}")
    print(f"Detected regressions: {reg_result['regressions']}")
    print("=" * 80)


if __name__ == "__main__":
    run_failure_analysis()
