# coding: utf-8
"""
اختبارات مصنع الإعدادات - Configuration Factory Tests
اختبارات pytest لـ config_factory.py
"""

import os
import sys
import pytest
from config_factory import (
    BaseConfig,
    DevelopmentConfig,
    ProductionConfig,
    get_config,
    get_config_for_environment
)


class TestBaseConfig:
    """اختبارات BaseConfig"""
    
    def test_initialization(self):
        """الاختبار: BaseConfig تم إنشاؤها بنجاح"""
        config = BaseConfig()
        assert config is not None
    
    def test_has_environment(self):
        """الاختبار: ENVIRONMENT موجود"""
        config = BaseConfig()
        assert hasattr(config, 'ENVIRONMENT')
    
    def test_environment_is_valid(self):
        """الاختبار: ENVIRONMENT قيمة صالحة"""
        config = BaseConfig()
        assert config.ENVIRONMENT in ['development', 'production']
    
    def test_has_secret_key(self):
        """الاختبار: SECRET_KEY موجود"""
        config = BaseConfig()
        assert hasattr(config, 'SECRET_KEY')
    
    def test_secret_key_not_empty(self):
        """الاختبار: SECRET_KEY ليس فارغاً"""
        config = BaseConfig()
        assert len(config.SECRET_KEY) > 0
    
    def test_has_port(self):
        """الاختبار: PORT موجود"""
        config = BaseConfig()
        assert hasattr(config, 'PORT')
    
    def test_port_is_integer(self):
        """الاختبار: PORT رقم صحيح"""
        config = BaseConfig()
        assert isinstance(config.PORT, int)
    
    def test_host_is_correct(self):
        """الاختبار: HOST موجود ويساوي 0.0.0.0"""
        config = BaseConfig()
        assert config.HOST == '0.0.0.0'
    
    def test_secret_key_generation(self, monkeypatch):
        """الاختبار: SECRET_KEY يتم توليده تلقائياً"""
        monkeypatch.delenv('SECRET_KEY', raising=False)
        config1 = BaseConfig()
        config2 = BaseConfig()
        
        assert len(config1.SECRET_KEY) > 0
        assert config1.SECRET_KEY != config2.SECRET_KEY
    
    def test_secret_key_from_environment(self, monkeypatch):
        """الاختبار: SECRET_KEY يُقرأ من المتغيرات"""
        monkeypatch.setenv('SECRET_KEY', 'custom_secret_key_for_testing')
        config = BaseConfig()
        assert config.SECRET_KEY == 'custom_secret_key_for_testing'
    
    def test_secret_key_length(self, monkeypatch):
        """الاختبار: SECRET_KEY بالطول الصحيح (64 حرف)"""
        monkeypatch.delenv('SECRET_KEY', raising=False)
        config = BaseConfig()
        assert len(config.SECRET_KEY) == 64
    
    def test_get_config_dict(self):
        """الاختبار: get_config_dict() يرجع قاموس"""
        config = BaseConfig()
        config_dict = config.get_config_dict()
        assert isinstance(config_dict, dict)
    
    def test_config_dict_contains_keys(self):
        """الاختبار: القاموس يحتوي على المفاتيح الأساسية"""
        config = BaseConfig()
        config_dict = config.get_config_dict()
        
        required_keys = ['ENVIRONMENT', 'SECRET_KEY', 'PORT', 'HOST']
        for key in required_keys:
            assert key in config_dict
    
    def test_repr(self):
        """الاختبار: __repr__ يحتوي على اسم الفئة وbیئة"""
        config = BaseConfig()
        repr_str = repr(config)
        assert 'BaseConfig' in repr_str
        assert 'environment=' in repr_str


