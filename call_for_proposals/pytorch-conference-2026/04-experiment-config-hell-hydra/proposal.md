# Managing experiment configuration hell with Hydra

- **Topic:** Training (techniques and libraries for training)
- **Submission Type:** Session Presentation (25 minutes)
- **Audience Level:** Intermediate
- **Presented this talk before?** No

---

## Description / Abstract

> Paste into Sessionize. Limit: 1200 characters.

Every PyTorch project starts with a clean `argparse` and ends in configuration
hell: a 200-line flag list, `if args.model == "..."` branches everywhere,
copy-pasted YAML per experiment, and a results table nobody can reproduce
because the exact config is lost. The model code is fine — the *configuration*
is what rots.

This talk is a practical guide to taming that sprawl with Hydra and OmegaConf.
We start from a real messy training script and refactor it: composing config
from modular groups (model / optimizer / data), overriding anything from the
command line, and sweeping hyperparameters with `--multirun` instead of bash
loops.

Then we go where most tutorials stop: making configs *type-safe and validated*.
I'll cover structured configs with dataclasses, the `ConfigStore`, the real
limitations (Union types, no custom validation, no `pathlib.Path`), and how to
close those gaps by validating into Pydantic models. Finally, how a multirun
sweep maps cleanly onto a workflow engine for distributed runs. You'll leave
with a config layout that keeps every experiment reproducible.

---

## Talk Outline (25 minutes)

### Hook (~3 min)
- The wave: PyTorch training code is easy to start and brutal to scale
  *organizationally* — the bottleneck isn't the model, it's the config.
- The pain everyone recognizes: the 200-flag `argparse`, `if`-branches on string
  flags, YAML copy-pasted per run, and the "what config produced this number?"
  question with no answer.
- **[Governing idea]** Configuration is real engineering. Treat it as a typed,
  composable, validated artifact — not an afterthought — and reproducibility,
  sweeps, and collaboration come almost for free.

### Chapter 1 — From argparse hell to composed config (~5 min)
- Start from a genuinely messy training script (live refactor).
- Hydra config groups: `model/`, `optimizer/`, `data/` as swappable modules.
- Composition + command-line overrides: `python train.py model=resnet50
  optimizer=adamw optimizer.lr=3e-4` — no code change.
- Output dir + config snapshot per run: reproducibility by default.

### Chapter 2 — Sweeps without bash loops (~4 min)
- `--multirun` over a grid: `optimizer.lr=1e-3,3e-4,1e-4 model=resnet50,vit_b16`.
- Variable interpolation (`${...}`) to kill redundant values.
- Why this beats hand-rolled `for` loops: every run is captured and named.

### Chapter 3 — Making config type-safe (where tutorials stop) (~6 min)
- Structured configs: describe config with dataclasses for runtime + static type
  checking; register with `ConfigStore`.
- The honest limitations (the expertise slide): `Union` types only partially
  supported, user methods unsupported, no `pathlib.Path`, and **no real
  validation** beyond type-checking.
- Closing the gap: validate the composed `DictConfig` into **Pydantic** models
  (`OmegaConf.to_object` / `to_container` → `MyConfig(**...)`) to get custom
  validators, constraints, and proper unions — fail fast on bad config *before*
  a GPU is allocated.

### Chapter 4 — Scaling a sweep to a cluster (~4 min)
- A multirun grid is just a list of configs to execute — that maps directly onto
  a parallel fan-out.
- A workflow engine (e.g. **Flyte**, as one open option) can run each config as
  an independent task with its own resources, caching identical configs and
  collecting results — framed as infra, not the subject.

### Conclusion / CTA (~3 min)
- The payoff: a config layout where any experiment is reproducible from its
  snapshot, sweeps are one flag, and bad configs fail before they waste compute.
- What this does **not** fix: it won't make a badly-factored *training script*
  good — config hygiene and code hygiene are separate problems.
- **CTA:** Refactor one training script to composed + validated config this week.
- OSS landscape: Hydra, OmegaConf, Pydantic, PyTorch Lightning / `torchrun`
  integrations.

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
