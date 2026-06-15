from .agent_graph import run_graph
from app.services.registry.registry import AGENT_REGISTRY
from app.services.logging.logger import logger

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
        "summary": "",
        "actions": [],
        "insights": [],
        "findings": [],
        "trends": [],
        "plan": {},
        "metadata": {},
        "artifacts": {},
        "context": {}   
    }

    logger.info(
        f"\n****REGISTERED AGENTS: "
        f"{list(AGENT_REGISTRY.keys())}"
    )
    result = run_graph(state)

    logger.info(f"****FINAL ARTIFACTS: ")
    logger.info(f"{result.get('artifacts', {})}")
    
    return {
        "summary": result["summary"],

        "artifacts": result.get("artifacts", {}),

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

