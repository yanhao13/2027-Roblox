import time
from functools import wraps
from prometheus_client import Counter, Histogram

AGENT_LATENCY = Histogram(
    "matcha_agent_execution_latency_seconds",
    "Time spent inside each specific multi-agent boundary layer.",
    ["agent_name"]
)
PIPELINE_REQUESTS = Counter(
    "matcha_pipeline_requests_total",
    "Total volume of user requests handled by the MATCHA ecosystem.",
    ["status"]
)


def track_agent_latency(agent_name: str):
    """Decorator to measure and record execution times for individual agents."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.perf_counter() - start_time
                AGENT_LATENCY.labels(agent_name=agent_name).observe(duration)
        return wrapper
    return decorator
