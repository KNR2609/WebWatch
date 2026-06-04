import os
import json
import difflib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from webdriver_manager.chrome import ChromeDriverManager

from core.dom_extractor import (
    extract_visible_text_from_dom,
    set_chrome_driver_path
)


WEBSITES_FILE = "websites.json"

BASELINE_DIR = "data/dom_text/baseline"
CURRENT_DIR = "data/dom_text/current"

RESULT_FILE = "results/dom_text_changes.json"

# Multi-threading workers
MAX_WORKERS = 8


def create_required_folders():
    os.makedirs(BASELINE_DIR, exist_ok=True)
    os.makedirs(CURRENT_DIR, exist_ok=True)
    os.makedirs("results", exist_ok=True)


def safe_filename(text):

    return (
        text.lower()
        .replace("https://", "")
        .replace("http://", "")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace(".", "_")
        .replace(" ", "_")
    )


def save_text(path, text):

    with open(path, "w", encoding="utf-8") as file:
        file.write(text)


def read_text(path):

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def get_changes(old_text, new_text):

    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    matcher = difflib.SequenceMatcher(
        None,
        old_lines,
        new_lines
    )

    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":
            continue

        old_part = old_lines[i1:i2]
        new_part = new_lines[j1:j2]

        max_len = max(
            len(old_part),
            len(new_part)
        )

        for index in range(max_len):

            before = (
                old_part[index]
                if index < len(old_part)
                else ""
            )

            after = (
                new_part[index]
                if index < len(new_part)
                else ""
            )

            if before != after:

                changes.append({
                    "before": before,
                    "after": after,
                    "changed_text": f"{before} -> {after}"
                })

    return changes


def process_page(
    website_name,
    page_name,
    url
):

    print(f"\nChecking: {website_name} | {page_name}")
    print(url)

    current_text = extract_visible_text_from_dom(url)

    if not current_text:

        return {
            "website": website_name,
            "page": page_name,
            "url": url,
            "status": "Extraction Failed",
            "total_changes": 0,
            "changes": []
        }

    file_key = safe_filename(
        f"{website_name}_{page_name}"
    )

    baseline_path = os.path.join(
        BASELINE_DIR,
        f"{file_key}.txt"
    )

    current_path = os.path.join(
        CURRENT_DIR,
        f"{file_key}.txt"
    )

    save_text(current_path, current_text)

    # Create baseline if not present
    if not os.path.exists(baseline_path):

        save_text(
            baseline_path,
            current_text
        )

        return {
            "website": website_name,
            "page": page_name,
            "url": url,
            "status": "Baseline Created",
            "total_changes": 0,
            "changes": []
        }

    baseline_text = read_text(
        baseline_path
    )

    changes = get_changes(
        baseline_text,
        current_text
    )

    if changes:

        return {
            "website": website_name,
            "page": page_name,
            "url": url,
            "status": "Text Change Detected",
            "total_changes": len(changes),
            "changes": changes
        }

    return {
        "website": website_name,
        "page": page_name,
        "url": url,
        "status": "No Text Change",
        "total_changes": 0,
        "changes": []
    }


def run_monitor():

    create_required_folders()

    print("\nPreparing ChromeDriver...")

    driver_path = ChromeDriverManager().install()

    set_chrome_driver_path(driver_path)

    print("ChromeDriver ready.")

    if not os.path.exists(WEBSITES_FILE):

        print(f"{WEBSITES_FILE} not found.")

        return []

    with open(
        WEBSITES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        websites = json.load(file)

    tasks = []

    for website in websites:

        website_name = website.get(
            "name",
            "Unknown Website"
        )

        pages = website.get(
            "pages",
            {}
        )

        for page_name, url in pages.items():

            tasks.append(
                (
                    website_name,
                    page_name,
                    url
                )
            )

    if not tasks:

        print("No pages found.")

        return []

    changed_results = []
    all_results = []

    print(f"\nStarting monitoring with {MAX_WORKERS} threads...\n")

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [

            executor.submit(
                process_page,
                website_name,
                page_name,
                url
            )

            for (
                website_name,
                page_name,
                url
            ) in tasks
        ]

        for future in as_completed(futures):

            try:

                result = future.result()

                all_results.append(result)

                print(
                    f"{result['website']} | "
                    f"{result['page']} -> "
                    f"{result['status']}"
                )

                if result["status"] == "Text Change Detected":

                    changed_results.append(result)

            except Exception as e:

                print(f"Thread Error: {e}")

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            changed_results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nMonitoring Completed.")
    print(f"Total pages checked: {len(all_results)}")
    print(f"Pages with changes: {len(changed_results)}")
    print(f"Results saved to: {RESULT_FILE}")

    return changed_results


if __name__ == "__main__":

    start_time = time.time()

    run_monitor()

    end_time = time.time()

    print(
        f"\nExecution Time: "
        f"{round(end_time - start_time, 2)} seconds"
    )