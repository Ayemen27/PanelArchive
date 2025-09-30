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