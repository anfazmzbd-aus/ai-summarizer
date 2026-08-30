const summaryForm = document.getElementById("summaryForm");
const inputText = document.getElementById("inputText");
const status = document.getElementById("status");
const result = document.getElementById("result");
const summaryText = document.getElementById("summaryText");
const error = document.getElementById("error");

summaryForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    status.textContent = "Generating summary...";
    status.classList.remove("hidden");
    result.classList.add("hidden");
    error.classList.add("hidden");

    try {
        const response = await fetch("/api/v1/summarize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text: inputText.value,
                provider: "fake",
                model: "demo",
            }),
        });

        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(
                payload.detail?.error?.message ||
                "The summarization request failed."
            );
        }

        const payload = await response.json();
        summaryText.textContent = payload.summary;
        result.classList.remove("hidden");
    } catch (requestError) {
        error.textContent = requestError.message;
        error.classList.remove("hidden");
    } finally {
        status.classList.add("hidden");
    }
});
