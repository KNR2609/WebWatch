import os

PHASE_2_ROOT = os.path.dirname(os.path.abspath(__file__))

# Create directories if they don't exist
DIRS = [
    os.path.join(PHASE_2_ROOT, 'data/screenshots/baseline'),
    os.path.join(PHASE_2_ROOT, 'data/screenshots/current'),
    os.path.join(PHASE_2_ROOT, 'data/screenshots/diff'),
    os.path.join(PHASE_2_ROOT, 'data/text/baseline'),
    os.path.join(PHASE_2_ROOT, 'data/text/current'),
    os.path.join(PHASE_2_ROOT, 'results')
]

for d in DIRS:
    os.makedirs(d, exist_ok=True)

CONFIG = {
    "PHASE_2_ROOT": PHASE_2_ROOT,
    "VIEWPORT": {"width": 1920, "height": 1080},
    "SSIM_THRESHOLD": 0.95,
    "CHANGES_JSON": os.path.join(PHASE_2_ROOT, "results", "changes.json"),
    "WEBSITES_JSON": os.path.join(PHASE_2_ROOT, "websites.json")
}
