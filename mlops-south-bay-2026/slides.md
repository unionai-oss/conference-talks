---
theme: seriph
title: The Orchestration Stack for Observable, Debuggable, and Durable Agents
titleTemplate: '%s | MLOps South Bay 2026'
info: |
  ## The Orchestration Stack for Observable, Debuggable, and Durable Agents
  Building agents that help themselves. Union.ai / Flyte.
drawings:
  persist: false
transition: none
fonts:
  sans: 'DM Sans'
  serif: 'DM Sans'
  mono: 'JetBrains Mono'
themeConfig:
  primary: '#FDB51F'
---

<style>
h1 { color: #FDB51F !important; }

h1, h2, h3, ul, li, p { text-align: left !important; }
  
:global(h1), :global(h2), :global(h3) {
  color: #FDB51F !important;
}
:global(.slidev-layout.cover h1),
:global(.slidev-layout.intro h1) {
  color: #FDB51F !important;
}
:global(.slidev-layout) {
  font-family: 'DM Sans', system-ui, sans-serif !important;
}
:global(.slidev-layout img) {
  display: block;
  margin-left: auto;
  margin-right: auto;
}
:global(.slidev-layout ul),
:global(.slidev-layout li) {
  text-align: left !important;
}

.two-cols-header {
  column-gap: 30px; /* Adjust the gap size as needed */
}
</style>

# The Orchestration Stack for Observable, Debuggable, and Durable Agents

<br />

### Niels Bantilan @ Union.ai

MLOps South Bay 2026

---
layout: center
---

# The hidden infrastructure problem

You built an agent, optimized its prompts, engineered its context, implemented an eval harness, and it works beautifully in development…

... then the infrastructure got in the way

- ❌ Tools making API calls are rate-limited.
- ⚠️ Parallelized subagents/tool calls leads to resource contention.
- 💥 Containers run out of memory, are killed by the scheduler, are preempted by other jobs.
- 🗑️ Agent memory loss or corruption, wiping out precious context.
- 🔓 Agent components (MCP, coding subagents) encourage poor security hygiene.

---
layout: center
---

# Agents Fail at Multiple Layers of the Orchestration Stack

The semantic and networking layers of the stack get a lot of attention, but the infrastructure layer is just as critical.

The problem isn't that agents fail. It's that recovering from failure is expensive and time-consuming because agents
have no way of observing what's going on at the infrastructure layer and safely getting themselves back on track.

---
layout: center
---

# What Agents are saying...

![Help yourself](https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm0xbXh1NmE0eWtyZzBlNWlhbm1iaWo4cG03YWNrbTQ2djB2YzFlaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/uRb2p09vY8lEs/giphy.gif)

---
layout: default
---

# Thesis: Five Design Elements for Production Agents

1. **Plain Python (or TS/JS)** — minimize DSLs; loops, fan-out, try/except stay trivial
2. **Make failures cheap** — global cache, run-level replay, memory persistence
3. **Infrastructure-level context** — let agents see OOM/network errors and request more resources
4. **Agent self-service tools** — secure tool building and orchestration
5. **Durability & observability hooks** — `@flyte.trace`, `@env.task`; works with any framework/stack
6. **Human-in-the-loop** — debugger and manual feedback when self-service isn't enough

---
layout: default
---

# Chapter 1: Where Agents Break — and Where Evals Miss

**Failure modes at each layer:**

| **Layer** | **Example failure** |
|-----------|---------------------|
| Infrastructure | OOM, container killed or preempted |
| Network | API rate-limiting, network timeouts |
| Logical | Programming bugs, data validation errors |
| Semantic | Hallucinated tool calls, logical errors |
| Tool execution | Bad arguments, tool timeouts, tool errors |
| Memory | State wiped or corrupted on crash, context loss |

---
layout: default
---

# The Context and Evaluation Gap

Your evals test **semantic correctness**: *"Does it answer right?"*

They often **miss**:

- Does it survive a network timeout?
- Does it recover from OOM?
- Does it preserve state across retries?

**Insight:** Agents can recover from *semantic* failures (prompts, context, control flow)
— but only if **infrastructure doesn't kill them first** 💥.

---
layout: two-cols-header
---

# Context Engineering as a Layer

If a crash **wipes the agent's state**, that context is worthless.

**Durability** (cache + replay + persistence) is what makes context engineering pay off in production.

<br>

::left::

#### ▶️ Normal Execution

<br>

```mermaid
flowchart LR
  P["<strong>🤖 Agent</strong>"]
  T1["<strong>🔧 Tool 1 ✅</strong>"]
  T2["<strong>🤖 Subagent 1 ✅</strong>"]
  T3["<strong>🪚 Tool 2 ❌</strong>"]

  P --> T1
  P --> T2
  P --> T3

  style T1 fill:#87CEEB,stroke:#1E90FF,stroke-width:2px,color:#00008B
  style T2 fill:#87CEEB,stroke:#1E90FF,stroke-width:2px,color:#00008B
  style T3 fill:#FFB6C1,stroke:#DC143C,stroke-width:2px,color:#8B0000
```

::right::

#### 📋 Replay Log

<br>

| **Step**         | **Component**              | **Status** |
|------------------|---------------------------|------------|
| 1                | 🔧 Tool 1                  | ✅         |
| 2                | 🤖 Subagent 1              | ✅         |
| 3                | 🪚 Tool 2                  | ❌         |

<style>
.two-cols-header {
  column-gap: 30px; /* Adjust the gap size as needed */
}
</style>

---
layout: two-cols-header
---

# Context Engineering as a Layer

If a crash **wipes the agent's state**, that context is worthless.

**Durability** (cache + replay + persistence) is what makes context engineering pay off in production.

<br>

::left::

#### 💥🔄 Crash Recovery

<br>

```mermaid
flowchart LR
  P["<strong>🤖 Agent</strong>"]
  T1["<strong>🔧 Tool 1 ✅</strong>"]
  T2["<strong>🤖 Subagent 1 ✅</strong>"]
  T3["<strong>🪚 Tool 2 ▶️</strong>"]

  P --> T1
  P --> T2
  P --> T3

  style T1 fill:#90EE90,stroke:#228B22,stroke-width:2px,color:#0d5c0d
  style T2 fill:#90EE90,stroke:#228B22,stroke-width:2px,color:#0d5c0d
  style T3 fill:#87CEEB,stroke:#1E90FF,stroke-width:2px,color:#00008B
```

::right::

#### 📋 Replay Log

<br>

| **Step**         | **Component**              | **Status** |
|------------------|---------------------------|------------|
| 1                | 🔧 Tool 1                  | ✅         |
| 2                | 🤖 Subagent 1              | ✅         |
| 3                | 🪚 Tool 2                  | ▶️         |

<style>
.two-cols-header {
  column-gap: 30px; /* Adjust the gap size as needed */
}
</style>

---
layout: default
---

# Chapter 2: Six Design Principles for Self-Healing Agents

1. **Plain Python/TS/JS** — DSLs add fragility; standard control flow makes debugging trivial
2. **Make crashes cheap** — cache + replay log + memory persistence
3. **Observability hooks** — `@flyte.trace`, `@env.task`
4. **Infrastructure-level context** — agents see and fix OOM/network; request more resources
5. **Agent self-service tools** — secure tool building and orchestration
6. **Human-in-the-loop** — debugger and manual feedback when self-service isn't enough

---
layout: two-cols-header
---

# Why Plain Python?

::left::

Loops, fan-out, conditionals, and **try/except** are trivial. No DSL surprises.

Provide **functional hooks** to trace and checkpoint — then get out of the AI engineer's way.

::right::

```python
# src/agent_demo.py (condensed)
@env.task
async def main(simulate_oom: bool = False) -> str:
    data = await fetch_data()
    return await process_step(
        data, simulate_oom=simulate_oom
    )
```

---
layout: two-cols-header
---

# Make Crashes Cheap: Cache + Replay + Persistence

::left::

- **Global cache** — reuse completed steps; no redoing work after a crash
- **Run-level replay log** — full reproducibility; rehydrate state when things go wrong
- **Memory persistence** — retrieved context survives retries; no losing semantic grounding

**Bonus:** Failed runs become **training data** for prompt and context iteration (e.g. context graph).

::right::

```python
# src/cacheable_step.py (condensed)
@env.task
async def fetch_data(source: str) -> flyte.io.File:
    f = flyte.io.File.new_remote()
    with open(f.path, "w") as out:
        out.write(f"context from {source}")
    return f
```

---
layout: two-cols-header
---

# Observability Hooks: Framework-Agnostic

::left::

- **Continuous eval:** pipe production traces into your eval framework; catch regressions early
- **Prompt debugging:** see which prompt variant led to which behavior at which step

::right::

```python
# src/agent_demo.py (condensed)
@env.task
async def fetch_data() -> flyte.io.File:
    ...

@env.task
async def process_step(
    data: flyte.io.File, simulate_oom: bool = False
) -> str:
    if simulate_oom:
        raise MemoryError(
            "Simulated OOM: container needs more memory"
        )
    ...
```

---
layout: two-cols-header
---

# Infrastructure as Context

::left::

Give the agent **system-level observability** in context:

- *"This tool is loading 32Gi but the container has 16Gi"*
- Agent can re-write the tool for less memory, or **request a bigger container**

Agents that write ML code can **dynamically adjust** tool resource requests as they scale.

::right::

```python
# src/infrastructure_as_context.py (condensed)
env_low = flyte.TaskEnvironment(
    name="infra-context-low",
    resources=flyte.Resources(cpu=1, memory="128Mi"),
    ...
)
env_high = flyte.TaskEnvironment(
    name="infra-context-high",
    resources=flyte.Resources(cpu=1, memory="512Mi"),
    ...
)

@main_env.task
async def main(payload: str, use_high: bool = False) -> str:
    if use_high:
        return await process_high(payload)
    try:
        return await process_low(payload)
    except MemoryError:
        return await process_high(payload)
```

---
layout: two-cols-header
---

# Agent Self-Service Tools

::left::

- **Catch and respond to exceptions:** no magic, just write Python to handle exceptions and retry logic
- **Code sandbox:** agents build their own tools safely; optional human review before registration
- **Orchestration sandbox:** compose tools into workflows; catch semantic, logical, network, and system errors and decide what to do next
- **Meta-agent:** agent that can fix bugs in the agent code itself

::right::

```python
# Code sandbox: src/code_sandbox.py
run_generated_code(script_content, a, b)
# ContainerTask or subprocess fallback

# Orchestration sandbox: src/orchestration_sandbox.py
@env.task
def add(x: int, y: int) -> int: ...

@env.sandboxed_task
def leaderboard(
    player_ids: list[int],
) -> dict[str, int]:
    for pid in player_ids:
        score = fetch_score(pid)
        total = add(total, score)
    return {"total": total, ...}

code_pipeline = flyte.sandboxed.code_to_task(
    "partial = add(x,y); result = multiply(partial, scale)",
    ...
)
```

---
layout: two-cols-header
---

# Human-in-the-Loop and Debugging

::left::

When self-service isn't enough:

- **Human-in-the-loop gates** — ultimate fallback for course correction or missing context
- **Platform-native debugger** — when the agent can't handle an exception, fail the run but **fully reproduce** the error with a live debugger

::right::

```python
# src/human_in_the_loop.py — PR 657 (flyteplugins-hitl)
task_env = flyte.TaskEnvironment(
    ..., depends_on=[hitl.env]
)

@task_env.task
async def main() -> int:
    x = await task1()
    event = await hitl.new_event.aio(
        "integer_input_event",
        data_type=int,
        scope="run",
        prompt="What should I add to x?",
    )
    y = await event.wait.aio()
    return await task2(x, y)
```

---
layout: two-cols-header
---

# Chapter 3: What This Looks Like in Practice

::left::

**Demo:** An agent that

1. **Crashes** (e.g. OOM or timeout)
2. **Resumes from cache** — no redoing completed work
3. **Realizes it needs more memory** — infrastructure as context
4. **Provisions more resources** and completes

**Evaluation loop:** Production traces → evals; often **80% of "failures"** are network timeouts or infra, not prompt issues.

::right::

```python
# src/agent_demo.py (condensed)
@env.task
async def fetch_data() -> flyte.io.File:
    ...  # cacheable; reused on retry

@env.task
async def process_step(
    data: flyte.io.File, simulate_oom: bool = False
) -> str:
    if simulate_oom:
        raise MemoryError(
            "Simulated OOM: container needs more memory"
        )
    ...

@env.task
async def main(simulate_oom: bool = False) -> str:
    data = await fetch_data()
    return await process_step(
        data, simulate_oom=simulate_oom
    )
```

---
layout: two-cols-header
---

# Lessons from the Field

**Dragonfly case study** — [How Dragonfly scales agentic research across 250k products](https://www.union.ai/case-study/how-dragonfly-scales-agentic-research-across-250k-products)

::left::

**🤔 Challenge:** Automated solutions architect; living knowledge graph of 250K+ software products. ~190 steps and ~95 LLM calls per product

**✅ Solution:** Tiered task environments on Flyte 2. Cross-run caching (convergence detection), checkpoint-based recovery, full auditability.

**🚀 Results:** 1 hour from local prototype to production-grade remote workflows. 2,000 concurrent workflows; 50% ⬇️ failure recovery time, 30% ⬆️ development velocity; 12 hrs/wk saved on infra.

::right::

```mermaid {scale: 0.47}
flowchart TD
  subgraph D["<strong>🛞 Driver</strong> (4 replicas)"]
    direction LR
    D1["R1"]
    D2["R2"]
    D3["R3"]
    D4["R4"]
    D1 -.- D2 -.- D3 -.- D4
  end
  subgraph C["<strong>🧠 Coordinator</strong> (8 replicas)"]
    direction LR
    C1["R1"]
    C2["R2"]
    C3["R3"]
    C4["..."]
    C8["R8"]
    C1 -.- C2 -.- C3 -.- C4 -.- C8
  end
  subgraph R["<strong>🔎 Researcher</strong> (12 replicas)"]
    direction LR
    R1["R1"]
    R2["R2"]
    R3["R3"]
    R4["R4"]
    R5["..."]
    R12["R12"]
    R1 -.- R2 -.- R3 -.- R4 -.- R5 -.- R12
  end
  subgraph T["<strong>🧰 Tool Layer</strong> (12 replicas)"]
    direction LR
    T1["R1"]
    T2["R2"]
    T3["R3"]
    T4["R4"]
    T5["..."]
    T12["R12"]
    T1 -.- T2 -.- T3 -.- T4 -.- T5 -.- T12
  end
  D --> C --> R --> T
```

---
layout: center
class: text-center
---

# Call to Action

**Tomorrow, do your agents a favor:**

- Build an **observability layer**: Flyte, W&B Weave, Arize Phoenix, LangSmith, MLFlow, etc.
- Don't aim for failure-proof — aim for **cheap failures**, **fast recovery**, and **eval feedback**
- Ask yourself: *"If this crashes at 2 AM, can it recover without me? Will I have the data to improve it?"*

**Help your agents help themselves.**

---
layout: center
class: text-center
---

# Thank You

**Learn more:** [Union.ai](https://union.ai) — come talk at the booth.

Questions?
