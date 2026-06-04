import requests


def validate_endpoint(
    url,
    timeout=10
):

    try:

        response = requests.get(
            url,
            timeout=timeout
        )

        if response.status_code == 200:
            return True

        return False

    except Exception:
        return False