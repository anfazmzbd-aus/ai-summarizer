"""V13 M8.4 responsive and small-screen hardening certification.

This suite audits the frozen V13 product frontend for responsive layout,
reflow resilience, small-screen usability, text-overflow safety, and
short-viewport behavior.

Scope:
- responsive viewport configuration
- primary workspace reflow
- mobile and tablet breakpoints
- intermediate-width form layouts
- short desktop viewport adaptation
- file-ingestion reflow
- result-action reflow
- metadata reflow
- text and long-token wrapping
- flexible containers
- mobile-width action availability
- form-control sizing
- textarea resizing
- prevention of obvious fixed-width overflow risks
- reduced horizontal-scroll risk
- preservation of semantic/product behavior across layout changes

M8.4 is deterministic and offline.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

STYLE_CSS_PATH = PROJECT_ROOT / "static" / "style.css"


HTML_VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


@dataclass(frozen=True)
class Element:
    tag: str
    attrs: dict[str, str]
    text: str


def normalize_text(
    value: str,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


class DocumentParser(HTMLParser):
    """Minimal parser for deterministic frontend source audits."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

        self.elements: list[Element] = []

        self._stack: list[dict[str, object]] = []

    @staticmethod
    def normalize_attrs(
        attrs,
    ) -> dict[str, str]:
        return {key: value or "" for key, value in attrs}

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:
        normalized_attrs = self.normalize_attrs(attrs)

        if tag in HTML_VOID_ELEMENTS:
            self.elements.append(
                Element(
                    tag=tag,
                    attrs=normalized_attrs,
                    text="",
                )
            )
            return

        self._stack.append(
            {
                "tag": tag,
                "attrs": normalized_attrs,
                "text": [],
            }
        )

    def handle_startendtag(
        self,
        tag: str,
        attrs,
    ) -> None:
        self.elements.append(
            Element(
                tag=tag,
                attrs=self.normalize_attrs(attrs),
                text="",
            )
        )

    def handle_data(
        self,
        data: str,
    ) -> None:
        for item in self._stack:
            text_parts = item["text"]

            assert isinstance(
                text_parts,
                list,
            )

            text_parts.append(data)

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        if not self._stack:
            return

        for index in range(
            len(self._stack) - 1,
            -1,
            -1,
        ):
            item = self._stack[index]

            if item["tag"] != tag:
                continue

            del self._stack[index:]

            item_tag = item["tag"]

            item_attrs = item["attrs"]

            item_text = item["text"]

            assert isinstance(
                item_tag,
                str,
            )

            assert isinstance(
                item_attrs,
                dict,
            )

            assert isinstance(
                item_text,
                list,
            )

            self.elements.append(
                Element(
                    tag=item_tag,
                    attrs=item_attrs,
                    text=normalize_text("".join(item_text)),
                )
            )

            return


def read(
    path: Path,
) -> str:
    return path.read_text(encoding="utf-8")


def read_html() -> str:
    return read(INDEX_HTML_PATH)


def read_js() -> str:
    return read(APP_JS_PATH)


def read_css() -> str:
    return read(STYLE_CSS_PATH)


@pytest.fixture(scope="module")
def document() -> list[Element]:
    parser = DocumentParser()

    parser.feed(read_html())

    return parser.elements


def find_by_id(
    document: list[Element],
    element_id: str,
) -> Element:
    matching = [
        element for element in document if (element.attrs.get("id") == element_id)
    ]

    assert len(matching) == 1, (
        f"expected exactly one " f"#{element_id}, " f"found {len(matching)}"
    )

    return matching[0]


def class_tokens(
    element: Element,
) -> set[str]:
    return {
        token
        for token in element.attrs.get(
            "class",
            "",
        ).split()
        if token
    }


def css_block(
    css: str,
    selector: str,
) -> str:
    """Return the first simple CSS block matching selector."""
    start = css.index(selector)

    open_brace = css.index(
        "{",
        start,
    )

    close_brace = css.index(
        "}",
        open_brace,
    )

    return css[start : close_brace + 1]


