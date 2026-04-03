# /// script
# dependencies = [
#    "flyte>=2.0.0b49",
# ]
# ///

"""
Human-in-the-Loop (HITL) — slide example.

Workflow pauses and waits for human input before continuing. Uses the
event-based API from the flyteplugins-hitl plugin (PR 657).

SDK usage:
- task_env = TaskEnvironment(..., depends_on=[hitl.env])
- event = await hitl.new_event.aio("event_name", data_type=int, scope="run", prompt="...")
- value = await event.wait.aio()

Requires: pip install flyteplugins-hitl  (or install from flyte-sdk repo plugins/hitl)
"""

import flyte

try:
    import flyteplugins.hitl as hitl
except ImportError:
    hitl = None

if hitl is not None:
    task_env = flyte.TaskEnvironment(
        name="hitl-demo",
        resources=flyte.Resources(cpu=1, memory="512Mi"),
        image=flyte.Image.from_uv_script(__file__, name="hitl-demo-image", python_version=(3, 13), pre=True),
        depends_on=[hitl.env],
    )
else:
    task_env = flyte.TaskEnvironment(
        name="hitl-demo",
        resources=flyte.Resources(cpu=1, memory="512Mi"),
        image=flyte.Image.from_uv_script(__file__, name="hitl-demo-image", python_version=(3, 13), pre=True),
    )


@task_env.task
async def task1() -> int:
    """Automated step: compute a value."""
    return 42


@task_env.task
async def task2(x: int, y: int) -> int:
    """Combine automated (x) and human (y) input."""
    return x + y


@task_env.task
async def main() -> int:
    """
    Orchestrate: run task1, wait for human input (HITL gate), then task2.
    When the plugin is not installed, we skip the event and use a default y=0.
    """
    x = await task1()

    if hitl is not None:
        # Human-in-the-loop: create event, serve app, wait for input
        event = await hitl.new_event.aio(
            "integer_input_event",
            data_type=int,
            scope="run",
            prompt="What should I add to x?",
        )
        y = await event.wait.aio()
    else:
        y = 0  # no plugin: no human gate

    return await task2(x, y)


if __name__ == "__main__":
    import argparse
    import os
    from flyte.remote import auth_metadata

    parser = argparse.ArgumentParser(description="HITL Example")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()

    flyte.init_passthrough(
        project=os.getenv("FLYTE_INTERNAL_EXECUTION_PROJECT"),
        domain=os.getenv("FLYTE_INTERNAL_EXECUTION_DOMAIN"),
    )
    with auth_metadata(("authorization", os.environ["FLYTE_PASSTHROUGH_API_KEY"])):
        if args.build:
            uri = flyte.build(task_env.image, wait=False)
            print(f"build run url: {uri}")
        else:
            run = flyte.with_runcontext(mode="remote").run(main)
            print(run.url)
