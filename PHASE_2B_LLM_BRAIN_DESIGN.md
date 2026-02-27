# SENTINEL Phase 2b: LLM Brain Design

This document details the transition from the `RuleBasedAnalyzer` to an `LLMAnalyzer` powered by the Claude API (`claude-sonnet-4-6`), focusing on true Causal Root Cause Analysis (RCA) while keeping execution deterministic and safe.

## 1. Evolved Domain Entities

To support LLM outputs and rich context, we need to update `app/core/entities.py`.

### Evolved `Diagnosis` Model
The `Diagnosis` model must capture the causal reasoning, alternative hypotheses, and strict confidence scores of the LLM.

```python
class Diagnosis(BaseModel):
    alert_id: str
    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0) # Enforce 0.0 to 1.0 bounding
    alternative_hypotheses: List[str] = Field(default_factory=list)
    reasoning_trace: str # Chain of thought, crucial for explainability/audit
    suggested_actions: List[ActionType]
```

### New `EnrichedContext` Model
```python
from typing import Optional, List
from pydantic import BaseModel
from .entities import Alert, Incident, RemediationPlan

class EnrichedContext(BaseModel):
    """Data object containing the original alert and historical DB context."""
    alert: Alert
    recent_similar_incidents: List[Incident] = Field(default_factory=list)
    past_remediations_for_source: List[RemediationPlan] = Field(default_factory=list)
    # Future placeholder: system_logs, metrics_snapshot
```

## 2. Evolved `IAnalysisModule` Contract

The `IAnalysisModule` must be updated in `app/core/interfaces.py` to accept the `EnrichedContext` instead of just the raw `Alert`.

```python
class IAnalysisModule(ABC):
    """Interface for RCA Analysis (e.g., Rule Engine, LLM)."""
    
    @abstractmethod
    async def analyze(self, context: EnrichedContext) -> Diagnosis:
        """Analyze an enriched context and produce a diagnosis."""
        pass
```

## 3. EnrichedContext Builder (PostgreSQL Queries)

Before calling `IAnalysisModule.analyze()`, an orchestration service (e.g., `ContextBuilderService`) must query PostgreSQL to populate the `EnrichedContext`.

**Required Queries (via standard Repositories):**

1.  **Recent Similar Incidents:**
    *   *Query:* Get incidents where `source` == `alert.source` OR `severity` == `alert.severity` within the last X hours.
    *   *Purpose:* Helps the LLM recognize if this is a flapping issue or part of a larger ongoing outage.
2.  **Past Remediations for Source:**
    *   *Query:* Get `remediation_plans` linked to incidents with `source` == `alert.source` where `status` == 'EXECUTED', ordered by created_at DESC (Limit 5).
    *   *Purpose:* Tells the LLM what actions were previously attempted to fix this specific service, preventing the LLM from suggesting a failed action in an infinite loop.

*⚠️ Architectural Decision for Validation:* We are currently defining similarity by exact match on `source` and date ranges. As we scale, we should transition this specific lookup to pgvector for semantic similarity matching of alert messages. For Phase 2b, exact match/SQL filters are acceptable.

## 4. LLMAnalyzer Class Design

The new `LLMAnalyzer` implements `IAnalysisModule`. It uses Anthropic's Claude API.

### Skeleton
```python
import instructor # Recommended for structured extraction
from anthropic import AsyncAnthropic

class LLMAnalyzer(IAnalysisModule):
    def __init__(self, api_key: str, fallback_analyzer: IAnalysisModule):
        self.client = instructor.from_anthropic(AsyncAnthropic(api_key=api_key))
        self.fallback = fallback_analyzer
        self.model = "claude-3-5-sonnet-20241022" # Note: Update to claude-3-7-sonnet if available

    async def analyze(self, context: EnrichedContext) -> Diagnosis:
        try:
            return await self._call_llm(context)
        except Exception as e:
            # Log error properly
            return await self.fallback.analyze(context)
            
    async def _call_llm(self, context: EnrichedContext) -> Diagnosis:
        prompt = self._build_prompt(context)
        
        # Uses instructor to force Claude to return data matching the Diagnosis Pydantic model
        diagnosis = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="You are SENTINEL, a Senior SRE Agent. Provide strict causal analysis, not probabilistic guessing.",
            messages=[{"role": "user", "content": prompt}],
            response_model=Diagnosis
        )
        return diagnosis
```

### Prompt Structure (Causal RCA)
The internal `_build_prompt` method should construct a prompt focused on causation.

```text
ALERT DEPLOYED:
Source: {context.alert.source}
Severity: {context.alert.severity}
Message: {context.alert.message}
Metadata: {context.alert.metadata}

HISTORICAL CONTEXT:
Recent similar incidents: {formatted_recent_incidents}
Past executed remediations for this source: {formatted_past_remediations}

INSTRUCTIONS FOR CAUSAL ANALYSIS:
1. Do not rely on probabilistic correlation. Construct a causal chain of events that leads to the observed alert.
2. Evaluate alternative hypotheses. If CPU is high, is it a memory leak causing GC thrashing, a sudden burst of legitimate traffic, or a looping unoptimized query?
3. Review 'Past executed remediations'. If 'RESTART_SERVICE' was executed an hour ago and the alert is back, do NOT suggest 'RESTART_SERVICE' again. You must escalate or find the real root cause.
4. Provide a 'reasoning_trace' documenting your step-by-step logic.
5. Provide a confidence score between 0.0 and 1.0. If you lack telemetry to be certain, keep the confidence low.
6. Suggest ActionTypes from the allowed list: [RESTART_SERVICE, CLEAR_CACHE, SCALE_UP, BLOCK_IP, NOTIFICATION, MANUAL_INTERVENTION].
```

## 5. Graceful Handling & Fallback

As shown in the skeleton above, `LLMAnalyzer` receives the `RuleBasedAnalyzer` in its constructor via Dependency Injection.

If the Anthropic API drops, times out, or returns severely hallucinated/unparseable JSON (which `instructor` catches via validation errors), the `except Exception` block catches the failure, logs the AI degradation, and seamlessly calls `await self.fallback.analyze(context)`. 

*⚠️ Architectural Decision for Validation:* The fallback analyzer currently only takes `Alert`. If `IAnalysisModule` changes to `EnrichedContext`, the `RuleBasedAnalyzer` must be updated to accept `EnrichedContext` (even if it just ignores the extra DB context and only looks at `context.alert`).

## 6. Updated Incident Lifecycle

With an LLM taking potentially 5-15 seconds to reason, the `status` of an `Incident` in PostgreSQL becomes critical for concurrency safety.

1. **Webhook Receive:** Wait for Alert.
2. **Phase 1 [OPEN]:** Incident is created in DB with status `OPEN`.
3. **Phase 2 [ANALYZING]:** 
    * The Orchestrator sets the Incident DB status to `ANALYZING`.
    * *Purpose:* If another identical alert webhook fires while Claude is thinking, the system queries the DB and sees `ANALYZING`. It groups the new alert under the existing Incident rather than spawning parallel LLM requests.
4. **Phase 3 [MITIGATING]:** LLM returns `Diagnosis`. Policy Engine returns `RemediationPlan`. Status changes to `MITIGATING` while the action is executing or awaiting human approval.
5. **Phase 4 [CLOSED]:** Action completes (success or manual close).
