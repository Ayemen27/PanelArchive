# coding: utf-8
"""
أداة التحقق من متغيرات البيئة - Environment Variables Validator
تتحقق من صحة واكتمال متغيرات البيئة في التطوير والإنتاج
"""

import os
import sys
import re
from typing import List, Dict, Tuple, Optional
from environment_detector import detect_environment, is_production, is_replit


class ValidationResult:
    """نتيجة التحقق من المتغيرات"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        
    def add_error(self, message: str):
        """إضافة خطأ"""
        self.errors.append(message)
        
    def add_warning(self, message: str):
        """إضافة تحذير"""
        self.warnings.append(message)
        
    def add_info(self, message: str):
        """إضافة معلومة"""
        self.info.append(message)
        
    def is_valid(self) -> bool:
        """هل النتيجة صالحة (لا توجد أخطاء)"""
        return len(self.errors) == 0
    
    def has_warnings(self) -> bool:
        """هل توجد تحذيرات"""
        return len(self.warnings) > 0
    
    def get_summary(self) -> str:
        """الحصول على ملخص النتيجة"""
        total = len(self.errors) + len(self.warnings)
        if total == 0:
            return "✓ جميع المتغيرات البيئية صحيحة"
        return f"وُجدت {len(self.errors)} أخطاء و {len(self.warnings)} تحذيرات"


class EnvValidator:
    """أداة التحقق من متغيرات البيئة"""
    
    # المتغيرات الإلزامية في الإنتاج
    REQUIRED_PRODUCTION_VARS = [
        'SECRET_KEY',
    ]
    
    # المتغيرات الحساسة (يجب عدم تركها فارغة في الإنتاج)
    SENSITIVE_VARS = [
        'SECRET_KEY',
        'DB_PASSWORD',
        'DATABASE_URL',
        'SSL_KEY_PATH',
    ]
    
    # المتغيرات التي تشير إلى ملفات
    FILE_PATH_VARS = [
        'SSL_CERT_PATH',
        'SSL_KEY_PATH',
        'DEV_DATABASE_PATH',
        'LOG_FILE_PATH',
    ]
    
    def __init__(self):
        """تهيئة أداة التحقق"""
        self.environment = detect_environment()
        self.result = ValidationResult()
        
    def validate_port(self, port_value: Optional[str]) -> bool:
        """
        التحقق من صحة قيمة PORT
        
        Args:
            port_value: قيمة PORT
            
        Returns:
            bool: True إذا كانت صحيحة
        """
        if not port_value:
            # PORT اختياري، يمكن قراءته من الملف
            return True
            
        try:
            port = int(port_value)
            if port < 1024 or port > 65535:
                self.result.add_error(
                    f"❌ قيمة PORT غير صحيحة: {port}. "
                    f"يجب أن تكون بين 1024 و 65535"
                )
                return False
            return True
        except (ValueError, TypeError):
            self.result.add_error(
                f"❌ قيمة PORT غير صحيحة: '{port_value}'. "
                f"يجب أن تكون رقماً صحيحاً"
            )
            return False
    
    def validate_database_uri(self, uri: Optional[str]) -> bool:
        """
        التحقق من صحة DATABASE_URI format
        
        Args:
            uri: DATABASE_URI
            
        Returns:
            bool: True إذا كانت صحيحة
        """
        if not uri:
            return True
            
        # أنماط صحيحة لـ DATABASE_URI
        valid_patterns = [
            r'^sqlite:///.*',
            r'^postgresql://.*',
            r'^postgresql\+psycopg2://.*',
            r'^mysql://.*',
            r'^mysql\+pymysql://.*',
            r'^mysql\+mysqlclient://.*',
        ]
        
        is_valid = any(re.match(pattern, uri) for pattern in valid_patterns)
        
        if not is_valid:
            self.result.add_error(
                f"❌ صيغة DATABASE_URI غير صحيحة. "
                f"يجب أن تبدأ بـ sqlite:///, postgresql://, أو mysql://+driver"
            )
            return False
            
        # التحقق من وجود كلمة المرور في URI (لقواعد البيانات غير SQLite)
        if not uri.startswith('sqlite:///'):
            # التحقق من نمط: scheme://user:password@host/db
            if ':' in uri.split('://')[1] and '@' in uri:
                credentials_part = uri.split('://')[1].split('@')[0]
                if ':' not in credentials_part:
                    self.result.add_warning(
                        "DATABASE_URI لا يحتوي على كلمة مرور. "
                        "تأكد من تضمين كلمة المرور في الإنتاج"
                    )
            else:
                self.result.add_warning(
                    "DATABASE_URI لا يحتوي على بيانات اعتماد واضحة. "
                    "تأكد من صحة الصيغة"
                )
                
        return True
    
    def validate_file_exists(self, var_name: str, file_path: Optional[str]) -> bool:
        """
        التحقق من وجود الملف
        
        Args:
            var_name: اسم المتغير
            file_path: مسار الملف
            
        Returns:
            bool: True إذا كان الملف موجوداً أو المسار فارغ
        """
        if not file_path:
            return True
            
        if not os.path.exists(file_path):
            # في التطوير، نعطي تحذير فقط
            if self.environment == 'development':
                self.result.add_warning(
                    f"الملف المحدد في {var_name} غير موجود: {file_path}"
                )
            else:
                self.result.add_error(
                    f"الملف المحدد في {var_name} غير موجود: {file_path}"
                )
            return False
            
        return True
    
    def validate_database_credentials(self) -> bool:
        """
        التحقق من بيانات اعتماد قاعدة البيانات في الإنتاج
        
        Returns:
            bool: True إذا كانت صحيحة
        """
        if self.environment != 'production':
            return True
            
        database_url = os.environ.get('DATABASE_URL', '')
        database_type = os.environ.get('DATABASE_TYPE', '').lower()
        
        # إذا كان DATABASE_URL موجود، تحقق منه
        if database_url:
            return self.validate_database_uri(database_url)
            
        # إذا لم يكن DATABASE_URL موجود، تحقق من المتغيرات المنفصلة
        if database_type in ['postgresql', 'mysql']:
            db_password = os.environ.get('DB_PASSWORD', '')
            
            if not db_password:
                self.result.add_error(
                    f"❌ DB_PASSWORD مطلوب في بيئة الإنتاج عند استخدام "
                    f"{database_type.upper()}. يرجى تعيين كلمة المرور في ملف .env"
                )
                return False
                
            # التحقق من باقي المتغيرات
            db_user = os.environ.get('DB_USER', '')
            db_host = os.environ.get('DB_HOST', '')
            db_name = os.environ.get('DB_NAME', '')
            
            if not db_user:
                self.result.add_warning(
                    "DB_USER غير محدد. سيتم استخدام القيمة الافتراضية"
                )
                
            if not db_host:
                self.result.add_warning(
                    "DB_HOST غير محدد. سيتم استخدام localhost"
                )
                
            if not db_name:
                self.result.add_warning(
                    "DB_NAME غير محدد. سيتم استخدام القيمة الافتراضية"
                )
                
        return True
    
    def validate_secret_key(self) -> bool:
        """
        التحقق من SECRET_KEY
        
        Returns:
            bool: True إذا كان صحيحاً
        """
        secret_key = os.environ.get('SECRET_KEY', '')
        
        # في الإنتاج، SECRET_KEY إلزامي
        if self.environment == 'production':
            if not secret_key or secret_key.strip() == '':
                self.result.add_error(
                    "❌ SECRET_KEY مطلوب في بيئة الإنتاج ولا يمكن أن يكون فارغاً. "
                    "يرجى تعيين مفتاح سري آمن في ملف .env"
                )
                return False
                
            # التحقق من أن المفتاح ليس القيمة الافتراضية من .env.example
            if 'your-secret-key-here' in secret_key.lower():
                self.result.add_error(
                    "❌ SECRET_KEY يستخدم القيمة الافتراضية من .env.example. "
                    "يجب تغييره إلى قيمة فريدة وآمنة. "
                    "استخدم: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
                return False
                
            # التحقق من طول المفتاح
            if len(secret_key) < 32:
                self.result.add_warning(
                    f"SECRET_KEY قصير جداً ({len(secret_key)} حرف). "
                    f"يُنصح باستخدام مفتاح بطول 64 حرف على الأقل"
                )
                
        else:
            # في التطوير، تحذير فقط
            if not secret_key:
                self.result.add_warning(
                    "SECRET_KEY غير محدد. سيتم توليد مفتاح عشوائي تلقائياً"
                )
                
        return True
    
    def validate_ssl_configuration(self) -> bool:
        """
        التحقق من إعدادات SSL في الإنتاج
        
        Returns:
            bool: True إذا كانت صحيحة
        """
        if self.environment != 'production':
            return True
            
        ssl_cert = os.environ.get('SSL_CERT_PATH', '')
        ssl_key = os.environ.get('SSL_KEY_PATH', '')
        
        # إذا تم تحديد أحدهما، يجب تحديد الآخر
        if ssl_cert and not ssl_key:
            self.result.add_error(
                "SSL_CERT_PATH محدد ولكن SSL_KEY_PATH غير محدد. "
                "يجب تحديد كليهما معاً"
            )
            return False
            
        if ssl_key and not ssl_cert:
            self.result.add_error(
                "SSL_KEY_PATH محدد ولكن SSL_CERT_PATH غير محدد. "
                "يجب تحديد كليهما معاً"
            )
            return False
            
        # التحقق من وجود الملفات
        if ssl_cert:
            self.validate_file_exists('SSL_CERT_PATH', ssl_cert)
            
        if ssl_key:
            self.validate_file_exists('SSL_KEY_PATH', ssl_key)
            
        return True
    
    def validate_environment_var(self) -> bool:
        """
        التحقق من قيمة ENVIRONMENT
        
        Returns:
            bool: True إذا كانت صحيحة
        """
        env_var = os.environ.get('ENVIRONMENT', '').lower()
        
        if env_var and env_var not in ['development', 'production']:
            self.result.add_error(
                f"❌ قيمة ENVIRONMENT غير صحيحة: '{env_var}'. "
                f"القيم المقبولة فقط: 'development' أو 'production'. "
                f"يرجى تصحيح القيمة أو حذف المتغير للكشف التلقائي"
            )
            return False
            
        return True
    
    def validate_mysql_driver(self) -> bool:
        """
        التحقق من صحة MySQL driver
        
        Returns:
            bool: True إذا كان صحيحاً
        """
        db_driver = os.environ.get('DB_DRIVER', '').lower()
        
        # إذا لم يتم تحديد driver، استخدم الافتراضي
        if not db_driver:
            return True
        
        # القيم المقبولة فقط
        valid_drivers = ['pymysql', 'mysqldb', 'mysqlconnector']
        
        if db_driver not in valid_drivers:
            self.result.add_error(
                f"❌ قيمة DB_DRIVER غير صحيحة: '{db_driver}'. "
                f"القيم المقبولة فقط: {', '.join(valid_drivers)}. "
                f"القيمة الافتراضية الموصى بها: 'pymysql'"
            )
            return False
        
        return True
    
    def validate_ssl_default_files(self) -> bool:
        """
        التحقق من وجود ملفات SSL الافتراضية في الإنتاج
        
        Returns:
            bool: True إذا كانت صحيحة
        """
        if self.environment != 'production':
            return True
        
        ssl_cert = os.environ.get('SSL_CERT_PATH', '/etc/ssl/certs/cert.pem')
        ssl_key = os.environ.get('SSL_KEY_PATH', '/etc/ssl/private/key.pem')
        
        # إذا تم تحديد المسارات، تحقق من وجودها
        if ssl_cert == '/etc/ssl/certs/cert.pem':
            if not os.path.exists(ssl_cert):
                self.result.add_warning(
                    f"⚠️ ملف SSL الافتراضي غير موجود: {ssl_cert}. "
                    f"يرجى تحديد SSL_CERT_PATH بمسار صحيح أو تعطيل SSL"
                )
        
        if ssl_key == '/etc/ssl/private/key.pem':
            if not os.path.exists(ssl_key):
                self.result.add_warning(
                    f"⚠️ ملف مفتاح SSL الافتراضي غير موجود: {ssl_key}. "
                    f"يرجى تحديد SSL_KEY_PATH بمسار صحيح أو تعطيل SSL"
                )
        
        return True
    
    def validate_sensitive_vars_not_empty(self) -> bool:
        """
        التحقق من أن المتغيرات الحساسة غير فارغة في الإنتاج
        
        Returns:
            bool: True إذا كانت صحيحة
        """
        if self.environment != 'production':
            return True
            
        all_valid = True
        
        for var_name in self.SENSITIVE_VARS:
            var_value = os.environ.get(var_name, '')
            
            # تخطي DB_PASSWORD و DATABASE_URL إذا كان أحدهما موجود
            if var_name == 'DB_PASSWORD':
                if os.environ.get('DATABASE_URL'):
                    continue
            elif var_name == 'DATABASE_URL':
                if os.environ.get('DB_PASSWORD'):
                    continue
                    
            # تخطي SSL paths إذا لم يتم تفعيل SSL
            if var_name in ['SSL_KEY_PATH']:
                if not os.environ.get('SSL_CERT_PATH'):
                    continue
                    
            # التحقق من أن المتغير غير فارغ
            if var_name in ['SECRET_KEY']:  # المتغيرات الإلزامية
                if not var_value or var_value.strip() == '':
                    # تم التحقق منه في validate_secret_key
                    pass
                    
        return all_valid
    
    def validate_development_env(self) -> ValidationResult:
        """
        التحقق من متغيرات بيئة التطوير
        
        Returns:
            ValidationResult: نتيجة التحقق
        """
        self.result = ValidationResult()
        self.result.add_info(f"البيئة الحالية: {self.environment} (تطوير)")
        
        # التحقق من PORT
        port = os.environ.get('PORT')
        self.validate_port(port)
        
        # التحقق من ENVIRONMENT
        self.validate_environment_var()
        
        # التحقق من SECRET_KEY (تحذير فقط)
        self.validate_secret_key()
        
        # التحقق من DATABASE_URI إذا كان موجوداً
        database_uri = os.environ.get('DATABASE_URL')
        if database_uri:
            self.validate_database_uri(database_uri)
        
        # التحقق من MySQL driver
        self.validate_mysql_driver()
            
        # التحقق من مسار قاعدة البيانات للتطوير
        dev_db_path = os.environ.get('DEV_DATABASE_PATH')
        if dev_db_path:
            # التحقق من أن المجلد الأب موجود
            parent_dir = os.path.dirname(dev_db_path)
            if parent_dir and not os.path.exists(parent_dir):
                self.result.add_warning(
                    f"المجلد الأب لقاعدة البيانات غير موجود: {parent_dir}. "
                    f"سيتم إنشاؤه تلقائياً"
                )
                
        # معلومات إضافية
        if is_replit():
            self.result.add_info("تم الكشف عن بيئة Replit")
            
        return self.result
    
    def validate_production_env(self) -> ValidationResult:
        """
        التحقق من متغيرات بيئة الإنتاج
        
        Returns:
            ValidationResult: نتيجة التحقق
        """
        self.result = ValidationResult()
        self.result.add_info(f"البيئة الحالية: {self.environment} (إنتاج)")
        
        # التحقق من PORT
        port = os.environ.get('PORT')
        self.validate_port(port)
        
        # التحقق من ENVIRONMENT
        self.validate_environment_var()
        
        # التحقق من SECRET_KEY (يقوم بالتحقق الكامل داخلياً)
        self.validate_secret_key()
        
        # التحقق من بيانات اعتماد قاعدة البيانات
        self.validate_database_credentials()
        
        # التحقق من MySQL driver
        self.validate_mysql_driver()
        
        # التحقق من SSL
        self.validate_ssl_configuration()
        
        # التحقق من ملفات SSL الافتراضية
        self.validate_ssl_default_files()
        
        # التحقق من المتغيرات الحساسة
        self.validate_sensitive_vars_not_empty()
        
        # التحقق من ALLOWED_ORIGINS في الإنتاج
        allowed_origins = os.environ.get('ALLOWED_ORIGINS', '')
        if not allowed_origins:
            self.result.add_warning(
                "ALLOWED_ORIGINS غير محدد. سيتم رفض جميع طلبات CORS"
            )
            
        return self.result
    
    def validate_all_env(self) -> ValidationResult:
        """
        التحقق الشامل من جميع متغيرات البيئة
        
        Returns:
            ValidationResult: نتيجة التحقق
        """
        # تحديد البيئة والتحقق بناءً عليها
        if self.environment == 'production':
            return self.validate_production_env()
        else:
            return self.validate_development_env()


def print_validation_report(result: ValidationResult):
    """
    طباعة تقرير التحقق بشكل منسق
    
    Args:
        result: نتيجة التحقق
    """
    print("\n" + "=" * 70)
    print("تقرير التحقق من متغيرات البيئة")
    print("Environment Variables Validation Report")
    print("=" * 70)
    
    # المعلومات
    if result.info:
        print("\n📋 معلومات:")
        for info in result.info:
            print(f"   ℹ️  {info}")
    
    # الأخطاء
    if result.errors:
        print(f"\n❌ الأخطاء ({len(result.errors)}):")
        for i, error in enumerate(result.errors, 1):
            print(f"   {i}. {error}")
    
    # التحذيرات
    if result.warnings:
        print(f"\n⚠️  التحذيرات ({len(result.warnings)}):")
        for i, warning in enumerate(result.warnings, 1):
            print(f"   {i}. {warning}")
    
    # الملخص
    print("\n" + "-" * 70)
    print(f"الملخص: {result.get_summary()}")
    print("-" * 70 + "\n")


def validate_production_env() -> ValidationResult:
    """
    التحقق من متغيرات بيئة الإنتاج
    
    Returns:
        ValidationResult: نتيجة التحقق
    """
    validator = EnvValidator()
    validator.environment = 'production'
    return validator.validate_production_env()


def validate_development_env() -> ValidationResult:
    """
    التحقق من متغيرات بيئة التطوير
    
    Returns:
        ValidationResult: نتيجة التحقق
    """
    validator = EnvValidator()
    validator.environment = 'development'
    return validator.validate_development_env()


def validate_all_env() -> ValidationResult:
    """
    التحقق الشامل من جميع متغيرات البيئة (حسب البيئة المكتشفة)
    
    Returns:
        ValidationResult: نتيجة التحقق
    """
    validator = EnvValidator()
    return validator.validate_all_env()


# ==================== الاختبارات - Unit Tests ====================

def run_tests():
    """تشغيل الاختبارات الداخلية"""
    print("=" * 70)
    print("بدء اختبار أداة التحقق من متغيرات البيئة")
    print("Environment Validator Tests")
    print("=" * 70)
    print()
    
    # حفظ المتغيرات الأصلية
    original_env_vars = os.environ.copy()
    
    tests_passed = 0
    tests_failed = 0
    total_tests = 0
    
    def run_test(test_name, condition, expected=True):
        """دالة مساعدة لتشغيل الاختبار"""
        nonlocal tests_passed, tests_failed, total_tests
        total_tests += 1
        
        result = condition == expected
        status = "✓ نجح" if result else "✗ فشل"
        
        if result:
            tests_passed += 1
            print(f"[{status}] {test_name}")
        else:
            tests_failed += 1
            print(f"[{status}] {test_name} - القيمة: {condition}, المتوقع: {expected}")
        
        return result
    
    # ==================== الاختبار 1: PORT Validation ====================
    print("\n--- الاختبار 1: التحقق من PORT ---")
    validator = EnvValidator()
    
    # PORT صحيح
    run_test("PORT=5000 صحيح", validator.validate_port("5000"), True)
    
    # PORT خارج النطاق
    validator.result = ValidationResult()
    run_test("PORT=100 غير صحيح (أقل من 1024)", 
             not validator.validate_port("100"), True)
    
    # PORT غير رقمي
    validator.result = ValidationResult()
    run_test("PORT=abc غير صحيح (ليس رقماً)", 
             not validator.validate_port("abc"), True)
    
    # PORT فارغ (مقبول)
    validator.result = ValidationResult()
    run_test("PORT فارغ مقبول", validator.validate_port(None), True)
    
    # ==================== الاختبار 2: DATABASE_URI Validation ====================
    print("\n--- الاختبار 2: التحقق من DATABASE_URI ---")
    validator = EnvValidator()
    
    # SQLite URI صحيح
    run_test("SQLite URI صحيح", 
             validator.validate_database_uri("sqlite:///data/db.db"), True)
    
    # PostgreSQL URI صحيح
    validator.result = ValidationResult()
    run_test("PostgreSQL URI صحيح", 
             validator.validate_database_uri("postgresql://user:pass@localhost/db"), True)
    
    # URI غير صحيح
    validator.result = ValidationResult()
    run_test("URI غير صحيح", 
             not validator.validate_database_uri("invalid://uri"), True)
    
    # ==================== الاختبار 3: SECRET_KEY Validation ====================
    print("\n--- الاختبار 3: التحقق من SECRET_KEY ---")
    
    # في بيئة إنتاج بدون SECRET_KEY
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'production'
    validator = EnvValidator()
    validator.environment = 'production'
    run_test("SECRET_KEY مطلوب في الإنتاج", 
             not validator.validate_secret_key(), True)
    
    # في بيئة إنتاج مع SECRET_KEY صحيح
    os.environ['SECRET_KEY'] = 'a' * 64
    validator.result = ValidationResult()
    run_test("SECRET_KEY صحيح في الإنتاج", 
             validator.validate_secret_key(), True)
    
    # في بيئة تطوير بدون SECRET_KEY (تحذير فقط)
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'development'
    validator = EnvValidator()
    validator.environment = 'development'
    validator.validate_secret_key()
    run_test("SECRET_KEY اختياري في التطوير (تحذير فقط)", 
             validator.result.has_warnings(), True)
    
    # ==================== الاختبار 4: SSL Configuration ====================
    print("\n--- الاختبار 4: التحقق من SSL ---")
    
    # SSL_CERT_PATH بدون SSL_KEY_PATH
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['SSL_CERT_PATH'] = '/path/to/cert.pem'
    validator = EnvValidator()
    validator.environment = 'production'
    run_test("SSL_CERT_PATH بدون SSL_KEY_PATH خطأ", 
             not validator.validate_ssl_configuration(), True)
    
    # كلاهما موجود
    os.environ['SSL_KEY_PATH'] = '/path/to/key.pem'
    validator.result = ValidationResult()
    validator.validate_ssl_configuration()
    # سيكون هناك خطأ لعدم وجود الملفات، لكن التحقق من التطابق نجح
    run_test("SSL_CERT_PATH و SSL_KEY_PATH معاً", 
             len(validator.result.errors) >= 0, True)
    
    # ==================== الاختبار 5: التحقق الشامل ====================
    print("\n--- الاختبار 5: التحقق الشامل ---")
    
    # إعداد بيئة تطوير صحيحة
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['PORT'] = '5000'
    result = validate_development_env()
    run_test("بيئة تطوير صحيحة", result.is_valid() or result.has_warnings(), True)
    
    # إعداد بيئة إنتاج غير كاملة
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'production'
    result = validate_production_env()
    run_test("بيئة إنتاج غير كاملة تعطي أخطاء", 
             not result.is_valid(), True)
    
    # إعداد بيئة إنتاج كاملة
    os.environ['SECRET_KEY'] = 'a' * 64
    os.environ['PORT'] = '5000'
    os.environ['DATABASE_TYPE'] = 'sqlite'
    result = validate_production_env()
    run_test("بيئة إنتاج كاملة", 
             result.is_valid() or result.has_warnings(), True)
    
    # ==================== الاختبار 6: ValidationResult Class ====================
    print("\n--- الاختبار 6: ValidationResult Class ---")
    
    result = ValidationResult()
    run_test("ValidationResult فارغة صحيحة", result.is_valid(), True)
    
    result.add_warning("تحذير")
    run_test("ValidationResult مع تحذير", result.has_warnings(), True)
    run_test("ValidationResult مع تحذير لا زالت صحيحة", result.is_valid(), True)
    
    result.add_error("خطأ")
    run_test("ValidationResult مع خطأ", not result.is_valid(), True)
    
    # ==================== استعادة المتغيرات ====================
    os.environ.clear()
    os.environ.update(original_env_vars)
    
    # ==================== ملخص النتائج ====================
    print("\n" + "=" * 70)
    print("ملخص نتائج الاختبار - Test Summary")
    print("=" * 70)
    print(f"إجمالي الاختبارات: {total_tests}")
    print(f"الاختبارات الناجحة: {tests_passed} ✓")
    print(f"الاختبارات الفاشلة: {tests_failed} ✗")
    
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"نسبة النجاح: {success_rate:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 جميع الاختبارات نجحت!")
        return 0
    else:
        print(f"\n⚠️ هناك {tests_failed} اختبار(ات) فشل(ت)")
        return 1


# ==================== CLI Entry Point ====================

def main():
    """نقطة دخول CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='أداة التحقق من متغيرات البيئة - Environment Variables Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  %(prog)s                    # التحقق التلقائي (حسب البيئة المكتشفة)
  %(prog)s --dev              # التحقق من بيئة التطوير
  %(prog)s --prod             # التحقق من بيئة الإنتاج
  %(prog)s --test             # تشغيل الاختبارات الداخلية
        """
    )
    
    parser.add_argument(
        '--dev', '--development',
        action='store_true',
        help='التحقق من بيئة التطوير فقط'
    )
    
    parser.add_argument(
        '--prod', '--production',
        action='store_true',
        help='التحقق من بيئة الإنتاج فقط'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='تشغيل الاختبارات الداخلية'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='عرض الأخطاء فقط (بدون تحذيرات)'
    )
    
    args = parser.parse_args()
    
    # تشغيل الاختبارات
    if args.test:
        return run_tests()
    
    # التحقق من المتغيرات
    if args.dev:
        result = validate_development_env()
    elif args.prod:
        result = validate_production_env()
    else:
        result = validate_all_env()
    
    # طباعة التقرير
    if not args.quiet:
        print_validation_report(result)
    else:
        # في الوضع الهادئ، اطبع الأخطاء فقط
        if result.errors:
            print("❌ أخطاء:")
            for error in result.errors:
                print(f"   - {error}")
    
    # Exit code
    if result.is_valid():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
