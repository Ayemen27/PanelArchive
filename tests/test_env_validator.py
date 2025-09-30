# coding: utf-8
"""
اختبارات أداة التحقق من متغيرات البيئة - Environment Validator Tests
اختبارات pytest لـ env_validator.py
"""

import os
import sys
import pytest
from env_validator import (
    ValidationResult,
    EnvValidator,
    validate_production_env,
    validate_development_env,
    validate_all_env
)


class TestValidationResult:
    """اختبارات ValidationResult"""
    
    def test_initialization(self):
        """الاختبار: ValidationResult تم إنشاؤها بنجاح"""
        result = ValidationResult()
        assert result is not None
    
    def test_initial_state_empty(self):
        """الاختبار: ValidationResult فارغ عند الإنشاء"""
        result = ValidationResult()
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.info) == 0
    
    def test_add_error(self):
        """الاختبار: add_error() يضيف خطأ"""
        result = ValidationResult()
        result.add_error("Test error")
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"
    
    def test_add_warning(self):
        """الاختبار: add_warning() يضيف تحذير"""
        result = ValidationResult()
        result.add_warning("Test warning")
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"
    
    def test_add_info(self):
        """الاختبار: add_info() يضيف معلومة"""
        result = ValidationResult()
        result.add_info("Test info")
        assert len(result.info) == 1
        assert result.info[0] == "Test info"
    
    def test_is_valid_with_no_errors(self):
        """الاختبار: is_valid() يعود True بدون أخطاء"""
        result = ValidationResult()
        result.add_warning("Warning")
        result.add_info("Info")
        assert result.is_valid() is True
    
    def test_is_valid_with_errors(self):
        """الاختبار: is_valid() يعود False مع أخطاء"""
        result = ValidationResult()
        result.add_error("Error")
        assert result.is_valid() is False
    
    def test_has_warnings(self):
        """الاختبار: has_warnings() يكشف التحذيرات"""
        result = ValidationResult()
        assert result.has_warnings() is False
        
        result.add_warning("Warning")
        assert result.has_warnings() is True
    
    def test_get_summary_no_issues(self):
        """الاختبار: get_summary() بدون مشاكل"""
        result = ValidationResult()
        summary = result.get_summary()
        assert "جميع المتغيرات البيئية صحيحة" in summary
    
    def test_get_summary_with_issues(self):
        """الاختبار: get_summary() مع مشاكل"""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        summary = result.get_summary()
        assert "1 أخطاء" in summary
        assert "1 تحذيرات" in summary


