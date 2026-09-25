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
const copySummaryButton = document.getElementById("copySummaryButton");
const downloadSummaryButton = document.getElementById(
    "downloadSummaryButton"
);
const regenerateSummaryButton = document.getElementById(
    "regenerateSummaryButton"
);
const copySummaryStatus = document.getElementById("copySummaryStatus");
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


const fileInput = document.getElementById("fileInput");
const chooseFileButton = document.getElementById("chooseFileButton");
const fileDropZone = document.getElementById("fileDropZone");
const fileStatus = document.getElementById("fileStatus");
const fileStatusText = document.getElementById("fileStatusText");
const fileError = document.getElementById("fileError");
const clearFileButton = document.getElementById("clearFileButton");

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;
const SUPPORTED_FILE_EXTENSIONS = Object.freeze([".txt", ".pdf"]);

let fileExtractionInProgress = false;
let currentFileName = null;


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
        fileExtractionInProgress ||
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
    updateResultActionEligibility();
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
        setCopySummaryStatus("");

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
    updateResultActionEligibility();
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
    updateResultActionEligibility();
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


function getFileExtension(fileName) {
    const normalized = fileName.trim().toLowerCase();

    for (const extension of SUPPORTED_FILE_EXTENSIONS) {
        if (normalized.endsWith(extension)) {
            return extension;
        }
    }

    return "";
}


function isSupportedFile(file) {
    return (
        file instanceof File &&
        getFileExtension(file.name) !== ""
    );
}


function setFileExtractionState(isLoading) {
    fileExtractionInProgress = isLoading;

    fileInput.disabled = isLoading;
    chooseFileButton.disabled = isLoading;
    clearFileButton.disabled = isLoading;

    fileDropZone.classList.toggle(
        "is-disabled",
        isLoading
    );

    fileDropZone.setAttribute(
        "aria-disabled",
        String(isLoading)
    );

    updateSubmitEligibility();
    updateResultActionEligibility();
}


function hideFileError() {
    fileError.textContent = "";
    fileError.classList.add("hidden");
}


function showFileError(message) {
    fileError.textContent = message;
    fileError.classList.remove("hidden");
}


function showFileStatus(message) {
    fileStatusText.textContent = message;
    fileStatus.classList.remove("hidden");
}


function clearFileStatus() {
    currentFileName = null;
    fileStatusText.textContent = "";
    fileStatus.classList.add("hidden");
    fileInput.value = "";
}


function resetFileSelection() {
    clearFileStatus();
    hideFileError();
}


function formatFileSize(sizeBytes) {
    if (sizeBytes < 1024) {
        return `${sizeBytes} B`;
    }

    const kibibytes = sizeBytes / 1024;

    if (kibibytes < 1024) {
        return `${kibibytes.toFixed(1)} KiB`;
    }

    return `${(kibibytes / 1024).toFixed(1)} MiB`;
}


function buildFileStatusMessage(fileMetadata) {
    const parts = [
        fileMetadata.name,
        formatFileSize(fileMetadata.size_bytes),
    ];

    if (
        fileMetadata.type === "pdf" &&
        Number.isInteger(fileMetadata.page_count)
    ) {
        const pageLabel =
            fileMetadata.page_count === 1
                ? "page"
                : "pages";

        parts.push(
            `${fileMetadata.page_count} ${pageLabel}`
        );
    }

    return parts.join(" • ");
}


async function extractFile(file) {
    hideFileError();

    if (!isSupportedFile(file)) {
        showFileError(
            "Choose a TXT or PDF file."
        );
        return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
        showFileError(
            "The uploaded file exceeds the maximum allowed size."
        );
        return;
    }

    setFileExtractionState(true);
    showFileStatus(`Extracting ${file.name}...`);

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
            "/api/v1/files/extract",
            {
                method: "POST",
                body: formData,
            }
        );

        const payload = await response
            .json()
            .catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                typeof payload.detail === "string"
                    ? payload.detail
                    : "The document could not be processed."
            );
        }

        if (
            typeof payload.text !== "string" ||
            payload.text.trim().length === 0 ||
            payload.file === null ||
            typeof payload.file !== "object" ||
            typeof payload.file.name !== "string" ||
            typeof payload.file.type !== "string" ||
            typeof payload.file.size_bytes !== "number"
        ) {
            throw new Error(
                "The document extraction response is invalid."
            );
        }

        inputText.value = payload.text;
        currentFileName = payload.file.name;

        showFileStatus(
            buildFileStatusMessage(payload.file)
        );

        updateInputState();
        inputText.focus();
    } catch (extractionError) {
        clearFileStatus();

        const message =
            extractionError instanceof Error
                ? extractionError.message
                : "The document could not be processed.";

        showFileError(message);
    } finally {
        setFileExtractionState(false);
    }
}