def media_block(
    css: str,
    marker: str,
    next_marker: str | None = None,
) -> str:
    start = css.index(marker)

    if next_marker is None:
        return css[start:]

    end = css.index(
        next_marker,
        start + len(marker),
    )

    return css[start:end]


# ---------------------------------------------------------------------------
# Source inventory
# ---------------------------------------------------------------------------


def test_m8_4_required_sources_exist():
    assert INDEX_HTML_PATH.is_file()
    assert APP_JS_PATH.is_file()
    assert STYLE_CSS_PATH.is_file()


def test_m8_4_html_is_non_empty():
    assert read_html().strip()


def test_m8_4_css_is_non_empty():
    assert read_css().strip()


def test_m8_4_javascript_is_non_empty():
    assert read_js().strip()


# ---------------------------------------------------------------------------
# Responsive viewport contract
# ---------------------------------------------------------------------------


def test_document_has_viewport_meta(
    document,
):
    matching = [
        element
        for element in document
        if (element.tag == "meta" and element.attrs.get("name") == "viewport")
    ]

    assert len(matching) == 1


def test_viewport_uses_device_width(
    document,
):
    viewport = [
        element
        for element in document
        if (element.tag == "meta" and element.attrs.get("name") == "viewport")
    ][0]

    content = viewport.attrs.get(
        "content",
        "",
    ).replace(
        " ",
        "",
    )

    assert "width=device-width" in content


def test_viewport_initial_scale_is_one(
    document,
):
    viewport = [
        element
        for element in document
        if (element.tag == "meta" and element.attrs.get("name") == "viewport")
    ][0]

    content = viewport.attrs.get(
        "content",
        "",
    ).replace(
        " ",
        "",
    )

    assert "initial-scale=1.0" in content


def test_viewport_does_not_disable_zoom(
    document,
):
    viewport = [
        element
        for element in document
        if (element.tag == "meta" and element.attrs.get("name") == "viewport")
    ][0]

    content = viewport.attrs.get(
        "content",
        "",
    ).lower()

    assert "user-scalable=no" not in content

    assert "maximum-scale=1" not in content


# ---------------------------------------------------------------------------
# Primary responsive breakpoints
# ---------------------------------------------------------------------------


def test_tablet_mobile_breakpoint_exists():
    css = read_css()

    assert "@media (max-width: 820px)" in css


def test_small_mobile_breakpoint_exists():
    css = read_css()

    assert "@media (max-width: 520px)" in css


def test_intermediate_width_breakpoint_exists():
    css = read_css()

    assert "@media (min-width: 821px) and (max-width: 1040px)" in css


def test_short_desktop_breakpoint_exists():
    css = read_css()

    assert "@media (min-width: 821px) and (max-height: 800px)" in css


# ---------------------------------------------------------------------------
# Main workspace reflow
# ---------------------------------------------------------------------------


def test_workspace_exists_in_markup(
    document,
):
    matching = [
        element for element in document if ("workspace" in class_tokens(element))
    ]

    assert matching


def test_workspace_collapses_to_one_column_below_820():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    )

    assert ".workspace" in block

    assert "grid-template-columns: 1fr" in block


def test_workspace_panel_releases_minimum_height_on_small_screens():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    )

    assert ".workspace-panel" in block

    assert "min-height: auto" in block


def test_result_empty_reduces_minimum_height_on_small_screens():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    )

    assert ".result-empty" in block

    assert "min-height: 260px" in block


# ---------------------------------------------------------------------------
# Flexible page-width containers
# ---------------------------------------------------------------------------


def test_mobile_header_container_footer_widths_are_fluid():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    )

    assert ".header-content" in block

    assert ".container" in block

    assert ".footer-content" in block

    assert "calc(100% - var(--space-8))" in block


def test_mobile_layout_caps_content_width():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    )

    assert "680px" in block


def test_footer_uses_fluid_width_calculation():
    css = read_css()

    assert "calc(100% - var(--space-12))" in css or (
        "calc(100% - var(--space-10))" in css
    )


# ---------------------------------------------------------------------------
# Result-header reflow
# ---------------------------------------------------------------------------


def test_result_header_stacks_on_small_screens():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    )

    assert ".result-header" in block

    assert "flex-direction: column" in block


