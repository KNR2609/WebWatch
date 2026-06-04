def filter_page(item):

    title = item.get("title", {}).get("rendered", "")
    excerpt = item.get("excerpt", {}).get("rendered", "")
    content = item.get("content", {}).get("rendered", "")

    meta = item.get("meta", {})

    resource_title = meta.get("resource_title", "")
    pdf_link = meta.get("pdf_link", "")
    redirect_url = meta.get(
        "thankyoupage_redirecturl",
        ""
    )

    filtered = {
        "slug": item.get("slug", ""),
        "status": item.get("status", ""),
        "link": item.get("link", ""),
        "title": title,
        "excerpt": excerpt,
        "content": content,
        "parent": item.get("parent", 0),
        "template": item.get("template", ""),
        "sponsored_by": sorted(
            item.get("sponsored_by", [])
        ),
        "meta": {
            "resource_title": resource_title,
            "pdf_link": pdf_link,
            "thankyoupage_redirecturl": redirect_url
        }
    }

    return filtered