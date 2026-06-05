# Building an AutoEnvFactory with OpenEnv and Flyte

- **Topic:** Training (techniques and libraries for training)
- **Submission Type:** Session Presentation (25 minutes)
- **Audience Level:** Intermediate
- **Presented this talk before?** No

---

## Description / Abstract

> Paste into Sessionize. Limit: 1200 characters.

RL post-training is bottlenecked by environment throughput, not compute. With
GRPO-style training you need thousands of concurrent episodes, but most
environment setups top out at dozens — and worse, every new task means writing a
new environment by hand.

OpenEnv (the Meta–PyTorch / Hugging Face standard) fixes the *interface*: a
Gymnasium-style `reset` / `step` / `state` API, packaged as a container, that
plugs straight into TRL's `GRPOTrainer` via `environment_factory`. This talk
asks the next question: can we *generate* OpenEnv-compatible environments from a
task spec, then scale them to the concurrency RL training actually demands?

I'll walk through an "AutoEnvFactory": take a task description, emit a valid
OpenEnv environment (action/observation models, reward, container), validate it
on the Hub's Human-Agent view, and serve thousands of concurrent episodes. I'll
show the TRL training loop consuming it, the real failure modes (reward shaping,
action-space sprawl, throughput ceilings), and how a workflow engine like Flyte
is one open way to fan environments and rollouts across a cluster. You'll leave
able to turn task specs into training environments.

---

## Talk Outline (25 minutes)

### Hook (~3 min)
- The wave: open RL post-training (GRPO, RLVR) is now within reach for the
  community via TRL, TorchForge, verl, and SkyRL.
- The bottleneck (quote the OpenEnv scaling work): training is starved by
  *environment throughput*, not GPUs — most setups max out at dozens of
  concurrent sessions, and authoring each new environment is manual.
- **[Governing idea]** If environments are the scarce resource, we should treat
  *environment creation and scaling as a first-class, automatable step* — turn a
  task spec into a standardized, verifiable, horizontally-scalable OpenEnv, the
  same way we turned models into checkpoints.

### Chapter 1 — OpenEnv as the contract (~4 min)
- The Gymnasium-style API: `reset()`, `step()`, `state()`; typed action /
  observation models; container-first deployment over HTTP/WebSocket.
- Why a standard matters: the same environment runs across TRL, TorchForge,
  verl, and SkyRL with no rollout glue.
- The Hub's Human-Agent view as a free correctness check before you spend a
  single GPU-hour.

### Chapter 2 — The AutoEnvFactory: spec → environment (~6 min)
- Input: a task description + the tools the agent may use.
- Output: a valid OpenEnv environment — action/observation Pydantic models, a
  reward function, and a Dockerfile — scaffolded with `openenv init`.
- The closed-contract trick (transferable from kernel-codegen work): generate
  the environment *against the OpenEnv spec schema* so a malformed environment
  fails validation before it is ever pushed or trained against.
- Running case study: a graph-traversal / "maze" task family, generated rather
  than hand-written.

### Chapter 3 — Plugging into the PyTorch training loop (~5 min)
- TRL `GRPOTrainer` with `environment_factory`: the trainer handles the
  multi-turn generate → parse-tool-call → `step` → feed-back loop with no custom
  rollout code.
- Generating trajectories efficiently with vLLM.
- The real implementation challenges (the expertise slide): reward shaping
  (dense vs. terminal), action-space sprawl (restrict to one action type),
  state validation, and context-length / OOM control (chunking + LoRA).

### Chapter 4 — Scaling environments to RL-grade concurrency (~5 min)
- The throughput tiers: local Docker for dev, HF Spaces for demos, multi-node
  behind a load balancer for >2K concurrent episodes (16K demonstrated).
- One container per GPU for GPU-backed environments.
- Orchestration: fanning environment servers + rollouts across a cluster. A
  workflow engine like **Flyte** is *one open option* for the map-style fan-out
  and lifecycle management — framed as infra, not the point.

### Conclusion / CTA (~3 min)
- The transferable idea: **generate environments, don't hand-write them** — and
  make them OpenEnv-standard so they're portable and scalable by construction.
- What this does **not** do: it won't invent reward signals for genuinely
  ambiguous tasks; verifiable-reward tasks generate cleanly, fuzzy ones still
  need human judgment.
- **CTA:** Contribute generated environments back to the OpenEnv Hub.
- OSS landscape: OpenEnv, TRL, TorchForge, verl, SkyRL, Gymnasium, vLLM.

---

## Speaker

- **Name:** Niels Bantilan
- **Tagline:** Chief Machine Learning Engineer, Union.ai
- **Company:** Union.ai
- **Bio (≤500 chars):** Niels is the Chief Machine Learning Engineer at Union, a
  core maintainer of Flyte, an open source workflow orchestration tool, and
  creator of Pandera, a data validation and testing tool for dataframes. His
  mission is to help data science and machine learning practitioners be more
  productive. His research interests include reinforcement learning, NLP, ML in
  creative applications, and fairness, accountability, and transparency in
  automated systems.
