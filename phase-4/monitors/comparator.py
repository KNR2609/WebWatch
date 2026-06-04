def compare_event_data(old_data, new_data):
    changes_detected = False

    for item_id, modified_date in new_data.items():

        old_modified = old_data.get(item_id)

        if old_modified != modified_date:
            changes_detected = True
            break

    return changes_detected


def compare_api_data(old_data, new_data):
    changes = []

    old_map = {
        item.get("slug"): item
        for item in old_data
    }

    new_map = {
        item.get("slug"): item
        for item in new_data
    }

    # NEW + UPDATED
    for slug, new_item in new_map.items():

        old_item = old_map.get(slug)

        if not old_item:
            changes.append({
                "type": "new",
                "slug": slug,
                "data": new_item
            })

            continue

        item_changes = {}

        for field in new_item:

            old_value = old_item.get(field)
            new_value = new_item.get(field)

            if old_value != new_value:
                item_changes[field] = {
                    "before": old_value,
                    "after": new_value
                }

        if item_changes:
            changes.append({
                "type": "updated",
                "slug": slug,
                "changes": item_changes
            })

    # DELETED
    for slug, old_item in old_map.items():

        if slug not in new_map:
            changes.append({
                "type": "deleted",
                "slug": slug,
                "data": old_item
            })

    return changes