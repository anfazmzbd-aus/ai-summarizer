"""V13 M7.6 realistic deterministic content-scenario certification.

This suite validates realistic product usage without external providers.

Coverage includes:

* general business text
* executive reporting
* meeting/action-item content
* research findings
* customer/operational insights
* technical architecture content
* incident/key-point content
* structured and noisy text
* Unicode and regional text
* long-form source content
* TXT-extracted source
* PDF-extracted source representation
* all product summary types
* all product summary lengths
* custom instructions
* approved product-model resolution
* response/result metadata contract
* deterministic offline execution

M7.6 introduces no new product functionality.

The purpose is not to judge LLM prose quality. Instead, it certifies that
realistic content and product selections survive the integrated product
boundary correctly and reach the canonical application path without
architectural drift.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.core.product_options import (
    SummaryLength,
    SummaryType,
    resolve_length_instruction,
    resolve_summary_profile,
)
from app.main import app
from app.routes import ai as ai_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

APPLICATION_PATH = PROJECT_ROOT / "app" / "api" / "application.py"

AI_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "ai.py"


client = TestClient(app)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_index_html() -> str:
    return read(INDEX_HTML_PATH)


def read_app_js() -> str:
    return read(APP_JS_PATH)


def read_application() -> str:
    return read(APPLICATION_PATH)


def read_ai_route() -> str:
    return read(AI_ROUTE_PATH)


def read_this_test_module() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def imported_modules() -> set[str]:
    tree = ast.parse(read_this_test_module())

    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)

        if (
            isinstance(
                node,
                ast.ImportFrom,
            )
            and node.module
        ):
            modules.add(node.module)

    return modules


def decorator_path(
    node: ast.expr,
) -> str:
    if isinstance(
        node,
        ast.Name,
    ):
        return node.id

    if isinstance(
        node,
        ast.Attribute,
    ):
        parent = decorator_path(node.value)

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    if isinstance(
        node,
        ast.Call,
    ):
        return decorator_path(node.func)

    return ""


def module_decorators() -> set[str]:
    tree = ast.parse(read_this_test_module())

    decorators: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            for decorator in node.decorator_list:
                decorators.add(decorator_path(decorator))

    return decorators


def build_catalogue() -> ProductModelCatalogue:
    return ProductModelCatalogue(
        (
            ProductModel(
                id="balanced",
                label="Balanced",
                provider="fake",
                model="runtime-balanced",
                is_default=True,
            ),
            ProductModel(
                id="quality",
                label="Quality",
                provider="fake",
                model="runtime-quality",
                is_default=False,
            ),
        )
    )


class FakeMetadata:
    strategy = "direct"
    chunk_count = 1
    intelligence_mode = "preserve"
    trace_id = "m7-6-realistic-trace"
    explainability_summary = "deterministic realistic scenario"
    attributes = {
        "intelligence_observability_status": "normal",
    }


class FakeResult:
    def __init__(
        self,
        *,
        summary: str,
        model: str,
    ) -> None:
        self.summary = summary
        self.model = model
        self.prompt_tokens = 40
        self.completion_tokens = 20
        self.metadata = FakeMetadata()

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class CapturingApplication:
    def __init__(
        self,
        captured: dict,
    ) -> None:
        self._captured = captured

    async def summarize(
        self,
        request,
    ):
        self._captured["request"] = request

        summary = (
            f"scenario-summary:"
            f"{request.summary_type.value}:"
            f"{request.summary_length.value}"
        )

        return FakeResult(
            summary=summary,
            model=request.model or "",
        )


@dataclass(frozen=True)
class Scenario:
    name: str
    text: str
    summary_type: str
    summary_length: str
    instructions: str | None = None
    product_model: str = "balanced"


BUSINESS_SOURCE = """
Quarterly Operations Review

Revenue increased by 8 percent compared with the previous quarter.
Customer complaints fell by 12 percent after the new escalation process
was introduced. Network availability remained at 99.94 percent.

Two operational risks remain. Spare-parts lead times increased from
four weeks to seven weeks, and contractor overtime exceeded budget by
11 percent.

Management approved three actions:
1. Renegotiate the critical-spares supply agreement by 15 October.
2. Reduce contractor overtime through revised shift allocation.
3. Complete the regional resilience review before the next board meeting.

