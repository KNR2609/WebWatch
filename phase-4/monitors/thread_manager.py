from concurrent.futures import (
    ThreadPoolExecutor
)

from config.settings import (
    MAX_WORKERS
)


def run_threads(
    function,
    items
):

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        executor.map(
            function,
            items
        )