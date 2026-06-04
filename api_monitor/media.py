from utils import (
    load_websites,
    fetch_all_api_data,
    get_rendered,
    process_api_result,
    add_api_failed_result
)


def filter_media_item(item):
    media_details = item.get("media_details", {}) or {}

    filtered_details = {
        "width": media_details.get("width"),
        "height": media_details.get("height"),
        "file": media_details.get("file"),
        "filesize": media_details.get("filesize"),
        "sizes": media_details.get("sizes", {}),
    }

    filtered = {
        "slug": item.get("slug", ""),
        "status": item.get("status", ""),
        "type": item.get("type", ""),
        "link": item.get("link", ""),
        "title": get_rendered(item.get("title")),
        "description": get_rendered(item.get("description")),
        "caption": get_rendered(item.get("caption")),
        "alt_text": item.get("alt_text", ""),
        "media_type": item.get("media_type", ""),
        "mime_type": item.get("mime_type", ""),
        "media_details": filtered_details,
    }

    return filtered


def run_media_monitor(results):
    websites = load_websites()

    for website in websites:
        website_name = website.get("name")
        website_url = website.get("url", "").rstrip("/")
        api_url = f"{website_url}/wp-json/wp/v2/media"

        try:
            raw_items = fetch_all_api_data(api_url)
            current_data = [filter_media_item(item) for item in raw_items]
            current_data.sort(key=lambda x: x.get("slug", ""))

            process_api_result(
                website_name,
                website_url,
                "media",
                api_url,
                current_data,
                results
            )

        except Exception as error:
            add_api_failed_result(
                website_name,
                website_url,
                "media",
                api_url,
                error,
                results
            )