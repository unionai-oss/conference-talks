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
</style>

# The Orchestration Stack for Observable, Debuggable, and Durable Agents

<br />

### Niels Bantilan @ Union.ai

MLOps South Bay 2026

---
layout: center
class: text-center
---

# The 2 AM Problem

Remember the last time you deployed an agent that worked perfectly in development…

…then **mysteriously failed in production at 2 AM**?

---
layout: center
class: text-center
---

# When Agents Fail, They Fail *Opaquely*

- Ran out of memory halfway through a task
- A network hiccup killed the entire workflow
- It just… **stopped**. No logs, no traces. Just silence.

Recovering felt like **archaeology**.

---
layout: center
class: text-center
---

# Help Agents Help Themselves

![Help yourself](https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm0xbXh1NmE0eWtyZzBlNWlhbm1iaWo4cG03YWNrbTQ2djB2YzFlaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/uRb2p09vY8lEs/giphy.gif)

The problem isn't that agents fail. It's that when they fail, we have no way to **observe**, **debug**, or **recover** cheaply.

---
layout: default
---

# Thesis: Five Design Elements for Production Agents

1. **Plain Python (or TS/JS)** — minimize DSLs; loops, fan-out, try/except stay trivial
2. **Make failures cheap** — global cache, run-level replay, memory persistence
3. **Infrastructure-level context** — let agents see OOM/network errors and request more resources
4. **Agent self-service tools** — secure tool building and orchestration
5. **Observability hooks** — `@flyte.trace`, `@env.task`; framework-agnostic, works with any stack
6. **Human-in-the-loop** — debugger and manual feedback when self-service isn't enough

---
layout: default
---

# Chapter 1: Where Agents Break — and Where Evals Miss

**The full stack:** code execution → tool calls → network → infrastructure → semantic context → memory

**Failure modes at each layer:**

| Layer | Example failure |
|-------|------------------|
| Infrastructure | OOM, container killed |
| Network | API throttling, timeouts |
| Tool execution | Bad args, timeout |
| Semantic | Hallucinated tool calls, wrong answer |
| Memory | State wiped on crash |

---
layout: default
---

# The Evaluation Gap

Your evals test **semantic correctness**: *"Does it answer right?"*

They often **miss**:

- Does it survive a network timeout?
- Does it recover from OOM?
- Does it preserve state across retries?

**Insight:** Agents can recover from *semantic* failures (prompts, context, control flow) — but only if **infrastructure doesn't kill them first**.

---
layout: default
---

# Context Engineering as a Layer

RAG, MCP servers, system prompts, skills → **semantic robustness**.

But if a crash **wipes the agent's state**, that context is worthless.

**Durability** (cache + replay + persistence) is what makes context engineering pay off in production.

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
layout: default
---

# Why Plain Python?

Loops, fan-out, conditionals, and **try/except** are trivial. No DSL surprises.

```python
# src/agent_demo.py (condensed)
@env.task
async def main(simulate_oom: bool = False) -> str:
    data = await fetch_data()
    return await process_step(data, simulate_oom=simulate_oom)
```

Provide **functional hooks** to trace and checkpoint — then get out of the AI engineer's way.

---
layout: default
---

# Make Crashes Cheap: Cache + Replay + Persistence

- **Global cache** — reuse completed steps; no redoing work after a crash
- **Run-level replay log** — full reproducibility; rehydrate state when things go wrong
- **Memory persistence** — retrieved context survives retries; no losing semantic grounding

```python
# src/cacheable_step.py (condensed)
@env.task
async def fetch_data(source: str) -> flyte.io.File:
    f = flyte.io.File.new_remote()
    with open(f.path, "w") as out:
        out.write(f"context from {source}")
    return f
```

**Bonus:** Failed runs become **training data** for prompt and context iteration (e.g. context graph).

---
layout: default
---

# Observability Hooks: Framework-Agnostic

```python
# src/agent_demo.py (condensed)
@env.task
async def fetch_data() -> flyte.io.File:
    ...

@env.task
async def process_step(data: flyte.io.File, simulate_oom: bool = False) -> str:
    if simulate_oom:
        raise MemoryError("Simulated OOM: container needs more memory")
    ...
```

- **Continuous eval:** pipe production traces into your eval framework; catch regressions early
- **Prompt debugging:** see which prompt variant led to which behavior at which step

---
layout: default
---

# Infrastructure as Context

Give the agent **system-level observability** in context:

- *"This tool is loading 32Gi but the container has 16Gi"*
- Agent can re-write the tool for less memory, or **request a bigger container**

Agents that write ML code can **dynamically adjust** tool resource requests as they scale (small run → low resources; production → more).

---
layout: default
---

# Agent Self-Service Tools

- **Catch and respond to exceptions:** no magic, just write Python to handle exceptions and retry logic
- **Code sandbox:** agents build their own tools safely; optional human review before registration
- **Orchestration sandbox:** compose tools into workflows; catch semantic, logical, network, and system errors and decide what to do next
- **Meta-agent:** agent that can fix bugs in the agent code itself

---
layout: default
---

# Human-in-the-Loop and Debugging

When self-service isn't enough:

- **Human-in-the-loop gates** — ultimate fallback for course correction or missing context
- **Platform-native debugger** — when the agent can't handle an exception, fail the run but **fully reproduce** the error with a live debugger

---
layout: default
---

# Chapter 3: What This Looks Like in Practice

**Demo:** An agent that

1. **Crashes** (e.g. OOM or timeout)
2. **Resumes from cache** — no redoing completed work
3. **Realizes it needs more memory** — infrastructure as context
4. **Provisions more resources** and completes

```python
# src/agent_demo.py (condensed)
@env.task
async def fetch_data() -> flyte.io.File:
    ...  # cacheable; reused on retry

@env.task
async def process_step(data: flyte.io.File, simulate_oom: bool = False) -> str:
    if simulate_oom:
        raise MemoryError("Simulated OOM: container needs more memory")
    ...

@env.task
async def main(simulate_oom: bool = False) -> str:
    data = await fetch_data()
    return await process_step(data, simulate_oom=simulate_oom)
```

**Evaluation loop:** Production traces → evals; often **80% of "failures"** are network timeouts or infra, not prompt issues.

---
layout: default
---

# Lessons from the Field

- Customers ship **faster** when they stop over-optimizing prompts for hypothetical cases and start making **orchestration resilient** to real-world failures
- **Start small.** Make crashes cheap. Turn production failures into evaluation data.

---
layout: center
class: text-center
---

# Call to Action

**Tomorrow, do your agent a favor:**

- Use an **observability tool**: LangSmith, W&B Weave, Arize Phoenix
- Don't aim for failure-proof — aim for **cheap failures** and **eval feedback**
- Ask: *"If this crashes at 2 AM, can it recover without me? Will I have the data to improve it?"*

**Help your agents help themselves.**

---
layout: center
class: text-center
---

# Thank You

**Learn more:** [Union.ai](https://union.ai) — come talk at the booth.

Questions?
