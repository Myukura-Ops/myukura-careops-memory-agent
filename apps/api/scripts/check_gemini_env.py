import os
import sys

def check_env():
    print("--- Gemini Env Check ---")
    
    # 1. Check GEMINI_ENABLED
    gemini_enabled_raw = os.environ.get("GEMINI_ENABLED", "false").lower()
    gemini_enabled = gemini_enabled_raw == "true"
    print(f"GEMINI_ENABLED: {gemini_enabled}")
    
    # 2. Check GEMINI_API_KEY presence
    api_key = os.environ.get("GEMINI_API_KEY", "")
    key_present = bool(api_key and "NOT_CONFIGURED" not in api_key and len(api_key) > 5)
    print(f"GEMINI_API_KEY present and looks valid: {key_present}")
    
    # 3. Print configured models
    primary_model = os.environ.get("GEMINI_PRIMARY_MODEL", "GEMINI_MODEL_NOT_CONFIGURED")
    print(f"GEMINI_PRIMARY_MODEL: {primary_model}")
    
    fallback_models = os.environ.get("GEMINI_FALLBACK_MODELS", "")
    print(f"GEMINI_FALLBACK_MODELS: {fallback_models}")
    
    # 4. Print max attempts and timeout
    max_attempts = os.environ.get("GEMINI_MAX_MODEL_ATTEMPTS", "3")
    print(f"GEMINI_MAX_MODEL_ATTEMPTS: {max_attempts}")
    
    timeout = os.environ.get("GEMINI_REQUEST_TIMEOUT_SECONDS", "20")
    print(f"GEMINI_REQUEST_TIMEOUT_SECONDS: {timeout}")
    
    print("------------------------")
    
    if not gemini_enabled or not key_present:
        print("\n[!] Gemini is not fully configured or enabled for local testing.")
        print("Please review docs/GEMINI_ACTIVATION_READINESS.md for instructions.")
        sys.exit(1)
    else:
        print("\n[OK] Gemini appears configured and ready for local testing.")
        sys.exit(0)

if __name__ == "__main__":
    check_env()
