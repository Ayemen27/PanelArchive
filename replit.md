# aaPanel - لوحة تحكم الخادم

## Overview
aaPanel is a powerful server management control panel built with Python/Flask, offering a graphical web interface for easy server administration. The project aims to provide a robust, multi-environment solution for both development (Replit) and production (VPS) deployments, focusing on ease of use, security, and maintainability. Key capabilities include multi-database support (SQLite, MySQL, PostgreSQL), advanced security features, and a scalable architecture. The business vision is to provide a comprehensive, user-friendly control panel that simplifies server management for a wide range of users, from developers to system administrators, with ambitions to capture a significant share of the server management software market due to its flexibility and open-source nature.

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
-   **Containerization:** A multi-stage `Dockerfile` is provided for production, utilizing `python:3.12-slim`, Gunicorn with `GeventWebSocketWorker`. Docker Compose is used for orchestration with `docker-compose.yml` (production) and `docker-compose.override.yml` (development), including PostgreSQL 15 and Redis 7 services. Blue-Green deployment strategy is implemented using `docker-compose.shared.yml`, `docker-compose.blue.yml`, and `docker-compose.green.yml` for zero-downtime deployments with isolated environments and shared services.
-   **Core Files & Structure:** `runserver.py` as the application entry point and `BTPanel/` for core application logic.
-   **UI/UX:** Focuses on a graphical web interface for server management.
-   **Security:** Enforces `SECRET_KEY` in production, supports SSL/TLS, and uses `.dockerignore` for sensitive data.
-   **Nginx Configuration:** Includes comprehensive Nginx setup for production, supporting HTTPS, WebSocket proxying, security headers, rate limiting, and performance optimizations. A two-phase setup script handles initial HTTP-only configuration for ACME challenges, followed by full HTTPS.
-   **systemd Integration:** Advanced `systemd` unit file (`aapanel.service`) for managing Gunicorn in production, running as a non-root user (`www`), with robust restart policies, resource limits, and security hardening. Gunicorn configuration (`gunicorn_config.py`) dynamically calculates workers and supports WebSockets.
-   **CI/CD Pipeline:** Implemented via GitHub Actions for automated testing (pytest, coverage, security scanning with Bandit and Safety), linting/formatting (Flake8, Black, isort), multi-platform Docker image builds (GitHub Container Registry, SBOM generation, vulnerability scanning with Grype), and automated Blue-Green deployments to VPS. Includes a robust rollback mechanism and comprehensive health checks.

