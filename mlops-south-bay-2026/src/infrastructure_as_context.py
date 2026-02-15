# /// script
# dependencies = [
#    "flyte>=2.0.0b49",
# ]
# ///

"""
Infrastructure as Context — slide example.

Shows how tasks can run with different resource profiles. The agent (or workflow)
can "see" that a step needs more memory and dispatch to a higher-resource
environment instead of failing opaquely.

Pattern:
- env_low: 128Mi — for cheap / exploratory steps
- env_high: 512Mi — for steps that need more memory (or retry after OOM)

In production, you'd feed resource hints (e.g. from observability) into context
so the agent can choose the right env or request a bigger container.
"""

import flyte
import flyte.io

# Low memory: cheap runs, may OOM on heavy steps
env_low = flyte.TaskEnvironment(
    name="infra-context-low",
    resources=flyte.Resources(cpu=1, memory="128Mi"),
    image=flyte.Image.from_uv_script(__file__, name="infra-context-image", python_version=(3, 13), pre=True),
)

# High memory: for steps that need more (retry path or explicit "provision more")
env_high = flyte.TaskEnvironment(
    name="infra-context-high",
    resources=flyte.Resources(cpu=1, memory="512Mi"),
    image=flyte.Image.from_uv_script(__file__, name="infra-context-image", python_version=(3, 13), pre=True),
)


@env_low.task
async def process_low(payload: str) -> str:
    """Runs in 128Mi. May OOM if payload is 'heavy' (simulated)."""
    if payload == "heavy":
        raise MemoryError("Simulated OOM: container has 128Mi, step needs more")
    return f"processed(low): {payload}"


@env_high.task
async def process_high(payload: str) -> str:
    """Runs in 512Mi. Same logic, enough headroom for 'heavy'."""
    return f"processed(high): {payload}"


# Single entry point: run with low or high resources.
# In production, observability tells the agent "container has 16Gi, step needs 32Gi"
# and the agent (or workflow) chooses the high-memory env for the next step.
main_env = flyte.TaskEnvironment(
    name="infra-context-demo",
    resources=flyte.Resources(cpu=1, memory="256Mi"),
    image=flyte.Image.from_uv_script(__file__, name="infra-context-image", python_version=(3, 13), pre=True),
    depends_on=[env_low, env_high],
)


@main_env.task
async def main(payload: str = "light", use_high: bool = False) -> str:
    """use_high=True = agent requested more resources (infrastructure as context)."""
    if use_high:
        return await process_high(payload)
    try:
        return await process_low(payload)
    except MemoryError:
        return await process_high(payload)


if __name__ == "__main__":
    import argparse
    import os
    from flyte.remote import auth_metadata

    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--payload", default="light", help="'light' or 'heavy' (heavy triggers simulated OOM on low)")
    parser.add_argument("--use-high", action="store_true", help="Skip low, run in high-memory env")
    args = parser.parse_args()

    flyte.init_passthrough(
        project=os.getenv("FLYTE_INTERNAL_EXECUTION_PROJECT"),
        domain=os.getenv("FLYTE_INTERNAL_EXECUTION_DOMAIN"),
    )
    with auth_metadata(("authorization", os.environ["FLYTE_PASSTHROUGH_API_KEY"])):
        if args.build:
            uri = flyte.build(main_env.image, wait=False)
            print(f"build run url: {uri}")
        else:
            run = flyte.with_runcontext(mode="remote").run(main, payload=args.payload, use_high=args.use_high)
            print(run.url)
