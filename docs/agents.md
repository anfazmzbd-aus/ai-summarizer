# Agents

## Summary Agent

Purpose:

Generate concise summary.

Input:

state["text"]

Output:

state["summary"]

---

## Actions Agent

Purpose:

Extract action items.

Examples:

* should
* must
* need to
* follow up

Output:

state["actions"]

---

## Insights Agent

Purpose:

Extract business insights.

Examples:

* Revenue trends
* Profit indicators
* Market expansion

Output:

state["insights"]

---

## Findings Agent

Purpose:

Extract research findings.

Examples:

* research
* study
* analysis
* results

Output:

state["findings"]

---

## Trend Agent

Status:

Experimental

Purpose:

Advanced trend analysis.

---

## Plan Agent

Status:

Experimental

Purpose:

Generate execution plans.

#Agent Execution Model (V7.5)

Each agent follows:
state (input)
   ↓
tool/logic
   ↓
state["artifacts"][key] update
   ↓
return state


##Standard Agent Template

@register_agent(
    name="agent_name",
    depends_on=["dependency_agents"],
    produces=["artifact_key"]
)
def agent(state):

    artifacts = state.get("artifacts", {})

    result = tool_logic(artifacts)

    state.setdefault("artifacts", {})["key"] = result

    return state

##Dependency Rules
depends_on defines execution ordering
missing dependencies are auto-injected into DAG
graph validator ensures correctness before execution












