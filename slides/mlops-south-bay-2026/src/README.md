# Chapter 3 Demo: Observable, Debuggable, Durable Agents

Runnable uv scripts that illustrate: **crash → resume from cache → provision more memory → complete**.

## Scripts (run in isolation)

| Script | Slide | Purpose |
|--------|--------|--------|
| `agent_demo.py` | Ch 3 | Crash → resume from cache → complete (simulate OOM, then recover). |
| `cacheable_step.py` | Make Crashes Cheap | One cacheable step; rerun with same `--source` for cache hit. |
| `infrastructure_as_context.py` | Infrastructure as Context | Two resource profiles (128Mi / 512Mi); orchestration chooses or retries with high memory. |
| `code_sandbox.py` | Agent Self-Service Tools | Run AI-generated code in a **raw container task** ([Union docs](https://www.union.ai/docs/v2/byoc/user-guide/task-programming/container-tasks/)). |
| `orchestration_sandbox.py` | Agent Self-Service Tools | **Orchestration sandbox**: `@env.sandboxed_task` and `code_to_task()` (PR 667). |
| `human_in_the_loop.py` | Human-in-the-Loop | Pause for human input via `hitl.new_event.aio()` / `event.wait.aio()` (PR 657). Requires `flyteplugins-hitl`. |

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Flyte remote: `FLYTE_INTERNAL_EXECUTION_PROJECT`, `FLYTE_INTERNAL_EXECUTION_DOMAIN`, `FLYTE_PASSTHROUGH_API_KEY`
- **Orchestration sandbox:** `pip install 'flyte[sandboxed]'` for `orchestration_sandbox.py`
- **HITL:** `pip install flyteplugins-hitl` for `human_in_the_loop.py`

## Run locally (with Flyte remote)

```bash
# Build image (once)
uv run agent_demo.py --build

# First run: "crash" at process step (simulated OOM)
uv run agent_demo.py --simulate-oom

# Second run: resume from cache, succeed (no flag = no simulated OOM)
uv run agent_demo.py
```

```bash
# Cache demo
uv run cacheable_step.py --source my-context
uv run cacheable_step.py --source my-context

# Infrastructure as context
uv run infrastructure_as_context.py --payload heavy --use-high

# Code sandbox / orchestration sandbox / HITL
uv run code_sandbox.py
uv run orchestration_sandbox.py
uv run human_in_the_loop.py
```

## Concepts

- **Cache:** Completed steps (e.g. `fetch_data`) are cached; after a crash, rerun reuses them.
- **Infrastructure as context:** Different `TaskEnvironment` resource profiles. **Code sandbox:** Raw container tasks. **Orchestration sandbox:** `@env.sandboxed_task` + `code_to_task()` (PR 667). **HITL:** `hitl.new_event.aio()` / `event.wait.aio()` (PR 657).
- **Cheap failures (legacy):** Simulated OOM in `process_step`; in production you’d retry with a task that has higher `Resources(memory="512Mi")`.
