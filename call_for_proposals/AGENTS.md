# AGENTS.md — Writing Conference Call-for-Proposal (CFP) Submissions

This file is the playbook for drafting conference talk proposals in this
directory. It is organized in two parts:

1. **Shared conventions** — house style, speaker profile, file layout, and
   workflow that apply to *every* conference.
2. **Per-conference guidelines** — one section per conference (e.g.
   `## PyTorch Conference`) with that event's submission target, required
   fields, hard limits, and the rules reviewers actually apply.

To add a new conference, append a new `## <Conference Name>` section under
"Per-conference guidelines" — leave the shared conventions untouched.

Read this before writing or editing any proposal.

---

# Shared conventions (apply to all conferences)

## Speaker profile (reuse unless told otherwise)

- **Name:** Niels Bantilan
- **Tagline / Title:** Chief Machine Learning Engineer, Union.ai
- **Company:** Union.ai
- **Bio (keep ≤500 chars; trim per conference limit):** Niels is the Chief
  Machine Learning Engineer at Union, a core maintainer of Flyte, an open source
  workflow orchestration tool, and creator of Pandera, a data validation and
  testing tool for dataframes. His mission is to help data science and machine
  learning practitioners be more productive. His research interests include
  reinforcement learning, NLP, ML in creative applications, and fairness,
  accountability, and transparency in automated systems.

> Note: the bio mentions Flyte/Union because it is the speaker's affiliation —
> that is fine. The *talk content* must still follow each conference's
> guidelines (e.g. ecosystem-first, no vendor pitch).

## House style (learned from an accepted PyTorch Conference 2025 submission)

