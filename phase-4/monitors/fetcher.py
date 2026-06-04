import requests
import time

from config.settings import (
    REQUEST_TIMEOUT,
    MAX_RETRIES
)

from monitors.pagination_handler import (
    build_paginated_url
)

from utils.logger import setup_logger


logger = setup_logger(
    "fetcher_logger",
    "logs/api_monitor.log"
)


def fetch_api_data(url):

    page = 1

    all_data = []

    while True:

        paginated_url = build_paginated_url(
            url,
            page
        )

        success = False

        for attempt in range(MAX_RETRIES):

            try:

                response = requests.get(
                    paginated_url,
                    timeout=REQUEST_TIMEOUT
                )

                # NO MORE PAGES
                if response.status_code == 400:

                    logger.info(
                        f"No more pages: "
                        f"{paginated_url}"
                    )

                    return all_data

                # ENDPOINT NOT FOUND
                if response.status_code == 404:

                    logger.warning(
                        f"404 Endpoint not found: "
                        f"{paginated_url}"
                    )

                    return []

                response.raise_for_status()

                data = response.json()

                # EMPTY RESPONSE
                if not data:

                    logger.info(
                        f"No data returned: "
                        f"{paginated_url}"
                    )

                    return all_data

                all_data.extend(data)

                logger.info(
                    f"Fetched page {page} "
                    f"from {paginated_url}"
                )

                success = True

                break

            except Exception as error:

                logger.error(
                    f"Failed fetching: "
                    f"{paginated_url} "
                    f"Attempt: {attempt + 1} "
                    f"Error: {str(error)}"
                )

                time.sleep(2)

        # ALL RETRIES FAILED
        if not success:

            logger.error(
                f"All retries failed for: "
                f"{paginated_url}"
            )

            return all_data

        page += 1