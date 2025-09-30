# ==============================================================================
# Dockerfile لتطبيق aaPanel
# Multi-stage Build لتقليل حجم الصورة النهائية
# ==============================================================================

# ==============================================================================
# المرحلة الأولى: Builder Stage
# تُستخدم لتثبيت جميع Dependencies وبناء الحزم
# ==============================================================================
FROM python:3.12-slim AS builder

# تعيين متغيرات البيئة لتحسين الأداء
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# تحديث النظام وتثبيت أدوات البناء والمكتبات المطلوبة
RUN apt-get update && apt-get install -y --no-install-recommends \
    # أدوات البناء الأساسية
    gcc \
    g++ \
    make \
    python3-dev \
    # مكتبات قواعد البيانات
    libpq-dev \
    default-libmysqlclient-dev \
    freetds-dev \
    # أدوات النظام المساعدة
    curl \
    wget \
    # مكتبات إضافية مطلوبة لبعض الحزم
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libcurl4-openssl-dev \
    # تنظيف الملفات المؤقتة لتقليل الحجم
    && rm -rf /var/lib/apt/lists/*

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملف requirements.txt أولاً للاستفادة من Docker cache
# إذا لم تتغير المتطلبات، لن يُعاد تثبيتها
COPY requirements.txt .

# ترقية pip وتثبيت setuptools و wheel
RUN pip install --upgrade pip setuptools wheel

# تثبيت جميع المكتبات المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# المرحلة الثانية: Runtime Stage
# الصورة النهائية الخفيفة التي ستعمل في الإنتاج
# ==============================================================================
FROM python:3.12-slim AS runtime

# تعيين متغيرات البيئة للإنتاج
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    ENVIRONMENT=production

# تثبيت المكتبات اللازمة فقط للتشغيل (runtime dependencies)
# نستثني أدوات البناء لتقليل الحجم
RUN apt-get update && apt-get install -y --no-install-recommends \
    # مكتبات قواعد البيانات (runtime فقط)
    libpq5 \
    libsybdb5 \
    freetds-common \
    # أدوات النظام الأساسية
    curl \
    wget \
    # مكتبات runtime إضافية
    libffi8 \
    libssl3 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    zlib1g \
    libcurl4 \
    # تنظيف الملفات المؤقتة
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير root للأمان
# استخدام UID/GID محددين للتوافق
RUN groupadd -r -g 1000 aapanel && \
    useradd -r -u 1000 -g aapanel -m -d /home/aapanel -s /bin/bash aapanel

# تعيين مجلد العمل
WORKDIR /app

# نسخ المكتبات المثبتة من مرحلة البناء
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# نسخ ملفات التطبيق (مع مراعاة .dockerignore)
COPY --chown=aapanel:aapanel . .

# إنشاء المجلدات الضرورية وتعيين الأذونات
RUN mkdir -p /app/data/db \
    /app/data/session \
    /app/data/sess_files \
    /app/logs \
    /app/logs/request \
    && chown -R aapanel:aapanel /app \
    && chmod -R 755 /app

# التبديل إلى المستخدم غير root
USER aapanel

# كشف المنفذ 5000
EXPOSE 5000

# فحص صحة التطبيق
# يتحقق من أن التطبيق يستجيب على المنفذ 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || curl -f http://localhost:5000/ || exit 1

# نقطة الدخول: تشغيل التطبيق باستخدام gunicorn للإنتاج
# يستخدم GeventWebSocketWorker لدعم WebSocket والأداء العالي
CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "2", "-b", "0.0.0.0:5000", "BTPanel:app"]
