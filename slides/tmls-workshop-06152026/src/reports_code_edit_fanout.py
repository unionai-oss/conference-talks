"""Directive helpers for the fan-out code-edit MLE agent."""

from __future__ import annotations

from typing import Any

from autoresearch_types import DatasetProfile
from research_history import format_research_history_for_directive


def directive_code_edit_fanout(
    n_experiments: int,
    profile: DatasetProfile,
    memory_key: str,
    *,
    batch_size: int = 3,
    max_batches: int | None = None,
    history: dict[str, Any] | None = None,
) -> str:
    """Build the user directive for the code-mode fan-out agent."""
    if max_batches is None:
        max_batches = max(1, (n_experiments + batch_size - 1) // batch_size)

    history_block = format_research_history_for_directive(history or {})

    return (
        f"Run {n_experiments} code-edit experiments on climbmix "
        f"({profile.n_parquet_files} shards, vocab_size={profile.vocab_size}) using "
        f"**batched parallel fan-out**. Work in up to {max_batches} batch(es) of "
        f"{batch_size} hypotheses at a time.\n\n"
        f"Use memory_key={memory_key!r} for all memory-backed tools.\n\n"
        "Workflow (CODE MODE — write Python plans each turn):\n"
        "1. ``get_code_edit_history()`` (if prior trials exist) + ``get_baseline_train_code`` "
        "+ ``inspect_dataset``; optionally ``search_arxiv``.\n"
        "2. Plan a batch: ``record_batch_plan(batch_id, experiments=[...])``.\n"
        "3. For each title in the batch: ``edit_train_code_batch(edits=[...])`` "
        "with ``config_overrides`` per title (preferred) — e.g. "
        "``{\"title\": \"deeper-6L\", \"config_overrides\": {\"n_layer\": 6}, \"change_summary\": \"...\"}``. "
        "Do not paste unchanged baseline ``train.py``.\n"
        "4. ``record_batch_hypotheses([...])`` then ``run_experiment_batch(titles, ...)`` "
        f"OR ``flyte_map('run_experiment', titles, budgets, keys, concurrency={batch_size})``.\n"
        "5. ``evaluate_batch_results(results, batch_id=...)`` — pick the best, discard failures.\n"
        "6. Iterate: fork promising edits into the next batch until "
        f"{n_experiments} experiments complete.\n"
        "7. Finish with a plain-text summary: best val_bpb, winning code changes, next batch idea.\n\n"
        f"**Batch diversity:** each parallel run in a batch must test a different hypothesis — "
        f"spread changes across learning_rate, depth/width (n_layer, n_embd, n_head), dropout, "
        f"and batch size. No duplicate configs; one or two knobs per edit.\n\n"
        "Do not repeat experiments already listed in prior research below. Fork the current "
        "best with ``read_train_code(best_title)`` before designing the next batch.\n\n"
        f"time_budget_sec=45. Platform retries sandbox OOM with more memory per run."
        f"{history_block}"
    )
