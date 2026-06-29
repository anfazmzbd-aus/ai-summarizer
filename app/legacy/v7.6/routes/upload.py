from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from pypdf import PdfReader

from app.services.agent_service import run_agents
from app.services.db_service import save_summary


router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    # ----------------------------
    # 1. Read PDF
    # ----------------------------
    pdf = PdfReader(file.file)

    extracted_text = ""

    for page in pdf.pages:
        extracted_text += page.extract_text() or ""

    if len(extracted_text.strip()) < 10:
        return JSONResponse(
            {
                "error": "PDF has no readable text"
            },
            status_code=400
        )

    # ----------------------------
    # 2. Run Agent Pipeline
    # ----------------------------
    result = run_agents(
        extracted_text,
        "medium"
    )

    # ----------------------------
    # 3. Save to DB
    # ----------------------------
    save_summary(
        extracted_text,
        result
    )

    # ----------------------------
    # 4. Response
    # ----------------------------
    return {
        "summary": result["summary"],
        "artifacts": result.get(
            "artifacts",
            {}
        ),
        "plan": result.get(
            "plan",
            {}
        ),
        "execution": result.get(
            "execution",
            {}
        )
    }