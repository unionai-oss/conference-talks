---
theme: seriph
title: Put resilient agents in production
titleTemplate: '%s | MLOps Seattle 2026'
info: |
  ## Put resilient agents in production with Union.ai / Flyte.
drawings:
  persist: false
transition: none
fonts:
  sans: 'DM Sans'
  serif: 'DM Sans'
  mono: 'Yellix'
themeConfig:
  primary: '#FDB51F'
routerMode: hash
mdc: true
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

# Put resilient agents in production

<br />

### Haytham Abuelfutuh @ Union.ai

MLOps Seattle 2026

---
layout: center
---

# So you built an agent...

You optimized the prompts, engineered the context, wrote an eval harness, and it works beautifully in development...

... then you tried to run it in production.

- ❌ Your tools need to query proprietary data sources with least-privilege access
- 💥 A tool call needs 32GB of RAM but your agent runtime is a single node
- ⚠️ You fan out 20 subagent calls and they're all fighting for the same resources
- 😵 Your container goes OOM, gets killed, and the spot instance vanishes
- 🗑️ All that hard-earned context? Gone. The agent starts from scratch.

---
layout: center
---

# The problem isn't that agents fail

It's that they can't figure out _why_ they failed.

An agent that sees "process killed" has no idea what to do. An agent that sees
"OOM: requested 32GB, limit 16GB" can actually fix the problem.

Recovery requires context from **every layer** of the stack — infrastructure, networking,
logical, and semantic — working together.

---
layout: default
---

# Where agents actually break

| **🧱 Layer** | **❌ What goes wrong** |
|-----------|---------------------|
| Semantic | Hallucinations, incorrect tool calls, context utilization errors |
| Logical | Programming bugs, data validation errors |
| Infrastructure | OOM, container killed or preempted, module not found |
| Network | API rate-limiting, network timeouts, ephemeral service outage |
| Tool execution | Bad arguments, tool timeouts, tool errors |
| Context | State wiped or corrupted on crash, context erasure, context bloat |

Most eval harnesses test **semantic correctness**: *"Does it answer correctly?"*

But nobody's evaluating: *"Can it survive getting OOM-killed on retry #3?"*

---
layout: default
---

# 3 Design Principles for resilient agents

<br>

1. **Dynamic** — plain code, provision infra on the fly. Adapt to failures in real time.
1. **Durable** — replay log, caching, state persistence. Survive failures without losing work.
1. **Defended** — sandboxes, human-in-the-loop. Bounded execution so agents can't spiral.

---
layout: two-cols-header
---

# Dynamic: Plain code that's infra-aware

No DSL — loops, fan-out, try/except are trivial. Exceptions deliver critical context from every layer.

::left::

<v-click at="1">

`TaskEnvironment` configures infra per concern: container image, resources, etc.

🔁 Loops, fan-out, conditionals, and *try/except* are trivial. No DSL surprises.

</v-click>

<v-click at="2">

🪝 Provide **functional hooks** to trace and checkpoint intermediate state — then get
out of the AI engineer's way.

</v-click>

<v-click at="3">

⭐️ Exceptions are a perfect delivery mechanism for critical context about failures
at all layers of the stack.

The Flyte SDK exposes system-level errors like `flyte.errors.OOMError` as exceptions.

</v-click>

::right::

```python {all|4-7,14|10|15,20}{at:1}
import flyte
from flyte.io import File, DataFrame

image = flyte.Image.from_debian_base().with_pip_packages(["pandas"])
agent_env = flyte.TaskEnvironment("agent", image=image)
tool_env = flyte.TaskEnvironment(
    "tools", image=image, resources=flyte.Resources(cpu=4, memory="4Gi")
)

@agent_env.task(retries=3)
async def mle_agent(data: DataFrame, max_iter: int) -> tuple[str, File]:
    code = await write_code("Write a Python script to train a model...")
    resources = {"memory": "128Mi", "cpu": 4}
    for _ in range(max_iter):
        try:
            model = await run_code.override(
                resources=flyte.Resources(**resources)
            )(code, data)
            break
        except flyte.errors.OOMError as exc:
            resources = await adjust_resources(
                prompt=f"Encountered error {exc}, adjust the memory"
            )
    ...
```

---
layout: two-cols-header
---

# Durable: Replay log

Automatically record the state of an agent and its subtasks at each step.
This avoids re-execution, prevents context loss, and recovers from crashes.

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
  column-gap: 30px;
}
</style>

---
layout: two-cols-header
---

# Durable: Caching & state persistence

Avoid redoing work. Persist state so retries don't lose context.

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

State (messages, data) is **auto-serialized** to object store between tasks — no manual pickle or bucket plumbing.

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

---
layout: two-cols-header
---

# Durable: Make failures cheap

Your agent _will_ fail. The question is: how expensive is each failure?

::left::

```python {all|1-2,12|4-5,13|7-8,14}
@flyte.trace
async def write_code(prompt: str) -> str: ...

@tool_env.task(cache="auto")
async def run_code(code: str, data: DataFrame) -> File: ...

@flyte.trace
async def finalize_answer(code: str, model: File) -> str: ...

@agent_env.task(retries=3)
async def mle_agent(prompt: str, data: DataFrame) -> tuple[str, File]:
    code = await write_code("Write a Python script to train a model...")
    model = await run_code(code, data)
    return await finalize_answer(code, model)
```

<v-click>

⭐️ Failed runs become *training data* or *additional context* for the agent to learn from.

</v-click>