The operations team expects the resilience programme to reduce
high-impact service interruptions during the next quarter.
""".strip()


MEETING_SOURCE = """
Weekly Delivery Meeting
Date: 18 September 2026

Participants: Operations, Engineering, Product, Finance.

Discussion:
- Engineering completed the API migration.
- Product reported two unresolved accessibility defects.
- Finance requested an updated infrastructure forecast.
- Operations confirmed that the production rehearsal is scheduled for
  30 September.

Decisions:
- Release candidate testing starts Monday.
- Accessibility defects must be closed before release certification.
- No new product features will enter the release branch.

Actions:
- Priya will close the keyboard-navigation defect by Friday.
- Nimal will provide the revised cloud-cost forecast by Thursday.
- Engineering will publish the rehearsal checklist before 28 September.
""".strip()


RESEARCH_SOURCE = """
Research Evaluation: Document Summarization Pilot

The pilot compared manual analyst summaries with AI-assisted summaries
across 120 internal documents. Reviewers scored factual coverage,
readability, and time saved.

The AI-assisted workflow reduced median preparation time from
34 minutes to 11 minutes. Factual coverage was similar for short and
medium documents, but reviewers identified more omissions in very long
documents containing multiple unrelated sections.

Participants preferred structured key-point output for operational
reports and narrative executive summaries for management papers.

The study did not evaluate regulated medical, legal, or financial
decision making. Results therefore apply only to the tested internal
document set.
""".strip()


TECHNICAL_SOURCE = """
System Architecture Change Record

The API gateway forwards POST /api/v1/summarize to the product API.
The product API creates a SummarizationApplicationRequest and invokes
the canonical SummarizationApplication.

The application evaluates bounded intelligence policy, resolves the
summary profile, and passes the request into the asynchronous
summarization pipeline adapter.

Provider credentials remain server-side. Browser clients receive only
approved public model identifiers from /api/v1/product-config.

File uploads use POST /api/v1/files/extract. The extraction service
returns normalized text to the browser. The browser then submits that
text through the same /api/v1/summarize endpoint.

Constraints:
- Python 3.11
- FastAPI
- deterministic offline regression by default
- no frontend provider credentials
- no secondary summarization execution path
""".strip()


CUSTOMER_FEEDBACK_SOURCE = """
Customer Feedback Review

Positive themes:
Customers consistently praised faster response times, improved status
notifications, and clearer escalation ownership.

Negative themes:
Several customers reported that outage messages were too technical.
Some users also found the account verification flow repetitive on
mobile devices.

Pattern:
Complaints were concentrated around communication clarity rather than
the underlying service restoration time.

Opportunity:
The support team proposed simpler outage language and a single mobile
verification checkpoint, subject to security approval.
""".strip()


INCIDENT_SOURCE = """
Service Incident Report INC-2048

Start: 08:42
End: 09:27
Affected region: Western region
Customer impact: Intermittent access to the self-service portal.

Timeline:
08:42 Monitoring detected elevated HTTP 503 responses.
08:47 Traffic was shifted away from one application node.
08:55 Engineering identified an exhausted database connection pool.
09:06 Connection limits were increased.
09:18 Error rates returned to normal.
09:27 Incident closed after observation period.

Root condition:
A deployment increased concurrent database sessions without updating
the connection-pool ceiling.

Follow-up:
Capacity settings will be added to the deployment verification
checklist.
""".strip()


GENERAL_SOURCE = """
The company introduced a hybrid working policy for its technology
teams. Employees may work remotely up to three days per week, while
teams must maintain agreed office coverage for customer-facing and
operational responsibilities.

Managers will review the arrangement after three months using employee
feedback, service performance, project delivery, and office-capacity
data. The policy does not change existing information-security
requirements.
""".strip()


STRUCTURED_SOURCE = """
PROJECT STATUS

Completed
* API contract freeze
* Accessibility review
* Database backup rehearsal

In progress
* Production runbook
* Capacity testing
* Final security review

Blocked
* External DNS approval

Risk: DNS approval must arrive before the release rehearsal.
Owner: Infrastructure team.
Target date: 29 September 2026.
""".strip()


NOISY_SOURCE = """
Update...   project is GREEN overall.

Budget:     within plan.
Schedule:   2 days ahead.

BUT:
vendor approval = pending
security sign-off = completed
training materials = completed

Next step??? obtain vendor approval, then run final rehearsal.

