import time
from typing import Tuple, List, Optional
from app.config import settings
from app.models.extraction import ExtractionResult
from app.models.model_chain import ModelAttemptMetadata
from app.services import observability
import asyncio

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

async def execute_model_chain(prompt: str) -> Tuple[Optional[ExtractionResult], List[ModelAttemptMetadata]]:
    chain = []
    
    if not settings.gemini_enabled or not genai:
        chain.append(ModelAttemptMetadata(
            model=settings.gemini_primary_model,
            role="primary",
            status="disabled",
            latency_ms=0,
            error_type="GEMINI_DISABLED"
        ))
        return None, chain

    client = genai.Client(api_key=settings.gemini_api_key)
    
    models_to_try = [
        (settings.gemini_primary_model, "primary")
    ]
    
    if settings.gemini_fallback_model and settings.gemini_fallback_model != "PHASE_3_FALLBACK_MODEL_PLACEHOLDER":
        models_to_try.append((settings.gemini_fallback_model, "fallback"))
        
    models_to_try.append((settings.gemini_secondary_fallback_model, "fallback"))

    for model_id, role in models_to_try:
        start_time = time.time()
        try:
            # We use a simple wrap to make it async compatible or use client.aio if available.
            # Assuming client.aio.models.generate_content exists in google-genai 0.3.0
            # If not, we run in executor, but let's try the native aio.
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResult,
                temperature=0.1
            )
            
            # Using asyncio.to_thread as a safe fallback in case client.aio is not fully stable
            # in this exact version, but let's assume it is.
            if hasattr(client, "aio"):
                response = await client.aio.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=config
                )
            else:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model_id,
                    contents=prompt,
                    config=config
                )
            
            latency = int((time.time() - start_time) * 1000)
            
            if not response.parsed:
                chain.append(ModelAttemptMetadata(
                    model=model_id,
                    role=role,
                    status="invalid_json",
                    latency_ms=latency,
                    error_type="GEMINI_INVALID_JSON"
                ))
                observability.trace_model_attempt(
                    run_id="unknown_run",
                    model=model_id,
                    status="invalid_json",
                    latency_ms=latency,
                    error_type="GEMINI_INVALID_JSON"
                )
                continue
                
            chain.append(ModelAttemptMetadata(
                model=model_id,
                role=role,
                status="success",
                latency_ms=latency
            ))
            
            observability.trace_model_attempt(
                run_id="unknown_run",
                model=model_id,
                status="success",
                latency_ms=latency
            )
            
            return response.parsed, chain
            
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                status = "timeout"
                error_type = "GEMINI_TIMEOUT"
            else:
                status = "failed"
                error_type = "GEMINI_MODEL_ERROR"
                
            chain.append(ModelAttemptMetadata(
                model=model_id,
                role=role,
                status=status,
                latency_ms=latency,
                error_type=error_type
            ))
            observability.trace_model_attempt(
                run_id="unknown_run",
                model=model_id,
                status=status,
                latency_ms=latency,
                error_type=error_type
            )
            
    # If we get here, all models failed
    observability.trace_degraded_mode_used(run_id="unknown_run")
    return None, chain
