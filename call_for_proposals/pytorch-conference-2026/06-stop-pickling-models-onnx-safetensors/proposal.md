# Stop pickling your models! Making models production-ready with ONNX and safetensors

- **Topic:** Inference (techniques and libraries for inference)
- **Submission Type:** Session Presentation (25 minutes)
- **Audience Level:** Intermediate
- **Presented this talk before?** No

---

## Description / Abstract

> Paste into Sessionize. Limit: 1200 characters.

`torch.save(model)` is convenient until it crosses a trust boundary. Pickle can
execute arbitrary code when loaded, ties your artifact to Python object
definitions, and makes production inference harder to reason about. If your
model artifact came from the internet, a partner, or an old training job, "just
load the pickle" is not a production plan.

This talk gives PyTorch users a practical artifact strategy for inference.
We'll separate the two things people often bundle together: model computation
and model weights. For portable computation, we'll use the modern
`torch.export`-based ONNX exporter (`torch.onnx.export(..., dynamo=True)`) and
verify the exported graph with ONNX Runtime. For tensor-only weights, we'll use
`safetensors`, a simple format designed to avoid arbitrary code execution during
deserialization.

Using a small PyTorch model as the running example, we'll build a production
handoff checklist: export with dynamic shapes, store large weights with external
data when needed, compare outputs against eager PyTorch, package metadata, and
decide when ONNX, safetensors, or native PyTorch serving is the right choice.
You'll leave with a safer model release pipeline.

---

## Talk Outline (25 minutes)

### Hook (~3 min)
- The scary fact: Python pickle is not a safe interchange format; unpickling
  untrusted files can execute code.
- The practical pain: even trusted pickles can break when class definitions,
  Python versions, or dependencies move.
- **[Governing idea]** A production model artifact should make trust boundaries,
  runtime requirements, and numerical equivalence explicit.

### Chapter 1 — What are we actually saving? (~4 min)
- Full Python object vs. `state_dict` vs. tensor weights vs. exported graph.
- Why "the model" is two things: computation + parameters.
- What PyTorch eager execution gives you, and what production runtimes need.

### Chapter 2 — ONNX for portable inference graphs (~6 min)
- ONNX as an open graph format for inference across runtimes/languages.
- The modern PyTorch path: `torch.onnx.export(..., dynamo=True)`, backed by
  `torch.export`.
- Dynamic shapes, external data for large weights, and exporter reports.
- Verification: compare ONNX Runtime outputs against eager PyTorch on a test
  battery before shipping.

### Chapter 3 — safetensors for tensor-only weights (~5 min)
- What `safetensors` does and does not store: tensors + metadata, not arbitrary
  Python objects.
- Why tensor-only deserialization is safer and faster to inspect.
- Where safetensors fits: Hugging Face models, PyTorch `state_dict` handoff,
  sharded checkpoints, and model cards.

### Chapter 4 — A production artifact checklist (~5 min)
- Save the exact input/output schema, dtype policy, dynamic shape constraints,
  preprocessing assumptions, model version, and dependency versions.
- Include equivalence tests and known unsupported ops.
- Decision matrix: native PyTorch serving, ONNX Runtime, TensorRT/OpenVINO
  downstream, safetensors-only weight exchange.

### Conclusion / CTA (~2 min)
- **CTA:** Stop treating pickle as your release format. Export graphs when you
  need portability, use tensor-only formats for weights, and verify every
  artifact before it enters serving.
- OSS landscape: PyTorch ONNX exporter, ONNX Runtime, safetensors, ModelScan,
  Hugging Face Hub.

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
