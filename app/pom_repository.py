import os
import json
import glob
import re
import datetime


class POMRepository:
    """Manages a persistent repository of Page Object Models.
    
    Checks existing POM files, reuses locators, and proposes new additions.
    Stores metadata about each Page Object for cross-reference.
    """

    def __init__(self, pages_dir: str = "./workspace/pages", 
                 metadata_file: str = "./workspace/pages/.pom_registry.json"):
        self.pages_dir = pages_dir
        self.metadata_file = metadata_file
        os.makedirs(pages_dir, exist_ok=True)
        self._ensure_registry()

    def _ensure_registry(self):
        """Create empty registry if it doesn't exist."""
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w') as f:
                json.dump({"pages": {}, "locators": {}}, f)

    def _load_registry(self) -> dict:
        """Load the POM registry metadata."""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"pages": {}, "locators": {}}

    def _save_registry(self, registry: dict):
        """Save the POM registry metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(registry, f, indent=2)

    def list_page_objects(self) -> list:
        """List all existing Page Object files."""
        pattern = os.path.join(self.pages_dir, "*.page.js")
        files = glob.glob(pattern)
        page_objects = []
        for f in files:
            name = os.path.basename(f).replace(".page.js", "")
            page_objects.append({"name": name, "path": f})
        return page_objects

    def load_page_object(self, page_name: str) -> str:
        """Load the content of a specific Page Object."""
        filepath = os.path.join(self.pages_dir, f"{page_name}.page.js")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def load_all_page_objects(self) -> str:
        """Load concatenated content of all Page Objects for LLM context."""
        pages = self.list_page_objects()
        combined = []
        for page in pages:
            content = self.load_page_object(page["name"])
            if content:
                combined.append(f"// === {page['name']}.page.js ===\n{content}")
        return "\n\n".join(combined)

    def save_page_object(self, page_name: str, code: str) -> str:
        """Save a new or updated Page Object. Returns the file path."""
        filepath = os.path.join(self.pages_dir, f"{page_name}.page.js")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Update registry with extracted locators
        self._update_registry_for_page(page_name, code)
        return filepath

    def _update_registry_for_page(self, page_name: str, code: str):
        """Extract locator selectors from Page Object code and update registry."""
        registry = self._load_registry()
        
        # Extract locator definitions (e.g., this.searchInput = 'input[name="q"]')
        locator_pattern = re.compile(r'this\.(\w+)\s*=\s*[\'"](.+?)[\'"]')
        locators = {}
        for match in locator_pattern.finditer(code):
            locator_name = match.group(1)
            selector = match.group(2)
            locators[locator_name] = selector
        
        # Also extract page URLs
        url_pattern = re.compile(r'this\.pageUrl\s*=\s*[\'"](.+?)[\'"]')
        page_url = ""
        url_match = url_pattern.search(code)
        if url_match:
            page_url = url_match.group(1)
        
        registry["pages"][page_name] = {
            "locators": locators,
            "page_url": page_url,
            "updated": datetime.datetime.now().isoformat()
        }
        
        # Also index by locator target for cross-referencing
        for locator_name, selector in locators.items():
            if selector not in registry["locators"]:
                registry["locators"][selector] = []
            if page_name not in [p["page"] for p in registry["locators"][selector]]:
                registry["locators"][selector].append({"page": page_name, "name": locator_name})
        
        self._save_registry(registry)

    def find_page_for_url(self, url: str) -> str:
        """Find which Page Object matches a given URL pattern."""
        registry = self._load_registry()
        for page_name, info in registry["pages"].items():
            if info.get("page_url") and info["page_url"] in url:
                return page_name
        return ""

    def find_locator(self, target_description: str) -> list:
        """Search for existing locators that match a description.
        Returns list of matches with page name and selector."""
        registry = self._load_registry()
        results = []
        target_lower = target_description.lower()
        
        for page_name, info in registry["pages"].items():
            for locator_name, selector in info.get("locators", {}).items():
                # Check if locator name or selector matches the description
                if target_lower in locator_name.lower() or target_lower in selector.lower():
                    results.append({
                        "page": page_name,
                        "locator_name": locator_name,
                        "selector": selector
                    })
        
        return results

    def propose_new_locators(self, generated_code: str) -> list:
        """Analyze newly generated code and propose locators that should be added to the repository.
        Returns list of proposed additions."""
        proposals = []
        
        # Find selectors in the generated code
        selector_pattern = re.compile(r'(?:locator|getByRole|getByText|getByPlaceholder|getByTestId|getByLabel)\([\'"](.+?)[\'"]')
        existing_selectors = set()
        
        # Get all existing selectors
        registry = self._load_registry()
        for page_name, info in registry["pages"].items():
            for locator_name, selector in info.get("locators", {}).items():
                existing_selectors.add(selector)
        
        for match in selector_pattern.finditer(generated_code):
            selector = match.group(1)
            if selector not in existing_selectors:
                proposals.append({
                    "selector": selector,
                    "context": generated_code[max(0, match.start()-50):match.end()+50],
                    "status": "new"
                })
        
        return proposals

