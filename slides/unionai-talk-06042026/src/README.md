# Flyte 2 devbox examples

Runnable examples from the **Container-enabled Asyncio is All You Need** talk. Each script is a [uv script](https://docs.astral.sh/uv/guides/scripts/) you can run with `uv run`.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/) (running)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Flyte CLI: `uv pip install flyte` or `uv sync` from this directory

## Start the devbox

```bash
flyte start devbox
```

The Flyte UI is at [http://localhost:30080](http://localhost:30080).

Config for the devbox is already checked in at [`.flyte/config.yaml`](./.flyte/config.yaml). To recreate it:

```bash
flyte create config \
    --endpoint localhost:30080 \
    --project flytesnacks \
    --domain development \
    --builder local \
    --insecure \
    --output .flyte/config.yaml
```

See the [Run on the devbox](https://www.union.ai/docs/v2/flyte/user-guide/run-modes/running-devbox/) docs for details.

When you're done:

```bash
flyte stop devbox
```

## Examples

| Script | Purpose |
|--------|---------|
| [`pure_python_async.py`](./pure_python_async.py) | Pure `asyncio` — no Flyte, runs in your Python process |
| [`flyte_hello_world.py`](./flyte_hello_world.py) | Same logic as the slides, with `@env.task` and devbox execution |
| [`anthropic_pbj_agent.py`](./anthropic_pbj_agent.py) | Claude agent with Flyte tasks as tools ([upstream example](https://github.com/flyteorg/flyte-sdk/blob/main/examples/genai/anthropic_pbj_agent.py)) |

### 1. Pure Python async

```bash
uv run pure_python_async.py
```

### 2. Hello world on the devbox

Local (in-process, no containers):

```bash
uv run flyte_hello_world.py --local
```

On the devbox:

```bash
uv run flyte_hello_world.py
```

Or with the Flyte CLI:

```bash
flyte run flyte_hello_world.py main --data '[0,1,2,3,4,5,6,7,8,9]'
```

### 3. Peanut butter & jelly agent

Install the Anthropic plugin, then store your API key in the devbox secret store:

```bash
uv sync --extra anthropic
flyte create secret anthropic_api_key --value "$ANTHROPIC_API_KEY"
uv run anthropic_pbj_agent.py
```

The agent runs three sandwich-making goals in parallel. Open the printed run URL in the devbox UI to inspect tool calls and task outputs.