Contact: operations@example.invalid
Reference: OPS-2026-091
""".strip()


UNICODE_SOURCE = """
Regional Service Update

Colombo operations reported stable service during the morning period.
The Negombo support team completed the planned customer-notification
exercise.

සිංහල පාරිභෝගික පණිවිඩ පරීක්ෂාව සාර්ථකව අවසන් කරන ලදී.

தமிழ் வாடிக்கையாளர் அறிவிப்பு மாதிரியும் சோதிக்கப்பட்டது.

The exercise confirmed that multilingual content can coexist with
English operational notes without changing the underlying workflow.
""".strip()


LONG_SOURCE = "\n\n".join(
    (
        f"Section {number}: "
        "The programme team reviewed delivery progress, operational "
        "risk, customer impact, dependencies, budget position, and "
        "next actions. The section records confirmed decisions and "
        "identifies accountable owners for outstanding work."
    )
    for number in range(1, 81)
)


TXT_EXTRACTED_SOURCE = """
Operations Checklist

1. Confirm monitoring dashboards are available.
2. Verify rollback instructions.
3. Confirm incident contacts.
4. Run smoke tests.
5. Record release approval.

Status: ready for rehearsal.
""".strip()


PDF_EXTRACTED_SOURCE = """
Board Paper: Reliability Programme

The reliability programme completed phase one within the approved
budget. Preventive maintenance coverage increased, two ageing platform
components were replaced, and incident-response exercises were
completed in all regions.

