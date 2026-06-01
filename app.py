from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
#from summarizer import summarize_text
from agents import run_agents
from fastapi.templating import Jinja2Templates
from pypdf import PdfReader
from database import engine, SessionLocal, Base
from models import Summary
from typing import Any
from typing import Annotated
import json
from starlette.requests import Request
#import os
#print("TEMPLATE PATH:", os.path.abspath("templates"))


app = FastAPI()

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/summarize", response_class=HTMLResponse)
def summarize(
    request: Request,
    text: str = Form(...),
    summary_length: str = Form(...)
):

    result = run_agents(text, summary_length)

    summary = result.get("summary", "")
    actions = result.get("actions", [])
    insights = result.get("insights", [])
    findings = result.get("findings", [])
    plan = result.get("plan", {})

    plan_text = f"""
Content Type: {plan.get('content_type', 'Unknown')}
Tools Selected: {', '.join(plan.get('tools', []))}
"""

    db = SessionLocal()
    db.add(Summary(
        original_text=text,
        summary=summary,
        content_type=result.get("content_type", "General"),
        agent_output=json.dumps(result)
    ))
    db.commit()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "summary": summary,
            "actions": actions,
            "insights": insights,
            "findings": findings,
            "plan_text": plan_text
        }
    )

@app.get("/summarize")
def test(request: Request):
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "summary": "TEST"
        }
    )

@app.get("/debug")
def debug():
    return {
        "agents_loaded": True,
        "status": "server running"
    }

@app.post("/api/summarize")
def summarize_api(data: dict):
    text = data.get("text")
    summary_length = data.get("summary_length", "medium")

    summary = summarize_text(text, summary_length)

    return JSONResponse({
        "summary": summary
    })

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    pdf = PdfReader(file.file)

    extracted_text = ""

    for page in pdf.pages:
        extracted_text += page.extract_text()

    summary = summarize_text(
        extracted_text,
        "medium"
    )

    db = SessionLocal()

    db_summary = Summary(
        original_text=extracted_text[:1000],
        summary=summary
    )

    db.add(db_summary)
    db.commit()
    db.close()

    return {
        "summary": summary
    }

#print("TEMPLATES TYPE:", type(templates))

from starlette.requests import Request

@app.get("/history")
def history(request: Request):

    db = SessionLocal()
    rows = db.query(Summary).order_by(Summary.id.desc()).all()
    db.close()

    summaries = [
        {
            "original_text": r.original_text,
            "summary": r.summary
        }
        for r in rows
    ]

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"summaries": summaries}
    )