# aaPanel - لوحة تحكم الخادم

## Overview
aaPanel is a powerful server management control panel built with Python/Flask. It provides a graphical web interface for easy server administration, aiming to be a robust, multi-environment solution for both development (Replit) and production (VPS). Key capabilities include multi-database support (SQLite, MySQL, PostgreSQL), advanced security features, and a scalable architecture. The project's vision is to simplify server management for a wide range of users, from developers to system administrators, leveraging its flexibility and open-source nature to capture a significant market share.

## User Preferences
### متطلبات التوثيق
- يجب تحديث حالة كل مهمة فور إنجازها
- توثيق واضح لما تم إنجازه وما تبقى
- تمكين الفريق من معرفة نقطة التوقف ونقطة الاستكمال
- 🔴 **إلزامي:** مراجعة `تقارير_مراجعة_ارشكتر.md` قبل البدء بأي مهمة

### التواصل
- **اللغة المفضلة**: العربية فقط في جميع الردود
- التوثيق يجب أن يكون واضح ومفصل

### 🔴 ملف تقارير Architect (إلزامي)
**جميع الوكلاء يجب أن:**
1. ✅ يقرأوا `تقارير_مراجعة_ارشكتر.md` قبل البدء
2. ✅ يحدثوا الملف عند حل أي مشكلة
3. ✅ يضيفوا مشاكل جديدة يكتشفها Architect
4. ✅ يوثقوا طريقة الحل والسبب

**الملف يحتوي على:**
- 10 مشاكل مكتشفة من مراجعة Architect الشاملة
- 1 محلولة (10%)، 9 تحتاج حل (90%)
- خطة عمل مفصلة لحل المشاكل المتبقية

## System Architecture
The project uses Python 3.12 and the Flask framework, served with Gunicorn in production. Core architectural decisions include a Factory Pattern for configuration management, an environment detector for runtime identification (Replit or VPS), and a validator for configuration.

**Key Architectural Features:**
-   **Multi-Environment Support:** Distinct configurations for Development (Replit, SQLite) and Production (VPS, external MySQL/PostgreSQL, Nginx, systemd).
-   **Configuration Management:** Dynamic settings loading via `BaseConfig`, `DevelopmentConfig`, and `ProductionConfig`.
-   **Environment Detection:** Automatic detection of Replit vs. VPS environments.
-   **Containerization:** Multi-stage `Dockerfile` with Gunicorn and `GeventWebSocketWorker`. Docker Compose for orchestration with PostgreSQL and Redis. Blue-Green deployment strategy for zero-downtime deployments.
-   **UI/UX:** Graphical web interface for server management.
-   **Security:** Enforces `SECRET_KEY`, supports SSL/TLS, and uses `.dockerignore`.
-   **Nginx Configuration:** Comprehensive Nginx setup for HTTPS, WebSocket proxying, security headers, rate limiting, and performance optimizations.
-   **systemd Integration:** Advanced `systemd` unit file (`aapanel.service`) for managing Gunicorn in production as a non-root user, with robust restart policies and security hardening.
-   **CI/CD Pipeline:** GitHub Actions for automated testing (pytest, coverage, security scanning), linting/formatting, multi-platform Docker image builds, and automated Blue-Green deployments to VPS, including rollback and health checks.
-   **Database Migrations:** Alembic and Flask-Migrate for managing database schema changes with validation.
-   **Database Backup Strategy:** Comprehensive backup system for SQLite, PostgreSQL, and MySQL, featuring automatic scheduling, integrity verification, and security measures.
-   **Monitoring & Alerting:** Health & Readiness Endpoints (`/health/live`, `/health/ready`, `/health/metrics`) for probes and Prometheus metrics. Integrated with Prometheus and Grafana for visualization. Alerting system via Prometheus Alertmanager with 11 alert rules, notifications via Slack and Email.
-   **Centralized Logging:** Grafana Loki and Promtail for centralized log aggregation. Loki runs as an internal-only service. Promtail collects logs from Docker containers, application, and system logs with metadata enrichment. Features structured JSON logging, 7-day retention, and a comprehensive Grafana dashboard. Log rotation is configured.
-   **SSL/TLS Security:** Comprehensive SSL/TLS configuration achieving A+ rating, featuring TLS 1.2/1.3 only, modern cipher suites, OCSP Stapling, and security headers (HSTS, X-Frame-Options, X-Content-Type-Options, CSP). Let's Encrypt integration with automatic renewal. Includes validation tools (`ssl_check.sh`, `test_ssl_renewal.sh`).

