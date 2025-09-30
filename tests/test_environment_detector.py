# coding: utf-8
"""
اختبارات كاشف البيئة - Environment Detector Tests
اختبارات pytest لـ environment_detector.py
"""

import os
import sys
import pytest
from environment_detector import (
    detect_environment,
    is_replit,
    is_production,
    get_environment_info
)


class TestDetectEnvironment:
    """اختبارات دالة detect_environment()"""
    
    def test_returns_valid_environment(self):
        """الاختبار: البيئة المكتشفة إما development أو production"""
        env = detect_environment()
        assert env in ['development', 'production']
    
    def test_manual_override_development(self, monkeypatch):
        """الاختبار: ENVIRONMENT=development يفرض development"""
        monkeypatch.setenv('ENVIRONMENT', 'development')
        assert detect_environment() == 'development'
    
    def test_manual_override_production(self, monkeypatch):
        """الاختبار: ENVIRONMENT=production يفرض production"""
        monkeypatch.setenv('ENVIRONMENT', 'production')
        assert detect_environment() == 'production'
    
    def test_invalid_environment_value(self, monkeypatch):
        """الاختبار: ENVIRONMENT بقيمة غير صالحة يعود للكشف التلقائي"""
        monkeypatch.setenv('ENVIRONMENT', 'invalid_value')
        monkeypatch.delenv('REPL_ID', raising=False)
        monkeypatch.delenv('REPL_OWNER', raising=False)
        env = detect_environment()
        assert env in ['development', 'production']
    
    def test_replit_detection_with_repl_id(self, monkeypatch):
        """الاختبار: وجود REPL_ID يكشف development"""
        monkeypatch.delenv('ENVIRONMENT', raising=False)
        monkeypatch.setenv('REPL_ID', 'test-repl-id-12345')
        assert detect_environment() == 'development'
    
    def test_replit_detection_with_repl_owner(self, monkeypatch):
        """الاختبار: وجود REPL_OWNER يكشف development"""
        monkeypatch.delenv('ENVIRONMENT', raising=False)
        monkeypatch.delenv('REPL_ID', raising=False)
        monkeypatch.setenv('REPL_OWNER', 'test-owner')
        assert detect_environment() == 'development'


class TestIsReplit:
    """اختبارات دالة is_replit()"""
    
    def test_returns_true_with_repl_id(self, monkeypatch):
        """الاختبار: is_replit() يعود True مع REPL_ID"""
        monkeypatch.setenv('REPL_ID', 'test-repl-id')
        assert is_replit() is True
    
    def test_returns_true_with_repl_owner(self, monkeypatch):
        """الاختبار: is_replit() يعود True مع REPL_OWNER"""
        monkeypatch.delenv('REPL_ID', raising=False)
        monkeypatch.setenv('REPL_OWNER', 'test-owner')
        assert is_replit() is True
    
    def test_returns_false_without_repl_vars(self, monkeypatch):
        """الاختبار: is_replit() يعود False بدون متغيرات Replit"""
        monkeypatch.delenv('REPL_ID', raising=False)
        monkeypatch.delenv('REPL_OWNER', raising=False)
        assert is_replit() is False


class TestIsProduction:
    """اختبارات دالة is_production()"""
    
    def test_matches_detect_environment(self):
        """الاختبار: is_production() يطابق detect_environment()"""
        current_env = detect_environment()
        assert is_production() == (current_env == 'production')
    
    def test_returns_true_in_production(self, monkeypatch):
        """الاختبار: is_production() يعود True في بيئة الإنتاج"""
        monkeypatch.setenv('ENVIRONMENT', 'production')
        assert is_production() is True
    
    def test_returns_false_in_development(self, monkeypatch):
        """الاختبار: is_production() يعود False في بيئة التطوير"""
        monkeypatch.setenv('ENVIRONMENT', 'development')
        assert is_production() is False


class TestGetEnvironmentInfo:
    """اختبارات دالة get_environment_info()"""
    
    def test_contains_required_keys(self):
        """الاختبار: environment_info يحتوي على المفاتيح المطلوبة"""
        info = get_environment_info()
        required_keys = [
            'environment',
            'is_replit',
            'is_production',
            'repl_id',
            'repl_owner',
            'has_systemd',
            'manual_override',
            'python_version',
            'os_name'
        ]
        for key in required_keys:
            assert key in info
    
    def test_environment_value_is_correct(self):
        """الاختبار: قيمة environment في المعلومات صحيحة"""
        current_env = detect_environment()
        info = get_environment_info()
        assert info['environment'] == current_env
    
    def test_manual_override_detection(self, monkeypatch):
        """الاختبار: manual_override يتم كشفه بشكل صحيح"""
        monkeypatch.setenv('ENVIRONMENT', 'development')
        info = get_environment_info()
        assert info['manual_override'] is True
        
        monkeypatch.delenv('ENVIRONMENT')
        info = get_environment_info()
        assert info['manual_override'] is False