class TestEnvValidator:
    """اختبارات EnvValidator"""
    
    def test_initialization(self):
        """الاختبار: EnvValidator تم إنشاؤها بنجاح"""
        validator = EnvValidator()
        assert validator is not None
    
    def test_validate_port_valid(self):
        """الاختبار: validate_port() مع منفذ صحيح"""
        validator = EnvValidator()
        assert validator.validate_port("8080") is True
        assert validator.validate_port("5000") is True
    
    def test_validate_port_invalid_range(self):
        """الاختبار: validate_port() مع منفذ خارج النطاق"""
        validator = EnvValidator()
        assert validator.validate_port("500") is False
        assert validator.validate_port("70000") is False
    
    def test_validate_port_invalid_value(self):
        """الاختبار: validate_port() مع قيمة غير صحيحة"""
        validator = EnvValidator()
        assert validator.validate_port("abc") is False
    
    def test_validate_port_none(self):
        """الاختبار: validate_port() مع None (اختياري)"""
        validator = EnvValidator()
        assert validator.validate_port(None) is True
    
    def test_validate_database_uri_sqlite(self):
        """الاختبار: validate_database_uri() مع SQLite"""
        validator = EnvValidator()
        assert validator.validate_database_uri("sqlite:///test.db") is True
    
    def test_validate_database_uri_postgresql(self):
        """الاختبار: validate_database_uri() مع PostgreSQL"""
        validator = EnvValidator()
        uri = "postgresql://user:pass@localhost:5432/db"
        assert validator.validate_database_uri(uri) is True
    
    def test_validate_database_uri_mysql(self):
        """الاختبار: validate_database_uri() مع MySQL"""
        validator = EnvValidator()
        uri = "mysql+pymysql://user:pass@localhost:3306/db"
        assert validator.validate_database_uri(uri) is True
    
    def test_validate_database_uri_invalid(self):
        """الاختبار: validate_database_uri() مع صيغة غير صحيحة"""
        validator = EnvValidator()
        assert validator.validate_database_uri("invalid://test") is False
    
    def test_validate_secret_key_production(self, monkeypatch):
        """الاختبار: validate_secret_key() في الإنتاج"""
        monkeypatch.setenv('ENVIRONMENT', 'production')
        validator = EnvValidator()
        validator.environment = 'production'
        
        monkeypatch.delenv('SECRET_KEY', raising=False)
        assert validator.validate_secret_key() is False
        
        monkeypatch.setenv('SECRET_KEY', 'valid_secret_key_for_testing')
        validator = EnvValidator()
        validator.environment = 'production'
        assert validator.validate_secret_key() is True
    
    def test_validate_environment_var_valid(self, monkeypatch):
        """الاختبار: validate_environment_var() مع قيمة صحيحة"""
        validator = EnvValidator()
        
        monkeypatch.setenv('ENVIRONMENT', 'development')
        assert validator.validate_environment_var() is True
        
        monkeypatch.setenv('ENVIRONMENT', 'production')
        assert validator.validate_environment_var() is True
    
    def test_validate_environment_var_invalid(self, monkeypatch):
        """الاختبار: validate_environment_var() مع قيمة غير صحيحة"""
        monkeypatch.setenv('ENVIRONMENT', 'invalid')
        validator = EnvValidator()
        assert validator.validate_environment_var() is False


class TestValidateProductionEnv:
    """اختبارات validate_production_env()"""
    
    @pytest.fixture(autouse=True)
    def setup_production_env(self, monkeypatch):
        """إعداد بيئة الإنتاج للاختبار"""
        monkeypatch.setenv('ENVIRONMENT', 'production')
        monkeypatch.setenv('SECRET_KEY', 'test_production_secret_key')
    
    def test_returns_validation_result(self):
        """الاختبار: validate_production_env() يرجع ValidationResult"""
        result = validate_production_env()
        assert isinstance(result, ValidationResult)
    
    def test_validates_secret_key(self, monkeypatch):
        """الاختبار: يتحقق من SECRET_KEY في الإنتاج"""
        monkeypatch.delenv('SECRET_KEY', raising=False)
        result = validate_production_env()
        assert result.is_valid() is False


class TestValidateDevelopmentEnv:
    """اختبارات validate_development_env()"""
    
    @pytest.fixture(autouse=True)
    def setup_development_env(self, monkeypatch):
        """إعداد بيئة التطوير للاختبار"""
        monkeypatch.setenv('ENVIRONMENT', 'development')
    
    def test_returns_validation_result(self):
        """الاختبار: validate_development_env() يرجع ValidationResult"""
        result = validate_development_env()
        assert isinstance(result, ValidationResult)
    
    def test_more_lenient_than_production(self):
        """الاختبار: التطوير أكثر تساهلاً من الإنتاج"""
        result = validate_development_env()
        assert result.is_valid() is True


class TestValidateAllEnv:
    """اختبارات validate_all_env()"""
    
    def test_returns_validation_result(self):
        """الاختبار: validate_all_env() يرجع ValidationResult"""
        result = validate_all_env()
        assert isinstance(result, ValidationResult)
    
    def test_detects_current_environment(self, monkeypatch):
        """الاختبار: validate_all_env() يكتشف البيئة الحالية"""
        monkeypatch.setenv('ENVIRONMENT', 'development')
        result = validate_all_env()
        assert any('تطوير' in info for info in result.info)
