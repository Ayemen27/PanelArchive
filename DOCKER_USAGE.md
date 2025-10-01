# دليل استخدام Docker لتطبيق aaPanel

## المقدمة
هذا الدليل يشرح كيفية بناء وتشغيل تطبيق aaPanel باستخدام Docker.

## المتطلبات الأساسية
- Docker 20.10 أو أحدث
- Docker Compose (اختياري)

## بناء الصورة

### بناء أساسي:
```bash
docker build -t aapanel:latest .
```

### بناء مع tag محدد:
```bash
docker build -t aapanel:v1.0.0 .
```

### فحص حجم الصورة:
```bash
docker images aapanel:latest
```

## متغيرات البيئة

### Development (اختيارية):
- `PORT`: المنفذ (default: 5000)
- `ENVIRONMENT`: development (default)

### Production (مطلوبة):
- `ENVIRONMENT`: production
- `SECRET_KEY`: مفتاح سري قوي (مطلوب للأمان ونظام النسخ الاحتياطي SHA-256+HMAC)
- `DATABASE_URL`: رابط قاعدة البيانات
- `SESSION_SECRET_KEY`: مفتاح الجلسات
- `PORT`: المنفذ (default: 5000)

⚠️ **ملاحظة مهمة عن SECRET_KEY:**
- يُستخدم في التحقق من سلامة النسخ الاحتياطية عبر HMAC-SHA256
- تغييره سيُبطل جميع النسخ الاحتياطية الموجودة (format v2)
- النسخ القديمة بنظام MD5 (v1) مدعومة للاستعادة مع العلم `--skip-md5`

## إعداد Volumes (مهم)

⚠️ **الأذونات المطلوبة:**
الحاوية تعمل كمستخدم غير root (aapanel:1000)، لذلك يجب إعداد الأذونات:

```bash
# إنشاء المجلدات على الـ host
mkdir -p data logs

# تعيين الأذونات
sudo chown -R 1000:1000 data logs
chmod -R 755 data logs
```

بدون هذه الخطوة، قد تفشل الحاوية في الكتابة.

## تشغيل الحاوية

### تشغيل بسيط:
```bash
docker run -d -p 5000:5000 --name aapanel aapanel:latest
```

### تشغيل مع volumes للبيانات:
```bash
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name aapanel \
  aapanel:latest
```

### تشغيل مع متغيرات بيئة (Development):
```bash
docker run -d \
  -p 5000:5000 \
  -e PORT=5000 \
  -e ENVIRONMENT=development \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name aapanel \
  aapanel:latest
```

**ملاحظة**: في بيئة Development، يتم توليد SECRET_KEY تلقائياً.

### تشغيل مع متغيرات بيئة (Production):
```bash
docker run -d \
  -p 5000:5000 \
  -e ENVIRONMENT=production \
  -e SECRET_KEY="your-secret-key-here" \
  -e DATABASE_URL="postgresql://user:pass@host:5432/dbname" \
  -e SESSION_SECRET_KEY="your-session-key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name aapanel \
  aapanel:latest
```

⚠️ **تنبيه مهم للإنتاج:**
- يجب توفير `SECRET_KEY` و `DATABASE_URL` و `SESSION_SECRET_KEY`
- عدم توفيرها سيؤدي لفشل التطبيق عند البدء
- لا تُشغّل ENVIRONMENT=production بدون المتغيرات المطلوبة

## فحص الصحة

### فحص حالة الحاوية:
```bash
docker ps | grep aapanel
docker logs aapanel
```

### فحص endpoint:
```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

### اختبار WebSocket:
```bash
# يمكن استخدام wscat أو أي أداة WebSocket
# المسارات المتاحة: /webssh, /sock_shell
wscat -c ws://localhost:5000/webssh
# أو
wscat -c ws://localhost:5000/sock_shell
```

## الأوامر المفيدة

### إيقاف وإزالة:
```bash
docker stop aapanel
docker rm aapanel
```

### الدخول إلى الحاوية:
```bash
docker exec -it aapanel /bin/bash
```

### عرض السجلات:
```bash
docker logs -f aapanel
```

## استكشاف الأخطاء

### الحاوية لا تبدأ:
1. فحص السجلات: `docker logs aapanel`
2. التحقق من المنفذ: `lsof -i :5000`
3. التحقق من الأذونات على volumes

### مشاكل WebSocket:
- التأكد من استخدام GeventWebSocketWorker
- التحقق من headers في الطلب
- فحص السجلات: `docker logs aapanel | grep -i websocket`

### مشاكل النسخ الاحتياطية:
- **فشل HMAC/Checksum عند الاستعادة:**
  - تأكد من أن SECRET_KEY في .env مطابق للمفتاح المستخدم عند إنشاء النسخة
  - للنسخ القديمة (MD5): استخدم `--skip-md5` للاستعادة
  ```bash
  python backups/backup_manager.py --restore backup.tar.gz --skip-md5
  ```
- **رفض النسخة الاحتياطية القديمة:**
  - النسخ بنظام v1 (MD5) تحتاج العلم `--skip-md5` للاستعادة
  - النسخ الجديدة (v2) تستخدم SHA-256 + HMAC تلقائياً

> **📚 للمزيد:** راجع [DEPLOYMENT_SECRETS.md](./DEPLOYMENT_SECRETS.md) لتفاصيل كاملة عن SECRET_KEY وتأثيره على النسخ الاحتياطية

## الأمان

### Best Practices:
1. عدم تشغيل كـ root (تم تطبيقه)
2. استخدام secrets management للبيانات الحساسة
3. تحديث الصورة بانتظام
4. فحص الثغرات: `docker scan aapanel:latest`

### Production Deployment:
- ⚠️ لا تُشغّل مباشرة على 0.0.0.0:5000 في الإنتاج
- استخدم Nginx/Caddy كـ reverse proxy
- فعّل SSL/TLS
- استخدم Docker secrets أو Vault للمتغيرات الحساسة

## المواصفات التقنية

- **Base Image**: python:3.12-slim
- **Architecture**: Multi-stage build
- **Web Server**: Gunicorn + GeventWebSocketWorker
- **Port**: 5000
- **User**: aapanel (UID/GID: 1000)
- **Health Check**: /health (fallback: /)
