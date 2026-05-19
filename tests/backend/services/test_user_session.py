# тесты user_session: TTL, хеш токена, статусы
from types import SimpleNamespace

import pytest
from starlette.requests import Request

from src.traffic_dtp.services import user_session as session_service


def _request(
    *,
    client_host: str | None = "127.0.0.1",
    headers: list[tuple[bytes, bytes]] | None = None,
) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/auth/login",
        "headers": headers or [],
        "client": (client_host, 0) if client_host else None,
    }
    return Request(scope)


def test_resolve_client_ip_from_forwarded():
    req = _request(
        client_host="10.0.0.1",
        headers=[(b"x-forwarded-for", b"203.0.113.50, 70.41.3.18")],
    )
    assert session_service.resolve_client_ip(req) == "203.0.113.50"


def test_resolve_client_ip_fallback_unknown():
    req = _request(client_host=None, headers=[])
    assert session_service.resolve_client_ip(req) == "unknown"


def test_resolve_user_agent_truncates():
    long_ua = "x" * 600
    req = _request(headers=[(b"user-agent", long_ua.encode())])
    assert len(session_service.resolve_user_agent(req)) == session_service.USER_AGENT_MAX_LEN


def test_hash_token_is_sha256_hex():
    h = session_service.hash_token("jwt-abc")
    assert len(h) == 64
    assert h == session_service.hash_token("jwt-abc")
