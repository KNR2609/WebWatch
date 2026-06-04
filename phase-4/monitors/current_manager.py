import os

from utils.file_utils import (
    load_json,
    save_json
)

from config.settings import (
    CURRENT_PATH
)


def get_current_path(
    website_name,
    api_name
):

    filename = (
        f"{website_name}_{api_name}.json"
    )

    return os.path.join(
        CURRENT_PATH,
        filename
    )


def save_current(
    website_name,
    api_name,
    data
):

    path = get_current_path(
        website_name,
        api_name
    )

    save_json(
        path,
        data
    )


def load_current(
    website_name,
    api_name
):

    path = get_current_path(
        website_name,
        api_name
    )

    return load_json(
        path,
        default=[]
    )


def delete_current(
    website_name,
    api_name
):

    path = get_current_path(
        website_name,
        api_name
    )

    if os.path.exists(path):

        os.remove(path)