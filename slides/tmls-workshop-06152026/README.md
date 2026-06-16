# Autoresearch with an MLE Agent — TMLS Workshop (2026-06-15)

A 30-minute technical workshop on building **durable, self-healing agents** on
Flyte, centered on one running example: an ML-engineer agent that does
[`karpathy/autoresearch`](https://github.com/karpathy/autoresearch)-style
hyperparameter search on a TinyGPT language model.

## Slides

Built with [Slidev](https://github.com/slidevjs/slidev):

- `pnpm install`
- `pnpm dev`
- visit <http://localhost:3030>

Edit [slides.md](./slides.md) to change the deck.

## Running code

The narrative is fueled by real, runnable code in [`src/`](./src). Three agent
variants share the same climbmix + TinyGPT stack:

- **`mle_agent.py`** — structured hyperparameter tools (workshop default in slides)
- **`mle_agent_code_edit.py`** — edits `train.py` directly and runs it in
  [`unionai-sandbox`](https://www.union.ai/docs/v2/union/user-guide/sandboxing/interactive-sandboxes/)
- **`mle_agent_code_edit_fanout.py`** — same code-edit loop, but **`code_mode=True`**
  so the agent writes Python plans and runs **batches of hypotheses in parallel**
  via `flyte_map` / `run_experiment_batch`

All three showcase the four constructs the talk dives into:

1. `flyte.ai.agents.Agent` — the tool-use loop
2. a tool `call_handler` that right-sizes compute and heals OOM
3. `MemoryStore` — durable agent memory across runs
4. Flyte reports — live leaderboard, activity feed, and memory inspector

See [`src/README.md`](./src/README.md) for how to run it.
