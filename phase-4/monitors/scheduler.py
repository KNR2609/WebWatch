from concurrent.futures import (
    ThreadPoolExecutor
)

from utils.file_utils import (
    load_json
)

from config.settings import (
    MAX_WORKERS
)

from monitors.website_processor import (
    process_website
)


def run_scheduler():

    websites = load_json(
        "config/websites.json",
        default=[]
    )

    if not websites:

        print(
            "No websites configured"
        )

        return

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        executor.map(
            process_website,
            websites
        )