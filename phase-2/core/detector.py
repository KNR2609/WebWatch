import os
import json
from .playwright_browser import PlaywrightBrowser
from .comparator import ImageComparator

class UIDetector:
    def __init__(self, config):
        self.browser = PlaywrightBrowser()
        self.comparator = ImageComparator()
        self.results_file = "results/changes.json"

    def run_monitoring(self, websites):
        all_changes = {}

        for site_name, pages in websites.items():
            site_changes = []
            for page_name, url in pages.items():
                base_path = f"data/screenshots/baseline/{site_name}_{page_name}.png"
                curr_path = f"data/screenshots/current/{site_name}_{page_name}.png"
                diff_path = f"data/screenshots/diff/{site_name}_{page_name}.png"

                # 1. Capture Current
                self.browser.capture_screenshot(url, curr_path)

                # 2. Check for Baseline (First Run Requirement)
                if not os.path.exists(base_path):
                    os.rename(curr_path, base_path)
                    continue

                # 3. Compare
                has_changed, score = self.comparator.compare(base_path, curr_path, diff_path)
                
                if has_changed:
                    site_changes.append({
                        "page_name": page_name,
                        "url": url,
                        "baseline": base_path,
                        "current": curr_path,
                        "diff": diff_path,
                        "score": round(score, 4)
                    })

            if site_changes:
                all_changes[site_name] = site_changes

        # Requirement 12: Overwrite old data
        with open(self.results_file, 'w') as f:
            json.dump(all_changes, f, indent=4)