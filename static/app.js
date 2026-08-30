const summaryForm = document.getElementById("summaryForm");
const inputText = document.getElementById("inputText");
const status = document.getElementById("status");
const result = document.getElementById("result");
const summaryText = document.getElementById("summaryText");
const error = document.getElementById("error");
const strategyValue = document.getElementById("strategyValue");
const chunkCountValue = document.getElementById("chunkCountValue");
const intelligenceModeValue = document.getElementById("intelligenceModeValue");
const observabilityStatusValue = document.getElementById(
    "observabilityStatusValue"
);

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
        const metadata = payload.metadata || {};

        summaryText.textContent = payload.summary;

        strategyValue.textContent = metadata.strategy || "—";
        chunkCountValue.textContent = metadata.chunk_count ?? "—";
        intelligenceModeValue.textContent = metadata.intelligence_mode || "—";
        observabilityStatusValue.textContent =
            metadata.observability_status || "—";

        result.classList.remove("hidden");s
    } catch (requestError) {
        error.textContent = requestError.message;
        error.classList.remove("hidden");
    } finally {
        status.classList.add("hidden");
    }
});
