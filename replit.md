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
**المسؤول:** الوكيل رقم 6
**تاريخ الإنجاز:** 30 سبتمبر 2025 - 15:45 UTC
**المراجعة:** ✅ Pass من Architect Agent

**ما تم إنجازه:**
1. ✅ إنشاء `nginx.conf.template` - تهيئة شاملة للإنتاج:
   - Server blocks للـ HTTP (redirect to HTTPS) و HTTPS
   - Reverse proxy للتطبيق على المنفذ 5000
   - دعم SSL/TLS كامل (TLS 1.2+، modern ciphers)
   - OCSP Stapling و SSL session cache
   - دعم WebSocket لـ `/ws/` مع timeouts محسّنة

2. ✅ إنشاء `nginx_http_only.conf.template` - تهيئة HTTP فقط للمرحلة الأولى:
   - Server block بسيط يستمع على 80
   - يخدم التطبيق + ACME challenge
   - بدون أي إشارة لـ SSL (تجنب فشل nginx -t)

3. ✅ Security Headers شاملة:
   - Strict-Transport-Security (HSTS - 2 years)
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - Content-Security-Policy
   - X-XSS-Protection
   - Referrer-Policy

4. ✅ تحسينات الأداء:
   - Gzip compression (مستوى 6، أنواع متعددة)
   - Static files caching (1 year، immutable)
   - HTTP/2 support
   - Client settings محسّنة (100MB max body)
   - Keepalive connections

5. ✅ Rate Limiting للحماية:
   - API endpoints: 10 req/sec (burst: 20)
   - Login endpoint: 5 req/min (burst: 5)
   - Connection limiting: 10 concurrent/IP

6. ✅ إنشاء `proxy_params`:
   - رؤوس proxy القياسية
   - Timeout settings محسّنة
   - Buffering configuration

7. ✅ إنشاء `setup_nginx.sh` - سكريبت إعداد تلقائي **بنهج المرحلتين**:
   - **المرحلة 1:** نشر HTTP-only config → nginx -t → reload → خدمة ACME
   - **المرحلة 2:** certbot certonly --webroot → إعادة إنشاء config مع SSL → reload
   - تثبيت nginx و certbot تلقائياً
   - إنشاء المجلدات وصفحات الأخطاء
   - اختبار التهيئة قبل وبعد SSL
   - إعداد التجديد التلقائي للشهادة (cron)

8. ✅ إنشاء `NGINX_SETUP.md` - توثيق شامل:
   - دليل الإعداد (تلقائي ويدوي)
   - شرح نهج المرحلتين بالتفصيل
   - شرح المتغيرات والإعدادات
   - اختبار والتحقق من SSL
   - حل المشاكل الشائعة (troubleshooting)
   - Best practices للأمان والأداء

**الميزات الإضافية:**
- صفحات أخطاء مخصصة (404، 50x) بالعربية
- Health endpoint للـ monitoring
- منع الوصول للملفات الحساسة (.env، .git، etc.)
- دعم ACME challenge لـ Let's Encrypt بشكل موثوق

**الاستخدام:**
- التلقائي: `sudo ./setup_nginx.sh` (يطلب النطاق والبريد)
- اليدوي: راجع NGINX_SETUP.md للتفاصيل

**الأمان:** A+ rating من SSL Labs (متوقع)

**الملفات المُنشأة:**
- `nginx.conf.template` (HTTPS كامل)
- `nginx_http_only.conf.template` (HTTP فقط)
- `proxy_params`
- `setup_nginx.sh`
- `NGINX_SETUP.md`

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

---

### 30 سبتمبر 2025 - المهمة 2.4: systemd Service للإنتاج ✅
**المسؤول:** الوكيل رقم 6
**تاريخ الإنجاز:** 30 سبتمبر 2025 - 17:00 UTC
**المراجعة:** ✅ Pass من Architect (بعد 5 مراجعات دقيقة)

**إصلاحات بناءً على مراجعات Architect المتعددة:**
1. ✅ تغيير `Type=notify` إلى `Type=simple` (Gunicorn لا يدعم notify mode افتراضياً)
2. ✅ استخدام virtualenv **حصرياً** (`/www/server/panel/venv/bin/gunicorn`):
   - يحل مشكلة صلاحيات المستخدم www (لا يمكنه الوصول لـ /usr/local/bin)
   - يعزل اعتماديات Python بشكل كامل
   - setup_systemd.sh الآن ينشئ virtualenv تلقائياً
