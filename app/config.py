import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env_list(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings:
    """Central application configuration, sourced from environment variables."""

    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

        self.test_gen_model = os.getenv("TEST_GEN_MODEL", "gemini-3.6-flash")
        self.code_gen_model = os.getenv("CODE_GEN_MODEL", "gemini-3.6-flash")
        self.vision_model = os.getenv("VISION_MODEL", "gemini-3.6-flash")

        self.gemini_timeout = int(os.getenv("GEMINI_TIMEOUT", "120"))
        self.gemini_max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "4"))

        self.upload_dir = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
        self.workspace_dir = os.getenv("WORKSPACE_DIR", os.path.join(BASE_DIR, "workspace"))
        self.static_dir = os.path.join(BASE_DIR, "app", "static")

        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'healing_memory.db')}")

        self.cors_origins = _env_list(
            "CORS_ORIGINS",
            "http://localhost:8077,http://127.0.0.1:8077",
        )

        self.environments = {
            "dev": os.getenv("DEV_HOST", "dev.ges.store"),
            "uat": os.getenv("UAT_HOST", "uat.ges.store"),
        }

        self.max_upload_bytes = int(os.getenv("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
        self.max_prompt_chars = int(os.getenv("MAX_PROMPT_CHARS", "20000"))

        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github_repo = os.getenv("GITHUB_REPO", "")
        self.github_branch = os.getenv("GITHUB_BRANCH", "main")

    @property
    def github_enabled(self) -> bool:
        return bool(self.github_token and self.github_repo)

    def resolve_host(self, env: str) -> str:
        if env in self.environments:
            return self.environments[env]
        return env.replace("https://", "").replace("http://", "")

    def resolve_url(self, env: str) -> str:
        return f"https://{self.resolve_host(env)}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
