from monitors.fetcher import (
    fetch_api_data
)

from monitors.baseline_manager import (
    load_baseline,
    save_baseline
)

from monitors.comparator import (
    compare_event_data
)

from monitors.pending_manager import (
    pending_exists
)

from monitors.api_monitor import (
    run_api_monitor
)

from config.settings import (
    BASELINE_EVENT_PATH
)

from utils.logger import (
    setup_logger
)


logger = setup_logger(
    "event_monitor",
    "logs/event_monitor.log"
)


EVENT_ENDPOINTS = [
    "posts",
    "pages",
    "media",
    "resources"
]


def run_event_monitor(
    website_name,
    website_url,
    initialize_only=False
):

    detected_changes = []

    for api_name in EVENT_ENDPOINTS:

        endpoint = (
            f"{website_url}"
            f"/wp-json/wp/v2/{api_name}"
        )

        current_data = fetch_api_data(
            endpoint
        )

        # ==============================
        # ENDPOINT NOT AVAILABLE
        # ==============================

        if current_data == []:

            logger.warning(
                f"Endpoint missing: "
                f"{website_name} - {api_name}"
            )

            continue

        # ==============================
        # STORE ONLY MODIFIED FIELD
        # ==============================

        filtered_current = {}

        for item in current_data:

            item_id = str(
                item.get("id")
            )

            filtered_current[item_id] = {
                "modified": item.get(
                    "modified",
                    ""
                )
            }

        # ==============================
        # LOAD EVENT BASELINE
        # ==============================

        baseline_data = load_baseline(
            BASELINE_EVENT_PATH,
            website_name,
            api_name
        )

        # ==============================
        # FIRST RUN BASELINE CREATION
        # ==============================

        if (
            initialize_only
            or
            not baseline_data
        ):

            save_baseline(
                BASELINE_EVENT_PATH,
                website_name,
                api_name,
                filtered_current
            )

            logger.info(
                f"Event baseline created for "
                f"{website_name} - {api_name}"
            )

            continue

        # ==============================
        # COMPARE EVENT DATA
        # ==============================

        changes_detected = compare_event_data(
            baseline_data,
            filtered_current
        )

        # ==============================
        # EVENT CHANGES FOUND
        # ==============================

        if changes_detected:

            logger.info(
                f"Changes detected in "
                f"{website_name} - {api_name}"
            )

            already_pending = pending_exists(
                website_name,
                api_name
            )

            if already_pending:

                logger.info(
                    f"Pending already exists for "
                    f"{website_name} - {api_name}"
                )

                # UPDATE EVENT BASELINE
                save_baseline(
                    BASELINE_EVENT_PATH,
                    website_name,
                    api_name,
                    filtered_current
                )

                continue

            # ==========================
            # TRIGGER API MONITOR FIRST
            # ==========================

            run_api_monitor(
                website_name,
                website_url,
                api_name
            )

            # ==========================
            # UPDATE EVENT BASELINE
            # AFTER API MONITOR RUNS
            # ==========================

            save_baseline(
                BASELINE_EVENT_PATH,
                website_name,
                api_name,
                filtered_current
            )

            detected_changes.append(
                api_name
            )

        else:

            logger.info(
                f"No changes detected in "
                f"{website_name} - {api_name}"
            )

    return detected_changes