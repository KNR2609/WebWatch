import os

from utils.file_utils import load_json, save_json

from config.settings import PENDING_PATH


def get_pending_path(website_name, api_name):
    filename = f"{website_name}_{api_name}.json"

    return os.path.join(
        PENDING_PATH,
        filename
    )


def pending_exists(website_name, api_name):
    path = get_pending_path(
        website_name,
        api_name
    )

    return os.path.exists(path)


def save_pending(
    website_name,
    api_name,
    data
):
    path = get_pending_path(
        website_name,
        api_name
    )

    save_json(path, data)


def load_pending(
    website_name,
    api_name
):
    path = get_pending_path(
        website_name,
        api_name
    )

    return load_json(path, default={})


def delete_pending(
    website_name,
    api_name
):
    path = get_pending_path(
        website_name,
        api_name
    )

    if os.path.exists(path):
        os.remove(path)