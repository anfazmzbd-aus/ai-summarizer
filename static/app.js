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

const summaryType =
    document.getElementById("summaryType");

const summaryLength =
    document.getElementById("summaryLength");

const modelSelection =
    document.getElementById("modelSelection");

const modelSelectionStatus =
    document.getElementById("modelSelectionStatus");

const customInstructions =
    document.getElementById("customInstructions");

const customInstructionsCount =
    document.getElementById("customInstructionsCount");


const UI_STATE = Object.freeze({
    IDLE: "idle",
    LOADING: "loading",
    SUCCESS: "success",
    ERROR: "error",
});


const MODEL_STATE = Object.freeze({
    LOADING: "loading",
    READY: "ready",
    ERROR: "error",
});


let currentState = UI_STATE.IDLE;
let currentModelState = MODEL_STATE.LOADING;


function countWords(value) {
    const normalizedValue = value.trim();

    if (!normalizedValue) {
        return 0;
    }

    return normalizedValue.split(/\s+/u).length;
}


function updateInstructionsCount() {
    customInstructionsCount.textContent =
        `${customInstructions.value.length} / 2000`;
}


function updateMetricLabel(
    element,
    count,
    singular,
    plural
) {
    element.textContent =
        count === 1 ? singular : plural;
}


function hasValidInput() {
    return inputText.value.trim().length > 0;
}


function hasAvailableModel() {
    return (
        currentModelState === MODEL_STATE.READY &&
        modelSelection.value.trim().length > 0
    );
}


function updateSubmitEligibility() {
    summarizeButton.disabled =
        currentState === UI_STATE.LOADING ||
        !hasValidInput() ||
        !hasAvailableModel();
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


function setModelState(nextState, message) {
    currentModelState = nextState;

    if (nextState === MODEL_STATE.LOADING) {
        modelSelection.disabled = true;
        modelSelectionStatus.textContent =
            message || "Loading available models...";
    }

    if (nextState === MODEL_STATE.READY) {
        modelSelection.disabled = false;
        modelSelectionStatus.textContent =
            message || "Model options are ready.";
    }

    if (nextState === MODEL_STATE.ERROR) {
        modelSelection.disabled = true;
        modelSelectionStatus.textContent =
            message || "Model options are unavailable.";
    }

    updateSubmitEligibility();
}


function clearModelOptions() {
    modelSelection.replaceChildren();
}


function createModelOption(model) {
    const option = document.createElement("option");

    option.value = model.id;
    option.textContent = model.label;

    if (model.is_default) {
        option.selected = true;
    }

    return option;
}


function populateModelOptions(models) {
    clearModelOptions();

    for (const model of models) {
        modelSelection.appendChild(
            createModelOption(model)
        );
    }
}


function isValidPublicModel(model) {
    return (
        model !== null &&
        typeof model === "object" &&
        typeof model.id === "string" &&
        model.id.trim().length > 0 &&
        typeof model.label === "string" &&
        model.label.trim().length > 0 &&
        typeof model.is_default === "boolean"
    );
}


function validateProductModels(models) {
    if (!Array.isArray(models) || models.length === 0) {
        return false;
    }

    if (!models.every(isValidPublicModel)) {
        return false;
    }

    const defaults = models.filter(
        (model) => model.is_default
    );

    return defaults.length === 1;
}


async function loadProductModels() {
    setModelState(
        MODEL_STATE.LOADING,
        "Loading available models..."
    );

    try {
        const response = await fetch(
            "/api/v1/product-config",
            {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                },
            }
        );

        if (!response.ok) {
            throw new Error(
                "Product configuration could not be loaded."
            );
        }

        const payload = await response.json();
        const models = payload.models;

        if (!validateProductModels(models)) {
            throw new Error(
                "Product configuration is invalid."
            );
        }

        populateModelOptions(models);

        setModelState(
            MODEL_STATE.READY,
            "Model options are ready."
        );
    } catch (configurationError) {
        clearModelOptions();

        const unavailableOption =
            document.createElement("option");

        unavailableOption.value = "";
        unavailableOption.textContent =
            "Models unavailable";

        modelSelection.appendChild(
            unavailableOption
        );

        setModelState(
            MODEL_STATE.ERROR,
            "Model options are unavailable."
        );
    }
}


inputText.addEventListener("input", updateInputState);


customInstructions.addEventListener(
    "input",
    updateInstructionsCount
);


modelSelection.addEventListener(
    "change",
    updateSubmitEligibility
);


summaryForm.addEventListener(
    "submit",
    async (event) => {
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

        if (!hasAvailableModel()) {
            modelSelection.focus();
            return;
        }

        setUIState(
        UI_STATE.LOADING,
        "Generating summary..."
    );

        try {
            /*
            * Product model options are loaded from the public
            * configuration endpoint. The selected product model ID is
            * resolved to its approved private runtime mapping by the
            * server before canonical summarization executes.
            */
            const response = await fetch("/api/v1/summarize", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    text: normalizedText,
                    provider: "fake",
                    model: "demo",
                    product_model: modelSelection.value,
                    summary_type: summaryType.value,
                    summary_length: summaryLength.value,
                    instructions: customInstructions.value.trim() || null,
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
    }
);


updateInputState();
updateInstructionsCount();
setUIState(UI_STATE.IDLE);
loadProductModels();