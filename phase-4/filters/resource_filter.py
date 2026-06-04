def filter_resource(item):

    title = item.get("title", {}).get("rendered", "")
    excerpt = item.get("excerpt", {}).get("rendered", "")
    content = item.get("content", {}).get("rendered", "")

    meta = item.get("meta", {})

    filtered = {
        "slug": item.get("slug", ""),
        "status": item.get("status", ""),
        "type": item.get("type", ""),
        "link": item.get("link", ""),
        "title": title,
        "excerpt": excerpt,
        "content": content,
        "categories": sorted(item.get("categories", [])),
        "tags": sorted(item.get("tags", [])),
        "geo-location": sorted(item.get("geo-location", [])),
        "resource_types": sorted(
            item.get("resource_types", [])
        ),
        "sponsored_by": sorted(
            item.get("sponsored_by", [])
        ),
        "meta": {
            "form-shortcode": meta.get(
                "form-shortcode",
                ""
            ),
            "resource_title": meta.get(
                "resource_title",
                ""
            ),
            "sdm_description": meta.get(
                "sdm_description",
                ""
            )
        }
    }

    return filtered