import os

from utils.file_utils import (
    load_json,
    save_json
)


def get_baseline_path(
    base_path,
    website_name,
    api_name
):

    filename = (
        f"{website_name}_{api_name}.json"
    )

    return os.path.join(
        base_path,
        filename
    )


def load_baseline(
    base_path,
    website_name,
    api_name
):

    path = get_baseline_path(
        base_path,
        website_name,
        api_name
    )

    return load_json(
        path,
        default={}
    )


def save_baseline(
    base_path,
    website_name,
    api_name,
    data
):

    path = get_baseline_path(
        base_path,
        website_name,
        api_name
    )

    save_json(
        path,
        data
    )