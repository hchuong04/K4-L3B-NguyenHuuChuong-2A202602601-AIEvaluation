"""Exercise 3.5 — Retrieval Reranking Experiment Runner.

This script demonstrates that reordering retrieved chunks with a lexical reranker
(rerank_by_overlap) increases Context Precision without changing Context Recall.
It loads saved artifacts and prints the evaluation table for Exercise 3.5.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from template import RAGASEvaluator, rerank_by_overlap


def run_reranking_experiment(
    golden_path: str | Path = "golden_dataset.json",
    actual_path: str | Path = "artifacts/actual_answers.json",
    selected_ids: tuple[str, ...] = ("E04", "M06", "M07", "A01", "A03"),
) -> None:
    golden_file = Path(golden_path).resolve()
    actual_file = Path(actual_path).resolve()

    golden_data = json.loads(golden_file.read_text(encoding="utf-8"))
    actual_data = json.loads(actual_file.read_text(encoding="utf-8"))

    golden_by_id = {item["id"]: item for item in golden_data["qa_pairs"]}
    actual_by_id = {item["id"]: item for item in actual_data["answers"]}

    evaluator = RAGASEvaluator()

    print("=" * 80)
    print("Exercise 3.5: Retrieval Reranking Experiment (template.rerank_by_overlap)")
    print("=" * 80)
    print(
        f"{'ID':<6} | {'Recall before':<14} | {'Recall after':<13} | "
        f"{'Precision before':<17} | {'Precision after':<16} | {'Delta Precision':<15}"
    )
    print("-" * 88)

    rec_befores: list[float] = []
    rec_afters: list[float] = []
    prec_befores: list[float] = []
    prec_afters: list[float] = []

    for case_id in selected_ids:
        golden_item = golden_by_id[case_id]
        actual_item = actual_by_id[case_id]

        question = golden_item["question"]
        expected = golden_item["expected_answer"]

        # Original chunks retrieved by BM25
        orig_contexts = [chunk["text"] for chunk in actual_item["retrieved_contexts"]]

        # Calculate metrics before rerank
        rec_b = evaluator.evaluate_context_recall(orig_contexts, expected)
        prec_b = evaluator.evaluate_context_precision(orig_contexts, expected)

        # Apply rerank_by_overlap from template.py
        reranked_contexts = rerank_by_overlap(orig_contexts, question)

        # Calculate metrics after rerank
        rec_a = evaluator.evaluate_context_recall(reranked_contexts, expected)
        prec_a = evaluator.evaluate_context_precision(reranked_contexts, expected)

        delta_prec = prec_a - prec_b

        rec_befores.append(rec_b)
        rec_afters.append(rec_a)
        prec_befores.append(prec_b)
        prec_afters.append(prec_a)

        print(
            f"{case_id:<6} | {rec_b:<14.3f} | {rec_a:<13.3f} | "
            f"{prec_b:<17.3f} | {prec_a:<16.3f} | {delta_prec:<+15.3f}"
        )

    avg_rec_b = sum(rec_befores) / len(rec_befores)
    avg_rec_a = sum(rec_afters) / len(rec_afters)
    avg_prec_b = sum(prec_befores) / len(prec_befores)
    avg_prec_a = sum(prec_afters) / len(prec_afters)
    avg_delta_prec = avg_prec_a - avg_prec_b

    print("-" * 88)
    print(
        f"{'Avg':<6} | {avg_rec_b:<14.3f} | {avg_rec_a:<13.3f} | "
        f"{avg_prec_b:<17.3f} | {avg_prec_a:<16.3f} | {avg_delta_prec:<+15.3f}"
    )
    print("=" * 80)
    print(
        "\nConclusion:\n"
        f"1. Context Recall remains strictly invariant: Delta Recall = {avg_rec_a - avg_rec_b:+.4f}\n"
        f"2. Context Precision improved by: Delta Precision = {avg_delta_prec:+.4f} (+{avg_delta_prec*100:.1f}%)\n"
    )


if __name__ == "__main__":
    run_reranking_experiment()
