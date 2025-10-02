# 👨‍💻 دليل المطورين - Developer Guide

<div align="center">

[![aaPanel](https://img.shields.io/badge/aaPanel-aaPanel-blue)](https://github.com/aaPanel/aaPanel)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.2.5-green.svg)](https://flask.palletsprojects.com/)

**دليل شامل للبدء بتطوير aaPanel**

**Comprehensive guide to start developing aaPanel**

</div>

---

## 📋 جدول المحتويات - Table of Contents

1. [نظرة عامة](#-نظرة-عامة---overview)
2. [المتطلبات الأساسية](#-المتطلبات-الأساسية---prerequisites)
3. [البدء السريع](#-البدء-السريع---quick-start)
4. [بنية المشروع](#-بنية-المشروع---project-structure)
5. [إعداد بيئة التطوير](#-إعداد-بيئة-التطوير---development-environment-setup)
6. [تشغيل الاختبارات](#-تشغيل-الاختبارات---running-tests)
7. [تطوير Docker](#-تطوير-docker---docker-development)
8. [المهام الشائعة](#-المهام-الشائعة---common-tasks)
9. [نصائح التصحيح](#-نصائح-التصحيح---debugging-tips)
10. [الأوامر المفيدة](#-الأوامر-المفيدة---useful-commands)
11. [المراجع](#-المراجع---references)

---

## 🌟 نظرة عامة - Overview

### ما هو aaPanel؟

**aaPanel** هي لوحة تحكم خادم قوية وسهلة الاستخدام مبنية بـ Python/Flask.

**aaPanel** is a powerful and user-friendly server control panel built with Python/Flask.

### التقنيات المستخدمة - Tech Stack

| المكون | التقنية | الإصدار |
|--------|---------|---------|
| **Backend** | Python | 3.12 |
| **Framework** | Flask | 2.2.5 |
| **Server** | Gunicorn | 20.1.0 |
| **Database** | PostgreSQL/MySQL/SQLite | 15+/8+/3+ |
| **Cache** | Redis | 7+ |
| **Container** | Docker | 20.10+ |
| **Monitoring** | Prometheus + Grafana | Latest |
| **Logging** | Loki + Promtail | Latest |

### الميزات الرئيسية - Key Features

- ✅ **Multi-Database Support** - دعم PostgreSQL, MySQL, SQLite
- ✅ **Environment Detection** - كشف تلقائي للبيئة (Replit/VPS)
- ✅ **Security Hardening** - تأمين متقدم للتطبيق
- ✅ **Blue-Green Deployment** - نشر بدون توقف
- ✅ **CI/CD Integration** - تكامل مع GitHub Actions
- ✅ **Monitoring & Alerting** - مراقبة وتنبيهات في الوقت الفعلي
- ✅ **Centralized Logging** - تسجيل موحد للأحداث
- ✅ **Automated Backups** - نسخ احتياطية تلقائية

---

## 📦 المتطلبات الأساسية - Prerequisites

### 1️⃣ Python 3.12

```bash
# تحقق من إصدار Python
# Check Python version
python3 --version
# يجب أن يكون >= 3.12
# Should be >= 3.12

# تثبيت Python 3.12 (Ubuntu/Debian)
# Install Python 3.12 (Ubuntu/Debian)
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

# تثبيت Python 3.12 (macOS with Homebrew)
brew install python@3.12
```

### 2️⃣ Git

```bash
# تحقق من Git
# Check Git
git --version

# تثبيت Git (Ubuntu/Debian)
sudo apt install git

# تثبيت Git (macOS)
brew install git
```

### 3️⃣ Docker و Docker Compose (اختياري - للتطوير)

```bash
# تحقق من Docker
# Check Docker
docker --version          # >= 20.10
docker-compose --version  # >= 1.29

# تثبيت Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# تثبيت Docker Compose
sudo apt install docker-compose

# تثبيت Docker (macOS)
# حمّل Docker Desktop من
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop
```

### 4️⃣ أدوات إضافية - Additional Tools

```bash
# pip (مدير حزم Python)
# pip (Python package manager)
python3 -m pip --version

# virtualenv
pip install virtualenv
```

---

## 🚀 البدء السريع - Quick Start

### الطريقة 1: التطوير المحلي (Local Development)

```bash
# 1️⃣ استنسخ المشروع - Clone the repository
git clone https://github.com/aaPanel/aaPanel.git
cd aaPanel

# 2️⃣ أنشئ بيئة افتراضية - Create virtual environment
python3 -m venv pyenv
source pyenv/bin/activate  # Linux/macOS
# أو - or
pyenv\Scripts\activate     # Windows

# 3️⃣ ثبّت المتطلبات - Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # للتطوير - for development

# 4️⃣ أنشئ ملف .env - Create .env file
cp .env.example .env
nano .env  # عدّل المتغيرات - Edit variables

# 5️⃣ شغّل التطبيق - Run the application
python runserver.py
```

**الوصول للتطبيق - Access the application:**
```
http://localhost:5000
```

### الطريقة 2: التطوير باستخدام Docker

```bash
# 1️⃣ استنسخ المشروع - Clone the repository
git clone https://github.com/aaPanel/aaPanel.git
cd aaPanel

# 2️⃣ أنشئ ملف .env - Create .env file
cp .env.example .env
nano .env

# 3️⃣ شغّل باستخدام docker-compose
# Run using docker-compose
docker-compose up --build

# للتشغيل في الخلفية - To run in background
docker-compose up -d

# لعرض السجلات - To view logs
docker-compose logs -f
```

**الوصول للتطبيق - Access the application:**
```
http://localhost:5000
```

### الطريقة 3: التطوير على Replit

```bash
# 1️⃣ افتح المشروع على Replit
# Open the project on Replit

# 2️⃣ انقر "Run" أو شغّل
# Click "Run" or execute:
python runserver.py

# ✅ البيئة ستُكتشف تلقائياً كـ "development"
# ✅ Environment will be auto-detected as "development"
# ✅ سيستخدم SQLite تلقائياً
# ✅ Will use SQLite automatically
```

---

## 📁 بنية المشروع - Project Structure

### الهيكل العام - Overall Structure

```
aaPanel/
│
├── 📁 BTPanel/                  # التطبيق الرئيسي - Main application
│   ├── __init__.py             # تهيئة Flask app
│   ├── routes/                 # المسارات - Routes
│   ├── static/                 # الملفات الثابتة - Static files
│   ├── templates/              # قوالب HTML - HTML templates
│   └── languages/              # ملفات الترجمة - Translation files
│
├── 📁 class/                    # فئات النسخة القديمة - Legacy classes
│   ├── public/                 # الفئات العامة - Public classes
│   ├── panelModel/             # نموذج اللوحة - Panel models
│   ├── databaseModel/          # نموذج قاعدة البيانات - Database models
│   └── ...
│
├── 📁 class_v2/                 # فئات النسخة الجديدة - New version classes
│   ├── panelModelV2/           # نموذج اللوحة V2
│   ├── databaseModelV2/        # نموذج قاعدة البيانات V2
│   └── ...
│
├── 📁 migrations/               # Database migrations (Alembic)
│   └── versions/               # ملفات الترحيل - Migration files
│
├── 📁 tests/                    # الاختبارات - Tests
│   ├── test_auth.py            # اختبارات المصادقة
│   ├── test_database.py        # اختبارات قاعدة البيانات
│   └── ...
│
├── 📁 backups/                  # النسخ الاحتياطية - Backups
│   ├── backup_manager.py       # مدير النسخ الاحتياطية
│   └── backup_validator.py     # التحقق من النسخ
│
├── 📁 monitoring/               # المراقبة - Monitoring
│   ├── prometheus/             # إعدادات Prometheus
│   └── grafana/                # لوحات Grafana
│
├── 📁 data/                     # البيانات - Data
│   ├── port.pl                 # المنفذ - Port
│   ├── db/                     # قاعدة بيانات SQLite
│   └── session/                # جلسات المستخدمين
│
├── 📁 logs/                     # السجلات - Logs
│   ├── request/                # سجلات الطلبات
│   └── ...
│
├── 📁 config/                   # إعدادات الإنتاج - Production configs
│   ├── nginx/                  # إعدادات Nginx
│   └── systemd/                # إعدادات systemd
│
├── 📄 config_factory.py         # مصنع الإعدادات - Config factory
├── 📄 environment_detector.py   # كاشف البيئة - Environment detector
├── 📄 db_pool.py                # Database connection pool
├── 📄 health_endpoints.py       # نقاط فحص الصحة - Health endpoints
├── 📄 runserver.py              # نقطة دخول التطبيق - Entry point
├── 📄 gunicorn_config.py        # إعدادات Gunicorn
│
├── 📄 requirements.txt          # متطلبات الإنتاج - Production deps
├── 📄 requirements-dev.txt      # متطلبات التطوير - Development deps
│
├── 📄 Dockerfile                # Docker image للإنتاج
├── 📄 docker-compose.yml        # Docker Compose للإنتاج
├── 📄 docker-compose.override.yml  # Override للتطوير
│
├── 📄 pytest.ini                # إعدادات pytest
├── 📄 .flake8                   # إعدادات Flake8
├── 📄 .coveragerc               # إعدادات coverage
│
├── 📄 .env.example              # مثال للمتغيرات البيئية
├── 📄 .gitignore                # ملفات Git المتجاهلة
│
├── 📄 README.md                 # نظرة عامة - Overview
├── 📄 CONTRIBUTING.md           # دليل المساهمة
├── 📄 DEVELOPER_GUIDE.md        # هذا الملف - This file
├── 📄 DEPLOYMENT.md             # دليل النشر
└── 📄 TROUBLESHOOTING.md        # استكشاف الأخطاء
```

### الملفات المهمة - Important Files

#### 1️⃣ `config_factory.py`

مصنع الإعدادات - يوفر إعدادات موحدة للتطبيق:

Config factory - Provides unified configuration for the application:

```python
from config_factory import get_config

# الحصول على الإعدادات المناسبة للبيئة الحالية
# Get appropriate config for current environment
config = get_config()

print(f"Environment: {config.ENVIRONMENT}")
print(f"Database: {config.SQLALCHEMY_DATABASE_URI}")
print(f"Port: {config.PORT}")
```

**الميزات:**
- كشف تلقائي للبيئة (development/production)
- دعم SQLite للتطوير و PostgreSQL للإنتاج
- إعدادات أمان تلقائية
- Connection pooling لقاعدة البيانات

#### 2️⃣ `environment_detector.py`

كاشف البيئة - يكتشف تلقائياً البيئة الحالية:

Environment detector - Automatically detects current environment:

```python
from environment_detector import (
    detect_environment,
    is_replit,
    is_production,
    get_environment_info
)

# كشف البيئة - Detect environment
env = detect_environment()  # "development" or "production"

# فحوصات محددة - Specific checks
if is_replit():
    print("Running on Replit")

if is_production():
    print("Running in production")

# معلومات تفصيلية - Detailed info
info = get_environment_info()
print(info)
```

#### 3️⃣ `runserver.py`

نقطة دخول التطبيق - Application entry point:

```python
# تشغيل التطبيق - Run the application
python runserver.py

# سيعرض - Will display:
# ============================================================
# 🚀 بدء تشغيل aaPanel
# ============================================================
# البيئة: development
# المضيف: 0.0.0.0
# المنفذ: 5000
# وضع التصحيح: True
# ============================================================
```

#### 4️⃣ `db_pool.py`

إدارة Connection Pool لقاعدة البيانات:

Database connection pool management:

```python
from db_pool import DatabasePool

# إنشاء pool
# Create pool
pool = DatabasePool(
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# الحصول على اتصال
# Get connection
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
```

#### 5️⃣ `health_endpoints.py`

نقاط فحص الصحة للمراقبة:

Health check endpoints for monitoring:

```bash
# فحص الصحة الأساسي - Basic health check
curl http://localhost:5000/health

# فحص صحة قاعدة البيانات - Database health
curl http://localhost:5000/health/db

# فحص صحة Redis - Redis health
curl http://localhost:5000/health/redis

# metrics للـ Prometheus
curl http://localhost:5000/metrics
```

---

## ⚙️ إعداد بيئة التطوير - Development Environment Setup

### 1️⃣ إنشاء Virtual Environment

```bash
# باستخدام venv (موصى به)
# Using venv (recommended)
python3 -m venv pyenv

# تفعيل البيئة - Activate environment
source pyenv/bin/activate  # Linux/macOS
pyenv\Scripts\activate     # Windows

# للخروج من البيئة - To deactivate
deactivate
```

**لماذا virtualenv؟ - Why virtualenv?**
- ✅ عزل المكتبات - Isolate dependencies
- ✅ تجنب التعارضات - Avoid conflicts
- ✅ سهولة الإدارة - Easy management

### 2️⃣ تثبيت المتطلبات - Install Dependencies

```bash
# تحديث pip أولاً - Update pip first
pip install --upgrade pip

# تثبيت متطلبات الإنتاج - Install production dependencies
pip install -r requirements.txt

# تثبيت متطلبات التطوير - Install development dependencies
pip install -r requirements-dev.txt
```

**محتويات `requirements-dev.txt`:**
```
pytest==7.4.3              # Testing framework
pytest-cov==4.1.0          # Coverage plugin
pytest-mock==3.12.0        # Mocking
flake8==6.1.0              # Linting
black==23.12.1             # Code formatting
isort==5.13.2              # Import sorting
bandit==1.7.6              # Security scanning
safety==2.3.5              # Dependency security
```

### 3️⃣ إعداد ملف .env

```bash
# انسخ المثال - Copy example
cp .env.example .env

# عدّل المتغيرات - Edit variables
nano .env
```

**إعدادات التطوير - Development Settings:**

```bash
# ==================== البيئة - Environment ====================
ENVIRONMENT=development

# ==================== الأمان - Security ====================
SECRET_KEY=dev-secret-key-change-in-production
SESSION_SECRET_KEY=dev-session-secret-key

# ==================== قاعدة البيانات - Database ====================
# SQLite للتطوير (افتراضي - default)
# DATABASE_URL=sqlite:///data/db/bt.db

# أو PostgreSQL إذا أردت - Or PostgreSQL if you want
# DATABASE_URL=postgresql://user:password@localhost:5432/aapanel_dev

# أو MySQL - Or MySQL
# DATABASE_URL=mysql://user:password@localhost:3306/aapanel_dev

# ==================== Redis (اختياري - optional) ====================
# REDIS_URL=redis://localhost:6379/0

# ==================== التطوير - Development ====================
DEBUG=true
FLASK_ENV=development

# ==================== المنفذ - Port ====================
PORT=5000
```

### 4️⃣ تهيئة قاعدة البيانات - Database Setup

```bash
# للتطوير بـ SQLite (لا حاجة لإعداد - no setup needed)
# SQLite سيُنشأ تلقائياً
# SQLite will be created automatically

# للتطوير بـ PostgreSQL
# For development with PostgreSQL

# 1. ثبّت PostgreSQL
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. أنشئ قاعدة بيانات
# Create database
sudo -u postgres psql
CREATE DATABASE aapanel_dev;
CREATE USER aapanel_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE aapanel_dev TO aapanel_user;
\q

# 3. حدّث DATABASE_URL في .env
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://aapanel_user:secure_password@localhost:5432/aapanel_dev

# 4. شغّل migrations
# Run migrations
flask db upgrade
```

### 5️⃣ التحقق من الإعداد - Verify Setup

```bash
# اختبر كشف البيئة - Test environment detection
python environment_detector.py

# يجب أن يعرض - Should display:
# ======================================================================
# Environment: development
# Is Replit: False
# Is Production: False
# Python Version: 3.12.x
# ======================================================================

# اختبر الإعدادات - Test config
python -c "from config_factory import get_config; c=get_config(); print(f'Env: {c.ENVIRONMENT}, DB: {c.SQLALCHEMY_DATABASE_URI}')"
```

---

## 🧪 تشغيل الاختبارات - Running Tests

### الأوامر الأساسية - Basic Commands

```bash
# تشغيل جميع الاختبارات - Run all tests
pytest

# تشغيل مع verbose output
pytest -v

# تشغيل مع عرض print statements
pytest -s

# تشغيل اختبارات محددة - Run specific tests
pytest tests/test_auth.py
pytest tests/test_auth.py::TestAuthentication::test_login_success
```

### اختبارات مع التغطية - Tests with Coverage

```bash
# تشغيل مع coverage - Run with coverage
pytest --cov=.

# تشغيل مع تقرير HTML
# Run with HTML report
pytest --cov=. --cov-report=html

# فتح التقرير - Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# تشغيل مع تقرير مفصل في terminal
# Run with detailed terminal report
pytest --cov=. --cov-report=term-missing
```

**مثال على التقرير - Coverage Report Example:**
```
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
config_factory.py           50      5    90%   45-50
environment_detector.py     30      2    93%   28-29
runserver.py                15      0   100%
------------------------------------------------------
TOTAL                       95      7    93%
```

### تشغيل حسب Markers

```bash
# اختبارات unit فقط - Unit tests only
pytest -m unit

# اختبارات integration فقط - Integration tests only
pytest -m integration

# تجاهل الاختبارات البطيئة - Skip slow tests
pytest -m "not slow"

# اختبارات الأمان فقط - Security tests only
pytest -m security
```

**تعريف Markers في `pytest.ini`:**
```ini
[pytest]
markers =
    unit: اختبارات الوحدة
    integration: اختبارات التكامل
    slow: اختبارات بطيئة
    security: اختبارات الأمان
```

### كتابة اختبار جديد - Writing a New Test

```python
# tests/test_example.py
import pytest
from BTPanel.example import example_function

class TestExample:
    """اختبارات لـ example_function"""
    
    @pytest.mark.unit
    def test_example_basic(self):
        """اختبار أساسي - Basic test"""
        result = example_function(10)
        assert result == 20
    
    @pytest.mark.unit
    def test_example_with_zero(self):
        """اختبار مع صفر - Test with zero"""
        result = example_function(0)
        assert result == 0
    
    @pytest.mark.unit
    def test_example_raises_error(self):
        """اختبار الاستثناءات - Test exceptions"""
        with pytest.raises(ValueError):
            example_function(-1)
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_example_integration(self):
        """اختبار تكامل - Integration test"""
        # هذا اختبار بطيء ويتطلب موارد خارجية
        # This is a slow test requiring external resources
        pass
```

---

## 🐳 تطوير Docker - Docker Development

### استخدام docker-compose.override.yml

ملف `docker-compose.override.yml` يوفر إعدادات تطوير مع Hot Reload:

`docker-compose.override.yml` provides development settings with Hot Reload:

```bash
# التشغيل (سيستخدم override تلقائياً)
# Run (will use override automatically)
docker-compose up

# أو بشكل صريح - Or explicitly
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# التشغيل في الخلفية - Run in background
docker-compose up -d

# إيقاف - Stop
docker-compose down

# إعادة البناء - Rebuild
docker-compose up --build
```

**الميزات في override:**
- ✅ Bind mount للكود (hot reload)
- ✅ SQLite للتطوير (لا حاجة لـ PostgreSQL)
- ✅ Redis للـ caching
- ✅ منفذ debugger (5678)
- ✅ إعادة تشغيل تلقائية

### Hot Reload

```bash
# عدّل أي ملف Python
# Edit any Python file

# Gunicorn سيعيد تحميل التطبيق تلقائياً
# Gunicorn will reload the app automatically

# راقب السجلات - Watch logs
docker-compose logs -f app
```

### التنفيذ داخل Container

```bash
# افتح shell داخل container
# Open shell inside container
docker-compose exec app bash

# شغّل أوامر Python - Run Python commands
docker-compose exec app python -c "from config_factory import get_config; print(get_config().ENVIRONMENT)"

# شغّل الاختبارات - Run tests
docker-compose exec app pytest

# شغّل migrations - Run migrations
docker-compose exec app flask db upgrade
```

### عرض السجلات - View Logs

```bash
# جميع السجلات - All logs
docker-compose logs

# سجلات تطبيق فقط - App logs only
docker-compose logs app

# متابعة السجلات - Follow logs
docker-compose logs -f

# آخر 50 سطر - Last 50 lines
docker-compose logs --tail=50 app
```

---

## 🔧 المهام الشائعة - Common Tasks

### 1️⃣ إضافة Migration جديد

```bash
# باستخدام Flask-Migrate / Alembic

# 1. أنشئ migration تلقائي
# Create auto migration
flask db migrate -m "Add user_role column"

# 2. راجع الملف المُنشأ
# Review generated file
# migrations/versions/xxxx_add_user_role_column.py

# 3. طبّق migration
# Apply migration
flask db upgrade

# 4. للتراجع - To rollback
flask db downgrade

# 5. لعرض السجل - To view history
flask db history
```

**مثال على Migration يدوي:**
```python
# migrations/versions/xxxx_add_user_role.py
def upgrade():
    op.add_column('users', sa.Column('role', sa.String(50), nullable=True))
    op.create_index('idx_user_role', 'users', ['role'])

def downgrade():
    op.drop_index('idx_user_role', 'users')
    op.drop_column('users', 'role')
```

### 2️⃣ إضافة Endpoint جديد

```python
# BTPanel/routes/example.py
from flask import Blueprint, jsonify, request
from typing import Dict, Any

bp = Blueprint('example', __name__, url_prefix='/api/example')

@bp.route('/hello', methods=['GET'])
def hello() -> Dict[str, Any]:
    """
    نقطة نهاية تجريبية - Example endpoint
    
    Returns:
        Dict[str, Any]: رسالة ترحيب - Welcome message
    """
    return jsonify({
        'message': 'Hello from aaPanel!',
        'status': 'success'
    })

@bp.route('/create', methods=['POST'])
def create() -> Dict[str, Any]:
    """
    إنشاء عنصر جديد - Create new item
    
    Returns:
        Dict[str, Any]: نتيجة العملية - Operation result
    """
    data = request.get_json()
    
    # التحقق من البيانات - Validate data
    if not data or 'name' not in data:
        return jsonify({
            'error': 'Name is required',
            'status': 'error'
        }), 400
    
    # المنطق هنا - Logic here
    
    return jsonify({
        'message': 'Created successfully',
        'status': 'success'
    }), 201
```

**تسجيل Blueprint:**
```python
# BTPanel/__init__.py
from flask import Flask
from BTPanel.routes import example

app = Flask(__name__)
app.register_blueprint(example.bp)
```

### 3️⃣ إضافة Test جديد

```python
# tests/test_example.py
import pytest
from BTPanel import app

@pytest.fixture
def client():
    """إنشاء test client - Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestExampleAPI:
    """اختبارات API مثال - Example API tests"""
    
    def test_hello_endpoint(self, client):
        """اختبار /api/example/hello"""
        response = client.get('/api/example/hello')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'message' in data
    
    def test_create_endpoint_success(self, client):
        """اختبار /api/example/create ناجح"""
        response = client.post('/api/example/create', json={
            'name': 'Test Item'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_create_endpoint_missing_name(self, client):
        """اختبار /api/example/create بدون name"""
        response = client.post('/api/example/create', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
```

### 4️⃣ تشغيل Linting

```bash
# Flake8 - فحص الأخطاء
# Flake8 - Check for errors
flake8 .

# Black - تنسيق الكود
# Black - Format code
black .

# Black - فحص فقط (بدون تعديل)
# Black - Check only (no modification)
black --check .

# isort - ترتيب imports
# isort - Sort imports
isort .

# isort - فحص فقط
# isort - Check only
isort --check .

# تشغيل الكل - Run all
flake8 . && black --check . && isort --check .
```

**إصلاح المشاكل تلقائياً:**
```bash
# إصلاح التنسيق - Fix formatting
black .

# إصلاح ترتيب imports - Fix import ordering
isort .
```

### 5️⃣ فحص الأمان

```bash
# Bandit - فحص نقاط ضعف الأمان
# Bandit - Security vulnerability scanner
bandit -r . -ll

# Safety - فحص المكتبات المعروفة بثغرات
# Safety - Check for known vulnerabilities in dependencies
safety check

# فحص شامل - Comprehensive check
bandit -r . -ll && safety check
```

---

## 🐛 نصائح التصحيح - Debugging Tips

### 1️⃣ استخدام Python Debugger (pdb)

```python
# أضف breakpoint في الكود - Add breakpoint in code
import pdb; pdb.set_trace()

# أو استخدم breakpoint() في Python 3.7+
# Or use breakpoint() in Python 3.7+
breakpoint()
```

**أوامر pdb المفيدة:**
```
n (next)       # السطر التالي - Next line
s (step)       # دخول الدالة - Step into function
c (continue)   # متابعة - Continue
p variable     # طباعة متغير - Print variable
l (list)       # عرض الكود - Show code
q (quit)       # خروج - Quit
```

### 2️⃣ Logging

```python
import logging

# إعداد logger - Setup logger
logger = logging.getLogger(__name__)

# مستويات مختلفة - Different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### 3️⃣ Flask Debug Mode

```bash
# في .env
# In .env
DEBUG=true
FLASK_ENV=development

# سيعطيك - Will give you:
# ✅ Auto-reload عند تغيير الكود
# ✅ تتبع الأخطاء التفاعلي في المتصفح
# ✅ معلومات تفصيلية عن الأخطاء
```

### 4️⃣ فحص قاعدة البيانات

```python
# فتح shell تفاعلي - Open interactive shell
flask shell

# داخل shell - Inside shell
from BTPanel import db
from BTPanel.models import User

# عرض جميع المستخدمين - Show all users
users = User.query.all()
for user in users:
    print(user.username)

# البحث - Search
user = User.query.filter_by(username='admin').first()
print(user)
```

### 5️⃣ مراقبة Performance

```python
# استخدم time decorator - Use time decorator
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    # كود بطيء - Slow code
    time.sleep(2)
```

---

## 📚 الأوامر المفيدة - Useful Commands

### Git Commands

```bash
# إنشاء فرع جديد - Create new branch
git checkout -b feature/my-feature

# حفظ التغييرات - Save changes
git add .
git commit -m "feat: add new feature"

# دفع الفرع - Push branch
git push origin feature/my-feature

# تحديث من upstream - Update from upstream
git fetch upstream
git merge upstream/main

# عرض الحالة - Show status
git status

# عرض السجل - Show log
git log --oneline --graph --all
```

### Python Commands

```bash
# عرض المكتبات المثبتة - Show installed packages
pip list

# عرض معلومات مكتبة - Show package info
pip show flask

# تجميد المتطلبات - Freeze requirements
pip freeze > requirements.txt

# تحديث المكتبات - Update packages
pip install --upgrade package_name

# إزالة مكتبة - Uninstall package
pip uninstall package_name
```

### Docker Commands

```bash
# عرض الحاويات - Show containers
docker ps
docker ps -a  # بما فيها المتوقفة - including stopped

# عرض الصور - Show images
docker images

# حذف حاوية - Remove container
docker rm container_name

# حذف صورة - Remove image
docker rmi image_name

# تنظيف - Clean up
docker system prune -a

# عرض استخدام الموارد - Show resource usage
docker stats
```

### Database Commands

```bash
# PostgreSQL
psql -U username -d database_name
\dt                    # عرض الجداول - Show tables
\d table_name          # وصف جدول - Describe table
\q                     # خروج - Quit

# MySQL
mysql -u username -p database_name
SHOW TABLES;           # عرض الجداول
DESCRIBE table_name;   # وصف جدول
EXIT;                  # خروج

# SQLite
sqlite3 data/db/bt.db
.tables                # عرض الجداول
.schema table_name     # وصف جدول
.quit                  # خروج
```

---

## 📖 المراجع - References

### الأدلة الرسمية - Official Guides

- 📄 [README.md](README.md) - نظرة عامة على المشروع
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - دليل المساهمة
- 🚀 [DEPLOYMENT.md](DEPLOYMENT.md) - دليل النشر
- 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - استكشاف الأخطاء

### التوثيق الخارجي - External Documentation

- 🐍 [Python 3.12 Documentation](https://docs.python.org/3.12/)
- 🌶️ [Flask Documentation](https://flask.palletsprojects.com/)
- 🦄 [Gunicorn Documentation](https://docs.gunicorn.org/)
- 🐘 [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- 🐬 [MySQL Documentation](https://dev.mysql.com/doc/)
- 🔴 [Redis Documentation](https://redis.io/documentation)
- 🐳 [Docker Documentation](https://docs.docker.com/)
- 📊 [Prometheus Documentation](https://prometheus.io/docs/)
- 📈 [Grafana Documentation](https://grafana.com/docs/)

### أدوات التطوير - Development Tools

- 🧪 [pytest Documentation](https://docs.pytest.org/)
- 🎨 [Black Documentation](https://black.readthedocs.io/)
- 📏 [Flake8 Documentation](https://flake8.pycqa.org/)
- 🔒 [Bandit Documentation](https://bandit.readthedocs.io/)
- 📦 [pip Documentation](https://pip.pypa.io/)

---

## 💡 نصائح عامة - General Tips

### للمطورين الجدد - For New Developers

1. ✅ **ابدأ صغيراً** - Start small
   - افهم بنية المشروع أولاً
   - Understand project structure first

2. ✅ **اقرأ الكود الموجود** - Read existing code
   - تعلم من الأمثلة الموجودة
   - Learn from existing examples

3. ✅ **اختبر دائماً** - Always test
   - اكتب اختبارات لكود الجديد
   - Write tests for new code

4. ✅ **استخدم Git بحكمة** - Use Git wisely
   - commits صغيرة ومنطقية
   - Small and logical commits

5. ✅ **اطلب المساعدة** - Ask for help
   - لا تتردد في طرح الأسئلة
   - Don't hesitate to ask questions

### أفضل الممارسات - Best Practices

- ✅ اتبع معايير البرمجة - Follow coding standards
- ✅ اكتب كود نظيف وقابل للصيانة - Write clean, maintainable code
- ✅ وثّق كودك - Document your code
- ✅ راجع كود الآخرين - Review others' code
- ✅ تعلم باستمرار - Keep learning

---

## 🆘 الحصول على المساعدة - Getting Help

### قنوات الدعم - Support Channels

- 💬 **GitHub Discussions**: https://github.com/aaPanel/aaPanel/discussions
- 📧 **Email**: support@aapanel.com
- 🌐 **Website**: https://www.aapanel.com
- 📖 **Documentation**: https://doc.aapanel.com

### قبل طلب المساعدة - Before Asking for Help

1. ✅ ابحث في Issues الموجودة - Search existing Issues
2. ✅ راجع التوثيق - Check documentation
3. ✅ جرّب استكشاف الخطأ - Try troubleshooting
4. ✅ أعد إنتاج المشكلة - Reproduce the issue

### عند طلب المساعدة - When Asking for Help

قدّم المعلومات التالية:

Provide the following information:

```markdown
**البيئة - Environment:**
- OS: Ubuntu 22.04
- Python: 3.12.0
- aaPanel Version: 1.0.0

**الوصف - Description:**
وصف واضح للمشكلة
Clear description of the issue

**خطوات إعادة الإنتاج - Steps to Reproduce:**
1. ...
2. ...
3. ...

**السلوك المتوقع - Expected Behavior:**
...

**السلوك الفعلي - Actual Behavior:**
...

**السجلات - Logs:**
```
(أضف السجلات هنا)
```

**لقطات الشاشة - Screenshots:**
(إن وجدت)
```

---

<div align="center">

**مع أطيب التمنيات في رحلتك التطويرية! 🚀**

**Best wishes on your development journey! 🚀**

**صُنع بـ ❤️ من قبل مجتمع aaPanel**

**Made with ❤️ by the aaPanel Community**

</div>
