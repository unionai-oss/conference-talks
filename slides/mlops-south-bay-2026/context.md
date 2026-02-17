# Proposal:

**Title:** The orchestration stack for observable, debuggable, and durable agents 

**Description:** With popular general purpose tools like Claude Code and OpenClaw, it’s easy to forget that there’s still a lot of work to do to incorporate agents into products that have strict security requirements and/or proprietary context to work really well. At the end of the day, AI engineers still need to build and maintain the artifacts that power agents, be it code, markdown files of skills and context, MCP servers, or vector databases.

On top of that, agents are uniquely able to recover from failures that occur at the semantic layer of the application, but it doesn’t come for free. To get durable, self-healing agents, we still need a cohesive toolchain to effectively observe, debug, version control, and recover from failures at the networking and logical layers.

In this talk, we’ll decompose the agent orchestration stack from beginning to end drawing from lessons learned at [Union.ai](http://Union.ai) building our own internal agents and working with customers who are shipping agents on our platform.

# Presentation

**Thesis:** Building a production agent that just does it job well with minimal intervention requires many components, and we’ve discovered five key core design elements that helps us and our customers build simple, maintainable, and secure agents:

1. Pick a general purpose programming language (Python or TS/JS) and use it! Minimize dependencies on DSLs to minimize surprise.
    1. This makes loops, fan-outs, parallelization, conditionals, try/except trivial
2. Make failures cheap with global caching, run-level replay logs, and memory persistence
3. Give it infrastructure-level context and access:
    1. Recover from OOMErrors, network errors, tool execution errors
    2. Need more compute or memory? Let the agent help itself to more
4. Let it build its own tools and orchestrate its own tool calls, securely
5. Expose hooks for observability, debugging, and interaction so you can use any framework (or none) (`@flyte.trace`, `@env.task`)

## Governing Idea

- By understanding how observability, debuggability, and durability apply at each layer of the agent orchestration stack
- You can more effectively diagnose and fix issues when building production agents; and set things up so that they can help themselves
- So you can ship reliable, self-healing agents faster with less maintenance overhead

## Outline: The Orchestration Stack for Observable, Debuggable, and Durable Agents

**20 minute talk**

### Intro

**Hook (2 minutes):**
Remember the last time you deployed an agent that worked perfectly in development, then mysteriously failed in production at 2 AM? Maybe it ran out of memory halfway through a task. Maybe a network hiccup killed the entire workflow. Or maybe it just... stopped, and you had no idea why because there were no logs, no traces, just silence. This is something many of you may have experienced building agent prototypes. The problem isn't that agents fail—it's that when they fail, they fail *opaquely*, and recovering feels like archaeology. You probably spent weeks optimizing your prompts and tweaking your evaluation suite, but none of that matters if your agent can't survive a network timeout. Today, I want to show you how to build agents that don't just work — I want to show how you can help agents help themselves [https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm0xbXh1NmE0eWtyZzBlNWlhbm1iaWo4cG03YWNrbTQ2djB2YzFlaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/uRb2p09vY8lEs/giphy.gif]

### Main Chapters

**Chapter 1: The Five Layers Where Agents Break—and Where Your Evals Miss (6 minutes)**

- Walk through the full orchestration stack: code execution → tool calls → network → infrastructure → semantic context → memory
- Real examples of failure modes at each layer (OOM errors, API throttling, logical bugs, hallucinated tool calls, user code bugs)
- **The evaluation gap**: Your evals test semantic correctness (does it answer right?) but miss infrastructure failures (does it survive production?)
- The key insight: agents can recover from semantic failures through prompt optimization, context engineering, and agentic control flow patterns — but only if the infrastructure doesn't kill them first
- **Context engineering as a layer**: The quality of context you provide (via RAG, MCP servers, system prompts, skills) determines semantic robustness, but it's worthless if crashes wipe the agent's state

**Chapter 2: Six Design Principles for Self-Healing Agents (8 minutes)**

- **Plain Python/TS/JS**: Why DSLs add fragility; how standard control flow makes debugging trivial
    - Provide functional hooks to trace and checkpoint intermediary state, then get out of the AI engineer (and the agent’s way).
    - Fanning out embarrassingly parallel sub-agents or tool calls becomes trivial
    - Complex conditional login becomes trivial
    - Catching exceptions becomes trivial
- **Make crashes cheap**: Global cache + run-level replay log + memory persistence = instant recovery without data loss
    - *Prompt optimization benefit*: Failed runs become training data—analyze where prompts led to errors, iterate, and redeploy without losing workflow state (✨ context graph ✨)
    - *Context engineering benefit*: Persist retrieved context across retries so agents don't lose semantic grounding mid-task
    - The run-level replay log provides full reproducibility and state rehydration when things go wrong
- **Observability hooks**: `@flyte.trace`, `@env.task`—framework-agnostic debugging that works with any stack
    - *Continuous evaluation*: Trace every production run, pipe it into your eval framework, catch regressions before customers do
    - *Prompt and context debugging*: See exactly which prompt variant led to which behavior at which step
- **Infrastructure-level context**: Let agents see and fix their own OOM/network errors; let them request more resources
    - Infrastructure-as-context: Give agents system-level observability in their context — “this tool call is loading 32Gi of data into memory but the container running the it only have 16Gi”. This allows the agent to re-write the tool to be more memory efficient or configure the tool container to have more memory.
    - Agent that writes ML code can dynamically adjust tool container resource requests as it iterates on models: start with small dataset and model size (low resource request) and gradual increase to user’s desired scale.
- **Agent self-service tools**: Secure tool building and orchestration (how to let agents extend themselves safely)
    - *Dynamic context building*: Let agents fetch exactly the context they need via MCP or custom tools, rather than front-loading everything
    - Code sandbox allows agents to safely build their own tools (extra security: put a human review gate before tool registration)
    - Orchestration sandbox allows agent to compose tools together into workflows.
    - Agent code can catch semantic, logical, network, or system-level errors and decide what to do next.
    - Meta-agent: an agent that can re-write the agent code and fix bugs in agent code itself.
- **Debugging and manual feedback components:** add human-in-the-loop gates that serve as an ultimate fallback if the self-service tools are not sufficient to unblock or course-corrent the agent, or if the agent is missing some fundamental piece of context that a human (or external system) needs to provide.
    - Platform-native debugger: when the agent can’t handle an exception, fail the run, but provide a way to fully reproduce the error with a live platform-native debugger.

**Chapter 3: What This Looks Like in Practice (3 minutes)**

- Quick demo/walkthrough: an agent that crashes, resumes from cache, realizes it needs more memory, provisions it, and completes
- **The evaluation loop**: Show how production traces feed back into evals, revealing that 80% of failures weren't prompt issues—they were network timeouts during context retrieval or semantic errors
- Lessons from Union.ai: customers ship faster when they stop over-optimizing prompts for hypothetical scenarios and start making their orchestration resilient to real-world failures

### Call to Action (1 minute)

Tomorrow, do your agent a favor and help them help themselves:

- Use an observability tool: langsmith, weights and biases weave, arize’s phoenix project
- Don’t think about how to make agents failure-proof, because they will inevitably fail. Think about how to make failures as cheap as possible, and how to turn them into eval feedback.
- Ask yourself: "If this crashes at 2 AM, can it recover without me? And will I have the data to improve it?"

Start small. Make crashes cheap. Turn production failures into evaluation data. Help your agents help themselves.

If you want to learn more about how Flyte implements these six design principles, come talk to me after this and visit the [Union.ai](http://Union.ai) booth *here*.

## Resources

- https://docs.google.com/document/d/1wy92ySPjoWPkHCBngtZiieIFKoR4mbNWDd1-A_W5HAU/edit?tab=t.0
- https://docs.google.com/document/d/1AD7VRCXF8L7xdupjZpaWQfsV6PicFatWE3djTRS4gm0/edit?tab=t.0
- https://docs.google.com/presentation/d/1XKZq7rDQSPnNRPXwPmGHS0aQ7B7gJi6_iA6xZRT2RvE/edit?slide=id.g38861d85c2c_0_455#slide=id.g38861d85c2c_0_455
- https://gist.github.com/LeonKolyang/65f30dab4146a19cd71c810365ec2c44
- https://hongsupshin.github.io/posts/2026-01-12/
- https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
