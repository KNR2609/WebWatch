BASELINE_EVENT_PATH = (
    "storage/baselines/event_monitor"
)

BASELINE_API_PATH = (
    "storage/baselines/api_monitor"
)

PENDING_PATH = (
    "storage/pending"
)

CURRENT_PATH = (
    "storage/current"
)

APPROVED_PATH = (
    "storage/approved"
)

REJECTED_PATH = (
    "storage/rejected"
)

EVENT_LOG = (
    "logs/event_monitor.log"
)

API_LOG = (
    "logs/api_monitor.log"
)

FAILURE_LOG = (
    "logs/failures.log"
)

REQUEST_TIMEOUT = 30

MAX_RETRIES = 3

MAX_WORKERS = 10

WEEKDAY_INTERVAL_MINUTES = 40

WEEKEND_RUN_TIMES = [
    "10:00",
    "18:00"
]