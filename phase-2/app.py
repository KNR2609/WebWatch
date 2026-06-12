from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
import shutil
import threading
import asyncio
from playwright.async_api import async_playwright
from core.comparator import ImageComparator
from phase2_config import CONFIG, PHASE_2_ROOT

app = Flask(__name__)
is_running = False
currently_testing = []
results_lock = threading.Lock()
testing_lock = threading.Lock()

async def async_background_task():
    global is_running, currently_testing
    
    try:
        with open(CONFIG["WEBSITES_JSON"], 'r', encoding='utf-8') as f:
            website_list = json.load(f)

        results = {}
        if os.path.exists(CONFIG["CHANGES_JSON"]):
            try:
                with open(CONFIG["CHANGES_JSON"], 'r', encoding='utf-8') as f:
                    results = json.load(f)
            except Exception as e:
                print(f"Failed to load existing changes: {e}")

        # Limit concurrency to 5 sites at a time
        sem = asyncio.Semaphore(5)
        comp = ImageComparator()

        async with async_playwright() as p:
            # Launch a single browser instance for all tasks
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-gpu"
                ]
            )

            async def process_site(site_data):
                async with sem:
                    site_name = site_data["name"]
                    pages = site_data["pages"]
                    changes_found = []

                    # Add to currently_testing list
                    with testing_lock:
                        currently_testing.append(site_name)

                    try:
                        # Create an isolated browser context for this site
                        context = await browser.new_context(
                            viewport={"width": 1920, "height": 1080},
                            user_agent=(
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/122.0.0.0 Safari/537.36"
                            ),
                            locale="en-US",
                            timezone_id="Asia/Kolkata",
                            java_script_enabled=True,
                            ignore_https_errors=True
                        )

                        for page_name, url in pages.items():
                            page = await context.new_page()
                            # Apply stealth fixes
                            await page.add_init_script("""
                                Object.defineProperty(navigator, 'webdriver', {
                                    get: () => undefined
                                });
                            """)
                            
                            clean_name = f"{site_name}_{page_name}".replace(" ", "_")
                            b_path_abs = os.path.join(PHASE_2_ROOT, "data", "screenshots", "baseline", f"{clean_name}.png")
                            c_path_abs = os.path.join(PHASE_2_ROOT, "data", "screenshots", "current", f"{clean_name}.png")
                            d_path_abs = os.path.join(PHASE_2_ROOT, "data", "screenshots", "diff", f"{clean_name}.png")
                            
                            b_path_rel = f"data/screenshots/baseline/{clean_name}.png"
                            c_path_rel = f"data/screenshots/current/{clean_name}.png"
                            d_path_rel = f"data/screenshots/diff/{clean_name}.png"
                            
                            try:
                                await page.goto(url, wait_until="load", timeout=90000)
                                await asyncio.sleep(3)
                                # Wait for fonts
                                await page.evaluate("() => document.fonts.ready")
                                
                                # Scroll down and back up to trigger dynamic image loads
                                for _ in range(3):
                                    await page.mouse.wheel(0, 1200)
                                    await asyncio.sleep(1.5)
                                
                                await page.evaluate("window.scrollTo(0,0)")
                                await asyncio.sleep(5)
                                
                                # Wait for lazy loaded images
                                try:
                                    await page.wait_for_function("""
                                        () => {
                                            const images = Array.from(document.images);
                                            if (images.length === 0) return true;
                                            const loaded = images.filter(img => img.complete);
                                            return (loaded.length / images.length) > 0.9;
                                        }
                                    """, timeout=20000)
                                except:
                                    pass
                                
                                await asyncio.sleep(3)
                                await page.screenshot(path=c_path_abs, full_page=True)
                                
                            except Exception as e:
                                print(f"Error capturing screenshot for {site_name} - {page_name}: {e}")
                                continue
                            finally:
                                await page.close()
                                
                            if os.path.exists(c_path_abs):
                                if not os.path.exists(b_path_abs):
                                    try:
                                        shutil.copy(c_path_abs, b_path_abs)
                                    except Exception as e:
                                        print(f"Error setting baseline for {site_name} - {page_name}: {e}")
                                    continue

                                try:
                                    changed, score = comp.compare(b_path_abs, c_path_abs, d_path_abs)
                                    if changed:
                                        changes_found.append({
                                            "page": page_name,
                                            "url": url,
                                            "score": round(score, 4),
                                            "baseline": b_path_rel,
                                            "current": c_path_rel,
                                            "diff": d_path_rel
                                        })
                                except Exception as e:
                                    print(f"Error comparing screenshots for {site_name} - {page_name}: {e}")

                        await context.close()

                    except Exception as e:
                        print(f"Error processing site {site_name}: {e}")
                    finally:
                        # Remove from currently_testing
                        with testing_lock:
                            if site_name in currently_testing:
                                currently_testing.remove(site_name)

                    # Update results file incrementally as soon as this site completes
                    with results_lock:
                        if changes_found:
                            results[site_name] = changes_found
                        else:
                            if site_name in results:
                                del results[site_name]

                        try:
                            with open(CONFIG["CHANGES_JSON"], "w", encoding='utf-8') as f:
                                json.dump(results, f, indent=4)
                        except Exception as e:
                            print(f"Failed to write changes.json: {e}")

            # Run all site tasks concurrently inside the event loop
            tasks = [process_site(site) for site in website_list]
            await asyncio.gather(*tasks)
            await browser.close()

    except Exception as e:
        print(f"Error in background task: {e}")
    finally:
        is_running = False
        with testing_lock:
            currently_testing.clear()