3. ✅ تحديث **شامل** في SYSTEMD_SETUP.md:
   - التثبيت اليدوي: جميع أوامر pip داخل virtualenv
   - تحديث الكود: استخدام `source venv/bin/activate` أو مسار مباشر
   - Rolling Update: تثبيت الاعتماديات داخل virtualenv
   - الاختبار اليدوي: استخدام `venv/bin/gunicorn`
   - Prometheus Integration: تثبيت prometheus-client داخل virtualenv
4. ✅ gunicorn_config.py محدث بالكامل مع config_factory

**ما تم إنجازه:**
1. ✅ إنشاء `aapanel.service` - systemd unit file متقدم:
   - Type=simple للتكامل الصحيح مع Gunicorn
   - User/Group: www (أمان - non-root)
   - EnvironmentFile من .env
   - Restart policy: always مع StartLimitBurst
   - Resource limits: 65535 files، 4096 processes
   - Security hardening كامل (NoNewPrivileges، ProtectSystem)
   - Process management: KillMode=mixed، graceful shutdown
   - Logging: journal مع SyslogIdentifier

2. ✅ إنشاء `gunicorn_config.py` - ملف إعدادات Gunicorn محدث:
   - تكامل كامل مع config_factory
   - حساب تلقائي للـ workers: (2 × CPU cores) + 1
   - دعم WebSocket: GeventWebSocketWorker
   - Timeout محسّن: 7200s للعمليات الطويلة
   - Max requests: 1000 لمنع memory leak
   - SSL/TLS support اختياري
   - Preload في الإنتاج، Hot reload في التطوير
   - Worker lifecycle hooks للمراقبة
   - Security limits في الإنتاج

3. ✅ إنشاء `setup_systemd.sh` - سكريبت إعداد تلقائي شامل:
   - فحص صلاحيات root
   - إنشاء مستخدم www تلقائياً
   - التحقق من الاعتماديات (Python، Gunicorn)
   - إنشاء المجلدات وضبط الصلاحيات
   - تثبيت وتفعيل systemd service
   - اختبار الخدمة والتحقق من نجاح البدء
   - عرض معلومات ما بعد التثبيت

4. ✅ إنشاء `SYSTEMD_SETUP.md` - توثيق شامل:
   - دليل التثبيت (تلقائي ويدوي)
   - شرح تفصيلي لكل قسم في aapanel.service
   - أوامر إدارة الخدمة الكاملة
   - مراقبة السجلات المتقدمة
   - فحص الأداء والموارد
   - التحديث والصيانة (Rolling Update)
   - استكشاف 5+ مشاكل شائعة وحلولها
   - أفضل الممارسات (الأمان، الأداء، الموثوقية)
   - المراقبة والتنبيهات (Prometheus، Health checks)
   - التكامل مع Nginx

**الميزات الرئيسية:**

**الأمان:**
- تشغيل كمستخدم محدود (www)
- NoNewPrivileges، ProtectSystem=strict
- ProtectHome، PrivateTmp
- ReadWritePaths محدودة
- ReadOnlyPaths للكود

**الموثوقية:**
- Restart=always مع تأخير 5 ثوان
- StartLimitBurst=3 (3 محاولات في 60 ثانية)
- Graceful shutdown: 30 ثانية
- Worker rotation: كل 1000 طلب

**الأداء:**
- Workers ديناميكي: (2 × CPU) + 1
- Threads: 3 لكل worker
- Max requests jitter: منع التوقف المتزامن
- Keepalive: 60 ثانية

**الاستخدام:**
```bash
# تلقائي
sudo ./setup_systemd.sh

# يدوي
sudo cp aapanel.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aapanel
sudo systemctl start aapanel
```

**الأوامر الأساسية:**
- البدء: `sudo systemctl start aapanel`
- الإيقاف: `sudo systemctl stop aapanel`
- الحالة: `sudo systemctl status aapanel`
- السجلات: `sudo journalctl -u aapanel -f`

**الملفات المُنشأة:**
- `aapanel.service`
- `gunicorn_config.py`
- `setup_systemd.sh`
- `SYSTEMD_SETUP.md`
