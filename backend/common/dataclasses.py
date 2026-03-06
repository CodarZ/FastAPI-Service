from dataclasses import dataclass


@dataclass
class UserAgentInfo:
    """User Agent."""

    user_agent: str
    os: str | None = None
    browser: str | None = None
    device: str | None = None
