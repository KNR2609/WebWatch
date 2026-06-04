from utils import (
    load_websites,
    fetch_all_api_data,
    get_rendered,
    get_sorted_list,
    process_api_result,
    add_api_failed_result
)


def filter_resource_item(item):
    meta = item.get("meta", {}) or {}

    filtered = {
        "slug": item.get("slug", ""),
        "status": item.get("status", ""),
        "type": item.get("type", ""),
        "link": item.get("link", ""),
        "title": get_rendered(item.get("title")),
        "excerpt": get_rendered(item.get("excerpt")),
        "content": get_rendered(item.get("content")),
        "categories": get_sorted_list(item, "categories"),
        "tags": get_sorted_list(item, "tags"),
        "geo-location": get_sorted_list(item, "geo-location"),
        "resource_types": get_sorted_list(item, "resource_types"),
        "sponsored_by": get_sorted_list(item, "sponsored_by"),
        "meta": {
            "form-shortcode": meta.get("form-shortcode", ""),
            "resource_title": meta.get("resource_title", ""),
            "sdm_description": meta.get("sdm_description", "")
        }
    }

    return filtered


def run_resources_monitor(results):
    websites = load_websites()

    for website in websites:
        website_name = website.get("name")
        website_url = website.get("url", "").rstrip("/")
        api_url = f"{website_url}/wp-json/wp/v2/resources"

        try:
            raw_items = fetch_all_api_data(api_url)
            current_data = [filter_resource_item(item) for item in raw_items]
            current_data.sort(key=lambda x: x.get("slug", ""))

            process_api_result(
                website_name,
                website_url,
                "resources",
                api_url,
                current_data,
                results
            )

        except Exception as error:
            add_api_failed_result(
                website_name,
                website_url,
                "resources",
                api_url,
                error,
                results
            )