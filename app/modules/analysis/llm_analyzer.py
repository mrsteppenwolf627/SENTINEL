"""
LLMAnalyzer: Root Cause Analysis powered by Claude via LangChain.

Uses langchain-anthropic with with_structured_output() for reliable Pydantic extraction.
Falls back to an injected IAnalysisModule (e.g. RuleBasedAnalyzer) on any error.
"""
from typing import List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from ...core.entities import ActionType, Diagnosis, EnrichedContext
from ...core.interfaces import IAnalysisModule
from ...core.logging import logger


class _LLMDiagnosisOutput(BaseModel):
    """Internal structured-output schema for the LLM response.

    Does NOT include alert_id (injected after the LLM call).
    All fields are required so the LLM must always provide them.
    """

    root_cause: str = Field(description="Primary identified root cause of the alert")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 (uncertain) to 1.0 (certain)",
    )
    alternative_hypotheses: List[str] = Field(
        description="List of alternative root cause hypotheses considered"
    )
    reasoning_trace: str = Field(
        description="Step-by-step chain-of-thought reasoning that led to the diagnosis"
    )
    suggested_actions: List[ActionType] = Field(
        description=(
            "Ordered list of remediation actions from: "
            "[RESTART_SERVICE, CLEAR_CACHE, SCALE_UP, BLOCK_IP, NOTIFICATION, MANUAL_INTERVENTION]"
        )
    )


_SYSTEM_PROMPT = (
    "You are SENTINEL, a Senior Site Reliability Engineer Agent. "
    "Your job is strict causal root-cause analysis — not probabilistic guessing. "
    "Always construct a causal chain of events and consider past remediation history "
    "before suggesting actions."
)


class LLMAnalyzer(IAnalysisModule):
    """LLM-powered RCA using Claude via LangChain with Pydantic structured output."""

    def __init__(
        self,
        api_key: str,
        model: str,
        fallback_analyzer: IAnalysisModule,
    ) -> None:
        self._llm = ChatAnthropic(model=model, api_key=api_key, max_tokens=1024)
        self._structured_llm = self._llm.with_structured_output(_LLMDiagnosisOutput)
        self._fallback = fallback_analyzer

    async def analyze(self, context: EnrichedContext) -> Diagnosis:
        """Analyze an enriched context. Falls back to rule engine on any error."""
        try:
            return await self._call_llm(context)
        except Exception as exc:
            logger.warning(
                "LLM analysis failed — falling back to rule engine",
                extra={"error": str(exc)[:200], "alert_id": context.alert.id},
            )
            return await self._fallback.analyze(context)

    async def _call_llm(self, context: EnrichedContext) -> Diagnosis:
        """Call the Claude API and return a structured Diagnosis."""
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=self._build_prompt(context)),
        ]
        llm_output: _LLMDiagnosisOutput = await self._structured_llm.ainvoke(messages)
        return Diagnosis(
            alert_id=context.alert.id,
            root_cause=llm_output.root_cause,
            confidence=llm_output.confidence,
            alternative_hypotheses=llm_output.alternative_hypotheses,
            reasoning_trace=llm_output.reasoning_trace,
            suggested_actions=llm_output.suggested_actions,
        )

    def _build_prompt(self, context: EnrichedContext) -> str:
        """Build the causal-RCA prompt from the enriched context."""
        recent_str = self._format_incidents(context.recent_similar_incidents)
        past_str = self._format_remediations(context.past_remediations_for_source)
        return (
            f"ALERT RECEIVED:\n"
            f"  Source:   {context.alert.source}\n"
            f"  Severity: {context.alert.severity}\n"
            f"  Message:  {context.alert.message}\n"
            f"  Metadata: {context.alert.metadata}\n\n"
            f"HISTORICAL CONTEXT:\n"
            f"  Recent similar incidents (last 24 h):\n{recent_str}\n\n"
            f"  Past executed remediations for this source:\n{past_str}\n\n"
            f"INSTRUCTIONS FOR CAUSAL ANALYSIS:\n"
            f"1. Construct a causal chain of events — do NOT rely on correlation alone.\n"
            f"2. Evaluate alternative hypotheses (e.g. memory leak vs. traffic spike vs. query loop).\n"
            f"3. If a past remediation (e.g. RESTART_SERVICE) was executed recently and the alert recurred, "
            f"do NOT suggest the same action — escalate or find the real root cause.\n"
            f"4. Provide a detailed reasoning_trace documenting your step-by-step logic.\n"
            f"5. Set confidence between 0.0 and 1.0 — keep it low if telemetry is insufficient.\n"
            f"6. Suggest actions only from: "
            f"[RESTART_SERVICE, CLEAR_CACHE, SCALE_UP, BLOCK_IP, NOTIFICATION, MANUAL_INTERVENTION]."
        )

    def _format_incidents(self, incidents: list) -> str:
        if not incidents:
            return "    None."
        return "\n".join(
            f"    - [{inc.status}] {inc.source}: {inc.message} (severity={inc.severity})"
            for inc in incidents
        )

    def _format_remediations(self, plans: list) -> str:
        if not plans:
            return "    None."
        return "\n".join(
            f"    - [{plan.status}] {plan.action_type}: {plan.diagnosis.root_cause}"
            for plan in plans
        )
