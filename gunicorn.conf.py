import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WEB_CONCURRENCY', 1))
threads = int(os.environ.get('PYTHON_MAX_THREADS', 1))
worker_class = "sync"
timeout = 30
