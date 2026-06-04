import os

from utils.file_utils import load_json

PENDING_PATH = "storage/pending"


def get_pending_files():

    if not os.path.exists(PENDING_PATH):
        return []

    return os.listdir(PENDING_PATH)


def get_pending_data(filename):

    file_path = os.path.join(
        PENDING_PATH,
        filename
    )

    return load_json(
        file_path,
        default=[]
    )