import re


def clean_rendered_content(text):

    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)

    text = text.strip()

    return text