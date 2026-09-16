const summaryForm = document.getElementById("summaryForm");
const inputText = document.getElementById("inputText");
const summarizeButton = document.getElementById("summarizeButton");
const buttonSpinner = document.getElementById("buttonSpinner");
const buttonLabel = document.getElementById("buttonLabel");

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
const summaryContent = document.getElementById("summaryContent");
const error = document.getElementById("error");

const strategyValue = document.getElementById("strategyValue");
const chunkCountValue = document.getElementById("chunkCountValue");
const intelligenceModeValue = document.getElementById(
    "intelligenceModeValue"
);
const observabilityStatusValue = document.getElementById(
    "observabilityStatusValue"
);


const UI_STATE = Object.freeze({
    IDLE: "idle",
    LOADING: "loading",
    SUCCESS: "success",
    ERROR: "error",
});


let currentState = UI_STATE.IDLE;


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


function hasValidInput() {
    return inputText.value.trim().length > 0;
}


function updateSubmitEligibility() {
    summarizeButton.disabled =
        currentState === UI_STATE.LOADING ||
        !hasValidInput();
}


function updateInputState() {
    const value = inputText.value;

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

    updateSubmitEligibility();
}


function hideStatus() {
    status.textContent = "";
    status.classList.add("hidden");
}


function hideError() {
    error.textContent = "";
    error.classList.add("hidden");
}


function showEmptyResult() {
    result.classList.add("hidden");
    resultEmpty.classList.remove("hidden");
}


function showResult() {
    resultEmpty.classList.add("hidden");
    result.classList.remove("hidden");
}


function setLoadingButton(isLoading) {
    buttonLabel.textContent = isLoading
        ? "Summarizing..."
        : "Summarize";

    buttonSpinner.classList.toggle(
        "hidden",
        !isLoading
    );
}


function setUIState(nextState, message = "") {
    currentState = nextState;

    document.body.dataset.uiState = nextState;

    if (nextState === UI_STATE.IDLE) {
        hideStatus();
        hideError();
        showEmptyResult();
        setLoadingButton(false);
    }

    if (nextState === UI_STATE.LOADING) {
        hideError();

        status.textContent =
            message || "Generating summary...";

        status.classList.remove("hidden");

        /*
         * Preserve a previous successful result while a new request
         * runs. For the first request, the empty state remains visible.
         */
        setLoadingButton(true);
    }

    if (nextState === UI_STATE.SUCCESS) {
        hideStatus();
        hideError();
        showResult();
        setLoadingButton(false);
    }

    if (nextState === UI_STATE.ERROR) {
        hideStatus();

        error.textContent =
            message || "The summarization request failed.";

        error.classList.remove("hidden");

        /*
         * A previous successful result remains available after a failed
         * regeneration. If there is no previous result, the empty state
         * remains visible.
         */
        setLoadingButton(false);
    }

    updateSubmitEligibility();
}


inputText.addEventListener("input", updateInputState);


summaryForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (currentState === UI_STATE.LOADING) {
        return;
    }

    const normalizedText = inputText.value.trim();

    if (!normalizedText) {
        updateInputState();
        inputText.focus();
        return;
    }

    setUIState(
        UI_STATE.LOADING,
        "Generating summary..."
    );

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

        setUIState(UI_STATE.SUCCESS);
        summaryContent.focus();
    } catch (requestError) {
        const message =
            requestError instanceof Error
                ? requestError.message
                : "The summarization request failed.";

        setUIState(UI_STATE.ERROR, message);
    }
});


updateInputState();
setUIState(UI_STATE.IDLE);