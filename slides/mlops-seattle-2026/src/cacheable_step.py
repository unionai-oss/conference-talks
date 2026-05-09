# /// script
# dependencies = [
#    "flyte>=2.0.0b49",
# ]
# ///

"""
Standalone demo: Make crashes cheap with a cacheable step.

Run this twice with the same inputs: second run reuses cached fetch_data output.
Shows that after a crash, completed work is not redone.
"""

import flyte
import flyte.io

env = flyte.TaskEnvironment(
    name="cacheable_step",
    resources=flyte.Resources(cpu=1, memory="256Mi"),
    image=flyte.Image.from_uv_script(__file__, name="cacheable-step-image", python_version=(3, 13), pre=True),
)


@env.task
async def fetch_data(source: str) -> flyte.io.File:
    """Simulates expensive context retrieval (RAG, API). Cacheable so retries don't redo it."""
    f = flyte.io.File.new_remote()
    with open(f.path, "w") as out:
        out.write(f"context from {source}")
    return f


@env.task
async def main(source: str = "default") -> str:
    data = await fetch_data(source)
    with open(data.path) as inp:
        return inp.read()


if __name__ == "__main__":
    import argparse
    import os

    from flyte.remote import auth_metadata

    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--source", default="default", help="Cache key; same source = cache hit on rerun")
    args = parser.parse_args()

    flyte.init_passthrough(
        project=os.getenv("FLYTE_INTERNAL_EXECUTION_PROJECT"),
        domain=os.getenv("FLYTE_INTERNAL_EXECUTION_DOMAIN"),
    )
    with auth_metadata(("authorization", os.environ["FLYTE_PASSTHROUGH_API_KEY"])):
        if args.build:
            uri = flyte.build(env.image, wait=False)
            print(f"build run url: {uri}")
        else:
            run = flyte.with_runcontext(mode="remote").run(main, source=args.source)
            print(run.url)
