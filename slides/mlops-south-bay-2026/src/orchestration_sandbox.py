# /// script
# dependencies = [
#    "flyte>=2.0.0b49",
#    "flyte[sandboxed]",
# ]
# ///

"""
Orchestration Sandbox — Agent Self-Service Tools (slide example).

Sandboxed tasks run pure Python in a Monty sandbox (Pydantic): side-effect free,
no filesystem/network. They can call regular @env.task workers; each call
pauses the sandbox, runs the worker in its container, and resumes with the result.

Syntax from PR 667 (flyte-sdk sandboxed). Use:
- @env.task for workers (run in containers)
- @env.sandboxed_task for orchestrators (control flow only)
- flyte.sandboxed.code_to_task() for code-string pipelines

Install: pip install 'flyte[sandboxed]'
"""

import flyte

# Optional: only if sandboxed is available
try:
    import flyte.sandboxed
except ImportError:
    flyte.sandboxed = None

env = flyte.TaskEnvironment(
    name="orchestration-sandbox-demo",
    image=flyte.Image.from_uv_script(__file__, name="orchestration-sandbox-image", python_version=(3, 13), pre=True),
    resources=flyte.Resources(cpu=1, memory="256Mi"),
)


# --- Worker tasks (run in their own containers) ---

@env.task
def fetch_score(player_id: int) -> int:
    """Simulate fetching a score from a DB or API."""
    scores = {1: 42, 2: 87, 3: 15, 4: 63, 5: 99}
    return scores.get(player_id, 0)


@env.task
def multiply(x: int, y: int) -> int:
    return x * y


@env.task
def add(x: int, y: int) -> int:
    return x + y


# --- Sandboxed orchestrator: only control flow; worker calls run in containers ---
# When the sandbox hits fetch_score(...), Monty pauses, Flyte runs the worker, then resumes.

if flyte.sandboxed is not None and hasattr(env, "sandboxed_task"):

    @env.sandboxed_task
    def leaderboard(player_ids: list[int]) -> dict[str, int]:
        """Compose tools into a workflow; catch and handle errors in Python."""
        total = 0
        best = 0
        for pid in player_ids:
            score = fetch_score(pid)
            total = add(total, score)
            if score > best:
                best = score
        bonus = multiply(best, 2)
        return {"total": total, "best": best, "bonus": bonus}

    # Code string → task (e.g. LLM-generated orchestration)
    code_pipeline = flyte.sandboxed.code_to_task(
        """
        partial = add(x, y)
        result = multiply(partial, scale)
        """,
        inputs={"x": int, "y": int, "scale": int},
        output=int,
        functions={"add": add, "multiply": multiply},
        name="code-pipeline",
    )
else:
    # Fallback when sandboxed not installed: regular task that does the same logic
    @env.task
    def leaderboard(player_ids: list[int]) -> dict[str, int]:
        total = 0
        best = 0
        for pid in player_ids:
            score = fetch_score(pid)
            total = add(total, score)
            if score > best:
                best = score
        bonus = multiply(best, 2)
        return {"total": total, "best": best, "bonus": bonus}

    code_pipeline = None


@env.task
async def main(player_ids: list[int] | None = None) -> dict[str, int]:
    """Run the sandboxed leaderboard (or fallback)."""
    ids = player_ids or [1, 2, 3]
    return await leaderboard(ids)


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
            run = flyte.with_runcontext(mode="remote").run(main, player_ids=[1, 2, 3])
            print(run.url)