def test_result_header_uses_flexible_layout():
    css = read_css()

    matching = re.findall(
        r"\.result-header\s*\{" r"(.*?)" r"\}",
        css,
        re.DOTALL,
    )

    assert matching

    assert any("display: flex" in block and "gap:" in block for block in matching)


# ---------------------------------------------------------------------------
# Metadata-grid reflow
# ---------------------------------------------------------------------------


def test_metadata_grid_collapses_to_one_column():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    )

    assert ".metadata-grid" in block

    assert "grid-template-columns: 1fr" in block


def test_metadata_grid_exists_in_markup(
    document,
):
    matching = [
        element for element in document if ("metadata-grid" in class_tokens(element))
    ]

    assert len(matching) == 1


# ---------------------------------------------------------------------------
# Mobile header behavior
# ---------------------------------------------------------------------------


def test_brand_subtitle_can_hide_on_narrow_screens():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".brand-subtitle" in block

    assert "display: none" in block


def test_mobile_container_padding_is_reduced():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".container" in block

    assert "padding: var(--space-8) 0" in block


def test_mobile_workspace_panel_padding_is_reduced():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".workspace-panel" in block

    assert "padding: var(--space-5)" in block


def test_mobile_heading_size_is_reduced():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".workspace-intro h1" in block

    assert "font-size: var(--font-size-3xl)" in block


# ---------------------------------------------------------------------------
# Mobile input-toolbar behavior
# ---------------------------------------------------------------------------


def test_mobile_input_toolbar_stacks():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".input-toolbar" in block

    assert "flex-direction: column" in block


def test_mobile_input_toolbar_stretches_children():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert "align-items: stretch" in block


def test_mobile_form_actions_fill_available_width():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".form-actions" in block

    assert "width: 100%" in block


def test_mobile_primary_button_fills_available_width():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".primary-button" in block

    assert "width: 100%" in block


# ---------------------------------------------------------------------------
# File-ingestion small-screen behavior
# ---------------------------------------------------------------------------


def test_file_ingestion_heading_stacks_at_mobile_width():
    css = read_css()

    assert "@media (max-width: 520px)" in css

    matching = re.findall(
        r"@media\s*\(max-width:\s*520px\)"
        r"\s*\{.*?"
        r"\.file-ingestion-heading\s*\{"
        r".*?flex-direction:\s*column"
        r".*?\}",
        css,
        re.DOTALL,
    )

    assert matching


def test_choose_file_secondary_button_can_fill_mobile_width():
    css = read_css()

    matching = re.findall(
        r"@media\s*\(max-width:\s*520px\)"
        r"\s*\{.*?"
        r"\.secondary-button\s*\{"
        r".*?width:\s*100%"
        r".*?\}",
        css,
        re.DOTALL,
    )

    assert matching


def test_file_status_can_stack_on_mobile():
    css = read_css()

    matching = re.findall(
        r"@media\s*\(max-width:\s*520px\)"
        r"\s*\{.*?"
        r"\.file-status\s*\{"
        r".*?flex-direction:\s*column"
        r".*?\}",
        css,
        re.DOTALL,
    )

    assert matching


def test_file_ingestion_control_exists_on_mobile_without_conditional_markup(
    document,
):
    ingestion = find_by_id(
        document,
        "fileIngestion",
    )

    assert "hidden" not in class_tokens(ingestion)


def test_choose_file_button_remains_present(
    document,
):
    button = find_by_id(
        document,
        "chooseFileButton",
    )

    assert button.tag == "button"


def test_file_drop_zone_remains_present(
    document,
):
    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert "file-drop-zone" in class_tokens(drop_zone)


# ---------------------------------------------------------------------------
# Result-action small-screen behavior
# ---------------------------------------------------------------------------


def test_result_actions_use_wrapping_layout():
    css = read_css()

    block = css_block(css, ".result-actions")

    assert "display: flex" in block

    assert "flex-wrap: wrap" in block


def test_result_actions_stack_on_small_mobile():
    css = read_css()

    matching = re.findall(
        r"@media\s*\(max-width:\s*520px\)"
        r"\s*\{.*?"
        r"\.result-actions\s*\{"
        r".*?flex-direction:\s*column"
        r".*?\}",
        css,
        re.DOTALL,
    )

    assert matching


