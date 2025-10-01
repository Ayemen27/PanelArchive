#!/usr/bin/env python3
# coding: utf-8
"""
Health & Readiness Endpoints
نقاط نهاية فحص الصحة والجاهزية للتطبيق

المسارات:
- /health/live - Liveness probe (يرجع دائماً 200 OK)
- /health/ready - Readiness probe (يفحص DB + Redis)
- /metrics - Prometheus metrics
"""

import time
import psutil
from datetime import datetime
from flask import jsonify, Blueprint
from typing import Dict, Any, Tuple

health_bp = Blueprint('health', __name__, url_prefix='/health')

app_start_time = time.time()

try:
    from config_factory import get_config
    config = get_config()
except ImportError:
    config = None

try:
    from db_pool import DatabaseConnectionPool
    db_pool = DatabaseConnectionPool(config=config)
except ImportError:
    db_pool = None


def get_uptime() -> float:
    """الحصول على uptime التطبيق بالثواني"""
    return time.time() - app_start_time


def check_database() -> Tuple[bool, str]:
    """
    فحص اتصال قاعدة البيانات
    
    Returns:
        Tuple[bool, str]: (حالة الصحة, رسالة)
    """
    if not db_pool:
        return False, "Database pool not available"
    
    try:
        is_healthy = db_pool.health_check()
        if is_healthy:
            return True, "Database connected"
        else:
            return False, "Database connection failed"
    except Exception as e:
        return False, f"Database error: {str(e)}"


def check_redis() -> Tuple[bool, str]:
    """
    فحص اتصال Redis
    
    Returns:
        Tuple[bool, str]: (حالة الصحة, رسالة)
    """
    if not config:
        return True, "Redis check skipped (no config)"
    
    redis_url = getattr(config, 'CACHE_REDIS_URL', None)
    if not redis_url:
        return True, "Redis not configured"
    
    try:
        import redis
        r = redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        return True, "Redis connected"
    except ImportError:
        return True, "Redis library not available"
    except Exception as e:
        return False, f"Redis error: {str(e)}"


@health_bp.route('/live', methods=['GET'])
def liveness():
    """
    Liveness Probe - يتحقق من أن التطبيق يعمل
    يرجع دائماً 200 OK إذا كان التطبيق قيد التشغيل
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': get_uptime()
    }), 200


@health_bp.route('/ready', methods=['GET'])
def readiness():
    """
    Readiness Probe - يتحقق من أن التطبيق جاهز لاستقبال الطلبات
    يفحص DB + Redis ويرجع 200 أو 503
    """
    checks = {}
    all_healthy = True
    
    db_healthy, db_message = check_database()
    checks['database'] = {
        'status': 'healthy' if db_healthy else 'unhealthy',
        'message': db_message
    }
    all_healthy = all_healthy and db_healthy
    
    redis_healthy, redis_message = check_redis()
    checks['redis'] = {
        'status': 'healthy' if redis_healthy else 'unhealthy',
        'message': redis_message
    }
    all_healthy = all_healthy and redis_healthy
    
    response = {
        'status': 'ready' if all_healthy else 'not_ready',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': get_uptime(),
        'checks': checks
    }
    
    status_code = 200 if all_healthy else 503
    return jsonify(response), status_code


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus Metrics - إحصائيات ومقاييس التطبيق
    """
    metrics_data = {
        'uptime_seconds': get_uptime(),
        'timestamp': datetime.utcnow().isoformat(),
        'system': {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    }
    
    if db_pool and hasattr(db_pool, 'stats'):
        db_stats = db_pool.stats.get_stats()
        metrics_data['database'] = {
            'connections_created': db_stats.get('connections_created', 0),
            'connections_closed': db_stats.get('connections_closed', 0),
            'total_queries': db_stats.get('total_queries', 0),
            'failed_queries': db_stats.get('failed_queries', 0),
            'success_rate': db_stats.get('success_rate', 100.0)
        }
        
        db_healthy, _ = check_database()
        metrics_data['database']['status'] = 'up' if db_healthy else 'down'
    
    redis_healthy, _ = check_redis()
    metrics_data['redis'] = {
        'status': 'up' if redis_healthy else 'down'
    }
    
    return jsonify(metrics_data), 200


def register_health_routes(app):
    """
    تسجيل health routes مع Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(health_bp)
