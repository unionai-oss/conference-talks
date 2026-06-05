# Introduction to OpenEnv

- **Topic:** Introduction (foundational concepts, beginner-friendly workflows)
- **Submission Type:** Session Presentation (25 minutes)
- **Audience Level:** Beginner
- **Presented this talk before?** No

---

## Description / Abstract

> Paste into Sessionize. Limit: 1200 characters.

Agentic RL is moving fast, but the ecosystem still has a basic plumbing problem:
everyone builds their own environment interface. A coding agent, a browser agent,
and a game-playing agent all need the same primitive loop — reset the world, take
an action, observe what changed, compute a reward — but every project wires that
loop differently.

OpenEnv, a Meta-PyTorch and Hugging Face collaboration, gives the PyTorch
community a shared contract for these environments: familiar Gymnasium-style
`reset`, `step`, and `state` APIs; containerized execution; Hub publishing; and
direct integration with TRL's `GRPOTrainer` through `environment_factory`.

This beginner-friendly talk starts from zero. We'll build a tiny environment,
turn its public methods into model-callable tools, train against it with TRL, and
explain when to use an environment instead of a stateless tool call or static
dataset. Along the way, we'll cover action/observation design, reward shaping,
and the scaling path from local Docker to hosted or clustered environments. You
will leave ready to build, publish, and train on your first OpenEnv.

---

## Talk Outline (25 minutes)

### Hook (~3 min)
- The wave: GRPO/RLVR, TRL, TorchForge, verl, and SkyRL are making open RL
  post-training practical.
- The bottleneck: agentic tasks need stateful worlds, but most teams still
  hand-roll the environment contract.
- **[Governing idea]** OpenEnv makes environments a reusable PyTorch ecosystem
  artifact, not one-off rollout glue.

### Chapter 1 — What is an environment? (~5 min)
- Static dataset vs. stateless tool call vs. stateful environment.
- The core loop: `reset` → action/tool method → observation → reward → repeat.
- Examples: Wordle, BrowserGym, code execution, graph navigation, games.

### Chapter 2 — The OpenEnv contract (~6 min)
- Gymnasium-style `reset`, `step`, and `state` mental model.
- Container-first deployment and WebSocket/server execution.
- Hub publishing and Human-Agent validation as the fastest sanity check.
- Why public methods and docstrings matter: TRL turns them into tool schemas.

### Chapter 3 — Training with TRL (~6 min)
- `GRPOTrainer(environment_factory=...)`: one environment instance per rollout.
- The trainer handles generate → parse tool call → execute method → feed
  observation back to the model.
- Minimal live example: an echo/counter/maze environment with a simple reward.
- When to use `environment_factory` vs. a custom `rollout_func`.

### Chapter 4 — Design and scaling lessons (~4 min)
- Good action spaces are small and typed; good observations are compact and
  verifiable.
- Reward shaping: start with terminal reward, add dense rewards only when needed.
- Scaling path: local Docker for development, Hub/Spaces for demos, multi-node
  service pools when training needs thousands of concurrent episodes.

### Conclusion / CTA (~1 min)
- **CTA:** Build one tiny OpenEnv this week and train a small model against it.
- OSS landscape: OpenEnv, TRL, TorchForge, verl, SkyRL, Gymnasium, BrowserGym.

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
