# Gunicorn configuration file for Geoportal Flask application
# This file is referenced in entrypoint.sh: gunicorn --config gunicorn.conf.py main:app

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:8874"  # Default port, can be overridden by environment
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"  # sync workers are fine for I/O bound apps
worker_connections = 1000
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "geoportal_gunicorn"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for production)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"
# ssl_version = "TLS"
# cert_reqs = 0
# ca_certs = None
# suppress_ragged_eofs = True
# do_handshake_on_connect = False

# Worker processes
preload_app = True  # Load application before forking workers (saves memory)
max_requests = 1000  # Restart workers after this many requests
max_requests_jitter = 50  # Random jitter to avoid all workers restarting at once

# Debugging
reload = os.getenv("FLASK_DEBUG", "false").lower() == "true"  # Auto-reload on code changes in development
spew = False  # Print every executed Python statement (debug only)

# Server hooks
def post_fork(server, worker):
    server.log.info("Worker %s spawned (pid: %s)", worker.pid, worker.pid)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers...")

def worker_int(worker):
    worker.log.info("Worker %s received INT or QUIT signal", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker %s received SIGABRT signal", worker.pid)

def pre_request(worker, req):
    worker.log.debug("%s %s", req.method, req.path)

def post_request(worker, req, environ, resp):
    pass

def child_exit(server, worker):
    server.log.info("Worker %s exited with status %s", worker.pid, worker.exitcode)

def worker_exit(server, worker):
    server.log.info("Worker %s exiting", worker.pid)

def nworkers_changed(server, new_value, old_value):
    server.log.info("Number of workers changed from %s to %s", old_value, new_value)

def on_exit(server):
    server.log.info("Server exiting")