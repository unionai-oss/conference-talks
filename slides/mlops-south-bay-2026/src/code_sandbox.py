# /// script
# dependencies = [
#    "flyte>=2.0.0b49",
# ]
# ///

"""
Code Sandbox — Agent Self-Service Tools (slide example).

Run AI-generated or dynamic code in an isolated container using Flyte's
raw container tasks. See: https://www.union.ai/docs/v2/byoc/user-guide/task-programming/container-tasks/

Pattern:
- ContainerTask runs a command in a container (e.g. uv run script.py)
- Inputs/outputs flow via input_data_dir / output_data_dir (copilot sidecar)
- Agents can "build their own tools" by generating script content and
  executing it safely in this sandbox; optional human review before registration.
"""

import pathlib

import flyte
import flyte.io

# ContainerTask may be in flyte.extras (Union 2.0 BYOC). If not available,
# use a regular @env.task that runs subprocess or a sandboxed runner.
try:
    from flyte.extras import ContainerTask
except ImportError:
    ContainerTask = None

env = flyte.TaskEnvironment(
    name="code-sandbox-demo",
    resources=flyte.Resources(cpu=1, memory="512Mi"),
    image=flyte.Image.from_uv_script(__file__, name="code-sandbox-image", python_version=(3, 13), pre=True),
)


def _make_code_runner():
    """Container task: run a Python script with args, return result from stdout."""
    if ContainerTask is None:
        return None
    return ContainerTask(
        name="python_code_runner",
        image=flyte.Image.from_base("ghcr.io/astral-sh/uv:debian-slim"),
        input_data_dir="/var/inputs",
        output_data_dir="/var/outputs",
        inputs={"script.py": flyte.io.File, "a": int, "b": int},
        outputs={"result": int},
        command=[
            "/bin/sh",
            "-c",
            "uv run /var/inputs/script.py {{.inputs.a}} {{.inputs.b}} > /var/outputs/result",
        ],
    )


code_runner = _make_code_runner()
container_env = flyte.TaskEnvironment.from_task("container_env", code_runner) if code_runner else None
if container_env is not None:
    env = flyte.TaskEnvironment(
        name="code-sandbox-demo",
        resources=flyte.Resources(cpu=1, memory="512Mi"),
        image=flyte.Image.from_uv_script(__file__, name="code-sandbox-image", python_version=(3, 13), pre=True),
        depends_on=[container_env],
    )


@env.task
async def run_generated_code(script_content: str, a: int, b: int) -> int:
    """
    Run agent-generated (or dynamic) code in a container sandbox.
    Saves script to a file, passes to ContainerTask, returns result.
    """
    if code_runner is None:
        # Fallback: run inline (no real sandbox). Install flyte[extras] for ContainerTask.
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(script_content.encode())
            path = f.name
        try:
            out = subprocess.run(
                ["python", path, str(a), str(b)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return int(out.stdout.strip()) if out.stdout.strip() else 0
        finally:
            pathlib.Path(path).unlink(missing_ok=True)

    # Save script to a Flyte File and invoke container task
    script_file = flyte.io.File.new_remote()
    with open(script_file.path, "w") as f:
        f.write(script_content)
    return await code_runner(**{"script.py": script_file, "a": a, "b": b})


# Example generated script: add two args and return
EXAMPLE_SCRIPT = """
import sys
a, b = int(sys.argv[1]), int(sys.argv[2])
print(a + b)
"""


@env.task
async def main(a: int = 10, b: int = 20) -> int:
    """Run example 'generated' script in sandbox."""
    return await run_generated_code(EXAMPLE_SCRIPT, a, b)


if __name__ == "__main__":
    import argparse
    import os
    from flyte.remote import auth_metadata

    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
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
            run = flyte.with_runcontext(mode="remote").run(main, a=10, b=20)
            print(run.url)
