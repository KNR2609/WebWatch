def filter_media(item):

    title = item.get("title", {}).get("rendered", "")

    description = item.get(
        "description",
        {}
    ).get("rendered", "")

    caption = item.get(
        "caption",
        {}
    ).get("rendered", "")

    media_details = item.get(
        "media_details",
        {}
    )

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
        "title": title,
        "description": description,
        "caption": caption,
        "alt_text": item.get("alt_text", ""),
        "media_type": item.get("media_type", ""),
        "mime_type": item.get("mime_type", ""),
        "media_details": filtered_details,
    }

    return filtered