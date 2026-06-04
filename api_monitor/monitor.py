import os
import json
import shutil
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WEBSITES_FILE = os.path.join(BASE_DIR, "websites.json")

BASELINE_DIR = os.path.join(BASE_DIR, "baselines")

RESULTS_DIR = os.path.join(BASE_DIR, "results")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.json")
CURRENT_DIR = os.path.join(RESULTS_DIR, "current")


API_TYPES = {
    "pages": "/wp-json/wp/v2/pages",
    "posts": "/wp-json/wp/v2/posts",
    "media": "/wp-json/wp/v2/media",
    "resources": "/wp-json/wp/v2/resources"
}


def ensure_folders():
    os.makedirs(BASELINE_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(CURRENT_DIR, exist_ok=True)

    if not os.path.exists(RESULTS_FILE):
        save_json(RESULTS_FILE, [])


def load_json(file_path, default_value):
    if not os.path.exists(file_path):
        return default_value

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except:
        return default_value


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_results():
    ensure_folders()
    return load_json(RESULTS_FILE, [])


def save_results(results):
    save_json(
        RESULTS_FILE,
        results
    )


def sanitize_filename(text):

    text=text.lower()

    result=""

    for char in text:

        if char.isalnum():
            result+=char

        else:
            result+="_"

    while "__" in result:
        result=result.replace("__","_")

    return result.strip("_")


def get_rendered(value):

    if isinstance(value,dict):
        return value.get("rendered","")

    return value or ""


def get_sorted_list(item,key):

    value=item.get(key,[])

    if isinstance(value,list):
        return sorted(value)

    return []


def filter_media_item(item):

    media_details=item.get(
        "media_details",
        {}
    ) or {}

    filtered_details={

        "width":
        media_details.get("width"),

        "height":
        media_details.get("height"),

        "file":
        media_details.get("file"),

        "filesize":
        media_details.get("filesize"),

        "sizes":
        media_details.get(
            "sizes",
            {}
        )
    }

    return {

        "slug":
        item.get("slug",""),

        "status":
        item.get("status",""),

        "type":
        item.get("type",""),

        "link":
        item.get("link",""),

        "title":
        get_rendered(
            item.get("title")
        ),

        "description":
        get_rendered(
            item.get("description")
        ),

        "caption":
        get_rendered(
            item.get("caption")
        ),

        "alt_text":
        item.get(
            "alt_text",
            ""
        ),

        "media_type":
        item.get(
            "media_type",
            ""
        ),

        "mime_type":
        item.get(
            "mime_type",
            ""
        ),

        "media_details":
        filtered_details
    }


def filter_post_item(item):

    return {

        "slug":
        item.get("slug",""),

        "status":
        item.get("status",""),

        "link":
        item.get("link",""),

        "title":
        get_rendered(
            item.get("title")
        ),

        "excerpt":
        get_rendered(
            item.get("excerpt")
        ),

        "content":
        get_rendered(
            item.get("content")
        ),

        "categories":
        get_sorted_list(
            item,
            "categories"
        ),

        "tags":
        get_sorted_list(
            item,
            "tags"
        )
    }


def filter_page_item(item):

    meta=item.get(
        "meta",
        {}
    ) or {}

    return {

        "slug":
        item.get("slug",""),

        "status":
        item.get("status",""),

        "link":
        item.get("link",""),

        "title":
        get_rendered(
            item.get("title")
        ),

        "excerpt":
        get_rendered(
            item.get("excerpt")
        ),

        "content":
        get_rendered(
            item.get("content")
        ),

        "parent":
        item.get("parent",0),

        "template":
        item.get(
            "template",
            ""
        ),

        "meta":{

            "resource_title":
            meta.get(
                "resource_title",
                ""
            ),

            "pdf_link":
            meta.get(
                "pdf_link",
                ""
            )
        }
    }


def filter_resource_item(item):

    meta=item.get(
        "meta",
        {}
    ) or {}

    return {

        "slug":
        item.get("slug",""),

        "status":
        item.get("status",""),

        "type":
        item.get("type",""),

        "link":
        item.get("link",""),

        "title":
        get_rendered(
            item.get("title")
        ),

        "content":
        get_rendered(
            item.get("content")
        ),

        "meta":{

            "resource_title":
            meta.get(
                "resource_title",
                ""
            )
        }
    }


def filter_items(api_type,items):

    filtered=[]

    for item in items:

        if api_type=="pages":
            filtered.append(
                filter_page_item(item)
            )

        elif api_type=="posts":
            filtered.append(
                filter_post_item(item)
            )

        elif api_type=="media":
            filtered.append(
                filter_media_item(item)
            )

        elif api_type=="resources":
            filtered.append(
                filter_resource_item(item)
            )

    filtered.sort(
        key=lambda x:
        x.get("slug")
        or x.get("link","")
    )

    return filtered


# FIXED FUNCTION
def fetch_all_api_data(api_url):

    all_items=[]

    page=1

    headers={

        "User-Agent":
        "Mozilla/5.0"
    }

    while True:

        paged_url=(
            f"{api_url}"
            f"?per_page=100"
            f"&page={page}"
        )

        try:

            response=requests.get(
                paged_url,
                headers=headers,
                timeout=40,
                allow_redirects=True
            )

        except requests.RequestException as e:

            raise Exception(
                f"Connection Error: {str(e)}"
            )


        if response.status_code==404:

            raise Exception(
                "Endpoint does not exist"
            )


        if response.status_code>=500:

            raise Exception(
                f"Server Error {response.status_code}"
            )


        if response.status_code==400 and page>1:
            break


        content_type=(
            response.headers.get(
                "Content-Type",
                ""
            ).lower()
        )


        if "application/json" not in content_type:

            preview=response.text[:100]

            raise Exception(
                f"Non JSON response: {preview}"
            )


        try:

            data=response.json()

        except:

            raise Exception(
                "Invalid JSON returned"
            )


        if not isinstance(data,list):

            raise Exception(
                "API response is not list"
            )


        if len(data)==0:
            break


        all_items.extend(data)

        total_pages=response.headers.get(
            "X-WP-TotalPages"
        )


        if total_pages:

            if page>=int(total_pages):
                break

        else:

            if len(data)<100:
                break

        page+=1

    return all_items


def item_key(item):

    return (
        item.get("slug")
        or
        item.get("link")
        or
        json.dumps(
            item,
            sort_keys=True
        )
    )


def compare_data(old_data,new_data):

    changes=[]

    old_map={
        item_key(i):i
        for i in old_data
    }

    new_map={
        item_key(i):i
        for i in new_data
    }

    all_keys=(
        set(old_map.keys())
        |
        set(new_map.keys())
    )

    for key in all_keys:

        old_item=old_map.get(key)
        new_item=new_map.get(key)

        if old_item!=new_item:

            changes.append({

                "changed_field":
                key,

                "old_value":
                old_item,

                "new_value":
                new_item
            })

    return changes


def process_api_type(
    website_name,
    website_url,
    api_type,
    results
):

    endpoint=API_TYPES[api_type]

    api_url=(
        website_url.rstrip("/")
        +endpoint
    )

    checked_time=datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    file_key=sanitize_filename(
        f"{website_name}_{api_type}"
    )

    baseline_file=os.path.join(
        BASELINE_DIR,
        f"{file_key}.json"
    )

    current_file=os.path.join(
        CURRENT_DIR,
        f"{file_key}.json"
    )

    try:

        raw_items=fetch_all_api_data(
            api_url
        )

        current_data=filter_items(
            api_type,
            raw_items
        )

    except Exception as error:

        error_text=str(error)

        if (
            "Endpoint does not exist"
            in error_text
            or
            "Non JSON response"
            in error_text
        ):
            return

        results.append({

            "id":
            len(results)+1,

            "website_name":
            website_name,

            "api_type":
            api_type,

            "website_url":
            website_url,

            "api_url":
            api_url,

            "status":
            "API Failed",

            "changed_field":
            "-",

            "old_value":
            "-",

            "new_value":
            error_text,

            "checked_time":
            checked_time,

            "approval_status":
            "Not Required"
        })

        return


    if not os.path.exists(
        baseline_file
    ):

        save_json(
            baseline_file,
            current_data
        )

        results.append({

            "id":
            len(results)+1,

            "website_name":
            website_name,

            "api_type":
            api_type,

            "website_url":
            website_url,

            "api_url":
            api_url,

            "status":
            "Baseline Created",

            "changed_field":
            "-",

            "old_value":
            "-",

            "new_value":
            "-",

            "checked_time":
            checked_time,

            "approval_status":
            "Not Required"
        })

        return

    baseline=load_json(
        baseline_file,
        []
    )

    changes=compare_data(
        baseline,
        current_data
    )

    if changes:

        save_json(
            current_file,
            current_data
        )

        for change in changes:

            results.append({

                "id":
                len(results)+1,

                "website_name":
                website_name,

                "api_type":
                api_type,

                "website_url":
                website_url,

                "api_url":
                api_url,

                "status":
                "Change Detected",

                "changed_field":
                change["changed_field"],

                "old_value":
                change["old_value"],

                "new_value":
                change["new_value"],

                "checked_time":
                checked_time,

                "approval_status":
                "Pending"
            })


def run_monitoring():

    ensure_folders()

    websites=load_json(
        WEBSITES_FILE,
        []
    )

    results=load_results()

    for website in websites:

        website_name=website["name"]

        website_url=website["url"]

        for api_type in API_TYPES:

            process_api_type(
                website_name,
                website_url,
                api_type,
                results
            )

    save_results(results)