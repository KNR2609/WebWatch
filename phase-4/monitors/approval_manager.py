from monitors.pending_manager import (
    delete_pending
)

from monitors.current_manager import (
    load_current,
    delete_current
)

from monitors.baseline_manager import (
    save_baseline
)

from config.settings import (
    BASELINE_API_PATH
)

from utils.logger import (
    setup_logger
)


logger = setup_logger(
    "approval_logger",
    "logs/approvals.log"
)


def approve_changes(
    website_name,
    api_name
):

    current_data = load_current(
        website_name,
        api_name
    )

    if not current_data:

        logger.warning(
            f"No current data found for "
            f"{website_name} - {api_name}"
        )

        return False

    # REPLACE BASELINE
    save_baseline(
        BASELINE_API_PATH,
        website_name,
        api_name,
        current_data
    )

    # CLEANUP
    delete_pending(
        website_name,
        api_name
    )

    delete_current(
        website_name,
        api_name
    )

    logger.info(
        f"Approved changes for "
        f"{website_name} - {api_name}"
    )

    return True


def reject_changes(
    website_name,
    api_name
):

    # DELETE ONLY CURRENT + PENDING
    delete_pending(
        website_name,
        api_name
    )

    delete_current(
        website_name,
        api_name
    )

    logger.info(
        f"Rejected changes for "
        f"{website_name} - {api_name}"
    )

    return True