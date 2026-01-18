from kombu import Exchange, Queue


class CeleryConfig:
    # Broker & Backend
    broker_connection_retry_on_startup = True
    broker_connection_retry = True
    broker_connection_max_retries = 3

    # Serialization
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]

    # Time
    timezone = "UTC"
    enable_utc = True

    # Exchanges
    hh_parsing_exchange = Exchange("hh_parsing", type="direct", durable=True)

    # Queues
    task_queues = (
        Queue(
            "hh_parsing_queue",
            hh_parsing_exchange,
            routing_key="parsing",
            durable=True,
        ),
    )

    # Routing

    task_routes = {
        "process_job_application": {
            "queue": "hh_parsing_queue",
            "routing_key": "parsing",
        },
    }

    # Task Execution
    task_acks_late = True
    worker_prefetch_multiplier = 1
    task_reject_on_worker_lost = False
    task_ignore_result = False

    # Task Tracking
    task_track_started = True

    # Result Backend
    result_expires = 3600
    result_backend_transport_options = {"retry_policy": {"timeout": 5.0}}

    # Timeouts
    task_soft_time_limit = 2400
    task_time_limit = 3600

    # Worker settings
    worker_max_tasks_per_child = 2000
    worker_disable_rate_limits = False

    # Logging
    worker_log_format = (
        "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
    )
    worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s/%(task_id)s] %(message)s"

    # Events
    worker_send_task_events = True
    task_send_sent_event = True