def background_task():
    asyncio.run(async_background_task())

def register_routes(flask_app):
    @flask_app.route('/data/screenshots/<path:subdir>/<filename>')
    def serve_screenshot(subdir, filename):
        screenshot_dir = os.path.join(PHASE_2_ROOT, 'data', 'screenshots', subdir)
        return send_from_directory(screenshot_dir, filename)

    @flask_app.route('/api/phase-2/status')
    def get_status():
        global is_running, currently_testing
        return jsonify({
            "running": is_running,
            "currently_testing": list(currently_testing)
        })

    @flask_app.route('/api/phase-2/run', methods=['POST'])
    def run_monitor():
        global is_running
        if is_running: 
            return jsonify({"status": "busy"}), 400
        
        is_running = True
        task = threading.Thread(target=background_task, daemon=True)
        task.start()
        return jsonify({"status": "started"})

    @flask_app.route('/api/dp-issues')
    def get_results():
        try:
            with open(CONFIG["WEBSITES_JSON"], 'r', encoding='utf-8') as f:
                websites_list = json.load(f)
        except Exception as e:
            return jsonify({"error": f"Failed to load websites: {e}"}), 500

        changes = {}
        if os.path.exists(CONFIG["CHANGES_JSON"]):
            try:
                with open(CONFIG["CHANGES_JSON"], 'r', encoding='utf-8') as f:
                    changes = json.load(f)
            except Exception as e:
                print(f"Failed to load changes: {e}")

        results = []
        for index, site in enumerate(websites_list):
            site_name = site["name"]
            pages = site.get("pages", {})
            site_url = pages.get("home", next(iter(pages.values())) if pages else f"https://{site_name.lower().replace(' ', '')}.com")
            site_changes = changes.get(site_name, [])

            issues = []
            for issue_idx, change in enumerate(site_changes):
                base_url = request.host_url
                if not base_url.endswith('/'):
                    base_url += '/'
                issues.append({
                    "id": f"issue-screenshot-{index}-{issue_idx}",
                    "page": change["page"],
                    "type": "screenshot",
                    "status": "pending",
                    "baselineScreenshot": f"{base_url}{change['baseline']}",
                    "currentScreenshot": f"{base_url}{change['current']}",
                    "differenceScreenshot": f"{base_url}{change['diff']}",
                })

            results.append({
                "id": f"website-{index}",
                "name": site_name,
                "url": site_url,
                "totalIssues": len(issues),
                "issues": issues
            })

        return jsonify(results)

    @flask_app.route('/api/phase-2/action', methods=['POST'])
    def handle_action():
        data = request.json
        action = data.get('action')
        website_name = data.get('website')
        page_name = data.get('page')
        
        clean_name = f"{website_name}_{page_name}".replace(" ", "_")
        baseline_abs = os.path.join(PHASE_2_ROOT, "data", "screenshots", "baseline", f"{clean_name}.png")
        current_abs = os.path.join(PHASE_2_ROOT, "data", "screenshots", "current", f"{clean_name}.png")
        diff_abs = os.path.join(PHASE_2_ROOT, "data", "screenshots", "diff", f"{clean_name}.png")

        if action == 'approve':
            if os.path.exists(current_abs):
                shutil.move(current_abs, baseline_abs)
        else:
            if os.path.exists(current_abs):
                os.remove(current_abs)
        
        if os.path.exists(diff_abs): 
            os.remove(diff_abs)
        
        # Update changes.json
        changes_file = CONFIG["CHANGES_JSON"]
        if os.path.exists(changes_file):
            try:
                with open(changes_file, 'r', encoding='utf-8') as f:
                    changes = json.load(f)
                
                if website_name in changes:
                    new_site_changes = [c for c in changes[website_name] if c.get('page') != page_name]
                    if new_site_changes:
                        changes[website_name] = new_site_changes
                    else:
                        del changes[website_name]
                        
                    with open(changes_file, 'w', encoding='utf-8') as f:
                        json.dump(changes, f, indent=4)
            except Exception as e:
                print(f"Error updating changes.json: {e}")
                
        return jsonify({"status": "success"})

# Register routes to the local app if run directly
register_routes(app)

if __name__ == '__main__':
    print("\n🚀 UI MONITOR: http://127.0.0.1:5001\n")
    app.run(debug=True, port=5001, use_reloader=False)