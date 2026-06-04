import os

from flask import (
    render_template,
    redirect,
    url_for
)

from utils.file_utils import load_json

from monitors.approval_manager import (
    approve_changes,
    reject_changes
)

PENDING_PATH = "storage/pending"


def register_routes(app):

    @app.route("/")
    def dashboard():

        pending_files = []

        if os.path.exists(PENDING_PATH):

            pending_files = os.listdir(
                PENDING_PATH
            )

        pending_data = []

        for file in pending_files:

            file_path = os.path.join(
                PENDING_PATH,
                file
            )

            data = load_json(
                file_path,
                default=[]
            )

            pending_data.append({
                "file": file,
                "changes_count": len(data)
            })

        return render_template(
            "dashboard.html",
            pending_data=pending_data
        )

    @app.route("/pending/<filename>")
    def pending_details(filename):

        file_path = os.path.join(
            PENDING_PATH,
            filename
        )

        data = load_json(
            file_path,
            default=[]
        )

        return render_template(
            "pending_changes.html",
            filename=filename,
            data=data
        )

    @app.route("/approve/<filename>")
    def approve(filename):

        filename = filename.replace(
            ".json",
            ""
        )

        parts = filename.split("_")

        website_name = "_".join(
            parts[:-1]
        )

        api_name = parts[-1]

        approve_changes(
            website_name,
            api_name
        )

        return redirect(
            url_for("dashboard")
        )

    @app.route("/reject/<filename>")
    def reject(filename):

        filename = filename.replace(
            ".json",
            ""
        )

        parts = filename.split("_")

        website_name = "_".join(
            parts[:-1]
        )

        api_name = parts[-1]

        reject_changes(
            website_name,
            api_name
        )

        return redirect(
            url_for("dashboard")
        )

    @app.route("/logs")
    def logs():

        log_file = (
            "logs/api_monitor.log"
        )

        try:

            with open(
                log_file,
                "r",
                encoding="utf-8"
            ) as file:

                logs_data = file.read()

        except Exception:

            logs_data = (
                "Unable to load logs"
            )

        return render_template(
            "logs.html",
            logs=logs_data
        )