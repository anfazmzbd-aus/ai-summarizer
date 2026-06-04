from .agent_graph import run_graph

def run_ai(text, summary_length):

    try:
        result = run_agents(
            text,
            summary_length
        )

        return result

    except Exception as e:
        return {
            "summary":
                f"Error: {str(e)}",

            "actions": [],
            "insights": [],
            "findings": [],
            "plan": {}
        }


def run_agents(
    text,
    summary_length
):

    state = {
        "text": text,
        "summary_length": summary_length,

        "selected_agents": [],

        "summary": "",
        "actions": [],
        "insights": [],
        "findings": [],
        "plan": {},
        #My entry
        "trends": [],
        "metadata": {}
    }

    result = run_graph(state)

    return {
        "summary": result["summary"],
        "actions": result["actions"],
        "insights": result["insights"],
        "findings": result["findings"],
        "trends": result.get("trends", []),
        "plan": result["plan"],
        "execution": result["execution"]
    }

def extract_actions(text: str):

    lines = text.split("\n")

    return [
        line.strip()
        for line in lines
        if "should" in line.lower()
        or "must" in line.lower()
        or "need" in line.lower()
    ]


def extract_insights(text: str):

    return [
        "Business context detected",
        "Key operational information identified"
    ]


def extract_findings(text: str):

    return [
        "Document analyzed",
        "No anomalies detected"
    ]