::right::

<div class="flex justify-center items-center h-full">

```mermaid {scale: 0.525}
flowchart TB
  subgraph Agent["Agent"]
    direction TB
    L[Write code<br>📋 Checkpointed]
    T[Run code<br>🎒 Cached]
    F[Finalize answer<br>📋 Checkpointed]
    L --> T --> F
  end

  subgraph State["Object store"]
    direction TB

    S1[Code]
    S2[Model]
  end

  L -.-> S1
  S1 -.-> T
  T -.-> S2
  S2 -.-> F
  F --> Out[Code, Model]

  style L fill:#9370DB,stroke:#6A0DAD,color:#fff
  style T fill:#9370DB,stroke:#6A0DAD,color:#fff
  style F fill:#9370DB,stroke:#6A0DAD,color:#fff
  style S1 fill:#FDB51F,stroke:#E5A31B,color:#000
  style S2 fill:#FDB51F,stroke:#E5A31B,color:#000
  style Out fill:#FDB51F,stroke:#E5A31B,color:#000
```

</div>

---
layout: two-cols-header
---

# Defended: Secure sandboxes

Agents write and execute code in isolated, secure containers — with a tight error-iteration loop.

::left::

<v-click at="1">

Agents build their own tools safely in a sandboxed container.

</v-click>

<v-click at="2">

Sandbox runs agent-generated code securely — no network access, no host escape.

</v-click>

<v-click at="3">

On error, the agent re-writes code and tries again without losing state.

</v-click>

::right::

```python {all|7-13|14|15-18}{at:1}
import flyte.sandbox

@agent_env.task(retries=3)
async def mle_agent(data: DataFrame, max_iter: int) -> File:
    code = await write_code("Write a Python script to train a model...")
    for _ in range(max_iter):
        try:
            code_sandbox = flyte.sandbox.create(
                code=code,
                inputs={"data": DataFrame},
                outputs={"model": File},
                data=data,
            )
            return await code_sandbox.run.aio(data=data)
        except flyte.errors.RuntimeUserError as exc:
            code, tests = await write_code(
                f"Re-write code \n{code}\nbased on error: {exc}."
            )
```

---
layout: two-cols-header
---

# Defended: Human-in-the-loop

::left::

Sometimes the agent genuinely can't figure it out. That's OK — the important thing is that it _knows_ it's stuck and asks for help instead of spiraling.

<v-click at="1">

When `max_iter` is exhausted, get more context from a human (or external system)

</v-click>

<v-click at="2">

Recursively call the agent with the additional context.

</v-click>

::right::

```python {all|17-22|23}{at:1}
import flyteplugins.hitl as hitl

agent_env = flyte.TaskEnvironment(..., depends_on=[hitl.env])

@agent_env(retries=3)
async def mle_agent(
    data: DataFrame, max_iter: int, ctx: str | None = None
) -> File:
    ...
    for _ in range(max_iter):
        try:
            return await pipeline(data)      
        except flyte.errors.RuntimeUserError as exc:
            # code re-write handling
            ...

    event = await hitl.new_event.aio(
        "get_more_context",
        data_type=str,
        prompt="Model training failed, please provide more context.",
    )
    more_context = await event.wait.aio()
    mle_agent(data, max_iter, ctx=more_context)
```

---
layout: center
---

# What this looks like in practice

Agents that request more memory and compute when a tool is memory/compute-bound.

<img src="/static/mle-agent-1.png" alt="MLE agent workflow with sandbox retries" style="filter: brightness(1.35);">

---
layout: center
---

# What this looks like in practice

Agents that recover from logical, networking, semantic, and tool execution failures — without starting from scratch.

<img src="/static/mle-agent-2.png" alt="MLE agent workflow with sandbox retries" style="filter: brightness(1.35);">

---
layout: center
---

# Real-world: deep research at scale

**Dragonfly** — [scaling agentic research across 250k products](https://www.union.ai/case-study/how-dragonfly-scales-agentic-research-across-250k-products)

An agent that builds a living knowledge graph of SaaS products.

- `250K+` software products
- `~200` steps per agent call
- `~100` LLM calls per product

<br>
<img src="/static/qr-code-dragonfly.png" alt="Dragonfly agentic research workflow" style="max-width: 180px;">

---
layout: two-cols-header
---

# How they scaled it

Tiered task environments on Flyte 2.

::left::

- **Cross-run caching**: pay for LLM API calls once.
- **Semantic convergence detection**: coordinator consolidates overlapping research streams.
- **Checkpoint-based recovery**: spot instance interruptions become a non-issue.
- **Full auditability**: every agent decision and tool call is traced.

::right::

```mermaid {scale: 0.55}
flowchart TD
  subgraph D["<strong>🛞 Agent</strong> (4 replicas)"]
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
  column-gap: 30px;
}
</style>

---
layout: center
class: text-center
---

# TL;DR — remember the 3 Ds

<v-clicks>

- **Dynamic** — plain code, infra as context. Agents can fix their own infra failures if they can see them.
- **Durable** — replay log, caching, state persistence. Don't aim for failure-proof — aim for cheap failures and fast recovery.
- **Defended** — sandboxes and human-in-the-loop. Let agents iterate safely, and escalate when stuck.

</v-clicks>

---
layout: center
class: text-center
---

# Thank You

Questions?

Come talk to me and the team at the [Union.ai](https://union.ai) booth.

<img src="/static/qr-code-union.png" alt="Union.ai booth" style="max-width: 180px;">
