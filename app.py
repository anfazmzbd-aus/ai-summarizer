from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from summarizer import summarize_text

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/summarize", response_class=HTMLResponse)
def summarize(
    text: str = Form(...),
    summary_length: str = Form(...)
):

    if len(text.strip()) < 20:
        return """
        <h2>Error</h2>
        <p>Please enter at least 20 characters.</p>
        <a href="/">Go Back</a>
        """

    summary = summarize_text(text, summary_length)

    return f"""
    <html>
    <head>
        <title>Summary Result</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>

    <body>
        <div class="container">

            <h1>Summary Result</h1>

            <textarea
                id="summaryText"
                rows="10">{summary}</textarea>

            <br><br>

            <button onclick="copySummary()">
                Copy Summary
            </button>

            <button onclick="downloadSummary()">
                Download TXT
            </button>

            <br><br>

            <a href="/">← Back</a>

        </div>

<script>
function copySummary() {{
    const text =
        document.getElementById("summaryText");

    navigator.clipboard.writeText(text.value);

    alert("Summary copied!");
}}

function downloadSummary() {{
    const text =
        document.getElementById("summaryText").value;

    const blob =
        new Blob([text], {{type:"text/plain"}});

    const link =
        document.createElement("a");

    link.href =
        URL.createObjectURL(blob);

    link.download =
        "summary.txt";

    link.click();
}}
</script>

    </body>
    </html>
    """


@app.post("/api/summarize")
def summarize_api(data: dict):
    text = data.get("text")
    summary_length = data.get("summary_length", "medium")

    summary = summarize_text(text, summary_length)

    return JSONResponse({
        "summary": summary
    })