# AutoKernel optimization with agents and vLLM

- **Topic:** Kernel Engineering (compilers, optimization, and domain-specific languages)
- **Submission Type:** Session Presentation (25 minutes)
- **Audience Level:** Advanced
- **Presented this talk before?** No

---

## Description / Abstract

> Paste into Sessionize. Limit: 1200 characters.

LLM inference kernels ship with tile shapes and configs tuned for some generic
case — rarely the exact shapes and GPU your model actually runs on. Hand-tuning
per model is the optimization nobody has time for, so it usually doesn't happen.

This talk shows how to build a backend-agnostic agent that does it for you.
Today it tunes raw Triton kernels and generates flash-attention source; the same
loop applies to Helion — PyTorch's kernel DSL that compiles `@helion.kernel`
down to Triton and exposes its own search space (`helion.Config`: block sizes,
loop orders, indexing, PID mapping). The agent proposes configs, compiles,
numerically verifies against a PyTorch reference, and microbenchmarks each
candidate with CUDA events.

The load-bearing design is a closed knob schema per backend: a hallucinated
config fails validation before it compiles, so an LLM proposer is an
accelerant, never a liability. I'll show measured speedups on real models
(L4-class GPUs), how vLLM serves as an in-process evaluator for engine-level
tuning, and how to fan candidates out across GPUs safely. You'll leave knowing
how to wrap a verify-and-measure loop around Triton, Helion, or any kernel DSL
you adopt.

---

## Talk Outline (25 minutes)

### Hook (~3 min)
- The wave: `torch.compile`, Triton, Helion, and vLLM have made fast LLM
  inference accessible — but the last mile, *per-shape kernel tuning*, is still
  manual and usually skipped.
- The bottleneck: autotuners exist (Triton's, Helion's built-in differential
  evolution over ~1500 configs), but nobody runs the full sweep for *their* model
  on *their* GPU. The decode-time GEMMs and attention kernels you actually run
  are configured for someone else's shapes.
- **[Governing idea]** You can wrap a *verify-and-measure loop* around kernel
  search so that an agent — rule-based or LLM-driven — tunes (and even writes)
  kernels for your exact shapes, and it is safe to do so because every candidate
  must *compile, numerically match a PyTorch reference, and beat the baseline on
  the clock* before it can win — regardless of whether the backend is raw Triton
  or a higher-level DSL like Helion that lowers to Triton.

### Chapter 1 — The search space, and why it's dangerous (~4 min)
- What we tune today: raw Triton matmul tile config (`block_m/n/k`, `group_m`,
  `num_warps`, `num_stages`) and flash-attention tiling (query/KV tiles).
- **Not Triton-only:** the same loop generalizes to Helion — write a kernel in
  PyTorch-with-tiles (`@helion.kernel`), let Helion compile it to exactly one
  Triton kernel, and have the agent search `helion.Config` knobs (block sizes,
  loop orders, L2 groupings, indexing strategy, PID mapping, warp specialization)
  instead of hand-authoring Triton tile code.
- Why letting an LLM emit kernel flags is risky: hallucinated knobs, silently
  wrong numerics, configs that OOM or wedge the GPU — at *any* layer of the stack.

### Chapter 2 — The closed-schema anti-hallucination gate (~4 min)
- A frozen Pydantic schema **per backend** where every knob is validated against
  an allowed set — `KernelConfig` for raw Triton, `HelionConfig` for Helion's
  `block_sizes` / `loop_orders` / `indexing` / `pid_type` / etc.
- The LLM emits configs as structured tool calls; out-of-schema values fail
  validation *before compilation*. The agent searches a real, bounded space and
  cannot invent flags — whether the compile target is Triton source or a Helion
  kernel that lowers to Triton.
- Two proposer layers: a deterministic rule prior (no API key) and an optional
  LLM proposer — the LLM is an accelerant, never required.

### Chapter 3 — The verify-and-measure contract (~5 min)
- Compile gate → verify gate (vs. `torch.matmul` / masked-softmax reference) →
  microbench with CUDA events. Early-exit at each gate.
- A wrong-but-fast kernel is *disqualified*, never penalized.
- Isolation: each candidate runs in a fresh OS subprocess for CUDA-state
  isolation, so a bad config can't poison its neighbours.
- Measured vs. modeled: real numbers come only from the GPU compile +
  CUDA-event path; an analytical roofline model stands in offline for CI.

### Chapter 4 — Going deeper: writing kernels, and tuning the engine (~5 min)
- Phase 2: generating flash-attention *source* over a closed transformation
  taxonomy (windowed KV-loop skip, boundary-split masking) — 2.3–3.9× over the
  un-transformed kernel on Gemma-3-1b (L4/L40S), same verify-and-measure contract.
- The full-model equivalence gate: does swapping the kernel change what the model
  *says*? Token-level greedy-decoding drift + an LLM judge.
- vLLM as an in-process evaluator: the same propose→evaluate→rank loop applied to
  engine-level knobs (quantization, KV-cache dtype, CUDA-graph sizes, speculative
  decoding) — composed fp8 + speculative for ~3.97× on Qwen-7B/L4.
- Parallel fan-out: one candidate per single-GPU worker with a concurrency cap.
  (`flyte.map` is one open way to do this; the loop is orchestrator-agnostic.)

### Conclusion / CTA (~4 min)
- The transferable pattern: *closed schema + verify-and-measure + isolation* lets
  you put an agent in the kernel-optimization loop without trusting it blindly —
  at the Triton layer, the Helion layer, or any DSL that compiles to a
  measurable backend.
- What this does **not** do: it doesn't replace attention math, doesn't do
  multi-GPU kernels, and modeled numbers are never performance claims.
- **CTA:** Stop shipping generic kernel configs. Wrap a verify-and-measure loop
  around the kernels you care about — raw Triton, Helion, or both — and let the
  agent run the tuning you never had time to run.
- Related OSS landscape: Triton, [Helion](https://github.com/pytorch/helion),
  `torch.compile`, vLLM, CUTLASS.

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
