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
  mono: 'Yellix'
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

# The agent infrastructure problem

You built an agent, optimized its prompts, engineered its context, implemented an eval harness, and it works beautifully in development…

... then the infrastructure got in the way

<v-clicks>

- ❌ Tools making API calls or querying databases are rate-limited.
- ⚠️ Parallelized subagents/tool calls leads to resource contention and degraded performance.
- 💥 Containers run out of memory, are killed by the scheduler, are preempted by other jobs.
- 🗑️ Agent memory loss or corruption, wiping out precious context.
- 🔓 Agent components (MCPs, coder subagents) are easy to configure insecurely.

</v-clicks>

---
layout: center
---

# Agents Fail at Multiple Layers of the Orchestration Stack

<!-- The semantic and networking layers of the stack get a lot of attention, but the infrastructure layer is just as critical. -->

The problem isn't that agents fail.

It's that recovering from failure is challenging without the full context of how the infrastructure, networking,
logical, and semantic layers interact so that the agent can figure out how to recover from it.

---
layout: center
---

# What Agents are saying...

![Help yourself](https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm0xbXh1NmE0eWtyZzBlNWlhbm1iaWo4cG03YWNrbTQ2djB2YzFlaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/uRb2p09vY8lEs/giphy.gif)

Agents can recover from infra-level failures, but only if we give<br>them the right context.

---
layout: default
---

# Design Principles for Self-Healing Agents

1. **Plain Python/TS/JS** — DSLs incur additional cognitive overhead (for both humans and agents)
1. **Durability & observability hooks** — `@env.task`, `@flyte.trace` works with any framework/stack
1. **Make failures cheap** — global caching, run-level replay log, and state persistence
1. **Infrastructure as context** — agents see and fix OOM/network errors; request more resources
1. **Agent self-service utilities** — secure tool building and orchestration
1. **Human-in-the-loop** — debugger and manual feedback when self-service isn't enough

---
layout: default
---

# Chapter 1: Where Agents Break

| **🧱 Layer** | **❌ Example failures** |
|-----------|---------------------|
| Infrastructure | OOM, container killed or preempted, image pull backoff |
| Network | API rate-limiting, network timeouts, ephemeral service outage |
| Logical | Programming bugs, data validation errors |
| Semantic | Hallucinations, incorrect tool calls, context utilization errors |
| Tool execution | Bad arguments, tool timeouts, tool errors |
| Memory | State wiped or corrupted on crash, context erasure |

---
layout: default
---

# The context and evaluation gap

Your evals typically test **semantic correctness**: *"Does it answer correctly?"*. Likewise, agents
typically focus on recovering from semantic failures: *"I need more context about topic X to answer correctly"*.

<v-clicks>

Agents often don't directly reason about:

- Surviving a network timeout
- Recovering from system-level errors
- Recalling state across retries

</v-clicks>

<v-clicks>

**💡 Insight:** agents can recover from errors at all the layers of the agent stack,
even infrastructure-level failures, but only with the right context and tools ✅.

</v-clicks>

---
layout: default
---

# Context engineering is also an infra problem

If a failure **wipes the agent's state**, that hard-earned context is worthless.

<br>

### Durability: what even is it?

<v-clicks>

It's about making the following very easy:

</v-clicks>

<v-clicks>

- 📋 **Run-level replay log**: immediately resume an agent roll-out where it left off
- 🎒 **Global caching**: don't re-execute shareable compute/io-bound workloads
- 💾 **Intermediate state persistence**: save and restore intermediate state between tasks

</v-clicks>


---
layout: two-cols-header
---

# Replay log

A service that records the state of an agent and its subtasks (tools, subagents, etc.)
at each step.

Avoids task re-execution, prevents memory/context loss, and even recovers from crashes
in the root agent process.


::left::

#### ▶️ Normal Execution

<br>

```mermaid {scale: 0.75}
flowchart LR
  P["<strong>🤖 Agent</strong>"]
  T1["<strong>🔧 Tool 1 ✅<br>Completed</strong>"]
  T2["<strong>🤖 Subagent 1 ✅<br>Completed</strong>"]
  T3["<strong>🪚 Tool 2 ❌<br>Failed</strong>"]

  P --> T1
  P --> T2
  P --> T3

  style P fill:#9370DB,stroke:#6A0DAD,color:#fff
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

---
layout: two-cols-header
---

# Replay log

A service that records the state of an agent and its subtasks (tools, subagents, etc.)
at each step.

Avoids task re-execution, prevents memory/context loss, and even recovers from crashes
in the root agent process.

::left::

#### 💥🔄 Crash Recovery

<br>

```mermaid {scale: 0.75}
flowchart LR
  P["<strong>🤖 Agent</strong>"]
  T1["<strong>🔧 Tool 1 ✅<br>Already done</strong>"]
  T2["<strong>🤖 Subagent 1 ✅<br>Already done</strong>"]
  T3["<strong>🪚 Tool 2 ▶⏳<br>In progress</strong>"]

  P --> T1
  P --> T2
  P --> T3

  style P fill:#9370DB,stroke:#6A0DAD,color:#fff
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
| 3                | 🪚 Tool 2                  | ⏳         |

