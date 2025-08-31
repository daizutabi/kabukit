from __future__ import annotations

import os


def load_env(name: str) -> str | None:
    load_dotenv()
    refresh_token = os.environ.get("JQUANTS_REFRESH_TOKEN")
    email = os.environ.get("JQUANTS_EMAIL")
    password = os.environ.get("JQUANTS_PASSWORD")
    return refresh_token, email, password
