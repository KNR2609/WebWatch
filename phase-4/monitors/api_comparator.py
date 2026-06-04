from utils.datetime_utils import (
    get_current_time
)


def compare_api_data(
    website_name,
    api_name,
    baseline_data,
    current_data
):

    changes = []

    baseline_map = {
        item.get("slug"): item
        for item in baseline_data
    }

    current_map = {
        item.get("slug"): item
        for item in current_data
    }

    # ==========================
    # NEW + UPDATED
    # ==========================

    for slug, current_item in current_map.items():

        baseline_item = baseline_map.get(
            slug
        )

        # NEW RECORD
        if not baseline_item:

            changes.append({
                "website": website_name,
                "api": api_name,
                "checked_time": (
                    get_current_time()
                ),
                "action": "new",
                "slug": slug,
                "before": None,
                "after": current_item
            })

            continue

        changed_fields = {}

        for field in current_item:

            baseline_value = (
                baseline_item.get(field)
            )

            current_value = (
                current_item.get(field)
            )

            if baseline_value != current_value:

                changed_fields[field] = {
                    "before": baseline_value,
                    "after": current_value
                }

        # UPDATED RECORD
        if changed_fields:

            changes.append({
                "website": website_name,
                "api": api_name,
                "checked_time": (
                    get_current_time()
                ),
                "action": "updated",
                "slug": slug,
                "changes": changed_fields
            })

    # ==========================
    # DELETED
    # ==========================

    for slug, baseline_item in baseline_map.items():

        if slug not in current_map:

            changes.append({
                "website": website_name,
                "api": api_name,
                "checked_time": (
                    get_current_time()
                ),
                "action": "deleted",
                "slug": slug,
                "before": baseline_item,
                "after": None
            })

    return changes