<style>
.two-cols-header {
  column-gap: 30px; /* Adjust the gap size as needed */
}
</style>


---
layout: two-cols-header
---

# Global Caching

Avoid re-executing workloads where the output can be **shared across all agent runs**.

::left::


Control which tools/subagents are cached and which are not.

```python
@env.task(cache="auto")
async def web_search_tool(url: str) -> str:
    ...

@env.task(cache="auto")
async def db_read_tool(query: str) -> str:
    ...

@env.task(cache="disable")
async def composer_subagent(content: str) -> None:
    ...
```

::right::

```mermaid {scale: 0.75}
flowchart TB

  subgraph I1["Invocation 1"]
    direction TB
    W1[Web Search ✅]
    D1[DB Read ✅]
    G1[Compose report]
    W1 --- D1 --- G1

    style W1 fill:#90EE90,stroke:#228B22,stroke-width:2px,color:#0d5c0d
    style D1 fill:#90EE90,stroke:#228B22,stroke-width:2px,color:#0d5c0d    
    style G1 fill:#87CEEB,stroke:#1E90FF,stroke-width:2px,color:#00008B
  end

  subgraph I2["Invocation 2"]
    direction TB
    W2[Web Search 👀]
    D2[DB Read 👀]
    G2[Compose report]
    W2 --- D2 --- G2

    style W2 fill:#90EE90,stroke:#228B22,stroke-width:2px,color:#0d5c0d
    style D2 fill:#90EE90,stroke:#228B22,stroke-width:2px,color:#0d5c0d
    style G2 fill:#87CEEB,stroke:#1E90FF,stroke-width:2px,color:#00008B
  end

  A[🤖 Agent] --write a report about LLMs--> I1
  A --write a report about LLMs--> I2
  style A fill:#9370DB,stroke:#6A0DAD,color:#fff
```



<!--
- Cache key: inputs + task name + interface hash + (optional) version
- `behavior="auto"`: cache version from source-code hash; invalidates when code changes
- `behavior="override"`: pin a version for stable cache across deploys
- Project/domain isolation so dev/staging/prod caches don’t collide
 -->

---
layout: two-cols-header
---

# Intermediate state persistence

**Abstract away** serializing and deserializing state (memory, data) to object store.

::left::

<!--
- **Materialized**: dataclasses, Pydantic — full content serialized between tasks
- **Offloaded**: `File`, `Dir`, `DataFrame` — stored in blob store; tasks get references, data fetched on use
- Same types work as inputs/outputs; no manual `pickle` or bucket plumbing for agent state
-->


```python {all|5,14|8,16|5,14|13,18}
class AgentState(BaseModel):
    messages: list[Message]

@env.task
async def llm(state: AgentState) -> AgentState: ...

@env.task
async def tool(state: AgentState) -> AgentState: ...

@env.task
async def agent() -> str:
    state = AgentState()
    while not await done(state):
        message = await llm(state)
        if is_tool_call(state):
            message = await tool(state)
        state.messages.append(message)
    return await compose_final_answer(state)
```

::right::


<div class="flex justify-center items-center h-full">

```mermaid {scale: 0.5}
flowchart TB
  subgraph agent["Agent Process"]
    direction TB
    C1[LLM call 1]
    T1[Tool call]
    C2[LLM call 2]

    C1 --> T1 --> C2
  end

  subgraph O["Object Store"]
    direction TB
    S1[State S']
    S2[State S'']
  end

  C1 --> S1
  S1 --> T1
  T1 --> S2
  S2 --> C2
  C2 --> Output

  style C1 fill:#9370DB,stroke:#6A0DAD,color:#fff
  style T1 fill:#9370DB,stroke:#6A0DAD,color:#fff
  style C2 fill:#9370DB,stroke:#6A0DAD,color:#fff
  style S1 fill:#FDB51F,stroke:#E5A31B,color:#000
  style S2 fill:#FDB51F,stroke:#E5A31B,color:#000
  style Output fill:#FDB51F,stroke:#E5A31B,color:#000
```

</div>

---
layout: default
---

# Chapter 2: Six Design Principles for Self-Healing Agents

1. **Plain Python/TS/JS** — DSLs incur additional cognitive overhead (for both humans and agents)
1. **Durability & observability hooks** — `@flyte.trace`, `@env.task`; works with any framework/stack
1. **Make failures cheap** — global caching, run-level replay log, and state persistence
1. **Infrastructure as context** — agents see and fix OOM/network; request more resources
1. **Agent self-service utilities** — secure tool building and orchestration
1. **Human-in-the-loop** — debugger and manual feedback when self-service isn't enough

---
layout: two-cols-header
---

# Plain Python/TS/JS

Or, any other general purpose programming language really.

::left::

🔁 Loops, fan-out, conditionals, and *try/except* are trivial. No DSL surprises.

<v-click at="2">

⭐️ Exceptions are a perfect delivery mechanism for critical context about failures
at all layers of the stack.

</v-click>

<v-click at="3">

🪝 Provide **functional hooks** to trace and checkpoint intermediate state — then get
out of the AI engineer's way.