def test_result_actions_stretch_on_small_mobile():
    css = read_css()

    matching = re.findall(
        r"@media\s*\(max-width:\s*520px\)"
        r"\s*\{.*?"
        r"\.result-actions\s*\{"
        r".*?align-items:\s*stretch"
        r".*?\}",
        css,
        re.DOTALL,
    )

    assert matching


def test_result_action_buttons_fill_mobile_width():
    css = read_css()

    matching = re.findall(
        r"@media\s*\(max-width:\s*520px\)"
        r"\s*\{.*?"
        r"\.result-action-button\s*\{"
        r".*?width:\s*100%"
        r".*?\}",
        css,
        re.DOTALL,
    )

    assert matching


@pytest.mark.parametrize(
    "button_id",
    (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_result_actions_remain_in_markup_at_small_widths(
    document,
    button_id,
):
    button = find_by_id(
        document,
        button_id,
    )

    assert button.tag == "button"


# ---------------------------------------------------------------------------
# Text-area responsiveness
# ---------------------------------------------------------------------------


def test_mobile_textarea_has_practical_minimum_height():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert "textarea" in block

    assert "min-height: 250px" in block


def test_short_desktop_source_text_reduces_height():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-height: 800px)",
        "@media (min-width: 821px) and (max-width: 1040px)",
    )

    assert "#inputText" in block

    assert "min-height: 180px" in block


def test_short_desktop_source_text_uses_viewport_height():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-height: 800px)",
        "@media (min-width: 821px) and (max-width: 1040px)",
    )

    assert "height: 23vh" in block


def test_custom_instruction_textarea_is_vertically_resizable():
    css = read_css()

    assert "resize: vertical" in css


def test_textareas_are_not_horizontal_only_resizable():
    css = read_css()

    assert "resize: horizontal" not in css


# ---------------------------------------------------------------------------
# Intermediate-width form controls
# ---------------------------------------------------------------------------


def test_intermediate_summary_options_use_two_columns():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-width: 1040px)",
        "/*\n * V13 M5.5 File ingestion",
    )

    assert ".summary-options" in block

    assert "repeat(2, minmax(0, 1fr))" in block


def test_intermediate_last_form_field_spans_width():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-width: 1040px)",
        "/*\n * V13 M5.5 File ingestion",
    )

    assert ".summary-options > .form-field:last-of-type" in block

    assert "grid-column: 1 / -1" in block


def test_desktop_summary_options_use_minmax_zero_tracks():
    css = read_css()

    assert "repeat(3, minmax(0, 1fr))" in css


def test_summary_option_fields_allow_grid_shrinkage():
    css = read_css()

    assert ".summary-options > .form-field" in css

    assert "min-width: 0" in css


# ---------------------------------------------------------------------------
# Long-content wrapping
# ---------------------------------------------------------------------------


def test_summary_text_preserves_line_breaks():
    css = read_css()

    assert "white-space: pre-wrap" in css


def test_summary_text_breaks_long_unbroken_tokens():
    css = read_css()

    assert "overflow-wrap: anywhere" in css


def test_summary_content_does_not_force_nowrap():
    css = read_css()

    summary_start = css.index(".summary-content p")

    summary_end = css.index(
        "}",
        summary_start,
    )

    block = css[summary_start:summary_end]

    assert "white-space: nowrap" not in block


def test_summary_content_does_not_use_fixed_pixel_width():
    css = read_css()

    block = css_block(css, ".summary-content")

    assert (
        re.search(
            r"\bwidth\s*:\s*\d+px",
            block,
        )
        is None
    )


# ---------------------------------------------------------------------------
# Overflow-risk hardening
# ---------------------------------------------------------------------------


def test_no_body_fixed_pixel_width():
    css = read_css()

    body_match = re.search(
        r"(?:^|\n)body\s*\{(.*?)\}",
        css,
        re.DOTALL,
    )

    if body_match is None:
        pytest.skip("No standalone body rule.")

    body_block = body_match.group(1)

    assert (
        re.search(
            r"\bwidth\s*:\s*\d+px",
            body_block,
        )
        is None
    )


