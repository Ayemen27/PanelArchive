# aaPanel - لوحة تحكم الخادم

## Overview

**aaPanel** is a powerful server management control panel built with Python/Flask, designed to provide a graphical web interface for easy server administration. The project aims to offer a robust, multi-environment solution for both development (Replit) and production (VPS) deployments, focusing on ease of use, security, and maintainability. Key capabilities include multi-database support (SQLite, MySQL, PostgreSQL), advanced security features, and a scalable architecture.

## User Preferences

### متطلبات التوثيق
- يجب تحديث حالة كل مهمة فور إنجازها
- توثيق واضح لما تم إنجازه وما تبقى
- تمكين الفريق من معرفة نقطة التوقف ونقطة الاستكمال

### التواصل
- **اللغة المفضلة**: العربية فقط في جميع الردود
- التوثيق يجب أن يكون واضح ومفصل

## System Architecture

The project leverages Python 3.12 and the Flask framework, served with Gunicorn for production environments. A core architectural decision is the implementation of a Factory Pattern for configuration management (`config_factory.py`), allowing seamless switching between development and production settings. An `environment_detector.py` automatically identifies the runtime environment (Replit or VPS), and `env_validator.py` ensures proper configuration.

**Key Architectural Features:**
-   **Multi-Environment Support:** Distinct configurations for Development (Replit, SQLite, DEBUG True) and Production (VPS, external MySQL/PostgreSQL, Nginx, systemd, DEBUG False).
-   **Configuration Management:** `config_factory.py` provides `BaseConfig`, `DevelopmentConfig`, and `ProductionConfig` classes, with `get_config()` dynamically loading the appropriate settings. `SECRET_KEY` is mandatory in production.
-   **Environment Detection:** `environment_detector.py` automatically detects Replit vs. VPS environments, with manual override via the `ENVIRONMENT` variable.
-   **Containerization:** A multi-stage `Dockerfile` is provided for production deployments, utilizing `python:3.12-slim`, Gunicorn with `GeventWebSocketWorker`, and running as a non-root user. Includes health checks and robust handling of dependencies like `pycurl` and `pymssql`.
-   **Docker Compose:** Complete orchestration setup with `docker-compose.yml` (production) and `docker-compose.override.yml` (development). Includes PostgreSQL 15, Redis 7, persistent volumes, health checks, and automatic environment switching. All secrets managed via `.env` file for security.
-   **Core Files & Structure:**
    -   `runserver.py`: Application entry point, now fully integrated with `config_factory`.
    -   `BTPanel/`: Core application logic.
    -   `data/`: Data and configuration files.
-   **UI/UX:** The project focuses on a graphical web interface for server management. (No specific color schemes or templates mentioned beyond this).
-   **Security:** Enforces `SECRET_KEY` in production, supports SSL/TLS, and includes .dockerignore for sensitive data.

## External Dependencies

-   **Web Server:** Gunicorn (with `GeventWebSocketWorker` for WebSocket support)
-   **Databases:**
    -   SQLite (for development/local)
    -   MySQL (for production)
    -   PostgreSQL (for production)
-   **Database Drivers:** `PyMySQL`, `psycopg2` (implied for PostgreSQL)
-   **Reverse Proxy/Web Server:** Nginx (for production environments on VPS)
-   **Process Management:** systemd (for production environments on VPS)
-   **Containerization:** Docker
## 📊 مراجعة التقدم السابق وملاحظات المدير Architect

### تاريخ المراجعة: 30 سبتمبر 2025 - الساعة 14:30 UTC
**المراجع:** Architect Agent (Opus 4.0)

#### نسبة جودة التنفيذ: **85%**

**✅ نقاط القوة:**
- توثيق مرحلي مترابط بين اقرأني/دليل البدء/خطة التطوير
- تنفيذ دقيق لمهام المرحلة الأولى (كاشف البيئة، مصنع الإعدادات، مدقق المتغيرات)
- حزمة الحاويات (Dockerfile + docker-compose) تغطي مساري الإنتاج/التطوير
- اختبارات داخلية شاملة: 90+ اختبار ناجح
- أمان محكم: جميع الأسرار في .env

**⚠️ نقاط الضعف والتحسينات المطلوبة:**
1. غياب اختبارات تحقق أوتوماتيكية للمهام المكتملة
2. عدم توثيق حالة مهام المرحلة الثانية بنفس مستوى التفصيل
3. nginx و systemd لم يتم البدء فيهما (ضروري للإنتاج)

**📋 التوصيات:**
1. إضافة اختبارات تكامل/وحدة تغطي سيناريو تشغيل الحاوية
2. استكمال المهمة 2.3 (nginx) و 2.4 (systemd) فوراً
3. توثيق نتائج التحقق الفعلية في الخطة