function handleSelectedFiles(files) {
    if (
        fileExtractionInProgress ||
        !files ||
        files.length === 0
    ) {
        return;
    }

    if (files.length > 1) {
        showFileError(
            "Upload one document at a time."
        );
        return;
    }

    extractFile(files[0]);
}


chooseFileButton.addEventListener(
    "click",
    () => {
        if (!fileExtractionInProgress) {
            fileInput.click();
        }
    }
);


fileInput.addEventListener(
    "change",
    () => {
        handleSelectedFiles(fileInput.files);
    }
);


fileDropZone.addEventListener(
    "click",
    () => {
        if (!fileExtractionInProgress) {
            fileInput.click();
        }
    }
);


fileDropZone.addEventListener(
    "keydown",
    (event) => {
        if (
            !fileExtractionInProgress &&
            (event.key === "Enter" || event.key === " ")
        ) {
            event.preventDefault();
            fileInput.click();
        }
    }
);


for (const eventName of ["dragenter", "dragover"]) {
    fileDropZone.addEventListener(
        eventName,
        (event) => {
            event.preventDefault();

            if (!fileExtractionInProgress) {
                fileDropZone.classList.add("is-dragging");
            }
        }
    );
}


for (const eventName of ["dragleave", "drop"]) {
    fileDropZone.addEventListener(
        eventName,
        (event) => {
            event.preventDefault();
            fileDropZone.classList.remove("is-dragging");
        }
    );
}


fileDropZone.addEventListener(
    "drop",
    (event) => {
        if (fileExtractionInProgress) {
            return;
        }

        handleSelectedFiles(
            event.dataTransfer?.files
        );
    }
);


clearFileButton.addEventListener(
    "click",
    () => {
        resetFileSelection();
        inputText.focus();
    }
);


inputText.addEventListener("input", updateInputState);


customInstructions.addEventListener(
    "input",
    updateInstructionsCount
);


modelSelection.addEventListener(
    "change",
    () => {
        updateSubmitEligibility();
        updateResultActionEligibility();
    }
);


function hasSummaryResult() {
    return summaryText.textContent.trim().length > 0;
}


function updateResultActionEligibility() {
    const actionsDisabled =
        currentState === UI_STATE.LOADING ||
        !hasSummaryResult();

    copySummaryButton.disabled = actionsDisabled;
    downloadSummaryButton.disabled = actionsDisabled;
    regenerateSummaryButton.disabled =
        actionsDisabled || fileExtractionInProgress ||
        !hasValidInput() ||
        !hasAvailableModel();
}


function setCopySummaryStatus(message) {
    copySummaryStatus.textContent = message;
}


async function copySummary() {
    if (
        currentState === UI_STATE.LOADING ||
        !hasSummaryResult()
    ) {
        return;
    }

    setCopySummaryStatus("");

    try {
        await navigator.clipboard.writeText(
            summaryText.textContent
        );

        setCopySummaryStatus("Summary copied.");
    } catch (copyError) {
        setCopySummaryStatus(
            "Summary could not be copied."
        );
    }
}


copySummaryButton.addEventListener(
    "click",
    copySummary
);


function padTimestampPart(value) {
    return String(value).padStart(2, "0");
}


function buildSummaryDownloadFileName(date = new Date()) {
    const day = padTimestampPart(date.getDate());
    const month = padTimestampPart(date.getMonth() + 1);
    const year = date.getFullYear();
    const hours = padTimestampPart(date.getHours());
    const minutes = padTimestampPart(date.getMinutes());
    const seconds = padTimestampPart(date.getSeconds());

    return (
        `ai-summary-${day}-${month}-${year}-` +
        `${hours}${minutes}${seconds}.txt`
    );
}


function downloadSummary() {
    if (
        currentState === UI_STATE.LOADING ||
        !hasSummaryResult()
    ) {
        return;
    }

    const summary = summaryText.textContent;
    const blob = new Blob(
        [summary],
        { type: "text/plain;charset=utf-8" }
    );

    const objectUrl = URL.createObjectURL(blob);
    const downloadLink = document.createElement("a");

    downloadLink.href = objectUrl;
    downloadLink.download = buildSummaryDownloadFileName();
    downloadLink.hidden = true;

    document.body.appendChild(downloadLink);

    try {
        downloadLink.click();
    } finally {
        downloadLink.remove();
        URL.revokeObjectURL(objectUrl);
    }
}


downloadSummaryButton.addEventListener(
    "click",
    downloadSummary
);


function regenerateSummary() {
    if (
        currentState === UI_STATE.LOADING ||
        fileExtractionInProgress ||
        !hasSummaryResult() ||
        !hasValidInput() ||
        !hasAvailableModel()
    ) {
        return;
    }

    summaryForm.requestSubmit();
}


regenerateSummaryButton.addEventListener(
    "click",
    regenerateSummary
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

            setCopySummaryStatus("");
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