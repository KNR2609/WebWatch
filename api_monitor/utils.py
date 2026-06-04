import os
import json
import shutil
import requests
import threading
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WEBSITES_FILE = os.path.join(BASE_DIR, "websites.json")
BASELINE_DIR = os.path.join(BASE_DIR, "baselines")

RESULTS_DIR = os.path.join(BASE_DIR, "results")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.json")
CHANGE_LOGS_FILE = os.path.join(RESULTS_DIR, "change_logs.json")
CURRENT_DIR = os.path.join(RESULTS_DIR, "current")

# IGNORE COMPLETE WEBSITE
IGNORED_WEBSITES = {
    "https://businessstoriestoday.com"
}

# IGNORE SPECIFIC API ENDPOINTS
IGNORED_API_URLS = {
    "https://focusedonhr.com/wp-json/wp/v2/resources",
    "https://theinsightstoday.com/wp-json/wp/v2/resources"
}

# THREAD LOCK
results_lock = threading.Lock()


def ensure_folders():
    os.makedirs(BASELINE_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(CURRENT_DIR, exist_ok=True)

    if not os.path.exists(RESULTS_FILE):
        save_json(RESULTS_FILE, [])

    if not os.path.exists(CHANGE_LOGS_FILE):
        save_json(CHANGE_LOGS_FILE, [])


def load_json(file_path, default_value):
    if not os.path.exists(file_path):
        return default_value

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default_value


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_websites():
    websites = load_json(WEBSITES_FILE, [])

    filtered_websites = []

    for website in websites:

        website_url = (
            website.get("url", "")
            .rstrip("/")
            .lower()
        )

        if website_url in IGNORED_WEBSITES:
            continue

        filtered_websites.append(website)

    return filtered_websites


def load_results():
    ensure_folders()
    return load_json(RESULTS_FILE, [])


def save_results(results):
    save_json(RESULTS_FILE, results)


def clear_results():
    """
    results.json should contain ONLY current run changes
    """
    save_json(RESULTS_FILE, [])


def load_change_logs():
    ensure_folders()
    return load_json(CHANGE_LOGS_FILE, [])


def save_change_logs(logs):
    save_json(CHANGE_LOGS_FILE, logs)


def cleanup_old_change_logs():
    logs = load_change_logs()

    # KEEP LOGS FOR 2 DAYS
    cutoff_time = datetime.now() - timedelta(days=2)

    fresh_logs = []

    for log in logs:
        checked_time = log.get("checked_time")

        try:
            log_time = datetime.strptime(
                checked_time,
                "%Y-%m-%d %H:%M:%S"
            )

            if log_time >= cutoff_time:
                fresh_logs.append(log)

        except Exception:
            continue

    save_change_logs(fresh_logs)


def sanitize_filename(text):
    text = text.lower()
    result = ""

    for char in text:
        if char.isalnum():
            result += char
        else:
            result += "_"

    while "__" in result:
        result = result.replace("__", "_")

    return result.strip("_")


def get_rendered(value):
    if isinstance(value, dict):
        return value.get("rendered", "")
    return value or ""


def get_sorted_list(item, key):
    value = item.get(key, [])

    if isinstance(value, list):
        return sorted(value)

    return []


def should_ignore_api(api_url):

    cleaned_url = api_url.rstrip("/").lower()

    ignored_urls = {
        url.rstrip("/").lower()
        for url in IGNORED_API_URLS
    }

    return cleaned_url in ignored_urls


def fetch_all_api_data(api_url):

    if should_ignore_api(api_url):
        return []

    all_items = []
    page = 1

    while True:

        paged_url = f"{api_url}?per_page=100&page={page}"

        response = requests.get(
            paged_url,
            timeout=40
        )

        if response.status_code == 400 and page > 1:
            break

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")

        data = response.json()

        if not isinstance(data, list):
            raise Exception("API response is not a list")

        if len(data) == 0:
            break

        all_items.extend(data)

        total_pages = response.headers.get("X-WP-TotalPages")

        if total_pages:

            if page >= int(total_pages):
                break

        else:

            if len(data) < 100:
                break

        page += 1

    return all_items


def item_key(item):
    return (
        item.get("slug")
        or item.get("link")
        or json.dumps(item, sort_keys=True)
    )


def compare_data(baseline_data, current_data):

    changes = []

    baseline_map = {
        item_key(item): item
        for item in baseline_data
    }

    current_map = {
        item_key(item): item
        for item in current_data
    }

    all_keys = set(baseline_map.keys()) | set(current_map.keys())

    for key in sorted(all_keys):

        baseline_item = baseline_map.get(key)
        current_item = current_map.get(key)

        if baseline_item is None:

            changes.append({
                "changed_field": key,
                "before_value": "-",
                "after_value": "New item added"
            })

            continue

        if current_item is None:

            changes.append({
                "changed_field": key,
                "before_value": "Item existed in baseline",
                "after_value": "-"
            })

            continue

        all_fields = set(
            baseline_item.keys()
        ) | set(
            current_item.keys()
        )

        for field in sorted(all_fields):

            before_value = baseline_item.get(field)
            after_value = current_item.get(field)

            if before_value != after_value:

                changes.append({
                    "changed_field": f"{key}.{field}",
                    "before_value": before_value,
                    "after_value": after_value
                })

    return changes


def add_to_change_logs(change_record):

    cleanup_old_change_logs()

    logs = load_change_logs()

    logs.append(change_record)

    save_change_logs(logs)


def process_api_result(
    website_name,
    website_url,
    api_type,
    api_url,
    current_data,
    results
):

    if should_ignore_api(api_url):
        return

    checked_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    file_key = sanitize_filename(
        f"{website_name}_{api_type}"
    )

    baseline_file = os.path.join(
        BASELINE_DIR,
        f"{file_key}.json"
    )

    current_file = os.path.join(
        CURRENT_DIR,
        f"{file_key}.json"
    )

    if not os.path.exists(baseline_file):

        save_json(
            baseline_file,
            current_data
        )

        return

    baseline_data = load_json(
        baseline_file,
        []
    )

    changes = compare_data(
        baseline_data,
        current_data
    )

    if not changes:
        return

    save_json(current_file, current_data)

    for change in changes:

        change_record = {
            "website_name": website_name,
            "api_type": api_type,
            "website_url": website_url,
            "api_url": api_url,
            "status": "Change Detected",
            "changed_field": change["changed_field"],
            "before_value": change["before_value"],
            "after_value": change["after_value"],
            "checked_time": checked_time,
            "approval_status": "Pending"
        }

        # THREAD SAFE APPEND
        with results_lock:
            change_record["id"] = len(results) + 1
            results.append(change_record)

        add_to_change_logs(change_record)


def add_api_failed_result(
    website_name,
    website_url,
    api_type,
    api_url,
    error,
    results
):

    if should_ignore_api(api_url):
        return

    checked_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    failed_record = {
        "website_name": website_name,
        "api_type": api_type,
        "website_url": website_url,
        "api_url": api_url,
        "status": "API Failed",
        "changed_field": "-",
        "before_value": "-",
        "after_value": str(error),
        "checked_time": checked_time,
        "approval_status": "Not Required"
    }

    # THREAD SAFE APPEND
    with results_lock:
        failed_record["id"] = len(results) + 1
        results.append(failed_record)

    add_to_change_logs(failed_record)


def approve_change(result_id):

    results = load_results()

    selected_result = None

    for result in results:

        if result.get("id") == result_id:
            selected_result = result
            break

    if not selected_result:
        return

    website_name = selected_result["website_name"]
    api_type = selected_result["api_type"]

    file_key = sanitize_filename(
        f"{website_name}_{api_type}"
    )

    baseline_file = os.path.join(
        BASELINE_DIR,
        f"{file_key}.json"
    )

    current_file = os.path.join(
        CURRENT_DIR,
        f"{file_key}.json"
    )

    if os.path.exists(current_file):
        shutil.copyfile(current_file, baseline_file)
        os.remove(current_file)

    for result in results:

        if (
            result.get("website_name") == website_name
            and result.get("api_type") == api_type
            and result.get("approval_status") == "Pending"
        ):
            result["approval_status"] = "Approved"

    save_results(results)


def reject_change(result_id):

    results = load_results()

    selected_result = None

    for result in results:

        if result.get("id") == result_id:
            selected_result = result
            break

    if not selected_result:
        return

    website_name = selected_result["website_name"]
    api_type = selected_result["api_type"]

    file_key = sanitize_filename(
        f"{website_name}_{api_type}"
    )

    current_file = os.path.join(
        CURRENT_DIR,
        f"{file_key}.json"
    )

    if os.path.exists(current_file):
        os.remove(current_file)

    for result in results:

        if (
            result.get("website_name") == website_name
            and result.get("api_type") == api_type
            and result.get("approval_status") == "Pending"
        ):
            result["approval_status"] = "Rejected"

    save_results(results)
