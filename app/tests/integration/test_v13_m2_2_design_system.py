"""V13 M2.2 frontend design-system contract tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_stylesheet() -> str:
    response = TestClient(app).get("/static/style.css")

    assert response.status_code == 200

    return response.text


def test_design_system_defines_semantic_color_tokens() -> None:
    stylesheet = get_stylesheet()

    assert "--color-background:" in stylesheet
    assert "--color-surface:" in stylesheet
    assert "--color-text:" in stylesheet
    assert "--color-text-muted:" in stylesheet
    assert "--color-border:" in stylesheet
    assert "--color-primary:" in stylesheet
    assert "--color-primary-hover:" in stylesheet
    assert "--color-error:" in stylesheet


def test_design_system_defines_typography_tokens() -> None:
    stylesheet = get_stylesheet()

    assert "--font-family-sans:" in stylesheet
    assert "--font-size-sm:" in stylesheet
    assert "--font-size-md:" in stylesheet
    assert "--font-size-xl:" in stylesheet
    assert "--font-weight-semibold:" in stylesheet
    assert "--line-height-body:" in stylesheet
    assert "--line-height-reading:" in stylesheet


def test_design_system_defines_spacing_tokens() -> None:
    stylesheet = get_stylesheet()

    assert "--space-1:" in stylesheet
    assert "--space-2:" in stylesheet
    assert "--space-4:" in stylesheet
    assert "--space-6:" in stylesheet
    assert "--space-8:" in stylesheet
    assert "--space-12:" in stylesheet
    assert "--space-16:" in stylesheet


def test_design_system_defines_shape_and_elevation_tokens() -> None:
    stylesheet = get_stylesheet()

    assert "--radius-sm:" in stylesheet
    assert "--radius-md:" in stylesheet
    assert "--radius-lg:" in stylesheet
    assert "--radius-pill:" in stylesheet
    assert "--shadow-sm:" in stylesheet
    assert "--shadow-card:" in stylesheet
    assert "--shadow-focus:" in stylesheet


def test_primary_button_uses_design_system_tokens() -> None:
    stylesheet = get_stylesheet()

    assert ".primary-button {" in stylesheet
    assert "background: var(--color-primary);" in stylesheet
    assert "color: var(--color-text-on-primary);" in stylesheet
    assert "border-radius: var(--radius-md);" in stylesheet


def test_textarea_uses_design_system_tokens() -> None:
    stylesheet = get_stylesheet()

    assert "textarea {" in stylesheet
    assert "border: 1px solid var(--color-border-strong);" in stylesheet
    assert "background: var(--color-surface);" in stylesheet
    assert "color: var(--color-text);" in stylesheet
    assert "box-shadow: var(--shadow-sm);" in stylesheet


def test_design_system_defines_visible_focus_states() -> None:
    stylesheet = get_stylesheet()

    assert ".brand:focus-visible" in stylesheet
    assert ".primary-button:focus-visible" in stylesheet
    assert "textarea:focus-visible" in stylesheet
    assert "var(--shadow-focus)" in stylesheet


def test_design_system_defines_status_semantics() -> None:
    stylesheet = get_stylesheet()

    assert ".status-message" in stylesheet
    assert ".error-message" in stylesheet
    assert "var(--color-info-subtle)" in stylesheet
    assert "var(--color-error-subtle)" in stylesheet


def test_design_system_preserves_responsive_layout() -> None:
    stylesheet = get_stylesheet()

    assert "@media (max-width: 820px)" in stylesheet
    assert "@media (max-width: 520px)" in stylesheet
    assert "grid-template-columns: 1fr;" in stylesheet


def test_design_system_respects_reduced_motion() -> None:
    stylesheet = get_stylesheet()

    assert "@media (prefers-reduced-motion: reduce)" in stylesheet
    assert "transition-duration: 0.01ms !important;" in stylesheet
    assert "animation-duration: 0.01ms !important;" in stylesheet


def test_design_system_preserves_supported_container_contract() -> None:
    stylesheet = get_stylesheet()

    assert ".container {" in stylesheet
    assert "--content-width:" in stylesheet
