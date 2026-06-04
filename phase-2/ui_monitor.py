import json
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont, ImageStat
from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from core.playwright_browser import start_browser, new_page
from core.dynamic_filter import remove_dynamic_elements
from core.comparator import compare_images

from config import *


def ensure_dirs():
    os.makedirs(BASELINE_DIR, exist_ok=True)
    os.makedirs(CURRENT_DIR, exist_ok=True)
    os.makedirs(DIFF_DIR, exist_ok=True)
    os.makedirs("results", exist_ok=True)


def resize_to_same(img1_path, img2_path):
    i1 = Image.open(img1_path)
    i2 = Image.open(img2_path)

    w = min(i1.width, i2.width)
    h = min(i1.height, i2.height)

    i1.crop((0, 0, w, h)).save(img1_path)
    i2.crop((0, 0, w, h)).save(img2_path)


def is_blank_screenshot(path):
    try:
        img = Image.open(path).convert("L")
        stat = ImageStat.Stat(img)
        mean = stat.mean[0]
        stddev = stat.stddev[0]
        return mean > 235 and stddev < 6
    except Exception:
        return False


def highlight(image_path, boxes, out_path):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    label_no = 1

    for (x, y, w, h) in boxes:
        if w < 20 or h < 20:
            continue

        draw.rectangle(
            [(x, y), (x + w, y + h)],
            outline="red",
            width=3
        )

        text_y = y - 18 if y > 20 else y + 5
        draw.text((x, text_y), f"Change {label_no}", fill="red", font=font)
        label_no += 1

    img.save(out_path)


def get_page_height(page):
    return page.evaluate("""
        () => {
            const body = document.body;
            const html = document.documentElement;

            if (!body && !html) return 0;

            const heights = [
                body ? body.scrollHeight : 0,
                body ? body.offsetHeight : 0,
                html ? html.clientHeight : 0,
                html ? html.scrollHeight : 0,
                html ? html.offsetHeight : 0
            ];

            return Math.max(...heights);
        }
    """)


def wait_for_complete_render(page):
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2500)

    try:
        page.wait_for_function(
            "() => document.readyState === 'complete'",
            timeout=15000
        )
    except Exception:
        pass

    try:
        page.wait_for_function(
            "() => Array.from(document.images).every(img => img.complete)",
            timeout=20000
        )
    except Exception:
        pass

    try:
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=15000
        )
    except Exception:
        pass

    prev_height = 0

    for _ in range(MAX_SCROLL_STEPS):
        current_height = get_page_height(page)

        if current_height <= 0:
            break

        page.evaluate(f"window.scrollTo(0, {current_height})")
        page.wait_for_timeout(WAIT_TIME_MS)

        if current_height == prev_height:
            break

        prev_height = current_height

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1500)

    page.add_style_tag(content="""
        * {
            animation: none !important;
            transition: none !important;
            scroll-behavior: auto !important;
        }
        video, iframe {
            display: none !important;
        }
    """)

    page.wait_for_timeout(1000)


def capture_full_page_by_stitch(page, out_path):
    screenshots = []

    total_height = get_page_height(page)
    viewport = page.viewport_size or {"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT}
    viewport_height = viewport["height"]

    if total_height <= 0:
        raise RuntimeError("Page height is 0; cannot capture page")

    y = 0
    idx = 0

    while y < total_height:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(700)

        temp_path = out_path.replace(".png", f"__part_{idx}.png")
        page.screenshot(path=temp_path)
        screenshots.append(temp_path)

        y += viewport_height
        idx += 1

    parts = [Image.open(p) for p in screenshots]
    width = parts[0].width
    height = sum(img.height for img in parts)

    stitched = Image.new("RGB", (width, height))

    y_offset = 0
    for img in parts:
        stitched.paste(img, (0, y_offset))
        y_offset += img.height

    stitched.save(out_path)

    for p in screenshots:
        if os.path.exists(p):
            os.remove(p)


def capture_stable_screenshot(page, path):
    capture_full_page_by_stitch(page, path)

    if is_blank_screenshot(path):
        page.wait_for_timeout(SCREENSHOT_RETRY_WAIT_MS)
        capture_full_page_by_stitch(page, path)

    if is_blank_screenshot(path):
        raise RuntimeError("Blank screenshot detected after retry")


def process_page(browser, site, page_name, url):
    context, page = new_page(browser)

    filename = f"{site}_{page_name}".replace(" ", "_").lower() + ".png"

    baseline = os.path.join(BASELINE_DIR, filename)
    current = os.path.join(CURRENT_DIR, filename)
    diff = os.path.join(DIFF_DIR, filename)

    try:
        try:
            page.goto(url, timeout=PAGE_LOAD_TIMEOUT, wait_until="domcontentloaded")
        except PlaywrightTimeoutError as e:
            print(f"Timeout in {site} | {page_name} | {url}: {e}")
            return None
        except PlaywrightError as e:
            print(f"Navigation error in {site} | {page_name} | {url}: {e}")
            return None

        wait_for_complete_render(page)
        remove_dynamic_elements(page)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)

        try:
            capture_stable_screenshot(page, current)
        except Exception as e:
            print(f"Screenshot error in {site} | {page_name} | {url}: {e}")
            return None

        if not os.path.exists(baseline):
            os.replace(current, baseline)
            return None

        resize_to_same(baseline, current)

        _, boxes = compare_images(baseline, current)

        if not boxes:
            if os.path.exists(current):
                os.remove(current)
            return None

        highlight(current, boxes, diff)

        return {
            "website": site,
            "page": page_name,
            "url": url,
            "baseline": f"/screenshots/baseline/{filename}",
            "current": f"/screenshots/current/{filename}",
            "diff": f"/screenshots/diff/{filename}"
        }

    except Exception as e:
        print(f"Error in {site} | {page_name} | {url}: {e}")
        return None

    finally:
        context.close()


def worker(site_data):
    playwright, browser = start_browser()
    results = []

    try:
        site_name = site_data["name"]

        for page_name, url in site_data["pages"].items():
            result = process_page(browser, site_name, page_name, url)
            if result:
                results.append(result)

    finally:
        browser.close()
        playwright.stop()

    return results


def run_monitor():
    ensure_dirs()

    with open("websites.json", "r", encoding="utf-8") as f:
        websites = json.load(f)

    grouped = {}

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(worker, site) for site in websites]

        for future in futures:
            site_results = future.result()

            for item in site_results:
                site_name = item["website"]
                grouped.setdefault(site_name, []).append(item)

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(grouped, f, indent=4)

    return grouped