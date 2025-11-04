import os
import logging
import psutil
from flask import Flask, jsonify
from prometheus_client import Counter, Gauge, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# -------------------------------------------------------
# Logging setup
# -------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Flask application setup
# -------------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------------
# Environment configuration
# -------------------------------------------------------
app_version = os.getenv("APP_VERSION", "1.0")
app_title = os.getenv("APP_TITLE", "Devops for Cloud Assignment")

# When running inside Kubernetes, HOSTNAME reflects the pod name
pod_identifier = os.getenv("HOSTNAME", "local-machine")

# -------------------------------------------------------
# Prometheus metrics setup
# -------------------------------------------------------
request_counter = Counter(
    "get_info_requests_total",
    "Count of requests received on /get_info endpoint",
    ["pod_name"]
)

cpu_usage = Gauge(
    "application_cpu_usage_percent",
    "Percentage of CPU used by the application",
    ["pod_name"]
)

memory_usage = Gauge(
    "application_memory_usage_percent",
    "Percentage of memory used by the application",
    ["pod_name"]
)

# -------------------------------------------------------
# Flask route - core business logic
# -------------------------------------------------------
@app.route("/get_info")
def get_info():
    """Handles the main endpoint returning version and host info."""
    logger.info(f"Processing request on pod: {pod_identifier}")

    # Update Prometheus metrics
    request_counter.labels(pod_name=pod_identifier).inc()
    cpu_usage.labels(pod_name=pod_identifier).set(psutil.cpu_percent(interval=None))
    memory_usage.labels(pod_name=pod_identifier).set(psutil.virtual_memory().percent)

    response_data = {
        "APP_VERSION": app_version,
        "APP_TITLE": app_title,
        "served_by": pod_identifier
    }

    return jsonify(response_data)

# -------------------------------------------------------
# Prometheus metrics endpoint integration
# -------------------------------------------------------
app_dispatch = DispatcherMiddleware(app, {
    "/metrics": make_wsgi_app()
})

# -------------------------------------------------------
# Local execution (for development / testing)
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
