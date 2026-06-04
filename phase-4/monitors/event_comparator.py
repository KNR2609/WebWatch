def compare_event_data(
    baseline_data,
    current_data
):

    for item_id, current_item in current_data.items():

        baseline_item = baseline_data.get(
            item_id,
            {}
        )

        baseline_modified = (
            baseline_item.get(
                "modified",
                ""
            )
        )

        current_modified = (
            current_item.get(
                "modified",
                ""
            )
        )

        # CHANGE DETECTED
        if baseline_modified != current_modified:

            return True

    return False