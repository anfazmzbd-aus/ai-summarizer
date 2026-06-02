from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.services.agent_service import run_agents
from app.services.db_service import save_summary

router = APIRouter()


@router.post("/summarize", response_class=HTMLResponse)
def summarize(
    text: str = Form(...),
    summary_length: str = Form(...)
):

    result = run_agents(text, summary_length)

    # 🔴 CRITICAL: SAVE TO DB
    save_summary(text, result)

    summary = result.get("summary", "")

    actions = result.get("actions", [])
    insights = result.get("insights", [])
    findings = result.get("findings", [])
    plan = result.get("plan", {})
    execution = result.get(
        "execution",
        {}
    )

    actions_html = "".join([f"<li>{a}</li>" for a in actions])
    insights_html = "".join([f"<li>{i}</li>" for i in insights])
    findings_html = "".join([f"<li>{f}</li>" for f in findings])

    return f"""
    <html>
    <body>

        <h2>Summary</h2>
        <p>{summary}</p>

        <h3>Actions</h3>
        <ul>{actions_html}</ul>

        <h3>Insights</h3>
        <ul>{insights_html}</ul>

        <h3>Findings</h3>
        <ul>{findings_html}</ul>

        <h3>Execution Plan</h3>
        <pre>{plan}</pre>
        
        <h3>Execution Metadata</h3>
        <pre>{execution}</pre>
        
        <a href="/">Back</a>

    </body>
    </html>
    """