## External Dependencies
-   **Web Server:** Gunicorn (with `GeventWebSocketWorker`)
-   **Databases:** SQLite (development), MySQL, PostgreSQL (production)
-   **Database Drivers:** `PyMySQL`, `psycopg2`
-   **Reverse Proxy/Web Server:** Nginx (production)
-   **Process Management:** systemd (production)
-   **Containerization:** Docker
-   **Caching/Message Broker:** Redis
-   **SSL Certificate Management:** Certbot (for Let's Encrypt)
-   **CI/CD Platform:** GitHub Actions
-   **Container Registry:** GitHub Container Registry (ghcr.io)
-   **Security Scanners:** Bandit, Safety, Anchore Grype

## 📊 حالة المشروع الحالية

### التقدم الإجمالي: 58% (3 مراحل + 1 مهمة من المرحلة 4)

#### ✅ المرحلة 1: البنية التحتية - مكتملة 100%
- ✅ environment_detector.py (14 اختبار بنسبة نجاح 100%)
- ✅ config_factory.py (54 اختبار بنسبة نجاح 100%)
- ✅ env_validator.py (19 اختبار بنسبة نجاح 100%)
- ✅ runserver.py محدّث ويستخدم config_factory

#### ✅ المرحلة 2: Containerization - مكتملة 100%
- ✅ Dockerfile (multi-stage build مع Python 3.12)
- ✅ docker-compose.yml (PostgreSQL 15 + Redis 7 + App)
- ✅ docker-compose.override.yml (للتطوير)
- ✅ docker-compose.prod.yml (للإنتاج)
- ✅ Blue-Green: docker-compose.blue/green/shared.yml
- ✅ nginx.conf.template (SSL/TLS + WebSocket)
- ✅ aapanel.service (systemd مع virtualenv)
- ✅ gunicorn_config.py (محدّث مع config_factory)

#### ✅ المرحلة 3: CI/CD Pipeline - مكتملة 100%
- ✅ .github/workflows/test.yml (96 اختبار pytest)
- ✅ .github/workflows/lint.yml (Flake8, Black, isort)
- ✅ .github/workflows/build.yml (multi-platform Docker)
- ✅ .github/workflows/deploy.yml (automated deployment)
- ✅ .github/workflows/blue-green-deploy.yml (zero-downtime)

#### 🟣 المرحلة 4: قاعدة البيانات - قيد التنفيذ (33%)
- ✅ تحسين نظام Migrations (مكتمل - الوكيل 9 + الوكيل 11)
- [ ] استراتيجية النسخ الاحتياطي
- [ ] Database Connection Pooling

#### ⏳ المرحلة 5: المراقبة - لم تبدأ
- [ ] Health & Readiness Endpoints
- [ ] Prometheus & Grafana
- [ ] نظام التنبيهات
- [ ] Centralized Logging

#### ⏳ المرحلة 6: الأمان - لم تبدأ
- [ ] SSL/TLS Setup
- [ ] Firewall Configuration
- [ ] Fail2Ban
- [ ] Security Hardening

#### ⏳ المرحلة 7: التوثيق - لم تبدأ
- [ ] توثيق النشر
- [ ] API Documentation
- [ ] دليل المطور

## 📝 آخر التغييرات

### 2025-10-01 (الوكيل رقم 12)
**إصلاح الثغرات الأمنية الحرجة في نظام النسخ الاحتياطي:**
- ✅ إضافة خيار --force للاستعادة بدون تأكيد يدوي
- ✅ إنشاء سكريبت تنظيف للملفات .info القديمة (fix_legacy_info_files.py)
- ✅ إصلاح جميع الثغرات الأمنية الحرجة:
  - ✅ **MD5 Verification Fail-Close**: رفض الاستعادة إذا لم يوجد .info أو MD5 (ما لم يُستخدم --skip-md5)
  - ✅ **Path Containment**: استخدام relative_to() بدلاً من string comparison لمنع تجاوز المسارات
  - ✅ **Safe Extraction**: منع symlinks, hardlinks, device files, special files
  - ✅ **Absolute Path Protection**: رفض المسارات المطلقة (/)
  - ✅ **Path Traversal Protection**: رفض (..) في المسارات
- ✅ تحديث backup_manager.py مع safe_members extraction
- ✅ إضافة CLI flags: --force, --skip-md5
- ✅ الموافقة من architect بعد 3 دورات مراجعة
- 📍 **المهمة التالية: المرحلة 4.2 - إكمال استراتيجية النسخ الاحتياطي (جدولة، رفع S3)**

### 2025-10-01 (الوكيل رقم 11)
**إكمال نظام Validation للـ Migrations:**
- ✅ مراجعة محادثات الوكيل رقم 10
- ✅ إنشاء migration_validator.py (645 سطر)
- ✅ نظام validation شامل:
  - validate_migration_file() - التحقق من بنية الملف
  - validate_upgrade_downgrade() - التحقق من دالتي upgrade/downgrade
  - validate_revision_format() - التحقق من تنسيق revision
  - check_sql_injection() - فحص SQL injection
  - validate_batch_mode() - التحقق من SQLite batch mode
  - validate_all_migrations() - التحقق من جميع migrations
- ✅ CLI interface كامل مع ألوان ANSI
- ✅ اختبار ناجح: 001_initial_baseline.py (PASSED)
- ✅ تحديث التوثيق (replit.md، خطة_التطوير.md، قائمة_التحقق.md)

### 2025-09-30 (الوكيل رقم 9) - مساءً
**المهمة 4.1: إنشاء نظام Migrations متكامل**
- ✅ تحليل البنية الحالية: 27 جدول في default.db
- ✅ تثبيت Alembic و Flask-Migrate
- ✅ إنشاء بنية migrations كاملة:
  - alembic.ini
  - migrations/env.py (متكامل مع config_factory)
  - migrations/script.py.mako
  - migrations/migrate.py
  - migrations/versions/001_initial_baseline.py
- ✅ كتابة 13 اختبار - نجحت جميعها 100%
- ✅ توثيق شامل: migrations/README.md, MIGRATIONS_GUIDE.md
- 📍 **المهمة التالية: المرحلة 4.2 - استراتيجية النسخ الاحتياطي**

### 2025-09-30 (الوكيل رقم 9) - صباحاً
**المراجعة الشاملة وتحديث التوثيق:**
- ✅ مراجعة جميع المراحل المكتملة (1، 2، 3)
- ✅ التحقق من وجود جميع الملفات والاختبارات
- ✅ environment_detector.py: 14 اختبار نجح 100%
- ✅ config_factory.py: جميع الاختبارات نجحت
- ✅ تحديث replit.md بحالة المشروع الفعلية
- ✅ توثيق الإنجازات والملفات المنشأة

### 2025-09-30 (الوكيل رقم 8)
- ✅ المهمة 3.2: GitHub Actions Build Workflow
- ✅ المهمة 3.3: Automated Deployment to VPS
- ✅ الملفات: build.yml, deploy.yml, docker-compose.prod.yml, deploy.sh

### 2025-09-30 (الوكيل رقم 7)
- ✅ المهمة 3.1: GitHub Actions Testing Workflow
- ✅ 96 اختبار pytest بنسبة نجاح 100%
- ✅ الملفات: test.yml, lint.yml, pytest.ini, tests/

### 2025-09-30 (الوكيل رقم 6)
- ✅ المهمة 2.4: systemd Service للإنتاج
- ✅ الملفات: aapanel.service, gunicorn_config.py, setup_systemd.sh, SYSTEMD_SETUP.md

### 2025-09-30 (الوكيل رقم 5)
- ✅ المهمة 2.3: nginx Configuration
- ✅ الملفات: nginx.conf.template, proxy_params, setup_nginx.sh, NGINX_SETUP.md

### 2025-09-30 (الفريق السابق)
- ✅ المرحلة 1 (البنية التحتية) مكتملة
- ✅ المهام 2.1 و 2.2 (Docker & Docker Compose)
- ✅ المهمة 3.4 (Blue-Green Deployment)

## 🎯 المهمة التالية
**المرحلة 4.2: استراتيجية النسخ الاحتياطي**
- الأولوية: متوسطة
- المدة المتوقعة: 3-4 ساعات
- المتطلبات: سكريبت backup تلقائي، جدولة يومية، رفع للسحابة (S3)، اختبار الاستعادة
