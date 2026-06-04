from utils import (
    load_websites,
    fetch_all_api_data,
    get_rendered,
    get_sorted_list,
    process_api_result,
    add_api_failed_result
)


def filter_page_item(item):
    meta = item.get("meta", {}) or {}

    filtered = {
        "slug": item.get("slug", ""),
        "status": item.get("status", ""),
        "link": item.get("link", ""),
        "title": get_rendered(item.get("title")),
        "excerpt": get_rendered(item.get("excerpt")),
        "content": get_rendered(item.get("content")),
        "parent": item.get("parent", 0),
        "template": item.get("template", ""),
        "sponsored_by": get_sorted_list(item, "sponsored_by"),
        "meta": {
            "resource_title": meta.get("resource_title", ""),
            "pdf_link": meta.get("pdf_link", ""),
            "thankyoupage_redirecturl": meta.get("thankyoupage_redirecturl", "")
        }
    }

    return filtered


def run_pages_monitor(results):
    websites = load_websites()

    for website in websites:
        website_name = website.get("name")
        website_url = website.get("url", "").rstrip("/")
        api_url = f"{website_url}/wp-json/wp/v2/pages"

        try:
            raw_items = fetch_all_api_data(api_url)
            current_data = [filter_page_item(item) for item in raw_items]
            current_data.sort(key=lambda x: x.get("slug", ""))

            process_api_result(
                website_name,
                website_url,
                "pages",
                api_url,
                current_data,
                results
            )

        except Exception as error:
            add_api_failed_result(
                website_name,
                website_url,
                "pages",
                api_url,
                error,
                results
            )