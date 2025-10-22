from datetime import datetime

def validate_timestamp(ts: str) -> bool:
    """Periksa apakah timestamp valid dalam format ISO8601"""
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def generate_event_id(prefix="evt") -> str:
    """Buat event_id unik (misalnya jika publisher tidak mengirim event_id)"""
    from uuid import uuid4
    return f"{prefix}-{uuid4().hex[:8]}"
