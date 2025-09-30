#!/usr/bin/env python3
#coding: utf-8
# +-------------------------------------------------------------------
# | aaPanel - Gunicorn Configuration with Config Factory
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 aaPanel(www.aapanel.com) All rights reserved.
# +-------------------------------------------------------------------

import os
import multiprocessing
from config_factory import get_config

# Load configuration from config factory
config = get_config()

# ============================================================================
# Server Socket
# ============================================================================
bind = f"0.0.0.0:{config.PORT}"

# IPv6 support (optional)
if os.path.exists('data/ipv6.pl'):
    bind = [f"[::0]:{config.PORT}", f"0.0.0.0:{config.PORT}"]

# ============================================================================
# Worker Processes
# ============================================================================
# حساب عدد العمال بناءً على CPU cores
# القاعدة العامة: (2 × CPU cores) + 1
workers = int(os.getenv('WORKERS', (2 * multiprocessing.cpu_count()) + 1))

# عدد الخيوط لكل عامل
threads = int(os.getenv('THREADS', 3))

# Worker class - دعم WebSocket
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'

# ============================================================================
# Server Mechanics
# ============================================================================
# مجلد العمل (المجلد الحالي)
BASE_DIR = os.getcwd()
chdir = BASE_DIR

# Daemon mode (False للـ systemd)
daemon = False

# PID file
pidfile = os.path.join(BASE_DIR, 'logs', 'panel.pid')

# ============================================================================
# Logging
# ============================================================================
# Log level (من config)
loglevel = 'debug' if config.DEBUG else 'info'

# Access log
accesslog = os.path.join(BASE_DIR, 'logs', 'access.log')

# Error log
errorlog = os.path.join(BASE_DIR, 'logs', 'error.log')

# Capture output
capture_output = True

# Enable stdio inheritance (للـ systemd)
enable_stdio_inheritance = True

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ============================================================================
# Process Naming
# ============================================================================
proc_name = 'aapanel'

# ============================================================================
# Server Performance
# ============================================================================
# Request timeout (2 ساعة للعمليات الطويلة)
timeout = 7200

# Keep-alive timeout
keepalive = 60

# Maximum requests per worker (لمنع memory leak)
max_requests = int(os.getenv('MAX_REQUESTS', 1000))
max_requests_jitter = int(os.getenv('MAX_REQUESTS_JITTER', 50))

# Graceful timeout
graceful_timeout = 30

# Backlog (عدد الاتصالات المعلقة)
backlog = 512

# ============================================================================
# SSL/TLS (optional)
# ============================================================================
if os.path.exists('data/ssl.pl'):
    certfile = 'ssl/certificate.pem'
    keyfile = 'ssl/privateKey.pem'
    ssl_version = 2  # TLSv1.2+
    ciphers = 'TLSv1.2 TLSv1.3'

# ============================================================================
# Application Loading
# ============================================================================
# Preload app (يحسن الأداء لكن يمنع hot reload)
preload_app = not config.DEBUG

# Hot reload (فقط في التطوير)
reload = config.DEBUG

# Reload engine
reload_engine = 'auto'

# ============================================================================
# Worker Lifecycle Hooks
# ============================================================================

def on_starting(server):
    """يُستدعى عند بدء Gunicorn master"""
    print(f"=" * 70)
    print(f"🚀 بدء تشغيل aaPanel - Gunicorn Master")
    print(f"=" * 70)
    print(f"البيئة: {config.ENVIRONMENT}")
    print(f"المنفذ: {config.PORT}")
    print(f"العمال: {workers}")
    print(f"الخيوط: {threads}")
    print(f"وضع التصحيح: {config.DEBUG}")
    print(f"=" * 70)

def on_reload(server):
    """يُستدعى عند إعادة التحميل"""
    print("♻️  إعادة تحميل Gunicorn...")

def when_ready(server):
    """يُستدعى عندما يكون الخادم جاهزاً"""
    print("✅ Gunicorn جاهز لاستقبال الطلبات")

def worker_int(worker):
    """يُستدعى عند مقاطعة عامل"""
    worker.log.info(f"Worker {worker.pid}: تلقى إشارة مقاطعة")

def worker_abort(worker):
    """يُستدعى عند إيقاف عامل"""
    worker.log.warning(f"Worker {worker.pid}: تم إيقافه بشكل غير متوقع")

def pre_fork(server, worker):
    """يُستدعى قبل fork عامل جديد"""
    pass

def post_fork(server, worker):
    """يُستدعى بعد fork عامل جديد"""
    worker.log.info(f"Worker {worker.pid}: بدء العمل")

def worker_exit(server, worker):
    """يُستدعى عند خروج عامل"""
    worker.log.info(f"Worker {worker.pid}: انتهى العمل")

def on_exit(server):
    """يُستدعى عند إيقاف Gunicorn"""
    print("👋 إيقاف aaPanel - Gunicorn")

# ============================================================================
# Security (Production)
# ============================================================================
if config.ENVIRONMENT == 'production':
    # Limit request line size (against DoS)
    limit_request_line = 4094
    
    # Limit request header size
    limit_request_fields = 100
    limit_request_field_size = 8190
    
    # Forward headers (للـ reverse proxy)
    forwarded_allow_ips = '*'
    
    # Secure scheme headers (للـ HTTPS via reverse proxy)
    secure_scheme_headers = {
        'X-FORWARDED-PROTOCOL': 'ssl',
        'X-FORWARDED-PROTO': 'https',
        'X-FORWARDED-SSL': 'on'
    }

# ============================================================================
# Development Settings
# ============================================================================
if config.DEBUG:
    # Reload on code changes
    reload = True
    reload_extra_files = [
        'BTPanel/__init__.py',
        'config_factory.py',
        'environment_detector.py'
    ]
    
    # Debug logging
    loglevel = 'debug'
    
    # Single worker for debugging
    workers = 1
    threads = 1