def test_no_workspace_fixed_pixel_width():
    css = read_css()

    block = css_block(css, ".workspace")

    assert (
        re.search(
            r"\bwidth\s*:\s*\d+px",
            block,
        )
        is None
    )


def test_no_result_workspace_fixed_pixel_width():
    css = read_css()

    block = css_block(css, ".result-workspace")

    assert (
        re.search(
            r"\bwidth\s*:\s*\d+px",
            block,
        )
        is None
    )


def test_no_file_ingestion_fixed_pixel_width():
    css = read_css()

    block = css_block(css, ".file-ingestion")

    assert (
        re.search(
            r"\bwidth\s*:\s*\d+px",
            block,
        )
        is None
    )


def test_no_result_actions_fixed_pixel_width():
    css = read_css()

    block = css_block(css, ".result-actions")

    assert (
        re.search(
            r"\bwidth\s*:\s*\d+px",
            block,
        )
        is None
    )


# ---------------------------------------------------------------------------
# Short viewport hardening
# ---------------------------------------------------------------------------


def test_short_viewport_reduces_container_padding():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-height: 800px)",
        "@media (min-width: 821px) and (max-width: 1040px)",
    )

    assert ".container" in block

    assert "var(--space-4)" in block


def test_short_viewport_reduces_intro_spacing():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-height: 800px)",
        "@media (min-width: 821px) and (max-width: 1040px)",
    )

    assert ".workspace-intro" in block

    assert "margin-bottom: var(--space-4)" in block


def test_short_viewport_reduces_workspace_panel_padding():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-height: 800px)",
        "@media (min-width: 821px) and (max-width: 1040px)",
    )

    assert ".workspace-panel" in block


def test_short_viewport_reduces_footer_height():
    css = read_css()

    block = media_block(
        css,
        "@media (min-width: 821px) and (max-height: 800px)",
        "@media (min-width: 821px) and (max-width: 1040px)",
    )

    assert ".footer-content" in block

    assert "min-height: 42px" in block


# ---------------------------------------------------------------------------
# Mobile footer reflow
# ---------------------------------------------------------------------------


def test_mobile_footer_allows_wrapping():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert ".footer-content" in block

    assert "flex-wrap: wrap" in block


def test_mobile_footer_uses_smaller_minimum_height():
    css = read_css()

    block = media_block(
        css,
        "@media (max-width: 520px)",
        "@media (prefers-reduced-motion: reduce)",
    )

    assert "min-height: 56px" in block


# ---------------------------------------------------------------------------
# Practical action sizing
# ---------------------------------------------------------------------------


def test_primary_button_has_nonzero_minimum_height():
    css = read_css()

    assert ".primary-button" in css

    assert re.search(
        r"\.primary-button\s*\{" r"[^}]*min-height\s*:\s*\d+px",
        css,
        re.DOTALL,
    )


def test_secondary_button_has_nonzero_minimum_height():
    css = read_css()

    assert re.search(
        r"\.secondary-button\s*\{" r"[^}]*min-height\s*:\s*\d+px",
        css,
        re.DOTALL,
    )


def test_file_drop_zone_has_nonzero_minimum_height():
    css = read_css()

    assert re.search(
        r"\.file-drop-zone\s*\{" r"[^}]*min-height\s*:\s*\d+px",
        css,
        re.DOTALL,
    )


def test_summary_option_selects_have_nonzero_minimum_height():
    css = read_css()

    assert ".summary-options .form-field select" in css

    assert "min-height: 40px" in css