</v-click>

::right::

```python {all|11-19|16-19|5,8}{at:1}
import flyte

env = flyte.TaskEnvironment("agent", image=flyte.Image.from_debian_base())

@flyte.trace
async def tool(x: int, y: int) -> AgentState: ...

@env.task(retries=RetryStrategy(5))
async def agent() -> str:
    state = AgentState()
    while not await done(state):
        message = await llm(state)
        if is_tool_call(state):
            try:
                message = await tool(parse_tool_call(state))
            except ToolArgsError as exc:
                message = await llm(
                    state, prompt=f"Fix the tool args: {str(exc)}"
                )
        state.messages.append(message)
    return await compose_final_answer(state)
```

---
layout: two-cols-header
---

# Durability & observability hooks

Make it really easy to trace, checkpoint, and persist intermediate state.

::left::

<v-click at="1">

`TaskEnvironment`: infrastructure-level configuration: container image, resources, etc.

</v-click>

<v-click at="2">

`@env.task`: containerized functions that auto-persist intermediate state

</v-click>

<v-click at="3">

`@flyte.trace`: helper functions inside a task that are tracked by the replay log

</v-click>

<!-- **Continuous eval:** pipe production traces into your eval framework; catch regressions early

**Prompt debugging:** see which prompt variant led to which behavior at which step -->

::right::

```python {all|3-7|9-10,15-21|12-13}{at:1}
import flyte

image = flyte.Image.from_debian_base().with_pip_packages(["pandas"])
agent_env = flyte.TaskEnvironment("agent", image=image)
train_model_env = flyte.TaskEnvironment(
    "train_model", image=image, resources=flyte.Resources(cpu=4, memory="4Gi")
)

@train_model_env.task
async def train_model_tool(code: str, data: flyte.io.DataFrame) -> AgentState: ...

@flyte.trace
async def llm(url: str) -> str: ...

@agent_env.task
async def agent(prompt: str, data: flyte.io.DataFrame) -> str:
    code = await llm(
        data,
        prompt="Write a Python script to train a model on the data"
    )
    return await train_model_tool(code, data)
```

<!-- the example should show tasks and traces -->
<!-- show a screenshot or gif of the Union UI -->

---
layout: two-cols-header
---

# Make failures cheap

::left::

- **Run-level replay log** — full reproducibility; rehydrate state when things go wrong
- **Global caching** — reuse completed steps; no redoing work after a crash
- **Intermediate state persistence** — retrieved context survives retries; no losing semantic grounding

**Bonus:** Failed runs become *training data* or *additional context* for the agent to learn from.

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

<!-- Example should show cache in task decorator, file object creation, and task retry config -->
<!-- Add mermaid cart diagram of how each component aids in recovery -->

---
layout: two-cols-header
---

# Infrastructure as context

::left::

Give the agent **infra-level context**:

- *"This tool OOM'd at 16Gi of memory, maybe I can (a) load less data or (b) request for more memory"*
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

<!--
example should show catching infra-level errors, parsing the error message, and
agent reacting to it
-->

---
layout: two-cols-header
---

# Agent self-service utilities

::left::

- **Catch and respond to exceptions:** no magic, just write Python to handle exceptions and retry logic
- **Code sandbox:** agents build their own tools safely; optional human review before registration
- **Orchestration sandbox:** compose tools into workflows; catch semantic, logical, network, and system errors and decide what to do next

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

<!-- example of container task sandbox, orchestration sandbox (code mode) -->

---
layout: two-cols-header
---

# Human-in-the-Loop and Debugging

::left::

When self-service isn't enough:

- **Human-in-the-loop gates** — ultimate fallback for course correction or missing context
- **Platform-native debugging** — when the agent can't handle an exception, fail the run but **fully reproduce** the error with a live debugger

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

<!-- add a more realistic example of human-in-the-loop being ultimate fallback (after a few try-excepts -->

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

**Evaluation loop:** Production traces become a data source for evals, or additional context for agents in the future.

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

<!-- add a gif of run the shows all the elements of the demo -->

---
layout: two-cols-header
---

# Lessons from the Field

**Dragonfly case study** — [How Dragonfly scales agentic research across 250k products](https://www.union.ai/case-study/how-dragonfly-scales-agentic-research-across-250k-products)

::left::

**🤔 Challenge:** Automated solutions architect - build a living knowledge graph of 250K+ software products. ~190 steps and ~95 LLM calls per product

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

<style>
.two-cols-header {
  column-gap: 30px; /* Adjust the gap size as needed */
}
</style>

---
layout: center
class: text-center
---

# Conclusion

**Tomorrow, do your agents a favor:**

- Observability is necessary but not sufficient: a durability layer helps agents recover quickly.
- Don't aim for failure-proof — aim for **cheap failures**, **fast recovery**, and **eval feedback**
- Try/except is critical: errors are the most natural way to deliver critical context to the agent.

**Help your agents help themselves.**

---
layout: center
class: text-center
---

# Thank You

**Learn more:** [Union.ai](https://union.ai) — come talk at the booth.

Questions?
