# /// script
# requires-python = ">=3.10"
# dependencies = [
#    "flyte>=2.0.0",
# ]
# ///
"""Hello-world Flyte 2 example from the talk slides.

Run locally (in-process):

    uv run flyte_hello_world.py --local

Run on the Flyte devbox (after ``flyte start devbox``):

    uv run flyte_hello_world.py

Or via the CLI:

    flyte run flyte_hello_world.py main --data '[0,1,2,3,4,5,6,7,8,9]'
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import flyte

env = flyte.TaskEnvironment(
    name="hello_world",
    image=flyte.Image.from_uv_script(__file__, name="hello-world", registry="localhost:30000"),
    resources=flyte.Resources(cpu=2, memory="1Gi"),
)


@env.task(retries=3, cache="auto")
async def predict(x: int) -> int:
    return 2 * x + 5


@env.task
async def main(data: list[int]) -> float:
    xs = await asyncio.gather(*(predict(x) for x in data))
    return sum(xs) / len(xs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    if args.local:
        mean = asyncio.run(main(data=args.data))
        print(f"Mean: {mean}")
    else:
        flyte.init_from_config()
        run = flyte.run(main, data=list(range(10)))
        print(f"View at: {run.url}")
        run.wait()
        print(f"Mean: {run.outputs()}")