The accepted 2025 talk ("Designing and building custom RL environments for
fine-tuning LLMs…") models the style we want. It generalizes to any technical
conference:

- **A single governing idea.** State the one-sentence thesis explicitly
  ("[Governing idea] the crux of my talk is that…"). Everything serves it.
- **Hook that names a current wave + a concrete bottleneck.** Tie to something
  the audience already cares about (a recent paper, a hot technique), then name
  the *specific* gap the talk fills.
- **A concrete case study as the spine.** The 2025 talk used a "Wikipedia Maze."
  Pick one running, demoable example and return to it.
- **Honest implementation challenges.** A dedicated section listing the real
  problems hit and the *specific* solution for each (OOM → chunking + LoRA;
  over-flexible action space → restrict to one action type). This is the part
  that proves expertise — never cut it.
- **Show results.** Reward/latency/speedup plots, before/after numbers, what
  was measured vs. modeled. Be explicit about what is measured vs. simulated.
- **Generalize at the end.** Show the pattern applies beyond the case study, then
  a crisp CTA. The 2025 talk ended on "Build environments, not datasets!"
- **Cite the open-source landscape.** Name the related OSS projects
  (Gymnasium, TRL, vLLM, verl, etc.) so reviewers see you know the field.
- **Tone:** plain, technical, first-person, opinionated but honest about scope
  and limitations. Include a "what this does *not* do" framing where relevant.

## File layout & workflow

```
call_for_proposals/
  AGENTS.md                         <- this file
  <conference-slug>/                <- e.g. pytorch-conference-2026/
    <NN>-<slug>/
      proposal.md                   <- the submission (fields in the conference's
                                       required-fields order)
      supporting-resources.md       <- mermaid diagrams + code snippets that
                                       ground the proposal (NOT submitted; used
                                       to justify technical depth while drafting)
```

**Workflow for each title:**
1. Research the open-source building blocks (project docs, ecosystem landscape,
   READMEs/blogs). Ground every claim.
2. Decide the single governing idea and the running case study.
3. Draft `proposal.md` with all of the target conference's required fields,
   respecting that conference's limits and guidelines.
4. Write `supporting-resources.md`: a mermaid architecture diagram + 1–3 code
   snippets that prove the talk is real. These are scratch grounding, not part
   of the submission.
5. Self-check against the conference's guidelines and checklist before done.

---

# Per-conference guidelines

## PyTorch Conference

The playbook for PyTorch Conference submissions: what a *good* submission looks
like, the hard constraints reviewers apply, and the open-source-first framing
that gets talks accepted.

### Submission target

**Event:** PyTorch Conference North America 2026 — San Jose, Oct 20–21.
**System:** Sessionize (Linux Foundation CFP tooling).
**Session CFP closes:** Sunday, June 7, 11:59 PM PDT.

Each proposal maps to one Sessionize submission. We draft in Markdown so we can
iterate, then copy the fields into Sessionize.

#### Submission types
- **Session Presentation** — 25 min, max 3 speakers (the default for these).
- **Lightning Talk** — 10 min, max 2 speakers.
- **Birds of a Feather (BoF)** — 25 min, discussion-driven.

#### 2026 topic tracks (pick exactly one)
- Applications — novel models, business use cases, ecosystem showcases
- Training — techniques and libraries for training
- Inference — techniques and libraries for inference
- Core PyTorch — changes to the framework itself
- Introduction — foundational concepts, beginner-friendly workflows
- Kernel Engineering — compilers, optimization, domain-specific languages
- Responsible AI — ethics, governance, security, sandboxing, privacy

#### Audience level
Beginner / Intermediate / Advanced / Any. Be honest — reviewers calibrate the
outline against the level you pick.

### Required fields per proposal (and hard limits)

Every `proposal.md` MUST contain these fields, in this order:

| Field | Constraint |
|---|---|
| **Session Title** | Short, specific, no vendor pitch. |
| **Description / Abstract** | **≤ 1200 characters** (Sessionize counts characters, not words). This is what reviewers and attendees read first. |
| **Talk Outline** | Hook → Main Chapters → Conclusion/CTA, with a rough time budget for a 25-min slot. Reviewers use this to judge depth and feasibility. |
| **Topic** | Exactly one track from the topic tracks above. |
| **Submission Type** | Session / Lightning / BoF. |
| **Audience Level** | Beginner / Intermediate / Advanced / Any. |
| **Presented this talk before?** | Yes/No. |
| **Speaker Bio** | **≤ 500 characters.** |

Always print the live character count for the Description and Bio so we know we
are inside the limit before submitting.

### Non-negotiable guidelines (these get talks rejected)

These are taken directly from the LF/PyTorch CFP page and from the organizer
note. Violating them is the most common reason a technically strong talk is cut.

1. **PyTorch / PyTorch-ecosystem first.** The talk must be valuable to a PyTorch
   practitioner using only open tools. Lead with the PyTorch-stack problem and
   the open-source building blocks (PyTorch, `torch.compile`, Triton, vLLM, TRL,
   Hydra, OmegaConf, OpenEnv, Gymnasium, Helion, Safetensors, etc.).
2. **No sales or marketing pitch.** "Talks that are sales/marketing pitches are
   almost always rejected." Do not center a single company's commercial product.
3. **Company-specific tools are context, not the subject.** Per the user's
   directive: any orchestration/infra layer (e.g. **Flyte/Union**) may appear in
   the description or outline **only if it is genuinely needed to ground the
   talk**, and it must be framed as one open option among others — never the
   headline, never the payoff. The transferable PyTorch lesson is the payoff.
4. **No closed-source / unlicensed tech as the subject.** Prefer OSS. (Flyte is
   open source; reference it as such and keep it in a supporting role.)
5. **Reviewers must see real expertise.** "Submissions that rely on AI-generated
   or templated content often lack the specificity needed to evaluate technical
   depth." So: concrete numbers, named failure modes, real constraints,
   hard-won lessons. No generic filler.
6. **Quality over quantity.** Each proposal should stand on its own as a strong,
   specific, engaging session.

### Pre-submission checklist

- [ ] Description ≤ 1200 chars (count printed).
- [ ] Bio ≤ 500 chars (count printed).
- [ ] Exactly one topic track selected, and it fits the title's bracket label.
- [ ] PyTorch / OSS ecosystem is the subject; any vendor tool (Flyte/Union) is
      supporting context only, framed as one open option.
- [ ] No sales/marketing language; no "our product solves X."
- [ ] Outline fits the time slot and shows real depth (named challenges,
      concrete solutions, measured vs. modeled results).
- [ ] Specific enough that a reviewer can judge subject-matter expertise.
- [ ] A concrete, demoable case study runs through the talk.
- [ ] Clear governing idea + CTA.