The board is asked to note the progress and approve phase-two capacity
work for the next financial period.
""".strip()


SCENARIOS = (
    Scenario(
        name="general_business",
        text=GENERAL_SOURCE,
        summary_type="general",
        summary_length="medium",
    ),
    Scenario(
        name="executive_operations",
        text=BUSINESS_SOURCE,
        summary_type="executive",
        summary_length="detailed",
        instructions=("Focus on decisions, risks, " "performance, and next actions."),
    ),
    Scenario(
        name="meeting_actions",
        text=MEETING_SOURCE,
        summary_type="action_items",
        summary_length="medium",
        instructions=("Preserve owners and deadlines."),
    ),
    Scenario(
        name="research_findings",
        text=RESEARCH_SOURCE,
        summary_type="findings",
        summary_length="detailed",
    ),
    Scenario(
        name="customer_insights",
        text=CUSTOMER_FEEDBACK_SOURCE,
        summary_type="insights",
        summary_length="medium",
        instructions=("Separate supported patterns " "from proposed actions."),
    ),
    Scenario(
        name="technical_architecture",
        text=TECHNICAL_SOURCE,
        summary_type="technical",
        summary_length="detailed",
        product_model="quality",
    ),
    Scenario(
        name="incident_key_points",
        text=INCIDENT_SOURCE,
        summary_type="key_points",
        summary_length="short",
    ),
    Scenario(
        name="structured_status",
        text=STRUCTURED_SOURCE,
        summary_type="key_points",
        summary_length="medium",
    ),
    Scenario(
        name="noisy_operational_text",
        text=NOISY_SOURCE,
        summary_type="general",
        summary_length="short",
    ),
    Scenario(
        name="unicode_regional_text",
        text=UNICODE_SOURCE,
        summary_type="general",
        summary_length="medium",
    ),
    Scenario(
        name="long_programme_report",
        text=LONG_SOURCE,
        summary_type="executive",
        summary_length="detailed",
    ),
    Scenario(
        name="txt_extracted_content",
        text=TXT_EXTRACTED_SOURCE,
        summary_type="action_items",
        summary_length="short",
    ),
    Scenario(
        name="pdf_extracted_content",
        text=PDF_EXTRACTED_SOURCE,
        summary_type="executive",
        summary_length="medium",
    ),
)


def execute_scenario(
    monkeypatch,
    scenario: Scenario,
):
    catalogue = build_catalogue()
    captured: dict = {}

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: CapturingApplication(captured),
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": scenario.text,
            "product_model": (scenario.product_model),
            "summary_type": (scenario.summary_type),
            "summary_length": (scenario.summary_length),
            "instructions": (scenario.instructions),
        },
    )

    return response, captured


# ---------------------------------------------------------------------------
# Scenario inventory
# ---------------------------------------------------------------------------


def test_realistic_scenario_set_is_non_empty():
    assert SCENARIOS


def test_realistic_scenarios_have_unique_names():
    names = [scenario.name for scenario in SCENARIOS]

    assert len(names) == len(set(names))


def test_realistic_scenarios_have_non_empty_source():
    for scenario in SCENARIOS:
        assert scenario.text.strip()


def test_realistic_scenarios_cover_all_summary_types():
    covered = {scenario.summary_type for scenario in SCENARIOS}

    expected = {value.value for value in SummaryType}

    assert covered == expected


def test_realistic_scenarios_cover_all_summary_lengths():
    covered = {scenario.summary_length for scenario in SCENARIOS}

    expected = {value.value for value in SummaryLength}

    assert covered == expected


def test_realistic_scenarios_include_custom_instructions():
    assert any(scenario.instructions for scenario in SCENARIOS)


def test_realistic_scenarios_include_default_instructions_path():
    assert any(scenario.instructions is None for scenario in SCENARIOS)


def test_realistic_scenarios_cover_multiple_approved_models():
    models = {scenario.product_model for scenario in SCENARIOS}

    assert models == {
        "balanced",
        "quality",
    }


# ---------------------------------------------------------------------------
# Product options remain authoritative
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "summary_type",
    list(SummaryType),
)
def test_each_summary_type_has_authoritative_profile(
    summary_type,
):
    profile = resolve_summary_profile(summary_type)

    assert profile.intent is not None
    assert profile.instruction.strip()


@pytest.mark.parametrize(
    "summary_length",
    list(SummaryLength),
)
def test_each_summary_length_has_authoritative_instruction(
    summary_length,
):
    instruction = resolve_length_instruction(summary_length)

    assert instruction.strip()


def test_frontend_exposes_every_supported_summary_type():
    html = read_index_html()

    for summary_type in SummaryType:
        assert f'value="{summary_type.value}"' in html


def test_frontend_exposes_every_supported_summary_length():
    html = read_index_html()

    for summary_length in SummaryLength:
        assert f'value="{summary_length.value}"' in html


# ---------------------------------------------------------------------------
# Realistic API scenarios
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_reaches_canonical_application(
    monkeypatch,
    scenario,
):
    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200
    assert "request" in captured


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_preserves_source_text(
    monkeypatch,
    scenario,
):
    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.text == scenario.text


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_preserves_summary_type(
    monkeypatch,
    scenario,
):
    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.summary_type.value == scenario.summary_type


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_preserves_summary_length(
    monkeypatch,
    scenario,
):
    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.summary_length.value == scenario.summary_length


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_preserves_instructions(
    monkeypatch,
    scenario,
):
    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.instructions == scenario.instructions


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_resolves_approved_model(
    monkeypatch,
    scenario,
):
    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    request = captured["request"]

    expected_model = (
        "runtime-quality" if scenario.product_model == "quality" else "runtime-balanced"
    )

    assert request.provider == "fake"
    assert request.model == expected_model


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_returns_deterministic_summary(
    monkeypatch,
    scenario,
):
    response, _ = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    expected = (
        "scenario-summary:" f"{scenario.summary_type}:" f"{scenario.summary_length}"
    )

    assert response.json()["summary"] == expected


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_realistic_scenario_preserves_response_contract(
    monkeypatch,
    scenario,
):
    response, _ = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["prompt_tokens"] == 40
    assert payload["completion_tokens"] == 20
    assert payload["total_tokens"] == 60

    assert payload["metadata"]["strategy"] == "direct"

    assert payload["metadata"]["chunk_count"] == 1

    assert payload["metadata"]["intelligence_mode"] == "preserve"

    assert payload["metadata"]["observability_status"] == "normal"


# ---------------------------------------------------------------------------
# Business scenario
# ---------------------------------------------------------------------------


def test_business_source_contains_metrics():
    assert "8 percent" in BUSINESS_SOURCE
    assert "99.94 percent" in BUSINESS_SOURCE


def test_business_source_contains_risks():
    assert "operational risks" in BUSINESS_SOURCE


def test_business_source_contains_actions():
    assert "Management approved three actions" in BUSINESS_SOURCE


def test_business_scenario_uses_executive_mode():
    scenario = next(item for item in SCENARIOS if item.name == "executive_operations")

    assert scenario.summary_type == "executive"

    assert scenario.summary_length == "detailed"


# ---------------------------------------------------------------------------
# Meeting scenario
# ---------------------------------------------------------------------------


def test_meeting_source_contains_decisions():
    assert "Decisions:" in MEETING_SOURCE


def test_meeting_source_contains_named_actions():
    assert "Priya" in MEETING_SOURCE
    assert "Nimal" in MEETING_SOURCE


def test_meeting_scenario_uses_action_items():
    scenario = next(item for item in SCENARIOS if item.name == "meeting_actions")

    assert scenario.summary_type == "action_items"


def test_meeting_scenario_requests_owner_preservation():
    scenario = next(item for item in SCENARIOS if item.name == "meeting_actions")

    assert scenario.instructions == "Preserve owners and deadlines."


# ---------------------------------------------------------------------------
# Research scenario
# ---------------------------------------------------------------------------


def test_research_source_contains_sample_size():
    assert "120 internal documents" in RESEARCH_SOURCE


def test_research_source_contains_measured_outcome():
    assert "34 minutes to 11 minutes" in RESEARCH_SOURCE


def test_research_source_contains_scope_limitation():
    assert "did not evaluate regulated medical" in RESEARCH_SOURCE


def test_research_scenario_uses_findings():
    scenario = next(item for item in SCENARIOS if item.name == "research_findings")

    assert scenario.summary_type == "findings"


# ---------------------------------------------------------------------------
# Technical scenario
# ---------------------------------------------------------------------------


def test_technical_source_contains_canonical_endpoint():
    assert "POST /api/v1/summarize" in TECHNICAL_SOURCE


def test_technical_source_contains_file_extraction_endpoint():
    assert "POST /api/v1/files/extract" in TECHNICAL_SOURCE


def test_technical_source_contains_security_constraint():
    assert "no frontend provider credentials" in TECHNICAL_SOURCE


def test_technical_scenario_uses_technical_summary():
    scenario = next(item for item in SCENARIOS if item.name == "technical_architecture")

    assert scenario.summary_type == "technical"

    assert scenario.product_model == "quality"


# ---------------------------------------------------------------------------
# Insight scenario
# ---------------------------------------------------------------------------


def test_customer_source_contains_positive_theme():
    assert "faster response times" in CUSTOMER_FEEDBACK_SOURCE


def test_customer_source_contains_negative_theme():
    assert "outage messages were too technical" in CUSTOMER_FEEDBACK_SOURCE


def test_customer_source_contains_supported_pattern():
    assert "communication clarity" in CUSTOMER_FEEDBACK_SOURCE


def test_customer_scenario_uses_insights():
    scenario = next(item for item in SCENARIOS if item.name == "customer_insights")

    assert scenario.summary_type == "insights"


# ---------------------------------------------------------------------------
# Incident scenario
# ---------------------------------------------------------------------------


def test_incident_source_contains_timeline():
    assert "08:42" in INCIDENT_SOURCE
    assert "09:27" in INCIDENT_SOURCE


def test_incident_source_contains_root_condition():
    assert "database connection pool" in INCIDENT_SOURCE


def test_incident_scenario_uses_key_points():
    scenario = next(item for item in SCENARIOS if item.name == "incident_key_points")

    assert scenario.summary_type == "key_points"

    assert scenario.summary_length == "short"


# ---------------------------------------------------------------------------
# Structured and noisy text
# ---------------------------------------------------------------------------


def test_structured_source_contains_sections():
    assert "Completed" in STRUCTURED_SOURCE
    assert "In progress" in STRUCTURED_SOURCE
    assert "Blocked" in STRUCTURED_SOURCE


def test_structured_source_preserves_bullet_content():
    assert "* Production runbook" in STRUCTURED_SOURCE


def test_noisy_source_contains_irregular_spacing():
    assert "Budget:     within plan." in NOISY_SOURCE


def test_noisy_source_contains_punctuation_noise():
    assert "Next step???" in NOISY_SOURCE


# ---------------------------------------------------------------------------
# Unicode content
# ---------------------------------------------------------------------------


def test_unicode_source_contains_sinhala():
    assert "සිංහල" in UNICODE_SOURCE


def test_unicode_source_contains_tamil():
    assert "தமிழ்" in UNICODE_SOURCE


def test_unicode_source_round_trips_through_api(
    monkeypatch,
):
    scenario = next(item for item in SCENARIOS if item.name == "unicode_regional_text")

    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    assert "සිංහල" in captured["request"].text

    assert "தமிழ்" in captured["request"].text


# ---------------------------------------------------------------------------
# Long-form source
# ---------------------------------------------------------------------------


def test_long_source_has_many_sections():
    assert LONG_SOURCE.count("Section ") == 80


def test_long_source_is_materially_larger_than_short_sources():
    assert len(LONG_SOURCE) > len(GENERAL_SOURCE) * 10


def test_long_source_round_trips_without_truncation(
    monkeypatch,
):
    scenario = next(item for item in SCENARIOS if item.name == "long_programme_report")

    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    assert captured["request"].text == LONG_SOURCE


# ---------------------------------------------------------------------------
# Extracted document representations
# ---------------------------------------------------------------------------


def test_txt_extracted_source_is_realistic():
    assert "Operations Checklist" in TXT_EXTRACTED_SOURCE

    assert "Status: ready for rehearsal." in TXT_EXTRACTED_SOURCE


def test_pdf_extracted_source_is_realistic():
    assert "Board Paper" in PDF_EXTRACTED_SOURCE

    assert "approve phase-two capacity" in PDF_EXTRACTED_SOURCE

    assert "work for the next financial period." in PDF_EXTRACTED_SOURCE


def test_txt_extracted_source_rejoins_canonical_summary_path(
    monkeypatch,
):
    scenario = next(item for item in SCENARIOS if item.name == "txt_extracted_content")

    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    assert captured["request"].text == TXT_EXTRACTED_SOURCE

    assert captured["request"].summary_type.value == "action_items"


def test_pdf_extracted_source_rejoins_canonical_summary_path(
    monkeypatch,
):
    scenario = next(item for item in SCENARIOS if item.name == "pdf_extracted_content")

    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    assert captured["request"].text == PDF_EXTRACTED_SOURCE

    assert captured["request"].summary_type.value == "executive"


def test_frontend_file_extraction_still_writes_to_main_source():
    js = read_app_js()

    assert "inputText.value = payload.text;" in js


def test_file_extraction_still_does_not_auto_summarize():
    js = read_app_js()

    extraction_start = js.index("async function extractFile(")

    extraction_end = js.index(
        "function handleSelectedFiles(",
        extraction_start,
    )

    extraction = js[extraction_start:extraction_end]

    assert "/api/v1/summarize" not in extraction


# ---------------------------------------------------------------------------
# Instruction handling
# ---------------------------------------------------------------------------


def test_realistic_instruction_is_preserved(
    monkeypatch,
):
    scenario = next(item for item in SCENARIOS if item.name == "executive_operations")

    response, captured = execute_scenario(
        monkeypatch,
        scenario,
    )

    assert response.status_code == 200

    assert captured["request"].instructions == scenario.instructions


def test_whitespace_instruction_normalizes_to_none(
    monkeypatch,
):
    catalogue = build_catalogue()
    captured = {}

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: CapturingApplication(captured),
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": GENERAL_SOURCE,
            "product_model": "balanced",
            "summary_type": "general",
            "summary_length": "medium",
            "instructions": "   \n\t   ",
        },
    )

    assert response.status_code == 200

    assert captured["request"].instructions is None


def test_instruction_at_limit_is_accepted(
    monkeypatch,
):
    catalogue = build_catalogue()
    captured = {}

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: CapturingApplication(captured),
    )

    instruction = "x" * 2000

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": GENERAL_SOURCE,
            "product_model": "balanced",
            "summary_type": "general",
            "summary_length": "medium",
            "instructions": instruction,
        },
    )

    assert response.status_code == 200

    assert captured["request"].instructions == instruction


def test_instruction_over_limit_is_rejected():
    response = client.post(
        "/api/v1/summarize",
        json={
            "text": GENERAL_SOURCE,
            "summary_type": "general",
            "summary_length": "medium",
            "instructions": ("x" * 2001),
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Invalid product-option scenarios
# ---------------------------------------------------------------------------


def test_unknown_summary_type_is_rejected():
    response = client.post(
        "/api/v1/summarize",
        json={
            "text": GENERAL_SOURCE,
            "summary_type": "not-a-type",
            "summary_length": "medium",
        },
    )

    assert response.status_code == 422


def test_unknown_summary_length_is_rejected():
    response = client.post(
        "/api/v1/summarize",
        json={
            "text": GENERAL_SOURCE,
            "summary_type": "general",
            "summary_length": "very-long",
        },
    )

    assert response.status_code == 422


def test_empty_realistic_source_is_rejected():
    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "   \n\t ",
            "summary_type": "general",
            "summary_length": "medium",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Frontend integrated scenario transport
# ---------------------------------------------------------------------------


def test_frontend_uses_current_text_for_realistic_sources():
    js = read_app_js()

    assert "const normalizedText = inputText.value.trim();" in js

    assert "text: normalizedText" in js


def test_frontend_uses_current_summary_type():
    js = read_app_js()

    assert "summary_type: summaryType.value" in js


def test_frontend_uses_current_summary_length():
    js = read_app_js()

    assert "summary_length: summaryLength.value" in js


def test_frontend_uses_current_instructions():
    js = read_app_js()

    assert "customInstructions.value.trim() || null" in js


def test_frontend_uses_approved_public_model_id():
    js = read_app_js()

    assert "product_model: modelSelection.value" in js


# ---------------------------------------------------------------------------
# Deterministic response/result workflow
# ---------------------------------------------------------------------------


def test_realistic_response_populates_summary_workspace():
    js = read_app_js()

    assert "summaryText.textContent = payload.summary;" in js


def test_realistic_response_populates_strategy():
    js = read_app_js()

    assert "metadata.strategy" in js


def test_realistic_response_populates_chunk_count():
    js = read_app_js()

    assert "metadata.chunk_count" in js


def test_realistic_response_populates_intelligence_mode():
    js = read_app_js()

    assert "metadata.intelligence_mode" in js


def test_realistic_response_populates_observability_status():
    js = read_app_js()

    assert "metadata.observability_status" in js


def test_realistic_success_uses_existing_result_actions():
    html = read_index_html()

    assert 'id="copySummaryButton"' in html

    assert 'id="downloadSummaryButton"' in html

    assert 'id="regenerateSummaryButton"' in html


# ---------------------------------------------------------------------------
# Canonical architecture invariants
# ---------------------------------------------------------------------------


def test_application_resolves_summary_profile():
    source = read_application()

    assert "resolve_summary_profile" in source


def test_application_resolves_length_instruction():
    source = read_application()

    assert "resolve_length_instruction" in source


def test_application_passes_summary_intent_to_pipeline():
    source = read_application()

    assert "intent=summary_profile.intent" in source


def test_ai_route_passes_product_controls_into_application_request():
    route = read_ai_route()

    assert "summary_type=request.summary_type" in route

    assert "summary_length=request.summary_length" in route

    assert "instructions=request.instructions" in route


def test_m7_6_keeps_single_summarization_endpoint():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_m7_6_does_not_add_content_specific_endpoints():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/executive-summary",
        "/api/v1/action-items",
        "/api/v1/findings",
        "/api/v1/insights",
        "/api/v1/technical-summary",
        "/api/v1/key-points",
    )

    for endpoint in forbidden:
        assert endpoint not in js


def test_m7_6_does_not_use_browser_provider_logic():
    js = read_app_js()

    assert "model.provider" not in js

    assert "model.runtime_model" not in js


def test_m7_6_remains_offline_deterministic():
    modules = imported_modules()

    network_client_roots = {
        "requests",
        "httpx",
        "openai",
    }

    imported_roots = {module.split(".", 1)[0] for module in modules}

    assert imported_roots.isdisjoint(network_client_roots)


def test_m7_6_has_no_live_marker():
    decorators = module_decorators()

    assert "pytest.mark.live" not in decorators


def test_m7_6_has_no_persistence_dependency():
    modules = imported_modules()

    persistence_roots = {
        "sqlalchemy",
        "sqlite3",
    }

    imported_roots = {module.split(".", 1)[0] for module in modules}

    assert imported_roots.isdisjoint(persistence_roots)

    assert not any(
        ".repository" in module or module.endswith(".database") for module in modules
    )


def test_m7_6_preserves_canonical_application_builder():
    route = read_ai_route()

    assert "build_summarization_application" in route


def test_m7_6_preserves_product_model_resolution():
    route = read_ai_route()

    assert "build_product_model_catalogue" in route

    assert "catalogue.resolve(" in route
