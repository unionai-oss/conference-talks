# Eliminate the training-serving skew with Feast and Flyte

- **Topic:** Inference (techniques and libraries for inference)
- **Submission Type:** Session Presentation (25 minutes)
- **Audience Level:** Intermediate
- **Presented this talk before?** No

---

## Description / Abstract

> Paste into Sessionize. Limit: 1200 characters.

Many production PyTorch models fail for a boring reason: the features they see in
serving are not the features they saw in training. A notebook joins historical
data one way, the online service recomputes it another way, and performance
quietly degrades. This is training-serving skew.

Feast, now part of the PyTorch ecosystem, attacks the skew at the feature layer:
define features once, retrieve point-in-time correct historical values for
training, and serve the latest values from a low-latency online store for
inference. Flyte complements that by making the feature engineering, materialize,
train, validate, and deploy steps reproducible workflows rather than a pile of
cron jobs and notebooks.

In this talk, we'll build a small recommendation-style PyTorch model end to end.
We'll define Feast feature views, create a training dataset with
`get_historical_features`, materialize online features, fetch them during
inference with `get_online_features`, and wire the whole path into a Flyte
workflow. You'll leave with a pattern for making PyTorch models see the same
features in training and production.

---

## Talk Outline (25 minutes)

### Hook (~3 min)
- The model looks good offline, then degrades in production. The architecture is
  fine; the feature path is not.
- Training-serving skew: same conceptual feature, two different implementations.
- **[Governing idea]** The fix is not another model. It is one feature contract
  shared by training and inference, plus reproducible workflows around it.

### Chapter 1 — What skew looks like in PyTorch (~4 min)
- Notebook join for training vs. API/database lookup for serving.
- Time leakage: using feature values that would not have existed at prediction
  time.
- Feature drift vs. feature skew: related, but different failure modes.

### Chapter 2 — Feast as the feature contract (~7 min)
- Entities, feature views, offline store, online store, registry.
- `get_historical_features`: point-in-time correct training data.
- `materialize`: push computed feature values to the online store.
- `get_online_features`: low-latency inference features converted to
  `torch.Tensor`.

### Chapter 3 — Flyte as the reproducible workflow layer (~5 min)
- Feature engineering task → Feast apply/materialize → training task →
  validation task → deployment handoff.
- Typed inputs/outputs, caching, resource requests, secrets, and scheduled runs.
- Keep the framing clear: Feast owns feature consistency; Flyte owns repeatable
  execution and lineage.

### Chapter 4 — Production checks (~4 min)
- Offline/online parity tests on a sample of entities.
- Point-in-time leakage tests.
- Feature freshness and missing-value checks.
- Shadow inference before full rollout.

### Conclusion / CTA (~2 min)
- **CTA:** Pick one production model and replace one duplicated feature path with
  a Feast definition shared by training and serving.
- OSS landscape: PyTorch, Feast, Flyte, Redis/PostgreSQL/DynamoDB online stores,
  BigQuery/Snowflake/Parquet offline stores.

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
