# Agentic Workflows

Six runnable Python examples covering the core building blocks of LLM agent
systems, from fixed pipelines to a fully autonomous tool-using agent. Built on
the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python).

| # | Pattern | Example | Use it when |
|---|---------|---------|-------------|
| 1 | [Prompt chaining](01_prompt_chaining.py) | Topic → outline → **gate** → draft → edit | The task splits cleanly into fixed steps |
| 2 | [Routing](02_routing.py) | Support ticket → classifier → specialist prompt | Inputs fall into distinct categories that need different handling |
| 3 | [Parallelization](03_parallelization.py) | 3 focused code reviews + 3-way merge vote | Independent subtasks, or you want confidence via multiple samples |
| 4 | [Orchestrator-workers](04_orchestrator_workers.py) | Planner decides subtasks → parallel workers → synthesizer | You can't know the subtasks until you see the input |
| 5 | [Evaluator-optimizer](05_evaluator_optimizer.py) | Generate code → strict review → revise, until PASS | Clear success criteria, and iteration measurably helps |
| 6 | [Autonomous agent](06_autonomous_agent.py) | Data-analyst agent with sandboxed file + calculator tools | Open-ended tasks where the model must choose its own steps |

Patterns 1–5 are **workflows**: your code controls the flow. Pattern 6 is an
**agent**: the model controls the flow. Start with the simplest one that works;
agents cost more and are harder to debug.

## Run them

Requires Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/).

```bash
cd workflows
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

python 01_prompt_chaining.py "Why vector databases matter for RAG"
python 02_routing.py "I was charged twice this month"
python 03_parallelization.py path/to/some_file.py
python 04_orchestrator_workers.py "Should a 10-person startup adopt Kubernetes?"
python 05_evaluator_optimizer.py "parse ISO-8601 durations into seconds"
python 06_autonomous_agent.py "Which region had the highest total revenue?"
```

Progress goes to stderr and the final result to stdout, so
`python 04_orchestrator_workers.py "..." > brief.md` works.

## Design notes

- **One place for model calls.** [`common.py`](common.py) sets the model
  (override it with `CLAUDE_MODEL`), turns on adaptive thinking, enables
  server-side refusal fallbacks, and raises on refusals so no step silently
  consumes an empty answer.
- **Structured outputs for control flow.** Every decision the code branches
  on (gate pass/fail, route, votes, plans, verdicts) uses a JSON schema, so
  there's no brittle string parsing.
- **Effort matched to the step.** Classification and gates run at `low` effort.
  Drafting, planning and evaluation run at `high`.
- **Guardrails on the agent.** It has a step budget, file access confined to
  `sandbox/`, and an AST-based calculator instead of `eval()`. Tool errors go
  back to the model as `is_error` results so it can recover.
- **Bounded loops.** The gate and evaluator loops have attempt limits, so a
  stubborn case ends instead of burning tokens.

## Live agents on this repository

[`.github/workflows/`](../.github/workflows) runs two of these ideas on real
GitHub events:

- **Issue triage** labels new issues and asks for missing details.
- **PR review** posts a review, and updates that same comment on each push
  instead of adding a new one.

To turn them on, add an `ANTHROPIC_API_KEY` secret under *Settings → Secrets
and variables → Actions*. Until then they exit cleanly without doing anything.
