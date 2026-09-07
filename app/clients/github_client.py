import base64
import os

import requests

from app.config import get_settings
from app.logging_conf import get_logger

log = get_logger(__name__)

API_ROOT = "https://api.github.com"


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    """Minimal GitHub Contents API client - no local git required."""

    def __init__(self, token: str | None = None, repo: str | None = None, branch: str | None = None):
        settings = get_settings()
        self.token = token or settings.github_token
        self.repo = repo or settings.github_repo
        self.branch = branch or settings.github_branch

        if not self.token or not self.repo:
            raise GitHubError(
                "GitHub is not configured. Set GITHUB_TOKEN and GITHUB_REPO in your .env file."
            )

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_existing_sha(self, path: str) -> str | None:
        r = requests.get(
            f"{API_ROOT}/repos/{self.repo}/contents/{path}",
            headers=self._headers,
            params={"ref": self.branch},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("sha")
        if r.status_code == 404:
            return None
        raise GitHubError(f"GitHub lookup failed for {path}: {r.status_code} {r.text[:300]}")

    def put_file(self, path: str, content: bytes, message: str) -> dict:
        """Create or update a single file in the repository."""
        payload = {
            "message": message,
            "content": base64.b64encode(content).decode("ascii"),
            "branch": self.branch,
        }

        sha = self._get_existing_sha(path)
        if sha:
            payload["sha"] = sha

        r = requests.put(
            f"{API_ROOT}/repos/{self.repo}/contents/{path}",
            headers=self._headers,
            json=payload,
            timeout=60,
        )
        if r.status_code not in (200, 201):
            raise GitHubError(f"GitHub upload failed for {path}: {r.status_code} {r.text[:300]}")

        return {
            "path": path,
            "commit": r.json().get("commit", {}).get("sha"),
            "html_url": r.json().get("content", {}).get("html_url"),
        }

    def push_files(self, files: list[tuple[str, str]], message: str) -> list[dict]:
        """Push local files as (local_path, repo_path) pairs."""
        results = []
        for local_path, repo_path in files:
            if not os.path.exists(local_path):
                log.warning("Skipping missing file for GitHub push: %s", local_path)
                continue
            with open(local_path, "rb") as fh:
                results.append(self.put_file(repo_path, fh.read(), message))
        return results
