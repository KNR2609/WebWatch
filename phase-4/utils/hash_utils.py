import hashlib
import json


def generate_hash(data):

    serialized = json.dumps(
        data,
        sort_keys=True
    )

    return hashlib.md5(
        serialized.encode()
    ).hexdigest()