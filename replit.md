# aaPanel - لوحة تحكم الخادم

## Overview
aaPanel is a powerful server management control panel built with Python/Flask, offering a graphical web interface for easy server administration. The project aims to provide a robust, multi-environment solution for both development (Replit) and production (VPS) deployments, focusing on ease of use, security, and maintainability. Key capabilities include multi-database support (SQLite, MySQL, PostgreSQL), advanced security features, and a scalable architecture.

## User Preferences
### متطلبات التوثيق
- يجب تحديث حالة كل مهمة فور إنجازها
- توثيق واضح لما تم إنجازه وما تبقى
- تمكين الفريق من معرفة نقطة التوقف ونقطة الاستكمال

### التواصل
- **اللغة المفضلة**: العربية فقط في جميع الردود
- التوثيق يجب أن يكون واضح ومفصل

## System Architecture
The project leverages Python 3.12 and the Flask framework, served with Gunicorn for production environments. Core architectural decisions include a Factory Pattern for configuration management (`config_factory.py`), an `environment_detector.py` for runtime environment identification (Replit or VPS), and `env_validator.py` for configuration validation.

**Key Architectural Features:**
-   **Multi-Environment Support:** Distinct configurations for Development (Replit, SQLite, DEBUG True) and Production (VPS, external MySQL/PostgreSQL, Nginx, systemd, DEBUG False).
-   **Configuration Management:** `config_factory.py` provides `BaseConfig`, `DevelopmentConfig`, and `ProductionConfig` classes for dynamic settings loading, with `SECRET_KEY` mandatory in production.
-   **Environment Detection:** `environment_detector.py` automatically detects Replit vs. VPS environments.
-   **Containerization:** A multi-stage `Dockerfile` is provided for production, utilizing `python:3.12-slim`, Gunicorn with `GeventWebSocketWorker`. Docker Compose is used for orchestration with `docker-compose.yml` (production) and `docker-compose.override.yml` (development), including PostgreSQL 15 and Redis 7 services.
-   **Core Files & Structure:** `runserver.py` as the application entry point and `BTPanel/` for core application logic.
-   **UI/UX:** Focuses on a graphical web interface for server management.
-   **Security:** Enforces `SECRET_KEY` in production, supports SSL/TLS, and uses `.dockerignore` for sensitive data.
-   **Nginx Configuration:** Includes comprehensive Nginx setup for production, supporting HTTPS, WebSocket proxying, security headers, rate limiting, and performance optimizations. A two-phase setup script handles initial HTTP-only configuration for ACME challenges, followed by full HTTPS.
-   **systemd Integration:** Advanced `systemd` unit file (`aapanel.service`) for managing Gunicorn in production, running as a non-root user (`www`), with robust restart policies, resource limits, and security hardening. Gunicorn configuration (`gunicorn_config.py`) dynamically calculates workers and supports WebSockets.

