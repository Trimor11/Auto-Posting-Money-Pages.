from typing import Dict


def injection_snippet(analytics_code: str | None) -> str:
    if not analytics_code:
        return ""
    return analytics_code


def log_event_payload(event: str, metadata: Dict | None = None) -> Dict:
    return {"event": event, "metadata": metadata or {}}
