import os

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    jsonify
)

from utils.file_utils import load_json

from monitors.approval_manager import (
    approve_changes,
    reject_changes
)

PENDING_PATH = "storage/pending"


def register_routes(app):

    @app.route("/pending-changes")
    @app.route("/pending-cganges")
    @app.route("/api/pending-changes")
    @app.route("/api/pending-cganges")
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

        if request.path.startswith("/api/"):
            return jsonify(pending_data)

        return render_template(
            "dashboard.html",
            pending_data=pending_data
        )

    @app.route("/pending/<filename>")
    @app.route("/api/pending/<filename>")
    def pending_details(filename):

        file_path = os.path.join(
            PENDING_PATH,
            filename
        )

        data = load_json(
            file_path,
            default=[]
        )

        if request.path.startswith("/api/"):
            return jsonify(data)

        return render_template(
            "pending_changes.html",
            filename=filename,
            data=data
        )

    @app.route("/approve/<filename>")
    @app.route("/api/approve/<filename>")
    def approve(filename):

        filename_clean = filename.replace(
            ".json",
            ""
        )

        parts = filename_clean.split("_")

        website_name = "_".join(
            parts[:-1]
        )

        api_name = parts[-1]

        approve_changes(
            website_name,
            api_name
        )

        if request.path.startswith("/api/"):
            return jsonify({"status": "success", "message": f"Approved changes for {filename}"})

        return redirect(
            url_for("dashboard")
        )

    @app.route("/reject/<filename>")
    @app.route("/api/reject/<filename>")
    def reject(filename):

        filename_clean = filename.replace(
            ".json",
            ""
        )

        parts = filename_clean.split("_")

        website_name = "_".join(
            parts[:-1]
        )

        api_name = parts[-1]

        reject_changes(
            website_name,
            api_name
        )

        if request.path.startswith("/api/"):
            return jsonify({"status": "success", "message": f"Rejected changes for {filename}"})

        return redirect(
            url_for("dashboard")
        )

    @app.route("/logs")
    @app.route("/api/logs")
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

        if request.path.startswith("/api/"):
            return jsonify({"logs": logs_data})

        return render_template(
            "logs.html",
            logs=logs_data
        )