import os
import sys
import threading
import time
import jinja2

# Set up paths so python can import from both phases
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'phase-1'))
sys.path.insert(0, os.path.join(project_root, 'phase-4'))

# Change working directory to phase-4 so its relative storage and log paths resolve correctly
os.chdir(os.path.join(project_root, 'phase-4'))

# Import the phase-1 Flask application and monitoring runner
# (This also automatically starts the phase-1 background scheduler)
from app import app as unified_app, run_monitoring  # type: ignore # noqa: E402

# Set up ChoiceLoader to resolve templates from both phase-1 and phase-4
phase_1_templates = os.path.join(project_root, 'phase-1', 'templates')
phase_4_templates = os.path.join(project_root, 'phase-4', 'dashboard', 'templates')

unified_app.jinja_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader(phase_1_templates),
    jinja2.FileSystemLoader(phase_4_templates)
])

# Set static folder to phase-4 dashboard's static directory
phase_4_static = os.path.join(project_root, 'phase-4', 'dashboard', 'static')
unified_app.static_folder = phase_4_static

# Register phase-4 routes on the unified Flask app
# (Note: we modified the dashboard route in phase-4 to '/pending-changes' to avoid collision with phase-1's homepage)
from dashboard.routes import register_routes as register_phase_4_routes  # type: ignore # noqa: E402
register_phase_4_routes(unified_app)

# Load and register phase-2 routes dynamically to avoid naming conflict with phase-1's app.py
import importlib.util
phase_2_path = os.path.join(project_root, 'phase-2')
sys.path.insert(0, phase_2_path)
spec = importlib.util.spec_from_file_location("phase_2_app", os.path.join(phase_2_path, "app.py"))
phase_2_app = importlib.util.module_from_spec(spec)
sys.modules["phase_2_app"] = phase_2_app
spec.loader.exec_module(phase_2_app)
sys.path.remove(phase_2_path)

phase_2_app.register_routes(unified_app)

# Phase-4 Scheduler loop
from monitors.scheduler import run_scheduler  # type: ignore # noqa: E402

def phase_4_scheduler_loop():
    while True:
        print("Running Phase-4 Scheduler...")
        try:
            run_scheduler()
            print("Phase-4 Scheduler Completed")
        except Exception as error:
            print(f"Phase-4 Scheduler Error: {str(error)}")
        
        # Run every 3 minutes (matching phase-4 run.py time.sleep)
        time.sleep(3 * 60)

# Start Phase-4 scheduler in a background daemon thread
scheduler_thread = threading.Thread(
    target=phase_4_scheduler_loop,
    daemon=True
)
scheduler_thread.start()

if __name__ == "__main__":
    # Run Phase-1 monitoring once on startup
    print("Running initial Phase-1 monitoring...")
    run_monitoring()

    print("Starting unified WebWatch project on http://localhost:5000")
    # Run server on port 5000, disabling reloader to prevent duplicate scheduler background threads
    unified_app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
