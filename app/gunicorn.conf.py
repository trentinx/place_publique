# gunicorn.conf.py

# Bind address and port
bind = "0.0.0.0:8080"

# Number of workers (processes)
# common rule = (2 * CPU) + 1
workers = 3

# Type of worker (sync by default, eventlet, gevent if async needed)
worker_class = "sync"

# Timeout (in seconds) before killing a blocked worker
timeout = 300

# Automatically restart workers if code changes (dev only)
reload = True

# Log file locations
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"

# Log level: debug, info, warning, error, critical
loglevel = "info"