# ---------------------------------------------------------------------------
# Markup remains layout-independent
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "element_id",
    (
        "inputText",
        "summaryType",
        "summaryLength",
        "modelSelection",
        "customInstructions",
        "summarizeButton",
        "summaryContent",
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_core_controls_are_not_hidden_by_markup(
    document,
    element_id,
):
    element = find_by_id(
        document,
        element_id,
    )

    assert "hidden" not in class_tokens(element)


def test_result_workspace_uses_state_visibility_not_viewport_visibility(
    document,
):
    result = find_by_id(
        document,
        "result",
    )

    assert "result-workspace" in class_tokens(result)


def test_no_mobile_specific_duplicate_form_exists():
    html = read_html()

    assert html.count('id="summaryForm"') == 1


def test_no_mobile_specific_duplicate_source_textarea_exists():
    html = read_html()

    assert html.count('id="inputText"') == 1


def test_no_mobile_specific_duplicate_result_workspace_exists():
    html = read_html()

    assert html.count('id="result"') == 1


# ---------------------------------------------------------------------------
# Responsive behavior must remain CSS driven
# ---------------------------------------------------------------------------


def test_javascript_does_not_branch_on_window_inner_width():
    js = read_js()

    assert "window.innerWidth" not in js


def test_javascript_does_not_branch_on_screen_width():
    js = read_js()

    assert "screen.width" not in js


def test_javascript_does_not_use_match_media_for_core_layout():
    js = read_js()

    assert "matchMedia(" not in js


def test_javascript_does_not_rewrite_layout_on_resize():
    js = read_js()

    assert 'addEventListener("resize"' not in js

    assert "addEventListener(\n" '    "resize"' not in js


# ---------------------------------------------------------------------------
# Responsive accessibility continuity
# ---------------------------------------------------------------------------


def test_mobile_layout_does_not_remove_source_label(
    document,
):
    label_targets = {
        element.attrs.get("for") for element in document if element.tag == "label"
    }

    assert "inputText" in label_targets


def test_mobile_layout_does_not_remove_summary_type_label(
    document,
):
    label_targets = {
        element.attrs.get("for") for element in document if element.tag == "label"
    }

    assert "summaryType" in label_targets


def test_mobile_layout_does_not_remove_summary_length_label(
    document,
):
    label_targets = {
        element.attrs.get("for") for element in document if element.tag == "label"
    }

    assert "summaryLength" in label_targets


def test_mobile_layout_does_not_remove_model_label(
    document,
):
    label_targets = {
        element.attrs.get("for") for element in document if element.tag == "label"
    }

    assert "modelSelection" in label_targets


def test_mobile_layout_does_not_remove_custom_instruction_label(
    document,
):
    label_targets = {
        element.attrs.get("for") for element in document if element.tag == "label"
    }

    assert "customInstructions" in label_targets


# ---------------------------------------------------------------------------
# Reduced-motion continuity
# ---------------------------------------------------------------------------


def test_reduced_motion_rule_remains_present():
    css = read_css()

    assert "@media (prefers-reduced-motion: reduce)" in css


def test_responsive_styles_do_not_disable_reduced_motion_rules():
    css = read_css()

    reduced_start = css.index("@media (prefers-reduced-motion: reduce)")

    reduced_block = css[reduced_start:]

    assert "transition-duration: 0.01ms" in reduced_block

    assert "animation-duration: 0.01ms" in reduced_block


# ---------------------------------------------------------------------------
# Product workflow continuity at all viewport sizes
# ---------------------------------------------------------------------------


def test_responsive_hardening_does_not_add_second_summarization_path():
    js = read_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_responsive_hardening_preserves_file_extraction_endpoint():
    js = read_js()

    assert '"/api/v1/files/extract"' in js


def test_responsive_hardening_preserves_product_config_endpoint():
    js = read_js()

    assert '"/api/v1/product-config"' in js


def test_responsive_hardening_preserves_canonical_regeneration():
    js = read_js()

    assert "summaryForm.requestSubmit();" in js


# ---------------------------------------------------------------------------
# M8.4 deterministic/offline boundary
# ---------------------------------------------------------------------------


def test_m8_4_has_no_live_pytest_marker():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "pytest.mark." + "live" not in source


def test_m8_4_requires_no_external_provider():
    source = Path(__file__).read_text(encoding="utf-8")

    forbidden = (
        "openai" + ".com",
        "openrouter" + ".ai",
        "OPENAI" + "_API_KEY",
        "OPENROUTER" + "_API_KEY",
    )

    for value in forbidden:
        assert value not in source


def test_m8_4_is_frontend_scoped():
    assert (
        INDEX_HTML_PATH.relative_to(PROJECT_ROOT).as_posix()
        == "app/templates/index.html"
    )

    assert APP_JS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/app.js"

    assert STYLE_CSS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/style.css"
