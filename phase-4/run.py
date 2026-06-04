import threading
import time

from monitors.scheduler import (
    run_scheduler
)

from dashboard.app import app


def scheduler_loop():

    while True:

        print(
            "Running Scheduler..."
        )

        try:

            run_scheduler()

            print(
                "Scheduler Completed"
            )

        except Exception as error:

            print(
                f"Scheduler Error: "
                f"{str(error)}"
            )

        # 30 MINUTES
        time.sleep(3 * 60)


if __name__ == "__main__":

    scheduler_thread = threading.Thread(
        target=scheduler_loop,
        daemon=True
    )

    scheduler_thread.start()

    app.run(
        debug=True,
        port=5000
    )