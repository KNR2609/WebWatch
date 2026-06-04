def filter_post(item):

    title = item.get("title", {}).get("rendered", "")
    excerpt = item.get("excerpt", {}).get("rendered", "")
    content = item.get("content", {}).get("rendered", "")

    filtered = {
        "slug": item.get("slug", ""),
        "status": item.get("status", ""),
        "link": item.get("link", ""),
        "title": title,
        "excerpt": excerpt,
        "content": content,
        "categories": sorted(item.get("categories", [])),
        "tags": sorted(item.get("tags", [])),
        "geo-location": sorted(item.get("geo-location", [])),
        "sticky": item.get("sticky", False),
        "format": item.get("format", ""),
    }

    return filtered