**🎯 الحالة الإجمالية:** 
- المرحلة 1: ✅ 100% مكتملة
- المرحلة 2: ⚙️ 50% مكتملة
- التقدم الإجمالي: **25.7%** من المشروع الكامل

---

## آخر التغييرات - Recent Changes

### 30 سبتمبر 2025 - المهمة 2.3: إعداد Nginx للإنتاج ✅
**المسؤول:** الوكيل رقم 5

**ما تم إنجازه:**
1. ✅ إنشاء `nginx.conf.template` - تهيئة شاملة للإنتاج:
   - Server blocks للـ HTTP (redirect to HTTPS) و HTTPS
   - Reverse proxy للتطبيق على المنفذ 5000
   - دعم SSL/TLS كامل (TLS 1.2+، modern ciphers)
   - OCSP Stapling و SSL session cache
   - دعم WebSocket لـ `/ws/` مع timeouts محسّنة

2. ✅ Security Headers شاملة:
   - Strict-Transport-Security (HSTS - 2 years)
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - Content-Security-Policy
   - X-XSS-Protection
   - Referrer-Policy

3. ✅ تحسينات الأداء:
   - Gzip compression (مستوى 6، أنواع متعددة)
   - Static files caching (1 year، immutable)
   - HTTP/2 support
   - Client settings محسّنة (100MB max body)
   - Keepalive connections

4. ✅ Rate Limiting للحماية:
   - API endpoints: 10 req/sec (burst: 20)
   - Login endpoint: 5 req/min (burst: 5)
   - Connection limiting: 10 concurrent/IP

5. ✅ إنشاء `proxy_params`:
   - رؤوس proxy القياسية
   - Timeout settings محسّنة
   - Buffering configuration

6. ✅ إنشاء `setup_nginx.sh` - سكريبت إعداد تلقائي:
   - تثبيت nginx و certbot تلقائياً
   - الحصول على شهادة SSL من Let's Encrypt
   - استبدال المتغيرات في template
   - إنشاء المجلدات وصفحات الأخطاء
   - اختبار التهيئة وإعادة تحميل nginx
   - إعداد التجديد التلقائي للشهادة (cron)

7. ✅ إنشاء `NGINX_SETUP.md` - توثيق شامل:
   - دليل الإعداد (تلقائي ويدوي)
   - شرح المتغيرات والإعدادات
   - اختبار والتحقق من SSL
   - حل المشاكل الشائعة (troubleshooting)
   - Best practices للأمان والأداء

**الميزات الإضافية:**
- صفحات أخطاء مخصصة (404، 50x) بالعربية
- Health endpoint للـ monitoring
- منع الوصول للملفات الحساسة (.env، .git، etc.)
- دعم ACME challenge لـ Let's Encrypt

**الاستخدام:**
- التلقائي: `sudo ./setup_nginx.sh` (يطلب النطاق والبريد)
- اليدوي: راجع NGINX_SETUP.md للتفاصيل

**الأمان:** A+ rating من SSL Labs (متوقع)

---

### 30 سبتمبر 2025 - المهمة 2.2: Docker Compose للتطوير ✅
**المسؤول:** Replit Agent

**ما تم إنجازه:**
1. ✅ إنشاء `docker-compose.yml` للإنتاج:
   - خدمة app مع Gunicorn + GeventWebSocketWorker
   - خدمة PostgreSQL 15-alpine مع health checks
   - خدمة Redis 7-alpine مع 256MB memory limit
   - Persistent volumes: postgres_data, redis_data, app_data, app_logs
   - Network: aapanel_network (bridge)
   - جميع الإعدادات من ملف .env للأمان

2. ✅ إنشاء `docker-compose.override.yml` للتطوير:
   - استخدام Gunicorn مع --reload للـ hot reload
   - SQLite للتطوير (لا حاجة لـ PostgreSQL)
   - Bind mount للكود (.:/app:cached)
   - Redis خفيف (128MB، بدون persistence)
   - منافذ إضافية للـ debugger (5678)

3. ✅ إنشاء `.env.docker.example`:
   - مرجع شامل لجميع المتغيرات المطلوبة
   - تعليمات واضحة بالعربية والإنجليزية
   - أمثلة للتطوير والإنتاج
   - ملاحظات أمنية مهمة

**التحسينات الأمنية:**
- جميع الأسرار في ملف .env (غير ملتزم في git)
- عدم وجود بيانات اعتماد hardcoded
- استخدام env_file بدلاً من environment inline
- Postgres healthcheck يستخدم متغيرات البيئة

**الاستخدام:**
- التطوير: `docker-compose up` (يستخدم override تلقائياً)
- الإنتاج: `docker-compose -f docker-compose.yml up`

**المراجعة:** Pass من architect - جاهز للإنتاج ✅
