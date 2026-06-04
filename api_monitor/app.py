from flask import Flask, render_template, redirect, url_for, jsonify
from concurrent.futures import ThreadPoolExecutor

from utils import (
    ensure_folders,
    load_results,
    save_results,
    clear_results,
    approve_change,
    reject_change
)

from pages import run_pages_monitor
from posts import run_posts_monitor
from media import run_media_monitor
from resources import run_resources_monitor

app = Flask(__name__)

ensure_folders()

is_running = False


@app.route("/")
def index():
    results = load_results()
    return render_template(
        "index.html",
        results=results,
        is_running=is_running
    )


@app.route("/run")
def run():
    global is_running

    if is_running:
        return redirect(url_for("index"))

    is_running = True

    try:

        # CLEAR PREVIOUS RUN RESULTS
        clear_results()

        results = []

        monitor_functions = [
            run_pages_monitor,
            run_posts_monitor,
            run_media_monitor,
            run_resources_monitor
        ]

        with ThreadPoolExecutor(max_workers=4) as executor:

            futures = []

            for monitor_function in monitor_functions:

                futures.append(
                    executor.submit(
                        monitor_function,
                        results
                    )
                )

            for future in futures:
                future.result()

        save_results(results)

    finally:
        is_running = False

    return redirect(url_for("index"))


@app.route("/status")
def status():
    return jsonify({"is_running": is_running})


@app.route("/approve/<int:result_id>")
def approve(result_id):
    approve_change(result_id)
    return redirect(url_for("index"))


@app.route("/reject/<int:result_id>")
def reject(result_id):
    reject_change(result_id)
    return redirect(url_for("index"))

#test
if __name__ == "__main__":
    app.run(
        debug=True,
        port=5004,
        threaded=True
    )
