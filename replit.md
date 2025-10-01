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
-   **Configuration Management:** `config_factory.py` provides `BaseConfig`, `DevelopmentConfig`, and `ProductionConfig` classes for dynamic settings loading.
-   **Environment Detection:** `environment_detector.py` automatically detects Replit vs. VPS environments.
-   **Containerization:** A multi-stage `Dockerfile` is provided, utilizing Gunicorn with `GeventWebSocketWorker`. Docker Compose is used for orchestration with PostgreSQL 15 and Redis 7 services. Blue-Green deployment strategy is implemented using `docker-compose.shared.yml`, `docker-compose.blue.yml`, and `docker-compose.green.yml` for zero-downtime deployments.
-   **UI/UX:** Focuses on a graphical web interface for server management.
-   **Security:** Enforces `SECRET_KEY` in production, supports SSL/TLS, and uses `.dockerignore` for sensitive data.
-   **Nginx Configuration:** Comprehensive Nginx setup for production, supporting HTTPS, WebSocket proxying, security headers, rate limiting, and performance optimizations.
-   **systemd Integration:** Advanced `systemd` unit file (`aapanel.service`) for managing Gunicorn in production, running as a non-root user (`www`), with robust restart policies, resource limits, and security hardening.
-   **CI/CD Pipeline:** Implemented via GitHub Actions for automated testing (pytest, coverage, security scanning with Bandit and Safety), linting/formatting (Flake8, Black, isort), multi-platform Docker image builds (GitHub Container Registry, SBOM generation, vulnerability scanning with Grype), and automated Blue-Green deployments to VPS. Includes a robust rollback mechanism and comprehensive health checks.
-   **Database Migrations:** Utilizes Alembic and Flask-Migrate for managing database schema changes, including a robust validation system for migration files and content.
-   **Database Backup Strategy:** Comprehensive backup system with support for SQLite, PostgreSQL, and MySQL, featuring automatic scheduling, SHA-256 + HMAC for integrity verification, and security measures against path traversal and unsafe extraction.
-   **Monitoring & Alerting:** Health & Readiness Endpoints (`/health/live`, `/health/ready`, `/health/metrics`) are implemented for liveness/readiness probes and Prometheus metrics, integrated with Prometheus and Grafana for visualization. Comprehensive alerting system configured with Prometheus Alertmanager, featuring 11 alert rules for resource monitoring (CPU, Memory, Disk), service availability (Application, Database, Redis), and performance thresholds. Notifications delivered via Slack (rich formatting) and Email (SMTP) with intelligent routing, grouping, and inhibition rules to prevent alert fatigue.
-   **Centralized Logging:** Grafana Loki and Promtail are deployed for centralized log aggregation and analysis. Loki runs as an internal-only service (no external port binding) for security, accessible via Grafana. Promtail collects logs from Docker containers, application logs, and system logs with container metadata enrichment via Docker socket (read-only mount). Features structured JSON logging in the application, 7-day retention with automatic compaction, and a comprehensive Grafana dashboard with 7 panels for log visualization, filtering by service/level/container, and LogQL search capabilities. Log rotation is configured (10MB max size, 5 backups) for application logs.

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
-   **Monitoring & Alerting:** Prometheus, Grafana, Alertmanager
-   **Notification Channels:** Slack, Email (SMTP)
-   **Centralized Logging:** Grafana Loki, Promtail
-   **Database Migration:** Alembic, Flask-Migrate