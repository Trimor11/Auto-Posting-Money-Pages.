from datetime import datetime, timedelta
from typing import Dict, Optional

from itsdangerous import BadSignature, URLSafeSerializer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_rate_limit_cache: Dict[str, list] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def build_session_serializer(secret_key: str) -> URLSafeSerializer:
    return URLSafeSerializer(secret_key, salt="apmp-admin")


def create_session_token(user_id: int, secret_key: str) -> str:
    serializer = build_session_serializer(secret_key)
    return serializer.dumps({"user_id": user_id, "ts": datetime.utcnow().isoformat()})


def decode_session_token(token: str, secret_key: str) -> Optional[int]:
    serializer = build_session_serializer(secret_key)
    try:
        payload = serializer.loads(token)
    except BadSignature:
        return None
    return payload.get("user_id")


def check_rate_limit(identifier: str, limit: int, per_seconds: int = 60) -> bool:
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=per_seconds)
    history = _rate_limit_cache.setdefault(identifier, [])
    # remove stale
    _rate_limit_cache[identifier] = [ts for ts in history if ts >= window_start]
    if len(_rate_limit_cache[identifier]) >= limit:
        return False
    _rate_limit_cache[identifier].append(now)
    return True
