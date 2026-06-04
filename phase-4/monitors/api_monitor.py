from monitors.fetcher import fetch_api_data

from monitors.baseline_manager import (
    load_baseline,
    save_baseline
)

from monitors.pending_manager import (
    save_pending
)

from monitors.current_manager import (
    save_current
)

from monitors.api_comparator import (
    compare_api_data
)

from config.settings import (
    BASELINE_API_PATH
)

from filters.post_filter import (
    filter_post
)

from filters.page_filter import (
    filter_page
)

from filters.media_filter import (
    filter_media
)

from filters.resource_filter import (
    filter_resource
)

from utils.logger import (
    setup_logger
)

from utils.constants import (
    IGNORED_API_ENDPOINTS,
    IGNORED_WEBSITES
)


logger = setup_logger(
    "api_monitor",
    "logs/api_monitor.log"
)


FILTER_MAP = {
    "posts": filter_post,
    "pages": filter_page,
    "media": filter_media,
    "resources": filter_resource
}


def run_api_monitor(
    website_name,
    website_url,
    api_name
):

    # ==========================================
    # IGNORE COMPLETE WEBSITE
    # ==========================================

    normalized_website = website_url.rstrip("/")

    if normalized_website in IGNORED_WEBSITES:

        logger.info(
            f"Ignored website: {website_url}"
        )

        return []

    endpoint = (
        f"{website_url}"
        f"/wp-json/wp/v2/{api_name}"
    )

    # ==========================================
    # IGNORE SPECIFIC API ENDPOINTS
    # ==========================================

    normalized_endpoint = endpoint.rstrip("/")

    if normalized_endpoint in IGNORED_API_ENDPOINTS:

        logger.info(
            f"Ignored API endpoint: {endpoint}"
        )

        return []

    current_data = fetch_api_data(
        endpoint
    )

    # ENDPOINT NOT AVAILABLE
    if current_data == []:

        logger.warning(
            f"Skipping unavailable endpoint: "
            f"{website_name} - {api_name}"
        )

        return []

    filter_function = FILTER_MAP.get(
        api_name
    )

    if not filter_function:

        logger.warning(
            f"No filter found for "
            f"{api_name}"
        )

        return []

    # FILTER CURRENT DATA
    filtered_current = [
        filter_function(item)
        for item in current_data
    ]

    # LOAD BASELINE
    baseline_data = load_baseline(
        BASELINE_API_PATH,
        website_name,
        api_name
    )

    # ==============================
    # FIRST RUN BASELINE CREATION
    # ==============================

    if not baseline_data:

        save_baseline(
            BASELINE_API_PATH,
            website_name,
            api_name,
            filtered_current
        )

        logger.info(
            f"API baseline created for "
            f"{website_name} - {api_name}"
        )

        return []

    # ==============================
    # COMPARE BASELINE VS CURRENT
    # ==============================

    changes = compare_api_data(
        website_name,
        api_name,
        baseline_data,
        filtered_current
    )

    # ==============================
    # CHANGES DETECTED
    # ==============================

    if changes:

        logger.info(
            f"API changes detected in "
            f"{website_name} - {api_name}"
        )

        # STORE ONLY DIFFERENCES
        save_pending(
            website_name,
            api_name,
            changes
        )

        # STORE FULL CURRENT DATA
        save_current(
            website_name,
            api_name,
            filtered_current
        )

    else:

        logger.info(
            f"No API changes in "
            f"{website_name} - {api_name}"
        )

    return changes