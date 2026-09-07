import os
from app.pom_repository import POMRepository
from app.config import get_settings
from app.services.validator import validate


class CodeScaffolder:
    def __init__(self, workspace_path: str | None = None):
        workspace_path = workspace_path or get_settings().workspace_dir
        self.workspace_path = workspace_path
        self.tests_dir = os.path.join(workspace_path, "tests")
        self.pages_dir = os.path.join(workspace_path, "pages")
        os.makedirs(self.tests_dir, exist_ok=True)
        os.makedirs(self.pages_dir, exist_ok=True)
        self.pom_repo = POMRepository(pages_dir=self.pages_dir)

    def save_test(self, test_name: str, code_content: str) -> str:
        """Writes the generated test spec inside the tests folder."""
        validate(code_content, f"test spec '{test_name}'")
        filename = f"{test_name}.spec.js" if not test_name.endswith(".spec.js") else test_name
        file_path = os.path.join(self.tests_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        return file_path

    def save_page_object(self, page_name: str, code_content: str) -> str:
        """Writes a Page Object Model class inside the pages folder and registers it."""
        validate(code_content, f"page object '{page_name}'")
        file_path = self.pom_repo.save_page_object(page_name, code_content)
        return file_path

    def read_test(self, test_name: str) -> str:
        filename = f"{test_name}.spec.js" if not test_name.endswith(".spec.js") else test_name
        file_path = os.path.join(self.tests_dir, filename)
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def read_page_object(self, page_name: str) -> str:
        return self.pom_repo.load_page_object(page_name)

    def get_existing_pom_context(self) -> str:
        """Get all existing Page Objects as context for code generation."""
        return self.pom_repo.load_all_page_objects()

    def propose_new_locators(self, generated_code: str) -> list:
        """Analyze generated code and propose new locators for the POM repository."""
        return self.pom_repo.propose_new_locators(generated_code)

    def get_page_for_url(self, url: str) -> str:
        """Find which Page Object matches a URL."""
        return self.pom_repo.find_page_for_url(url)

