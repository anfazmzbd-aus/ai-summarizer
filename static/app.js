const summaryForm = document.getElementById("summaryForm");
const inputText = document.getElementById("inputText");
const summarizeButton = document.getElementById("summarizeButton");

const inputMetrics = document.getElementById("inputMetrics");
const wordCount = document.getElementById("wordCount");
const wordCountLabel = document.getElementById("wordCountLabel");
const characterCount = document.getElementById("characterCount");
const characterCountLabel = document.getElementById(
    "characterCountLabel"
);

const status = document.getElementById("status");
const result = document.getElementById("result");
const resultEmpty = document.getElementById("resultEmpty");
const summaryText = document.getElementById("summaryText");
const error = document.getElementById("error");

const strategyValue = document.getElementById("strategyValue");
const chunkCountValue = document.getElementById("chunkCountValue");
const intelligenceModeValue = document.getElementById(
    "intelligenceModeValue"
);
const observabilityStatusValue = document.getElementById(
    "observabilityStatusValue"
);


function countWords(value) {
    const normalizedValue = value.trim();

    if (!normalizedValue) {
        return 0;
    }

    return normalizedValue.split(/\s+/u).length;
}


function updateMetricLabel(element, count, singular, plural) {
    element.textContent = count === 1 ? singular : plural;
}


function updateInputState() {
    const value = inputText.value;
    const normalizedValue = value.trim();

    const words = countWords(value);
    const characters = value.length;

    wordCount.textContent = String(words);
    characterCount.textContent = String(characters);

    updateMetricLabel(
        wordCountLabel,
        words,
        "word",
        "words"
    );

    updateMetricLabel(
        characterCountLabel,
        characters,
        "character",
        "characters"
    );

    summarizeButton.disabled = normalizedValue.length === 0;
}


inputText.addEventListener("input", updateInputState);


summaryForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const normalizedText = inputText.value.trim();

    if (!normalizedText) {
        updateInputState();
        inputText.focus();
        return;
    }

    status.textContent = "Generating summary...";
    status.classList.remove("hidden");

    result.classList.add("hidden");
    error.classList.add("hidden");

    try {
        const response = await fetch("/api/v1/summarize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                text: normalizedText,
                provider: "fake",
                model: "demo",
            }),
        });

        if (!response.ok) {
            const payload = await response
                .json()
                .catch(() => ({}));

            throw new Error(
                payload.detail?.error?.message ||
                "The summarization request failed."
            );
        }

        const payload = await response.json();
        const metadata = payload.metadata || {};

        summaryText.textContent = payload.summary;

        strategyValue.textContent =
            metadata.strategy || "—";

        chunkCountValue.textContent =
            metadata.chunk_count ?? "—";

        intelligenceModeValue.textContent =
            metadata.intelligence_mode || "—";

        observabilityStatusValue.textContent =
            metadata.observability_status || "—";

        resultEmpty.classList.add("hidden");
        result.classList.remove("hidden");
    } catch (requestError) {
        error.textContent =
            requestError instanceof Error
                ? requestError.message
                : "The summarization request failed.";

        error.classList.remove("hidden");
    } finally {
        status.classList.add("hidden");
    }
});


updateInputState();