class TestDevelopmentConfig:
    """اختبارات DevelopmentConfig"""
    
    def test_initialization(self):
        """الاختبار: DevelopmentConfig تم إنشاؤها بنجاح"""
        config = DevelopmentConfig()
        assert config is not None
    
    def test_debug_enabled(self):
        """الاختبار: DEBUG مفعل في التطوير"""
        config = DevelopmentConfig()
        assert config.DEBUG is True
    
    def test_database_type_sqlite(self):
        """الاختبار: DATABASE_TYPE هو sqlite"""
        config = DevelopmentConfig()
        assert config.DATABASE_TYPE == 'sqlite'
    
    def test_database_uri_sqlite(self):
        """الاختبار: DATABASE_URI يبدأ بـ sqlite:///"""
        config = DevelopmentConfig()
        assert config.DATABASE_URI.startswith('sqlite:///')
    
    def test_development_mode_enabled(self):
        """الاختبار: DEVELOPMENT_MODE مفعل"""
        config = DevelopmentConfig()
        assert config.DEVELOPMENT_MODE is True
    
    def test_session_cookie_not_secure(self):
        """الاختبار: SESSION_COOKIE_SECURE معطل في التطوير"""
        config = DevelopmentConfig()
        assert config.SESSION_COOKIE_SECURE is False
    
    def test_log_level_debug(self):
        """الاختبار: LOG_LEVEL هو DEBUG"""
        config = DevelopmentConfig()
        assert config.LOG_LEVEL == 'DEBUG'
    
    def test_testing_disabled(self):
        """الاختبار: TESTING معطل افتراضياً"""
        config = DevelopmentConfig()
        assert config.TESTING is False
    
    def test_show_sql_queries(self):
        """الاختبار: SHOW_SQL_QUERIES مفعل"""
        config = DevelopmentConfig()
        assert config.SHOW_SQL_QUERIES is True
    
    def test_auto_reload_enabled(self):
        """الاختبار: AUTO_RELOAD مفعل"""
        config = DevelopmentConfig()
        assert config.AUTO_RELOAD is True
    
    def test_cors_enabled(self):
        """الاختبار: CORS_ENABLED مفعل في التطوير"""
        config = DevelopmentConfig()
        assert config.CORS_ENABLED is True
    
    def test_cors_origins_all(self):
        """الاختبار: CORS_ORIGINS يسمح بالجميع في التطوير"""
        config = DevelopmentConfig()
        assert config.CORS_ORIGINS == ['*']
    
    def test_inherits_from_base_config(self):
        """الاختبار: DevelopmentConfig يرث من BaseConfig"""
        assert issubclass(DevelopmentConfig, BaseConfig)


class TestProductionConfig:
    """اختبارات ProductionConfig"""
    
    @pytest.fixture(autouse=True)
    def setup_secret_key(self, monkeypatch):
        """إعداد SECRET_KEY للسماح بإنشاء ProductionConfig"""
        monkeypatch.setenv('SECRET_KEY', 'test_secret_key_for_production_testing')
    
    def test_initialization(self):
        """الاختبار: ProductionConfig تم إنشاؤها بنجاح"""
        config = ProductionConfig()
        assert config is not None
    
    def test_debug_disabled(self):
        """الاختبار: DEBUG معطل في الإنتاج"""
        config = ProductionConfig()
        assert config.DEBUG is False
    
    def test_database_type_valid(self):
        """الاختبار: DATABASE_TYPE في الإنتاج صالح"""
        config = ProductionConfig()
        assert config.DATABASE_TYPE in ['postgresql', 'mysql']
    
    def test_session_cookie_secure(self):
        """الاختبار: SESSION_COOKIE_SECURE مفعل في الإنتاج"""
        config = ProductionConfig()
        assert config.SESSION_COOKIE_SECURE is True
    
    def test_ssl_enabled(self):
        """الاختبار: SSL_ENABLED مفعل"""
        config = ProductionConfig()
        assert config.SSL_ENABLED is True
    
    def test_development_mode_disabled(self):
        """الاختبار: DEVELOPMENT_MODE معطل"""
        config = ProductionConfig()
        assert config.DEVELOPMENT_MODE is False
    
    def test_log_level_warning(self):
        """الاختبار: LOG_LEVEL هو WARNING"""
        config = ProductionConfig()
        assert config.LOG_LEVEL == 'WARNING'
    
    def test_testing_disabled(self):
        """الاختبار: TESTING معطل"""
        config = ProductionConfig()
        assert config.TESTING is False
    
    def test_show_sql_queries_disabled(self):
        """الاختبار: SHOW_SQL_QUERIES معطل"""
        config = ProductionConfig()
        assert config.SHOW_SQL_QUERIES is False
    
    def test_auto_reload_disabled(self):
        """الاختبار: AUTO_RELOAD معطل"""
        config = ProductionConfig()
        assert config.AUTO_RELOAD is False
    
    def test_cors_disabled(self):
        """الاختبار: CORS_ENABLED معطل افتراضياً"""
        config = ProductionConfig()
        assert config.CORS_ENABLED is False
    
    def test_session_cookie_samesite_strict(self):
        """الاختبار: SESSION_COOKIE_SAMESITE هو Strict"""
        config = ProductionConfig()
        assert config.SESSION_COOKIE_SAMESITE == 'Strict'
    
    def test_requires_secret_key(self, monkeypatch):
        """الاختبار: ProductionConfig يتطلب SECRET_KEY"""
        monkeypatch.delenv('SECRET_KEY', raising=False)
        with pytest.raises(RuntimeError):
            ProductionConfig()
    
    def test_rejects_empty_secret_key(self, monkeypatch):
        """الاختبار: ProductionConfig يرفض SECRET_KEY فارغ"""
        monkeypatch.setenv('SECRET_KEY', '')
        with pytest.raises(RuntimeError):
            ProductionConfig()
    
    def test_inherits_from_base_config(self):
        """الاختبار: ProductionConfig يرث من BaseConfig"""
        assert issubclass(ProductionConfig, BaseConfig)
    
    def test_database_uri_postgresql(self, monkeypatch):
        """الاختبار: DATABASE_URI للـ PostgreSQL"""
        monkeypatch.setenv('DATABASE_TYPE', 'postgresql')
        monkeypatch.setenv('DB_USER', 'testuser')
        monkeypatch.setenv('DB_PASSWORD', 'testpass')
        monkeypatch.setenv('DB_HOST', 'localhost')
        monkeypatch.setenv('DB_NAME', 'testdb')
        
        config = ProductionConfig()
        assert 'postgresql://' in config.DATABASE_URI
        assert 'testuser' in config.DATABASE_URI
        assert 'testpass' in config.DATABASE_URI
    
    def test_database_uri_mysql(self, monkeypatch):
        """الاختبار: DATABASE_URI للـ MySQL"""
        monkeypatch.setenv('DATABASE_TYPE', 'mysql')
        monkeypatch.setenv('DB_USER', 'testuser')
        monkeypatch.setenv('DB_PASSWORD', 'testpass')
        monkeypatch.setenv('DB_HOST', 'localhost')
        monkeypatch.setenv('DB_NAME', 'testdb')
        
        config = ProductionConfig()
        assert 'mysql+' in config.DATABASE_URI
        assert 'testuser' in config.DATABASE_URI
        assert 'testpass' in config.DATABASE_URI


