#!/usr/bin/env python3
# coding: utf-8
"""
اختبارات Health & Readiness Endpoints
Tests for health check endpoints
"""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    """إنشاء Flask test client"""
    try:
        from BTPanel import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    except ImportError:
        pytest.skip("Flask app not available")


class TestHealthEndpoints:
    """اختبارات نقاط نهاية الصحة"""
    
    def test_liveness_endpoint(self, client):
        """اختبار /health/live - يجب أن يرجع 200 OK دائماً"""
        response = client.get('/health/live')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'alive'
        assert 'timestamp' in data
        assert 'uptime_seconds' in data
        assert isinstance(data['uptime_seconds'], (int, float))
        assert data['uptime_seconds'] >= 0
    
    def test_readiness_endpoint(self, client):
        """اختبار /health/ready - يفحص DB + Redis"""
        response = client.get('/health/ready')
        
        assert response.status_code in [200, 503]
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] in ['ready', 'not_ready']
        assert 'timestamp' in data
        assert 'uptime_seconds' in data
        assert 'checks' in data
        
        checks = data['checks']
        assert 'database' in checks
        assert 'redis' in checks
        
        for service in ['database', 'redis']:
            assert 'status' in checks[service]
            assert checks[service]['status'] in ['healthy', 'unhealthy']
            assert 'message' in checks[service]
    
    def test_metrics_endpoint(self, client):
        """اختبار /metrics - Prometheus metrics"""
        response = client.get('/health/metrics')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'uptime_seconds' in data
        assert 'timestamp' in data
        assert 'system' in data
        
        system = data['system']
        assert 'cpu_percent' in system
        assert 'memory_percent' in system
        assert 'disk_percent' in system
        
        assert isinstance(system['cpu_percent'], (int, float))
        assert 0 <= system['cpu_percent'] <= 100
        assert isinstance(system['memory_percent'], (int, float))
        assert 0 <= system['memory_percent'] <= 100
        
        if 'database' in data:
            db = data['database']
            assert 'status' in db
            assert db['status'] in ['up', 'down']
            assert 'connections_created' in db
            assert 'total_queries' in db
        
        if 'redis' in data:
            redis = data['redis']
            assert 'status' in redis
            assert redis['status'] in ['up', 'down']
    
    def test_readiness_when_healthy(self, client):
        """اختبار readiness عندما تكون الخدمات صحية"""
        response = client.get('/health/ready')
        data = json.loads(response.data)
        
        if data['status'] == 'ready':
            assert response.status_code == 200
            for service, check in data['checks'].items():
                assert check['status'] == 'healthy'
    
    def test_readiness_when_unhealthy(self, client):
        """اختبار readiness عندما تكون الخدمات غير صحية"""
        response = client.get('/health/ready')
        data = json.loads(response.data)
        
        if data['status'] == 'not_ready':
            assert response.status_code == 503
            has_unhealthy = False
            for service, check in data['checks'].items():
                if check['status'] == 'unhealthy':
                    has_unhealthy = True
                    break
            assert has_unhealthy, "Status is not_ready but no unhealthy service found"
    
    def test_all_endpoints_return_json(self, client):
        """التأكد من أن جميع endpoints ترجع JSON"""
        endpoints = ['/health/live', '/health/ready', '/health/metrics']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.content_type == 'application/json'
            
            data = json.loads(response.data)
            assert isinstance(data, dict)
    
    def test_endpoints_performance(self, client):
        """اختبار أداء endpoints - يجب أن تكون سريعة"""
        import time
        
        endpoints = ['/health/live', '/health/ready', '/health/metrics']
        
        for endpoint in endpoints:
            start = time.time()
            response = client.get(endpoint)
            duration = time.time() - start
            
            assert response.status_code in [200, 503]
            assert duration < 5.0, f"{endpoint} took {duration}s - too slow!"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
