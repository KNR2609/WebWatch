import os

# Create directories if they don't exist
DIRS = [
    'data/screenshots/baseline',
    'data/screenshots/current',
    'data/screenshots/diff',
    'results'
]

for d in DIRS:
    os.makedirs(d, exist_ok=True)

CONFIG = {
    "VIEWPORT": {"width": 1920, "height": 1080},
    "SSIM_THRESHOLD": 0.95,
    "CHANGES_JSON": "results/changes.json",
    "WEBSITES_JSON": "websites.json"
}