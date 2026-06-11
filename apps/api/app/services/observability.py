import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Optional OpenTelemetry Integration
tracer = None
try:
    if settings.dynatrace_enabled or settings.observability_provider == "dynatrace":
        from opentelemetry import trace
        # Only initialize if explicitly configured, otherwise leave tracer=None
        if settings.otel_exporter_otlp_endpoint:
            tracer = trace.get_tracer(settings.otel_service_name)
except ImportError:
    pass
except Exception as e:
    logger.warning(f"Failed to initialize OpenTelemetry: {e}")

def _start_span(name: str, attributes: dict) -> Any:
    """Helper to start an OTel span if configured."""
    if tracer:
        try:
            span = tracer.start_span(name)
            span.set_attributes(attributes)
            return span
        except Exception:
            return None
    return None

def trace_agent_run_started(run_id: str, mode: str):
    if not settings.observability_enabled:
        return
    try:
        span = _start_span("careops.agent_run", {"run_id": run_id, "mode": mode, "status": "started"})
        if span:
            span.end()
        
        if settings.arize_enabled or settings.observability_provider == "arize":
            logger.info(f"[ARIZE_HOOK] run_started - run_id={run_id}, mode={mode}")
            
        if settings.dynatrace_enabled and not tracer:
            logger.info(f"[DYNATRACE_HOOK] (Local) run_started - run_id={run_id}, mode={mode}")
    except Exception as e:
        logger.warning(f"Observability hook failed: {e}")

def trace_model_attempt(run_id: str, model: str, status: str, latency_ms: int, error_type: Optional[str] = None):
    if not settings.observability_enabled:
        return
    try:
        attrs = {"run_id": run_id, "model": model, "status": status, "latency_ms": latency_ms}
        if error_type:
            attrs["error_type"] = error_type
            
        span = _start_span("careops.model_attempt", attrs)
        if span:
            span.end()
            
        if settings.arize_enabled or settings.observability_provider == "arize":
            logger.info(f"[ARIZE_HOOK] model_attempt - run_id={run_id}, model={model}, status={status}, latency={latency_ms}ms, error_type={error_type}")
            
        if settings.dynatrace_enabled and not tracer:
            logger.info(f"[DYNATRACE_HOOK] (Local) model_attempt - run_id={run_id}, model={model}, status={status}, latency={latency_ms}ms")
    except Exception as e:
        logger.warning(f"Observability hook failed: {e}")

def trace_safety_result(run_id: str, safety_status: str, blocked_count: int):
    if not settings.observability_enabled:
        return
    try:
        span = _start_span("careops.safety_verifier", {"run_id": run_id, "safety_status": safety_status, "blocked_count": blocked_count})
        if span:
            span.end()
            
        if settings.arize_enabled or settings.observability_provider == "arize":
            logger.info(f"[ARIZE_HOOK] safety_result - run_id={run_id}, status={safety_status}, blocked_count={blocked_count}")
    except Exception as e:
        logger.warning(f"Observability hook failed: {e}")

def trace_mcp_tool_call(run_id: str, tool_name: str, status: str, latency_ms: int):
    if not settings.observability_enabled:
        return
    try:
        span = _start_span("careops.mcp_tool_call", {"run_id": run_id, "tool_name": tool_name, "tool_status": status, "latency_ms": latency_ms})
        if span:
            span.end()
            
        if settings.arize_enabled or settings.observability_provider == "arize":
            logger.info(f"[ARIZE_HOOK] mcp_tool_call - run_id={run_id}, tool_name={tool_name}, status={status}, latency={latency_ms}ms")
    except Exception as e:
        logger.warning(f"Observability hook failed: {e}")

def trace_agent_run_completed(run_id: str, status: str):
    if not settings.observability_enabled:
        return
    try:
        span = _start_span("careops.agent_run_completed", {"run_id": run_id, "status": status})
        if span:
            span.end()
            
        if settings.arize_enabled or settings.observability_provider == "arize":
            logger.info(f"[ARIZE_HOOK] run_completed - run_id={run_id}, status={status}")
    except Exception as e:
        logger.warning(f"Observability hook failed: {e}")

def trace_degraded_mode_used(run_id: str):
    if not settings.observability_enabled:
        return
    try:
        span = _start_span("careops.degraded_mode", {"run_id": run_id})
        if span:
            span.end()
            
        if settings.arize_enabled or settings.observability_provider == "arize":
            logger.info(f"[ARIZE_HOOK] degraded_mode_used - run_id={run_id}")
    except Exception as e:
        logger.warning(f"Observability hook failed: {e}")
