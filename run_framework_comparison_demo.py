"""Exercise 3.4 — Framework Comparison Demonstration (RAGAS vs DeepEval).

This script demonstrates how evaluation data from golden_dataset.json and
artifacts/actual_answers.json is prepared and evaluated in both RAGAS and DeepEval,
comparing their metric models, schema requirements, and execution styles.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def demonstrate_framework_comparison() -> None:
    golden_file = Path("golden_dataset.json").resolve()
    actual_file = Path("artifacts/actual_answers.json").resolve()

    golden_data = json.loads(golden_file.read_text(encoding="utf-8"))
    actual_data = json.loads(actual_file.read_text(encoding="utf-8"))

    print("=" * 80)
    print("Exercise 3.4: Framework Comparison — RAGAS vs DeepEval on OrbitTech Dataset")
    print("=" * 80)

    # 1. Schema mapping comparison
    sample_g = golden_data["qa_pairs"][0]  # E01
    sample_a = actual_data["answers"][0]

    print("\n--- 1. DATA SCHEMA MAPPING ---")
    print("Common Input:")
    print(f"  Question:        {sample_g['question'][:60]}...")
    print(f"  Actual Answer:   {sample_a['actual_answer'][:60]}...")
    print(f"  Expected Answer: {sample_g['expected_answer'][:60]}...")
    print(f"  Retrieved Chunks Count: {len(sample_a['retrieved_contexts'])}")

    print("\n[RAGAS Schema Requirement]:")
    print("  from datasets import Dataset")
    print("  ragas_dataset = Dataset.from_dict({")
    print("      'question': [sample_g['question']],")
    print("      'answer': [sample_a['actual_answer']],")
    print("      'contexts': [[c['text'] for c in sample_a['retrieved_contexts']]],")
    print("      'ground_truth': [sample_g['expected_answer']],")
    print("  })")

    print("\n[DeepEval Schema Requirement]:")
    print("  from deepeval.test_case import LLMTestCase")
    print("  test_case = LLMTestCase(")
    print("      input=sample_g['question'],")
    print("      actual_output=sample_a['actual_answer'],")
    print("      retrieval_context=[c['text'] for c in sample_a['retrieved_contexts']],")
    print("      expected_output=sample_g['expected_answer'],")
    print("  )")

    # 2. Execution & CI/CD workflow comparison
    print("\n--- 2. CI/CD INTEGRATION & ASSERTION SYNTAX ---")
    print("[RAGAS Execution]:")
    print("  from ragas import evaluate")
    print("  from ragas.metrics import faithfulness, answer_relevancy, context_precision")
    print("  result = evaluate(ragas_dataset, metrics=[faithfulness, answer_relevancy])")
    print("  assert result['faithfulness'] >= 0.70  # Custom assertion in script")

    print("\n[DeepEval Execution (Pytest Native)]:")
    print("  from deepeval import assert_test")
    print("  from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric")
    print("  metric = FaithfulnessMetric(threshold=0.7)")
    print("  assert_test(test_case, [metric])  # Native Pytest failure report & CLI exit code")

    # 3. Summary comparison table
    print("\n--- 3. COMPARISON SUMMARY ---")
    print(
        f"{'Dimension':<25} | {'RAGAS':<25} | {'DeepEval':<25}"
    )
    print("-" * 80)
    print(f"{'Decomposition':<25} | {'Sentence-level claims':<25} | {'G-Eval prompt weighting':<25}")
    print(f"{'Strictness':<25} | {'Higher (Discrete ratio)':<25} | {'Moderate (Goal-oriented)':<25}")
    print(f"{'Adversarial Refusals':<25} | {'Flagged ungrounded':<25} | {'Guardrail Pass capable':<25}")
    print(f"{'Best suited for':<25} | {'R&D / Algorithm tuning':<25} | {'Production CI/CD / QA':<25}")
    print("=" * 80)


if __name__ == "__main__":
    demonstrate_framework_comparison()