class TestGetConfig:
    """اختبارات دالة get_config()"""
    
    def test_returns_config_object(self):
        """الاختبار: get_config() يرجع كائن"""
        config = get_config()
        assert config is not None
    
    def test_returns_base_config_instance(self):
        """الاختبار: get_config() يرجع BaseConfig أو فئة فرعية"""
        config = get_config()
        assert isinstance(config, BaseConfig)
    
    def test_development_environment(self, monkeypatch):
        """الاختبار: get_config() يرجع DevelopmentConfig في بيئة التطوير"""
        monkeypatch.setenv('ENVIRONMENT', 'development')
        config = get_config()
        assert isinstance(config, DevelopmentConfig)
    
    def test_production_environment(self, monkeypatch):
        """الاختبار: get_config() يرجع ProductionConfig في بيئة الإنتاج"""
        monkeypatch.setenv('ENVIRONMENT', 'production')
        monkeypatch.setenv('SECRET_KEY', 'test_secret_key')
        config = get_config()
        assert isinstance(config, ProductionConfig)


class TestGetConfigForEnvironment:
    """اختبارات دالة get_config_for_environment()"""
    
    def test_development_string(self):
        """الاختبار: get_config_for_environment('development') يرجع DevelopmentConfig"""
        config = get_config_for_environment('development')
        assert isinstance(config, DevelopmentConfig)
    
    def test_production_string(self, monkeypatch):
        """الاختبار: get_config_for_environment('production') يرجع ProductionConfig"""
        monkeypatch.setenv('SECRET_KEY', 'test_secret_key')
        config = get_config_for_environment('production')
        assert isinstance(config, ProductionConfig)
    
    def test_dev_shortcut(self):
        """الاختبار: get_config_for_environment('dev') يرجع DevelopmentConfig"""
        config = get_config_for_environment('dev')
        assert isinstance(config, DevelopmentConfig)
    
    def test_prod_shortcut(self, monkeypatch):
        """الاختبار: get_config_for_environment('prod') يرجع ProductionConfig"""
        monkeypatch.setenv('SECRET_KEY', 'test_secret_key')
        config = get_config_for_environment('prod')
        assert isinstance(config, ProductionConfig)
    
    def test_invalid_environment_raises_error(self):
        """الاختبار: get_config_for_environment() يرفع ValueError لقيمة غير صالحة"""
        with pytest.raises(ValueError):
            get_config_for_environment('invalid')
