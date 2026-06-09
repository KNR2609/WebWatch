import json
from flask import Flask, render_template
from flask_cors import CORS
from monitor import check_website
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
CORS(app)

# Global variable to store latest monitoring results
latest_results = []


def run_monitoring():
    global latest_results

    with open("sites.json") as f:
        sites = json.load(f)

    results = []

    # Multithreading (10 workers)
    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = [
            executor.submit(check_website, site["name"], site["url"])
            for site in sites
        ]

        for future in as_completed(futures):
            results.append(future.result())

    latest_results = results
    print("Monitoring executed for all sites")


# Scheduler → runs every 10 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(run_monitoring, "interval", minutes=10)
scheduler.start()


@app.route("/")
def home():

    stats = {
        "total": len(latest_results),
        "good": 0,
        "slow": 0,
        "veryslow": 0,
        "serverdown": 0,
        "websitedown": 0
    }

    for site in latest_results:

        if site.status == "Good":
            stats["good"] += 1

        elif site.status == "Slow":
            stats["slow"] += 1

        elif site.status == "Very Slow":
            stats["veryslow"] += 1

        elif site.status == "Server Down":
            stats["serverdown"] += 1

        elif site.status == "Website Down":
            stats["websitedown"] += 1

    return render_template(
        "index.html",
        results=latest_results,
        stats=stats
    )


@app.route("/api/monitor")
def get_monitor_data():
    stats = {
        "total": len(latest_results),
        "good": 0,
        "slow": 0,
        "veryslow": 0,
        "serverdown": 0,
        "websitedown": 0
    }

    results_list = []
    for index, site in enumerate(latest_results):
        if site.status == "Good":
            stats["good"] += 1
        elif site.status == "Slow":
            stats["slow"] += 1
        elif site.status == "Very Slow":
            stats["veryslow"] += 1
        elif site.status == "Server Down":
            stats["serverdown"] += 1
        elif site.status == "Website Down":
            stats["websitedown"] += 1

        results_list.append({
            "id": f"site-{index}",
            "name": site.name,
            "url": site.url,
            "status": site.status,
            "responseTime": round(site.response_time, 2) if site.response_time is not None else None,
            "httpCode": site.status_code if site.status_code is not None else None,
            "httpMessage": site.http_message if site.http_message is not None else "N/A"
        })

    return {
        "results": results_list,
        "stats": stats
    }


if __name__ == "__main__":

    # Run monitoring once when server starts
    run_monitoring()

    app.run(host="0.0.0.0", port=5000, debug=True)