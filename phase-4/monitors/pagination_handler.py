def build_paginated_url(
    base_url,
    page,
    per_page=100
):

    separator = "&" if "?" in base_url else "?"

    return (
        f"{base_url}"
        f"{separator}page={page}"
        f"&per_page={per_page}"
    )