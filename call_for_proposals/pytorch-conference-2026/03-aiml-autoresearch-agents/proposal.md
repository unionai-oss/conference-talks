# AI/ML Autoresearch with agents

- **Topic:** Introduction (foundational concepts, beginner-friendly workflows)
- **Submission Type:** Session Presentation (25 minutes)
- **Audience Level:** Beginner
- **Presented this talk before?** No

---

## Description / Abstract

> Paste into Sessionize. Limit: 1200 characters.

"AI that does AI research" sounds like hype — until you break it into parts you
already know. An autoresearch agent is just a loop: form a hypothesis, write
PyTorch code, run an experiment, read the metrics, decide what to try next. The
hard part isn't intelligence; it's making each step verifiable so the loop
doesn't drift into confident nonsense.

This beginner-friendly session builds intuition for autonomous ML research
agents from the ground up. We start with the manual research loop every
practitioner runs by hand, then add one piece of automation at a time:
idea generation, an agent that edits and runs a `torch` training script,
metric-driven ranking, and a tree search over experiments (the pattern behind
The AI Scientist and similar systems).

Along the way I'll show the design principles that separate a useful research
agent from a demo: closed action spaces, "thin control over thick state" (the
File-as-Bus pattern), and verification gates so results are trustworthy. Using
two concrete case studies — auto-tuning kernels and auto-generating RL
environments — you'll leave knowing how to put an agent to work on your own
experiments, and where to keep a human in the loop.

---

## Talk Outline (25 minutes)

### Hook (~3 min)
- The wave: 2026 brought autonomous ML research systems (The AI Scientist passing
  a workshop peer review; long-horizon "AiScientist"-style agents) from novelty
  to something you can actually run.
- The fear/skepticism: "agents that do research" sounds like it either replaces
  you or hallucinates papers. Both miss what's actually happening.
- **[Governing idea]** Autoresearch is not magic — it's the *manual research loop
  you already run*, automated step by step, where the real engineering is making
  each step **verifiable** so the loop compounds instead of drifting.

### Chapter 1 — The research loop you already run (~4 min)
- Hypothesis → implement in PyTorch → train → read metrics → revise. Draw it as a
  loop on one slide.
- Reframe: a "dataset" is a frozen experience buffer; an "experiment" is one step
  of search. Agents automate the *search*, not the science.

### Chapter 2 — Automating one step at a time (~6 min)
- **Idea generation:** an LLM proposes hypotheses (and debates them).
- **Implementation:** an agent edits and runs a `torch` training script.
- **Evaluation:** metric-driven ranking of runs — the agent reads `loss`/`acc`
  the way you do.
- **Search:** agentic *tree search* over experiments (num_workers parallel paths,
  a bounded number of nodes), guided by an experiment-manager agent.

### Chapter 3 — What separates a useful agent from a demo (~6 min)
- **Closed action spaces:** the agent picks from a bounded menu (configs,
  transformations) so it can't invent invalid moves — shown concretely later.
- **Thin control over thick state (File-as-Bus):** keep orchestration light; put
  the durable project state (plans, code, logs, results) in files so long runs
  stay coherent across agent invocations.
- **Verification gates:** compile/verify/measure before a result counts — the
  single most important reason to trust the output.

### Chapter 4 — Two concrete case studies (~4 min)
- **Autoresearch on kernels:** an agent proposes Triton kernel configs, then
  *compiles → verifies vs. a PyTorch reference → benchmarks* before keeping one.
- **Autoresearch on environments:** an agent generates RL training environments
  from a task spec, validated against a standard (OpenEnv) before training.
- Both are the same loop with different action spaces and the same verify gate.

### Conclusion / CTA (~2 min)
- Where to keep a human: choosing the question, the reward, and the ship/no-ship
  call. Agents accelerate the search; humans own the judgment.
- **CTA:** Pick one tedious step in your research loop and automate *just that
  one* with a verification gate. Start small.
- OSS landscape: PyTorch, TRL, vLLM, Gymnasium, OpenEnv, plus the open
  AI-Scientist / agentic-tree-search projects.

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
