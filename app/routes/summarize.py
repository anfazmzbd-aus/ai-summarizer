from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.services.agent_service import run_agents
from app.services.db_service import save_summary
from app.services.logging.logger import logger

router = APIRouter()


@router.post("/summarize", response_class=HTMLResponse)
def summarize(
    text: str = Form(...),
    summary_length: str = Form(...)
):

    result = run_agents(text, summary_length)
    logger.debug("=== DEBUG: FINAL RESULT ===")
    logger.debug(f"SUMMARY result: {result}")
    # 🔴 CRITICAL: SAVE TO DB
    save_summary(text, result)

    summary = result.get("summary", "")

    artifacts = result.get(
        "artifacts",
        {}
    )

    plan = result.get("plan", {})
    execution = result.get("execution" ,{})

    artifact_html = ""

    for name, values in artifacts.items():

        if not values:
            continue

        items = "".join(
            [
                f"<li>{item}</li>"
                for item in values
            ]
        )   
        title = (
            name
            .replace("_", " ")
            .title()
        )
        artifact_html += f"""
        <h3>{title}</h3>
        <ul>{items}</ul>
        """

    logger.info("==============Application AI Summarizer==============")
    logger.info("==============EXECUTION END==============")

    return f"""
    <html>
    <body>

        <h2>Summary</h2>
        <p>{summary}</p>

        {artifact_html}

        <h3>Execution Plan</h3>
        <pre>{plan}</pre>
        
        <h3>Execution Metadata</h3>
        <pre>{execution}</pre>

        <a href="/">Back</a>

    </body>
    </html>
    """