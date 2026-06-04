import time
from playwright.sync_api import sync_playwright


class PlaywrightBrowser:

    def capture_screenshot(self, url, path):

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-gpu"
                ]
            )

            context = browser.new_context(
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

            page = context.new_page()

            # Stealth fixes
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });

                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1,2,3,4,5]
                });

                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)

            try:

                # Use LOAD instead of networkidle
                page.goto(
                    url,
                    wait_until="load",
                    timeout=90000
                )

                # Small natural wait
                time.sleep(3)

                # Wait for fonts
                page.evaluate("""
                    () => document.fonts.ready
                """)

                # VERY LIGHT scrolling only
                for _ in range(3):

                    page.mouse.wheel(0, 1200)

                    time.sleep(1.5)

                # Back to top
                page.evaluate("window.scrollTo(0,0)")

                # Wait for images naturally
                time.sleep(5)

                # Wait until most images loaded
                try:

                    page.wait_for_function("""
                        () => {
                            const images = Array.from(document.images);

                            if (images.length === 0)
                                return true;

                            const loaded = images.filter(img => img.complete);

                            return (loaded.length / images.length) > 0.9;
                        }
                    """, timeout=20000)

                except:
                    pass

                # Final stabilization
                time.sleep(3)

                # Screenshot
                page.screenshot(
                    path=path,
                    full_page=True
                )

                print(f"Screenshot saved: {path}")

            except Exception as e:

                print(f"Error on {url}: {e}")

            finally:

                browser.close()