## External Dependencies
-   **Web Server:** Gunicorn
-   **Databases:** SQLite, MySQL, PostgreSQL
-   **Database Drivers:** `PyMySQL`, `psycopg2`
-   **Reverse Proxy/Web Server:** Nginx
-   **Process Management:** systemd
-   **Containerization:** Docker
-   **Caching/Message Broker:** Redis
-   **SSL Certificate Management:** Certbot (Let's Encrypt), OpenSSL
-   **CI/CD Platform:** GitHub Actions
-   **Container Registry:** GitHub Container Registry (ghcr.io)
-   **Security Scanners:** Bandit, Safety, Anchore Grype
-   **Monitoring & Alerting:** Prometheus, Grafana, Alertmanager
-   **Notification Channels:** Slack, Email (SMTP)
-   **Centralized Logging:** Grafana Loki, Promtail
-   **Database Migration:** Alembic, Flask-Migrate

## Recent Changes

### October 2, 2025 - Agent #37
**Task 9.1: Database Connection Pool Integration** ✅ Completed
- **Achievement:** Successfully integrated DatabaseConnectionPool with BTPanel and health endpoints
- **Implementation:**
  - ✅ BTPanel/__init__.py (lines 6681-6700): Imports and initializes db_pool with config_factory
  - ✅ health_endpoints.py: Updated to use db_pool from app.config for health checks
  - ✅ Error handling: Safe fallback to None if pool initialization fails
  - ✅ Integration: db_pool passed to register_health_routes and stored in app.config['DB_POOL']
- **Architect Review:** Pass ✅ - "Database connection pool integration into BTPanel is correctly wired and functioning"
- **Impact:**
  - Connection pooling now active for better performance
  - Health checks can monitor database pool statistics
  - Retry logic available through pool
  - Better resource management under load
- **Files Modified:** BTPanel/__init__.py, health_endpoints.py
- **Status:** Production-ready - Critical issue #2 resolved (20% completion of Phase 9)

### October 2, 2025 - Agent #35
**Phase 9 Added: Fixing Discovered Issues** 🚀 In Progress
- **Major Update:** Added comprehensive Phase 9 to fix all issues discovered by Architect review
- **10 Tasks Created:** Prioritized by severity (Critical → High → Medium)
- **Implementation:**
  - 🔥 Critical tasks (2): db_pool integration, backup_manager scheduling
  - ⚠️ High priority tasks (4): CI/CD, Monitoring, Backup tests, VPS security
  - 💡 Medium priority tasks (4): SECRET_KEY, health endpoints tests, Docker builds, Documentation
- **Time Estimate:** 9-10 hours total
- **Reference:** `تقارير_مراجعة_ارشكتر.md` for complete details
- **Updated Files:** خطة_التطوير.md, ملخص_الخطة.md, قائمة_التحقق.md
- **Status:** Ready for implementation - prioritized roadmap created

### October 2, 2025 - Agent #35
**Critical Import Fix** ✅ Completed
- **Issue Found:** Direct import `from BTPanel import app` was failing with `ModuleNotFoundError: No module named 'public'`
- **Root Cause:** `class` directory was not in `sys.path` when BTPanel was imported directly (only worked via runserver.py)
- **Solution Applied:**
  - ✅ Added sys.path setup in `BTPanel/__init__.py` before importing `hook_import`
  - ✅ Both `class` and `class_v2` directories now added to sys.path automatically
  - ✅ Application now works in all import scenarios
- **Testing:** ✅ Verified successful import and application startup on port 39417
- **Files Modified:** `BTPanel/__init__.py` (lines 9-20)
- **Status:** Production-ready - import issue resolved

### October 2, 2025 - Agent #34
**Phase 8: Replit Full Compatibility** ✅ Completed
- **Major Achievement:** Application now runs successfully in both Replit and VPS environments
- **Smart Solution:** Modified `get_panel_path()` once instead of fixing 67 files individually
- **Implementation:**
  - ✅ Task 8.1: Fixed hardcoded paths via dynamic `get_panel_path()` in `class/public/common.py`
  - ✅ Task 8.2: Created `.env` file from `.env.example` for development
  - ✅ Task 8.3: Fixed log paths in `BTPanel/__init__.py` to use dynamic `os.getcwd()/logs/app.log`
  - ✅ Task 8.4: Complete Replit testing - application runs on port 39417 without errors
  - ✅ Task 8.5: Updated documentation with changes
- **Technical Details:**
  - Removed `os.chdir()` from `class/nginx.py` and `class/apache.py` (eliminated side effects)
  - `get_panel_path()` now auto-detects environment and returns correct path
  - Logs directory created automatically: `/home/runner/workspace/logs/`
  - Both environments use same codebase with zero code duplication
- **Architect Review:** Pass ✅ - No security issues, VPS compatibility maintained
- **Status:** Production-ready - full dual-environment support achieved

### October 2, 2025 - Agent #33
**Phase 8 Planning**
- Identified compatibility issue with Replit
- Root cause analysis: hardcoded `/www/server/panel` paths
- Created implementation plan for dynamic path handling

### October 2, 2025 - Agent #32
**Task 7.3: Developer Documentation** ✅ Completed
- Created `CONTRIBUTING.md` - Comprehensive contribution guide with coding standards, Git workflow, testing requirements, and PR process
- Created `DEVELOPER_GUIDE.md` - Complete developer onboarding guide with quick start, project structure, development setup, and common tasks
- **Architect Review:** Pass ✅ - Both guides accurately reflect the repository's architecture and provide clear bilingual guidance
- **Files:** CONTRIBUTING.md (comprehensive), DEVELOPER_GUIDE.md (complete)
- **Status:** Production-ready - guides ready for team distribution and linking from README

### October 1, 2025
**Major Updates:**
- **Security Hardening (6.4):** Complete system hardening with setup_security_hardening.sh, security_check.sh, and comprehensive SECURITY_HARDENING_GUIDE.md
- **Firewall (6.2):** IPv6 bug fix in setup_firewall.sh - eliminates SSH lockout risk
- **Fail2Ban (6.3):** Critical IP extraction fix in aapanel filter (multi-IP scenarios)
- **Centralized Logging (5.4):** Loki + Promtail integration with structured JSON logging and 7-day retention
- **Alerting (5.3):** 11 alert rules with Slack/Email notifications via Alertmanager
- **Monitoring (5.2):** Prometheus + Grafana setup with auto-provisioned dashboards (after 4 architect iterations)
- **Health Endpoints (5.1):** /health/live, /health/ready, /health/metrics with system monitoring
- **Connection Pool (4.3):** db_pool.py with retry logic and pool statistics
- **Backup System (4.2):** SHA-256 + HMAC security upgrade with backward compatibility for MD5 backups
- **Database Migrations (4.1):** Alembic integration with migration_validator.py (13 tests, 100% pass)

### September 30, 2025
**Infrastructure & CI/CD Completed:**
- **Blue-Green Deployment (3.4):** Zero-downtime deployment with automatic rollback
- **VPS Deployment (3.3):** Automated deployment workflow with health checks
- **Docker Build (3.2):** Multi-platform builds with SBOM and vulnerability scanning
- **Testing Pipeline (3.1):** 96 pytest tests, linting (Flake8, Black, isort), security scanning
- **systemd (2.4):** Production-ready service with virtualenv and security hardening
- **Nginx (2.3):** A+ SSL rating configuration with Let's Encrypt integration
- **Docker Compose (2.2):** Production and development environments with PostgreSQL + Redis
- **Docker (2.1):** Multi-stage Dockerfile with Gunicorn + GeventWebSocketWorker
- **Infrastructure (1.1-1.4):** environment_detector, config_factory, .env validation, runserver.py integration