# /// script
# dependencies = [
#    "flyte>=2.0.0b49",
# ]
# ///

"""
Chapter 3 demo: Agent that crashes, resumes from cache, provisions more memory, completes.

Run 1: main(simulate_oom=True)  -> fetch_data runs, process_step fails (simulated OOM).
Run 2: main(simulate_oom=False) -> fetch_data from cache, process_step succeeds.

In production you'd retry with a task that has higher Resources (e.g. 512Mi vs 128Mi).
"""

import flyte
import flyte.io

env = flyte.TaskEnvironment(
    name="agent_demo",
    resources=flyte.Resources(cpu=1, memory="512Mi"),
    image=flyte.Image.from_uv_script(__file__, name="agent-demo-image", python_version=(3, 13), pre=True),
)


@env.task
async def fetch_data() -> flyte.io.File:
    """Cacheable step: retrieve context. On retry after crash, this is reused."""
    f = flyte.io.File.new_remote()
    with open(f.path, "w") as out:
        out.write("cached context payload")
    return f


@env.task
async def process_step(data: flyte.io.File, simulate_oom: bool = False) -> str:
    """Heavy step: can 'OOM' (simulated) or succeed. Simulates 'provision more memory' via param."""
    if simulate_oom:
        raise MemoryError("Simulated OOM: container needs more memory")
    with open(data.path) as inp:
        return inp.read() + " -> processed"


@env.task
async def main(simulate_oom: bool = False) -> str:
    """Orchestration: fetch (cacheable) then process. Set simulate_oom=False to 'recover' with more resources."""
    data = await fetch_data()
    return await process_step(data, simulate_oom=simulate_oom)


if __name__ == "__main__":
    import argparse
    import os

    from flyte.remote import auth_metadata

    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--simulate-oom", action="store_true", help="First run: crash at process_step")
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
            run = flyte.with_runcontext(mode="remote").run(main, simulate_oom=args.simulate_oom)
            print(run.url)