## External Dependencies
-   **Web Server:** Gunicorn (with `GeventWebSocketWorker`)
-   **Databases:** SQLite (development), MySQL, PostgreSQL (production)
-   **Database Drivers:** `PyMySQL`, `psycopg2`
-   **Reverse Proxy/Web Server:** Nginx (production)
-   **Process Management:** systemd (production)
-   **Containerization:** Docker
-   **Caching/Message Broker:** Redis
-   **SSL Certificate Management:** Certbot (for Let's Encrypt)

## Recent Changes
### 2025-09-30: CI/CD Pipeline - GitHub Actions Setup (المهمة 3.1) ✅
**المسؤول:** الوكيل رقم 7

**ما تم إنجازه:**
1. **اختبارات شاملة (96 اختبار pytest - 100% نجاح)**
   - `tests/test_environment_detector.py` - 14 اختبار
   - `tests/test_config_factory.py` - 54 اختبار
   - `tests/test_env_validator.py` - 19 اختبار
   - `tests/__init__.py` و `tests/README.md`

2. **GitHub Actions Workflows**
   - `.github/workflows/test.yml` - اختبارات تلقائية، coverage، security scanning (Bandit + Safety)
   - `.github/workflows/lint.yml` - linting (Flake8)، formatting (Black + isort) - بدون continue-on-error

3. **ملفات الإعدادات**
   - `pytest.ini` - تكوين pytest شامل
   - `.flake8` - معايير linting
   - `.coveragerc` - تغطية الكود

4. **حزم التطوير**
   - `requirements-dev.txt` - منفصل تماماً عن requirements.txt، يحتوي على:
     * pytest، pytest-cov، pytest-mock
     * flake8، black، isort
     * bandit، safety

5. **تنظيف requirements.txt**
   - إزالة جميع أدوات التطوير (كانت مضافة بالخطأ)
   - إزالة 23 مكتبة مكررة
   - حذف السطر "db" الخاطئ
   - النتيجة: 127 سطراً نظيفاً (بدلاً من 167)

**التحديات وحلولها:**
- **التحدي 1:** workflows كانت تستخدم `continue-on-error: true` على Black/isort
  - **الحل:** إزالة `continue-on-error` لفرض معايير الكود
- **التحدي 2:** requirements.txt ملوث بأدوات تطوير مكررة مرتين
  - **الحل:** تنظيف شامل وفصل كامل للاعتماديات

**الحالة النهائية:** ✅ Pass من Architect - جاهز للإنتاج

**نسبة التقدم الإجمالية:** 28.6% (المرحلة 3.1 من أصل 7 مراحل)

### 2025-09-30: CI/CD Pipeline - Docker Build Automation (المهمة 3.2) ✅
**المسؤول:** الوكيل رقم 8

**ما تم إنجازه:**
1. **GitHub Actions Workflow للبناء التلقائي**
   - `.github/workflows/build.yml` - workflow شامل لبناء ورفع Docker images
   - Build triggers: push (main/develop)، tags (v*.*.*)، manual dispatch
   - Multi-platform builds: linux/amd64، linux/arm64

2. **Docker Registry Integration**
   - GitHub Container Registry (ghcr.io) كـ registry رسمي
   - تسجيل دخول تلقائي باستخدام GITHUB_TOKEN
   - Permissions محددة: contents:read، packages:write، id-token:write

3. **Tagging Strategy المتقدم**
   - Branch names: main → main، develop → develop
   - Semantic versions: v1.2.3 → 1.2.3، 1.2، 1
   - Git SHA: short format (7 أحرف)
   - Tag "latest": للـ main branch فقط
   - OCI labels كاملة (title، description، vendor، maintainer)

4. **Performance Optimization**
   - Docker Buildx مع multi-platform support
   - Layer caching: GitHub Actions Cache (type=gha, mode=max)
   - BUILDKIT_INLINE_CACHE للتحسين الإضافي

5. **Security Features**
   - SBOM generation (Software Bill of Materials) - SPDX format
   - Vulnerability scanning: Anchore Grype
   - SARIF report upload لـ GitHub Security
   - Severity cutoff: critical (لا يفشل البناء)

6. **Automated Testing**
   - Test job منفصل يختبر الصورة المبنية
   - Pull image بواسطة digest (موثوقية 100%)
   - Health check تلقائي (curl http://localhost:5000/)
   - عرض logs قبل التنظيف

**التحديات وحلولها:**
- **التحدي 1:** SHA tag mismatch - test job كان يحاول pull tag غير موجود
  - **الحل:** استخدام digest outputs من build job بدلاً من github.sha
  - النتيجة: test job الآن يستخدم `needs.build.outputs.digest` للدقة الكاملة

**الحالة النهائية:** ✅ Pass من Architect - جاهز للإنتاج

**نسبة التقدم الإجمالية:** 35.7% (المرحلة 3.2 من أصل 7 مراحل)

### 2025-09-30: CI/CD Pipeline - VPS Deployment Automation (المهمة 3.3) ✅
**المسؤول:** الوكيل رقم 8

**ما تم إنجازه:**
1. **GitHub Actions Workflow للنشر التلقائي**
   - `.github/workflows/deploy.yml` - workflow شامل للنشر على VPS
   - Trigger: بعد build ناجح على main branch، أو manual dispatch
   - SSH deployment آمن باستخدام SSH keys
   - 9 خطوات متكاملة: إعداد SSH → backup → نسخ ملفات → تنفيذ → health check → rollback

2. **docker-compose.prod.yml - Production Configuration**
   - استخدام صور مبنية من ghcr.io (لا حاجة لـ build context)
   - Environment variables: REGISTRY، IMAGE_NAME، IMAGE_TAG
   - PostgreSQL 15 + Redis 7 + health checks شاملة
   - Persistent volumes للبيانات والـ logs

3. **Deployment Script (deploy.sh)**
   - التحقق من المتطلبات (Docker، Docker Compose، .env)
   - Pull الصورة الجديدة من ghcr.io
   - إيقاف آمن للخدمات الحالية
   - تنظيف الموارد غير المستخدمة
   - بدء الخدمات الجديدة
   - Health check شامل (15 محاولة × 5 ثوانٍ)
   - عرض ملخص النشر والإحصائيات

4. **Advanced Rollback Mechanism (3 iterations مع architect)**
   - **خطوة 3:** حفظ docker-compose.yml القديم → docker-compose.prev.yml **قبل** الاستبدال
   - **خطوة 4:** نسخ docker-compose.prod.yml الجديد واستبداله
   - **خطوة 8:** rollback عند الفشل (deployment أو health check):
     * استعادة docker-compose.prev.yml الحقيقي
     * إعادة تشغيل بالتكوين السابق
     * fallback: إعادة تشغيل النسخة الحالية

5. **Documentation (DEPLOYMENT_SECRETS.md)**
   - توثيق شامل للـ secrets المطلوبة (9 متغيرات)
   - تعليمات إعداد VPS خطوة بخطوة
   - Security best practices
   - Troubleshooting guide
   - Maintenance instructions

**التحديات وحلولها (3 مشاكل حرجة):**
- **التحدي 1:** docker-compose.yml يستخدم build context محلي
  - **الحل:** إنشاء docker-compose.prod.yml يستخدم image من ghcr.io
  
- **التحدي 2:** rollback condition لا يغطي فشل health check
  - **الحل:** تغيير من `if: failure() && steps.deploy.outcome == 'failure'` إلى `if: failure()`
  
- **التحدي 3:** backup timing خاطئ - ينسخ الملف الجديد بدلاً من القديم
  - **الحل:** فصل خطوة backup (خطوة 3) قبل نسخ الملفات (خطوة 4)
  - النتيجة: docker-compose.prev.yml يحتوي على النسخة الحقيقية القديمة

**الميزات الرئيسية:**
- ✅ SSH deployment آمن مع key management
- ✅ Docker image من ghcr.io (لا حاجة لملفات على VPS)
- ✅ Health checks متعددة المستويات
- ✅ Rollback تلقائي موثوق (architect approved بعد 3 iterations)
- ✅ Resource cleanup تلقائي
- ✅ توثيق شامل للإعداد والصيانة

**الحالة النهائية:** ✅ Pass من Architect - جاهز للإنتاج (بعد 3 مراجعات)

**نسبة التقدم الإجمالية:** 42.9% (المرحلة 3.3 من أصل 7 مراحل)