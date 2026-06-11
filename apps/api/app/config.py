from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    project_name: str = "MyuKura CareOps API"
    phase: str = "0"
    
    cors_allowed_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]
    
    # Phase 2 Config
    app_env: str = "local"
    runtime: str = "local"
    demo_access_code: Optional[str] = None
    demo_access_required: bool = True
    max_source_note_chars: int = 6000
    demo_synthetic_data_only: bool = True
    allow_real_patient_data: bool = False
    log_source_note_content: bool = False
    trace_source_note_content: bool = False
    state_backend: str = "memory"
    mongodb_uri: str = "PHASE_2_PLACEHOLDER"
    mongodb_database: str = "myukura_careops_demo"
    mongodb_connect_timeout_ms: int = 5000
    mongodb_app_name: str = "myukura-careops-memory-agent"
    demo_mode: bool = True
    
    # Gemini
    gemini_enabled: bool = False
    gemini_provider: str = "developer_api"
    gemini_api_key: str = "PHASE_3_PLACEHOLDER"
    gemini_primary_model: str = "GEMINI_MODEL_NOT_CONFIGURED"
    gemini_fallback_models: str = ""
    gemini_request_timeout_seconds: int = 20
    gemini_max_model_attempts: int = 3
    gemini_timeout_seconds: int = 30
    gemini_max_retries: int = 2
    google_cloud_project: str = "PHASE_3_PLACEHOLDER"
    google_cloud_location: str = "us-central1"
    
    # Observability
    observability_enabled: bool = False
    observability_provider: str = "none"

    # Dynatrace / OpenTelemetry
    dynatrace_enabled: bool = False
    otel_service_name: str = "myukura-careops-memory-agent"
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_exporter_otlp_headers: Optional[str] = None
    otel_resource_attributes: str = "deployment.environment=local-demo,service.namespace=myukura"
    
    # Arize / Phoenix Optional
    arize_enabled: bool = False
    arize_project_name: str = "myukura-careops-memory-agent"
    arize_api_key: Optional[str] = None
    arize_space_id: Optional[str] = None
    phoenix_collector_endpoint: Optional[str] = None
    
    # Partner Outbox & Exporters
    partner_outbox_enabled: bool = True
    partner_max_attempts: int = 3
    partner_export_timeout_seconds: int = 10
    
    arize_export_enabled: bool = False
    arize_mcp_enabled: bool = False
    arize_endpoint: Optional[str] = None
    
    elastic_export_enabled: bool = False
    elastic_mcp_enabled: bool = False
    elastic_endpoint: Optional[str] = None
    elastic_api_key: Optional[str] = None
    elastic_index: str = "myukura-careops-audit"

    # Official MongoDB MCP Server (read-only memory reads)
    mongodb_mcp_enabled: bool = False
    mongodb_mcp_command: str = "npx"
    mongodb_mcp_args: str = "-y,mongodb-mcp-server@latest,--readOnly"
    mongodb_mcp_startup_timeout_seconds: int = 20
    mongodb_mcp_call_timeout_seconds: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
