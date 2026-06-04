from monitors.event_monitor import (
    run_event_monitor
)

from monitors.api_monitor import (
    run_api_monitor
)

from monitors.baseline_manager import (
    load_baseline
)

from config.settings import (
    BASELINE_EVENT_PATH,
    BASELINE_API_PATH
)

from utils.constants import (
    API_NAMES
)

from utils.lock_manager import (
    get_website_lock
)


def process_website(website):

    website_name = website.get("name")

    website_url = website.get("url")

    lock = get_website_lock(
        website_name
    )

    with lock:

        # ==============================
        # CHECK FIRST RUN
        # ==============================

        event_baseline = load_baseline(
            BASELINE_EVENT_PATH,
            website_name,
            "posts"
        )

        api_baseline = load_baseline(
            BASELINE_API_PATH,
            website_name,
            "posts"
        )

        first_run = (
            not event_baseline
            or
            not api_baseline
        )

        # ==============================
        # FIRST RUN
        # CREATE BOTH BASELINES
        # ==============================

        if first_run:

            print(
                f"Creating baselines for "
                f"{website_name}"
            )

            # CREATE EVENT BASELINES
            run_event_monitor(
                website_name,
                website_url,
                initialize_only=True
            )

            # CREATE API BASELINES
            for api_name in API_NAMES:

                run_api_monitor(
                    website_name,
                    website_url,
                    api_name
                )

            print(
                f"Baselines created for "
                f"{website_name}"
            )

            return

        # ==============================
        # NORMAL FLOW
        # ==============================

        detected_changes = run_event_monitor(
            website_name,
            website_url
        )

        for api_name in detected_changes:

            run_api_monitor(
                website_name,
                website_url,
                api_name
            )