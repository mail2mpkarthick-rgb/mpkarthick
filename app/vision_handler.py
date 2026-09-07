import os
import json
from typing import List, Optional
from app.agent import GeminiAgent
from app.dom_inspector import DOMInspector


class VisionHandler:
    """Handles multimodal image input — interprets screenshots with Moondream,
    merges with DOM context, and flags mismatches."""

    def __init__(self, agent: GeminiAgent, dom_inspector: DOMInspector):
        self.agent = agent
        self.dom_inspector = dom_inspector
        self.MIN_CONFIDENCE_THRESHOLD = 0.3  # Below this, flag for user

    def analyze_images(self, image_paths: List[str]) -> dict:
        """Analyze multiple images and return merged interpretation."""
        if not image_paths:
            return {"elements": [], "confidence": 1.0, "warnings": [], "error": None}

        all_elements = []
        all_warnings = []
        total_confidence = 0.0
        image_count = len(image_paths)

        for img_path in image_paths:
            if not os.path.exists(img_path):
                all_warnings.append(f"Image not found: {img_path}")
                continue

            result = self.agent.analyze_image(img_path)
            confidence = result.get("confidence", 0)
            total_confidence += confidence

            if result.get("error") and confidence == 0:
                all_warnings.append(f"Could not analyze image {os.path.basename(img_path)}: {result['error']}")
            elif confidence < self.MIN_CONFIDENCE_THRESHOLD:
                all_warnings.append(
                    f"Low confidence interpreting {os.path.basename(img_path)} "
                    f"(confidence: {confidence:.1f}). Elements may be inaccurate."
                )
            
            elements = result.get("elements", [])
            all_elements.extend(elements)

        avg_confidence = total_confidence / image_count if image_count > 0 else 0

        return {
            "elements": all_elements,
            "confidence": avg_confidence,
            "warnings": all_warnings,
            "error": None
        }

    def merge_with_dom(self, vision_result: dict, dom_data: dict) -> dict:
        """Merge vision-identified elements with actual DOM structure.
        Flags mismatches where an element from the image cannot be found in the DOM."""
        if not vision_result.get("elements"):
            return {
                "merged_elements": [],
                "mismatches": [],
                "warnings": vision_result.get("warnings", []) + ["No elements identified from image(s)"],
                "description": vision_result.get("raw_description", "")
            }

        merged = []
        mismatches = []
        dom_elements = dom_data.get("elements", [])

        for img_el in vision_result.get("elements", []):
            label = img_el.get("label", img_el.get("text", "")).lower().strip()
            el_type = img_el.get("type", "").lower().strip()

            # Try to match against DOM
            matches = self.dom_inspector.find_element_in_dom(dom_data, label)

            if matches:
                # Take highest confidence match
                best_match = matches[0]
                merged.append({
                    "image_element": img_el,
                    "dom_element": best_match["element"],
                    "match_confidence": best_match["confidence"],
                    "match_found": True
                })
            else:
                mismatches.append({
                    "image_element": img_el,
                    "reason": f"Element '{label}' (type: {el_type}) not found in live DOM"
                })

        return {
            "merged_elements": merged,
            "mismatches": mismatches,
            "warnings": vision_result.get("warnings", [])
        }

    def format_image_context(self, vision_result: dict, dom_data: dict = None) -> str:
        """Format vision+DOM context for LLM prompt inclusion."""
        if dom_data:
            merged = self.merge_with_dom(vision_result, dom_data)
        else:
            merged = {"merged_elements": [], "mismatches": [], "warnings": vision_result.get("warnings", [])}

        lines = []
        lines.append("=== IMAGE / SCREENSHOT ANALYSIS ===")
        lines.append(f"Confidence: {vision_result.get('confidence', 0):.1f}")

        if vision_result.get("elements"):
            lines.append(f"\nIdentified Elements ({len(vision_result['elements'])}):")
            for el in vision_result["elements"]:
                label = el.get("label", el.get("text", "unnamed"))
                el_type = el.get("type", "unknown")
                position = el.get("position", "")
                state = el.get("state", "")
                lines.append(f"  - {el_type} '{label}' [{position}] state: {state}")
        elif vision_result.get("raw_description"):
            lines.append(f"\nRaw Description:\n{vision_result['raw_description']}")

        if merged.get("mismatches"):
            lines.append(f"\nMISMATCHES (elements in image not found in DOM): {len(merged['mismatches'])}")
            for m in merged["mismatches"]:
                lines.append(f"  - {m['reason']}")

        if merged.get("merged_elements"):
            lines.append(f"\nDOM-Verified Elements ({len(merged['merged_elements'])}):")
            for m in merged["merged_elements"]:
                img = m["image_element"]
                dom = m.get("dom_element", {})
                label = img.get("label", img.get("text", "unknown"))
                selector_hints = []
                attrs = dom.get("attrs", {})
                if "data-testid" in attrs:
                    selector_hints.append(f"data-testid={attrs['data-testid']}")
                if "id" in attrs:
                    selector_hints.append(f"#{attrs['id']}")
                if "aria-label" in attrs:
                    selector_hints.append(f"aria-label={attrs['aria-label']}")
                hint = ", ".join(selector_hints) if selector_hints else dom.get("tag", "?")
                lines.append(f"  - '{label}' -> <{dom.get('tag','?')}> [{hint}] (confidence: {m['match_confidence']})")

        if merged.get("warnings"):
            lines.append(f"\nWarnings:")
            for w in merged["warnings"]:
                lines.append(f"  - {w}")

        return "\n".join(lines)

