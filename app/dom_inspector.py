import os
import json
import subprocess

class DOMInspector:
    """Extracts live DOM structure from target pages for locator grounding."""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = workspace_path

    def extract_dom(self, url: str, selectors: list = None, headless: bool = True) -> dict:
        """Navigates to a URL via Playwright and extracts element structure.
        
        Args:
            url: Target URL to inspect
            selectors: Optional list of selectors to target
            headless: Whether to run browser in headless mode (default: True)
        
        Returns a dict with extracted elements and their attributes.
        """
        # Safely escape strings for embedding in JavaScript
        safe_url = json.dumps(url)
        safe_headless = json.dumps(headless)
        script = '''
        const { chromium } = require('@playwright/test');
        (async () => {
            const browser = await chromium.launch({ headless: ''' + safe_headless + ''' });
            const page = await browser.newPage();
            try {
                await page.goto(''' + safe_url + ''', { waitUntil: 'networkidle', timeout: 30000 });
                
                // Extract all interactive elements
                const elements = await page.evaluate(() => {
                    const interactive = 'button, a, input, select, textarea, [role="button"], [role="link"], [role="combobox"], [role="textbox"], [role="searchbox"], [tabindex]:not([tabindex="-1"])';
                    const nodes = document.querySelectorAll(interactive);
                    const result = [];
                    const seen = new Set();
                    
                    nodes.forEach((el, index) => {
                        const tag = el.tagName.toLowerCase();
                        const text = (el.textContent || '').trim().substring(0, 100);
                        const attrs = {};
                        for (const attr of ['id', 'class', 'name', 'type', 'placeholder', 'aria-label', 'role', 'data-testid', 'href', 'title', 'value']) {
                            const val = el.getAttribute(attr);
                            if (val) attrs[attr] = val;
                        }
                        
                        // Get unique identifier
                        const key = tag + '|' + (attrs.id || '') + '|' + (attrs['data-testid'] || '') + '|' + text;
                        if (!seen.has(key)) {
                            seen.add(key);
                            result.push({ tag, text: text.substring(0, 80), attrs, index });
                        }
                    });
                    
                    // Also get headings for page structure context
                    const headings = [];
                    document.querySelectorAll('h1, h2, h3, h4').forEach(h => {
                        headings.push({ tag: h.tagName.toLowerCase(), text: (h.textContent || '').trim().substring(0, 80) });
                    });
                    
                    return { elements, headings, title: document.title, url: window.location.href };
                });
                
                await browser.close();
                console.log(JSON.stringify(elements));
            } catch (e) {
                await browser.close();
                console.log(JSON.stringify({ error: e.message }));
            }
        })();
        '''

        # Write temp script
        script_path = os.path.join(self.workspace_path, '_dom_inspect.js')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)

        try:
            result = subprocess.run(
                ['node', '_dom_inspect.js'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=45
            )
            output = result.stdout.strip()
            if output:
                parsed = json.loads(output)
                if 'error' in parsed:
                    return {"success": False, "error": parsed['error'], "elements": [], "headings": []}
                return {"success": True, **parsed}
            return {"success": False, "error": "No output from DOM inspector", "elements": []}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "DOM inspection timed out", "elements": []}
        except Exception as e:
            return {"success": False, "error": str(e), "elements": []}
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    def format_dom_context(self, dom_data: dict) -> str:
        """Formats DOM data into a readable string for LLM prompts."""
        if not dom_data.get("success"):
            return f"[DOM inspection failed: {dom_data.get('error', 'unknown error')}]"
        
        lines = []
        lines.append(f"Page Title: {dom_data.get('title', 'N/A')}")
        lines.append(f"Page URL: {dom_data.get('url', 'N/A')}")
        
        headings = dom_data.get("headings", [])
        if headings:
            lines.append("\nPage Structure (Headings):")
            for h in headings:
                lines.append(f"  <{h['tag']}> {h['text']}")
        
        elements = dom_data.get("elements", [])
        if elements:
            lines.append(f"\nInteractive Elements ({len(elements)} found):")
            for el in elements[:50]:  # Limit to 50 elements
                tag = el.get('tag', '')
                text = el.get('text', '')[:60]
                attrs = el.get('attrs', {})
                
                # Build a readable selector hint
                hints = []
                if 'data-testid' in attrs:
                    hints.append(f"data-testid={attrs['data-testid']}")
                if 'id' in attrs:
                    hints.append(f"#{attrs['id']}")
                if 'aria-label' in attrs:
                    hints.append(f"aria-label=\"{attrs['aria-label']}\"")
                if 'name' in attrs:
                    hints.append(f"name={attrs['name']}")
                if 'placeholder' in attrs:
                    hints.append(f"placeholder=\"{attrs['placeholder']}\"")
                if 'role' in attrs:
                    hints.append(f"role={attrs['role']}")
                
                hint_str = ", ".join(hints) if hints else tag
                text_str = f" '{text}'" if text else ""
                lines.append(f"  <{tag}>{text_str} [{hint_str}]")
        
        return "\n".join(lines)

    def find_element_in_dom(self, dom_data: dict, element_description: str) -> list:
        """Try to match a described element against the extracted DOM.
        Returns list of potential matches sorted by confidence."""
        elements = dom_data.get("elements", [])
        matches = []
        
        description_lower = element_description.lower()
        
        for el in elements:
            score = 0
            text = el.get('text', '').lower()
            attrs = el.get('attrs', {})
            tag = el.get('tag', '')
            
            # Check text match
            if description_lower in text or text in description_lower:
                score += 3
            
            # Check aria-label match
            aria = attrs.get('aria-label', '').lower()
            if aria and (description_lower in aria or aria in description_lower):
                score += 3
            
            # Check placeholder match
            placeholder = attrs.get('placeholder', '').lower()
            if placeholder and (description_lower in placeholder or placeholder in description_lower):
                score += 2
            
            # Check name attribute match
            name = attrs.get('name', '').lower()
            if name and (description_lower in name or name in description_lower):
                score += 2
            
            # Check data-testid match
            testid = attrs.get('data-testid', '').lower()
            if testid and (description_lower in testid or testid in description_lower):
                score += 2
            
            # Check id match
            el_id = attrs.get('id', '').lower()
            if el_id and (description_lower in el_id or el_id in description_lower):
                score += 1
            
            if score > 0:
                matches.append({"element": el, "confidence": score})
        
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches

