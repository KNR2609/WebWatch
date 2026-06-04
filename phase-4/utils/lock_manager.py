import threading


website_locks = {}


def get_website_lock(website_name):

    if website_name not in website_locks:

        website_locks[website_name] = (
            threading.Lock()
        )

    return website_locks[website_name]