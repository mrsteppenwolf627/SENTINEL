"""Tests for LLMAnalyzer fallback behavior.

These tests do NOT call the real Anthropic API.
They verify that when _call_llm raises an exception, LLMAnalyzer
transparently delegates to the fallback analyzer.
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.modules.analysis.llm_analyzer import LLMAnalyzer
from app.core.entities import Alert, AlertSeverity, Diagnosis, ActionType, EnrichedContext


def _make_context(message: str = "Test alert") -> EnrichedContext:
    alert = Alert(
        source="test-server",
        severity=AlertSeverity.WARNING,
        message=message,
    )
    return EnrichedContext(alert=alert)


def _make_diagnosis(alert_id: str) -> Diagnosis:
    return Diagnosis(
        alert_id=alert_id,
        root_cause="Fallback: Memory leak detected",
        confidence=1.0,
        suggested_actions=[ActionType.RESTART_SERVICE],
        reasoning_trace="Rule matched: memory in message",
    )


@pytest.mark.asyncio
async def test_llm_analyzer_falls_back_on_api_error():
    """When _call_llm raises an exception, the fallback analyzer result is returned."""
    context = _make_context()
    expected = _make_diagnosis(context.alert.id)

    fallback = AsyncMock()
    fallback.analyze.return_value = expected

    analyzer = LLMAnalyzer(
        api_key="test-key-not-real",
        model="claude-sonnet-4-6",
        fallback_analyzer=fallback,
    )

    with patch.object(analyzer, "_call_llm", side_effect=Exception("API timeout")):
        result = await analyzer.analyze(context)

    assert result == expected
    fallback.analyze.assert_awaited_once_with(context)


@pytest.mark.asyncio
async def test_llm_analyzer_falls_back_on_validation_error():
    """When _call_llm raises a validation error (bad LLM output), fallback is used."""
    context = _make_context("Database connection refused")
    expected = _make_diagnosis(context.alert.id)

    fallback = AsyncMock()
    fallback.analyze.return_value = expected

    analyzer = LLMAnalyzer(
        api_key="test-key-not-real",
        model="claude-sonnet-4-6",
        fallback_analyzer=fallback,
    )

    with patch.object(analyzer, "_call_llm", side_effect=ValueError("Invalid JSON from LLM")):
        result = await analyzer.analyze(context)

    assert result.root_cause == "Fallback: Memory leak detected"
    fallback.analyze.assert_awaited_once_with(context)
