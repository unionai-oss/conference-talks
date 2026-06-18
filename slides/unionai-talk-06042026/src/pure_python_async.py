# /// script
# requires-python = ">=3.10"
# ///
"""Basic pure-Python asyncio example from the talk.

Runs entirely in your local Python process — no Flyte, no containers.
Compare with ``flyte_hello_world.py``, which adds Flyte task decorators
and can run the same logic on the devbox.
"""

import asyncio


async def predict(x: int) -> int:
    await asyncio.sleep(0.1)
    return 2 * x + 5


async def main(data: list[int]) -> float:
    xs = await asyncio.gather(*(predict(x) for x in data))
    return sum(xs) / len(xs)


if __name__ == "__main__":
    mean = asyncio.run(main(data=list(range(10))))
    print(f"Mean: {mean}")
