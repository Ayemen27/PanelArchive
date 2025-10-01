# 📝 دليل إعداد نظام السجلات المركزي - Grafana Loki + Promtail

## نظرة عامة

تم إعداد نظام **Centralized Logging** شامل لـ aaPanel باستخدام:

- **Grafana Loki** - نظام تخزين واستعلام السجلات
- **Promtail** - عميل جمع السجلات
- **Grafana** - واجهة عرض وتحليل السجلات

### ✨ المميزات

- ✅ **سجلات مركزية** - جميع السجلات في مكان واحد
- ✅ **بحث فوري** - استعلامات قوية باستخدام LogQL
- ✅ **JSON Structured Logs** - سجلات منظمة قابلة للتحليل
- ✅ **Log Rotation** - إدارة تلقائية لحجم السجلات
- ✅ **Retention Policy** - حفظ السجلات لمدة 7 أيام
- ✅ **Dashboard جاهز** - visualizations جاهزة للاستخدام
- ✅ **Blue-Green Compatible** - يدعم نشر Blue-Green

---

## 📋 جدول المحتويات

1. [البنية التقنية](#البنية-التقنية)
2. [الإعداد السريع](#الإعداد-السريع)
3. [إعداد البيئة](#إعداد-البيئة)
4. [الوصول للخدمات](#الوصول-للخدمات)
5. [البحث في السجلات](#البحث-في-السجلات)
6. [استكشاف الأخطاء](#استكشاف-الأخطاء)
7. [Best Practices](#best-practices)
8. [الصيانة](#الصيانة)

---

## 🏗️ البنية التقنية

### تدفق السجلات

```
┌─────────────────────────────────────────────────┐
│              aaPanel Application                 │
│         (Structured JSON Logging)                │
│         ↓                                        │
│    /app/logs/app.log                            │
└─────────────────────────────────────────────────┘
                 │
                 │ File-based logs
                 ↓
┌─────────────────────────────────────────────────┐
│              Docker Containers                   │
│       /var/lib/docker/containers/               │
│         (JSON formatted logs)                    │
└─────────────────────────────────────────────────┘
                 │
                 │ Collects & parses
                 ↓
┌─────────────────────────────────────────────────┐
│                 Promtail                         │
│            (Port 9080)                           │
│         - Reads log files                        │
│         - Parses JSON                            │
│         - Adds labels                            │
│         - Sends to Loki                          │
└─────────────────────────────────────────────────┘
                 │
                 │ HTTP Push
                 ↓
┌─────────────────────────────────────────────────┐
│                   Loki                           │
│            (Port 3100)                           │
│         - Stores logs                            │
│         - Indexes by labels                      │
│         - Retention: 7 days                      │
│         - Compaction enabled                     │
└─────────────────────────────────────────────────┘
                 │
                 │ LogQL queries
                 ↓
┌─────────────────────────────────────────────────┐
│                 Grafana                          │
│            (Port 3000)                           │
│         - Visualizes logs                        │
│         - Dashboard: "aaPanel Logs"              │
│         - Search & filter                        │
└─────────────────────────────────────────────────┘
```

### الملفات المستخدمة

| الملف | الوصف |
|-------|--------|
| `loki-config.yml` | تكوين Loki الرئيسي |
| `promtail-config.yml` | تكوين Promtail لجمع السجلات |
| `grafana-loki-datasource.yml` | مصدر بيانات Loki في Grafana |
| `grafana-loki-dashboard.json` | Dashboard السجلات في Grafana |
| `.env.logging.example` | متغيرات البيئة للسجلات |
| `BTPanel/__init__.py` | Structured logging في التطبيق |
| `docker-compose.yml` | تكوين Docker للإنتاج |
| `docker-compose.shared.yml` | تكوين Blue-Green |

---

## 🚀 الإعداد السريع

### 1. البيئة الأساسية (Development/Production)

```bash
# 1. انسخ ملف البيئة
cp .env.logging.example .env
# أو أضف محتوياته إلى .env الموجود

# 2. تحقق من وجود جميع الملفات
ls -la loki-config.yml promtail-config.yml grafana-loki-*.yml

# 3. شغّل جميع الخدمات (بما فيها Loki و Promtail)
docker-compose up -d

# 4. تحقق من حالة الخدمات
docker-compose ps

# يجب أن ترى:
# - aapanel_loki (healthy)
# - aapanel_promtail (running)
# - aapanel_grafana (healthy)

# 5. افتح Grafana
# URL: http://localhost:3000
# تسجيل الدخول: credentials من .env (GRAFANA_ADMIN_USER/PASSWORD)

# 6. انتقل إلى Dashboard "aaPanel Logs - Loki Dashboard"
```

### 2. بيئة Blue-Green Deployment

```bash
# 1. شغّل الخدمات المشتركة (بما فيها Loki)
docker-compose -f docker-compose.shared.yml up -d

# 2. تحقق من حالة الخدمات المشتركة
docker-compose -f docker-compose.shared.yml ps

# يجب أن ترى:
# - aapanel_loki_shared (healthy)
# - aapanel_promtail_shared (running)
# - aapanel_grafana_shared (healthy)

# 3. شغّل البيئة الزرقاء أو الخضراء
docker-compose -f docker-compose.blue.yml up -d
# أو
docker-compose -f docker-compose.green.yml up -d

# 4. Loki و Grafana متاحان على نفس المنافذ
# Loki: http://localhost:3100
# Grafana: http://localhost:3000
```

---

## 🔑 الوصول للخدمات

### Loki API

**⚠️ ملاحظة أمنية مهمة:**  
Loki **لا يوجد له port binding خارجي** لأسباب أمنية. يمكن الوصول إليه **فقط داخل Docker network** عبر `http://loki:3100`.

- **Internal URL**: `http://loki:3100` (داخل Docker network فقط)
- **Status**: `http://loki:3100/ready` (internal)
- **Metrics**: `http://loki:3100/metrics` (internal)
- **Config**: `http://loki:3100/config` (internal)

**للوصول إلى Loki API من خارج Docker:**

```bash
# Option 1: استخدم Grafana UI (الطريقة الموصى بها)
# افتح http://localhost:3000 → Explore → Loki datasource

# Option 2: استخدم docker exec للوصول من داخل container
docker exec -it aapanel_app sh
curl http://loki:3100/ready

# Option 3: استخدم port forwarding مؤقت (للتطوير فقط)
docker run --rm --network aapanel_network alpine/curl \
  -G -s "http://loki:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="aapanel"}'
```

**⚠️ لا تقم بإضافة port binding لـ Loki في Production!**  
Loki لا يملك authentication مدمج، لذلك تعريضه للخارج يعرض جميع السجلات للوصول غير المصرح.

### Promtail API

- **URL**: `http://localhost:9080`
- **Metrics**: `http://localhost:9080/metrics`
- **Targets**: `http://localhost:9080/targets`

```bash
# تحقق من targets النشطة
curl http://localhost:9080/targets
```

### Grafana Dashboards

1. افتح Grafana: `http://localhost:3000`
2. سجّل الدخول بالـ credentials من `.env`
3. انتقل إلى **Dashboards** → **aaPanel Logs - Loki Dashboard**

**Dashboard Panels:**
- **Log Rate by Level** - معدل السجلات حسب المستوى
- **Log Volume by Job** - حجم السجلات حسب الوظيفة
- **Log Stream** - تدفق السجلات الفوري
- **Error Logs** - جدول الأخطاء فقط
- **Top Containers** - الحاويات الأكثر إنتاجاً للسجلات
- **Total Errors/Warnings** - مقاييس إجمالية

---

## 🔍 البحث في السجلات

### LogQL Basics

LogQL هي لغة الاستعلام في Loki (مشابهة لـ PromQL).

**البنية الأساسية:**

```logql
{label_selector} |= "search_text" | json | filter
```

### أمثلة استعلامات شائعة

#### 1. جميع سجلات التطبيق

```logql
{job="aapanel"}
```

#### 2. سجلات الأخطاء فقط

```logql
{job="aapanel"} | json | level="ERROR"
```

#### 3. سجلات تحتوي على نص معين

```logql
{job="aapanel"} |= "database connection"
```

#### 4. سجلات من module معين

```logql
{job="aapanel"} | json | module="auth"
```

#### 5. سجلات من Docker container معين

```logql
{job="docker", container_name="aapanel_app"}
```

#### 6. معدل الأخطاء في آخر 5 دقائق

```logql
sum(rate({job="aapanel"} | json | level="ERROR" [5m]))
```

#### 7. عدد السجلات حسب المستوى

```logql
sum by (level) (count_over_time({job="aapanel"} | json [1h]))
```

#### 8. سجلات مع exceptions

```logql
{job="aapanel"} | json | exception != ""
```

#### 9. أبطأ 10 requests (إذا كان log يحتوي على duration)

```logql
topk(10, 
  sum by (function) (
    avg_over_time({job="aapanel"} | json | unwrap duration [5m])
  )
)
```

#### 10. تصفية متقدمة

```logql
{job="aapanel"} 
| json 
| level=~"ERROR|CRITICAL" 
| module!="test" 
| line_format "{{.timestamp}} [{{.level}}] {{.message}}"
```

### LogQL Operators

| Operator | الوصف | مثال |
|----------|--------|------|
| `=` | Equal | `level="ERROR"` |
| `!=` | Not equal | `level!="DEBUG"` |
| `=~` | Regex match | `level=~"ERROR\|CRITICAL"` |
| `!~` | Regex not match | `module!~"test.*"` |
| `\|=` | Contains | `\|= "database"` |
| `!=` | Not contains | `!= "debug"` |
| `\|~` | Regex contains | `\|~ "error.*connection"` |
| `!~` | Regex not contains | `!~ "test.*"` |

### Pipeline Stages في Grafana

```logql
{job="aapanel"} 
| json                              # Parse JSON
| level="ERROR"                     # Filter by level
| line_format "{{.message}}"        # Format output
```

---

## 🛠️ استكشاف الأخطاء

### 1. Loki لا يعمل

**الأعراض:**
- Dashboard في Grafana فارغ
- خطأ "Loki: Bad Gateway"

**التشخيص:**

```bash
# تحقق من حالة Loki
docker-compose ps loki

# اعرض logs
docker-compose logs loki

# تحقق من /ready endpoint
curl http://localhost:3100/ready
```

**الحلول:**

```bash
# إعادة تشغيل Loki
docker-compose restart loki

# إذا استمرت المشكلة، أعد إنشاء الـ container
docker-compose down
docker-compose up -d loki

# تحقق من ملف التكوين
docker-compose exec loki cat /etc/loki/local-config.yaml
```

### 2. Promtail لا يجمع السجلات

**الأعراض:**
- لا توجد سجلات جديدة في Loki
- Promtail targets empty
- رسالة خطأ: "failed to get docker container info"

**التشخيص:**

```bash
# تحقق من حالة Promtail
docker-compose ps promtail

# اعرض logs
docker-compose logs promtail

# تحقق من targets
curl http://localhost:9080/targets

# تحقق من Docker socket mount
docker inspect aapanel_promtail | grep -A 5 "docker.sock"
```

**الحلول:**

```bash
# تحقق من أن volumes موصولة بشكل صحيح
docker inspect aapanel_promtail | grep -A 10 Mounts

# تحقق من صلاحيات الملفات
ls -la /var/lib/docker/containers
ls -la logs/

# تأكد من أن Docker socket mounted (يجب أن يكون read-only)
# يجب أن ترى: /var/run/docker.sock:/var/run/docker.sock:ro

# إعادة تشغيل Promtail
docker-compose restart promtail
```

**ملاحظة:** Promtail يحتاج إلى access للـ Docker socket (`/var/run/docker.sock`) لإثراء السجلات بمعلومات الـ containers (مثل container_name). هذا الـ mount يكون **read-only** لأسباب أمنية.

### 3. التطبيق لا يكتب JSON logs

**التشخيص:**

```bash
# اعرض آخر سجل
tail -f logs/app.log

# يجب أن ترى JSON مثل:
# {"timestamp": "2024-01-01 12:00:00", "level": "INFO", ...}
```

**الحلول:**

```bash
# تحقق من متغيرات البيئة
docker-compose exec app env | grep LOG_

# يجب أن يكون:
# LOG_FORMAT=json
# LOG_LEVEL=INFO

# إذا لم تكن موجودة، أضفها إلى .env
echo "LOG_FORMAT=json" >> .env
echo "LOG_LEVEL=INFO" >> .env

# أعد تشغيل التطبيق
docker-compose restart app
```

### 4. مشاكل في Performance

**الأعراض:**
- Loki بطيء
- استعلامات تستغرق وقتاً طويلاً

**التشخيص:**

```bash
# تحقق من حجم البيانات
docker exec aapanel_loki du -sh /tmp/loki

# تحقق من استخدام الذاكرة
docker stats aapanel_loki
```

**الحلول:**

```yaml
# في loki-config.yml، قلل retention:
limits_config:
  retention_period: 72h  # بدلاً من 168h

# أو زد الـ compaction frequency:
compactor:
  compaction_interval: 5m  # بدلاً من 10m
```

### 5. Dashboard فارغ في Grafana

**الأعراض:**
- Dashboard "aaPanel Logs" لا يعرض بيانات
- "No data" في جميع panels

**التشخيص:**

```bash
# تحقق من أن Loki datasource معرّف
curl http://localhost:3000/api/datasources | grep loki

# تحقق من وجود بيانات في Loki
curl -G -s "http://localhost:3100/loki/api/v1/label/job/values"
```

**الحلول:**

1. في Grafana، انتقل إلى **Configuration** → **Data Sources**
2. تحقق من أن "Loki" موجود ومتصل
3. اضغط **Test** للتحقق من الاتصال
4. إذا كان هناك خطأ، تحقق من URL: `http://loki:3100`

---

## 🔒 الأمان والخصوصية

### 1. Loki Internal-Only Architecture

**Loki لا يملك port binding خارجي** في التكوين الحالي لأسباب أمنية:

✅ **المميزات الأمنية:**
- Loki لا يملك authentication مدمج
- جميع السجلات مكشوفة بدون تشفير
- الوصول محصور داخل Docker network فقط
- Grafana تصل إلى Loki عبر internal DNS (`http://loki:3100`)

❌ **لا تقم بـ:**
```yaml
# ❌ خطأ - لا تضف port binding في Production!
loki:
  ports:
    - "3100:3100"  # خطر أمني!
```

✅ **بدلاً من ذلك:**
```yaml
# ✅ صحيح - internal-only
loki:
  # No ports section
  networks:
    - aapanel_network
```

### 2. Promtail Docker Socket Access

Promtail يحتاج إلى Docker socket لإثراء السجلات، لكن **read-only** فقط:

```yaml
promtail:
  volumes:
    # ✅ صحيح - read-only mount
    - /var/run/docker.sock:/var/run/docker.sock:ro
    
    # ❌ خطأ - لا تستخدم read-write!
    # - /var/run/docker.sock:/var/run/docker.sock
```

**لماذا read-only؟**
- يمنع Promtail من التحكم في containers أخرى
- يقلل سطح الهجوم (attack surface)
- يكفي لقراءة metadata فقط

### 3. Reverse Proxy للوصول الآمن

إذا كنت **تحتاج** للوصول إلى Loki من خارج Docker:

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name logs.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://loki:3100;
        
        # Basic auth
        auth_basic "Loki Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        # IP whitelist
        allow 192.168.1.0/24;
        deny all;
    }
}
```

---

## 📖 Best Practices

### 1. مستويات السجلات (Log Levels)

استخدم مستويات السجلات بحكمة:

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug information")    # Development only
logger.info("Normal operation")               # Production
logger.warning("Warning: something unexpected") # Production
logger.error("Error occurred")                 # Production - يجب مراجعتها
logger.critical("Critical failure!")           # Production - emergency
```

**التوصيات:**
- **Production**: `LOG_LEVEL=INFO` (أو `WARNING`)
- **Staging**: `LOG_LEVEL=INFO`
- **Development**: `LOG_LEVEL=DEBUG`

### 2. Structured Logging

اكتب سجلات منظمة بمعلومات إضافية:

```python
logger.info("User logged in", extra={
    "user_id": 123,
    "username": "john",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
})
```

هذا يسمح بالبحث:
```logql
{job="aapanel"} | json | user_id="123"
```

### 3. لا تُسجّل معلومات حساسة

❌ **خطأ:**
```python
logger.info(f"Login attempt: password={password}")
```

✅ **صحيح:**
```python
logger.info("Login attempt", extra={"username": username})
```

**معلومات حساسة:**
- كلمات المرور
- Tokens/API keys
- أرقام بطاقات الائتمان
- معلومات شخصية (PII)

### 4. استخدم Context

أضف context للسجلات لتسهيل debugging:

```python
try:
    process_order(order_id)
except Exception as e:
    logger.error(
        "Failed to process order",
        exc_info=True,  # يضيف stack trace
        extra={
            "order_id": order_id,
            "customer_id": customer_id,
            "error_type": type(e).__name__
        }
    )
```

### 5. Log Rotation

تأكد من أن log rotation يعمل:

```bash
# تحقق من حجم الملفات
ls -lh logs/

# يجب أن ترى:
# app.log
# app.log.1
# app.log.2
# ... (حتى LOG_BACKUP_COUNT)
```

### 6. Monitoring و Alerts

أنشئ alerts للأخطاء الحرجة:

```yaml
# في Grafana Alerting
{job="aapanel"} | json | level="CRITICAL"
# Alert when: count > 0 in last 5 minutes
```

### 7. Retention Policy

اضبط retention حسب احتياجاتك:

| البيئة | Retention | السبب |
|--------|-----------|-------|
| Development | 24h-72h | مساحة محدودة |
| Staging | 7d-14d | testing و debugging |
| Production | 30d-90d | compliance و auditing |

### 8. Labels vs Fields

**Labels** (للتصفية السريعة):
- job
- level
- container_name
- environment

**Fields** (للبحث النصي):
- message
- exception
- user_id
- request_id

```logql
# ✅ سريع - استخدام labels
{job="aapanel", level="ERROR"}

# ❌ بطيء - البحث في message
{job="aapanel"} |= "error"
```

---

## 🔧 الصيانة

### 1. النسخ الاحتياطي

**نسخ احتياطي لبيانات Loki:**

```bash
# إيقاف Loki مؤقتاً
docker-compose stop loki

# نسخ البيانات
docker run --rm \
  -v aapanel_loki_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/loki-backup-$(date +%Y%m%d).tar.gz /data

# إعادة تشغيل Loki
docker-compose start loki
```

**استعادة من نسخة احتياطية:**

```bash
# إيقاف Loki
docker-compose stop loki

# حذف البيانات القديمة
docker volume rm aapanel_loki_data
docker volume create aapanel_loki_data

# استعادة البيانات
docker run --rm \
  -v aapanel_loki_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/loki-backup-20240101.tar.gz -C /

# إعادة تشغيل Loki
docker-compose start loki
```

### 2. تنظيف البيانات القديمة

Loki ينظف البيانات تلقائياً حسب `retention_period`، لكن يمكنك تنظيف يدوياً:

```bash
# دخول إلى Loki container
docker exec -it aapanel_loki sh

# حذف ملفات قديمة (مثال)
find /tmp/loki -type f -mtime +30 -delete

# خروج
exit

# إعادة تشغيل Loki
docker-compose restart loki
```

### 3. مراقبة المساحة

```bash
# تحقق من مساحة القرص
df -h /var/lib/docker/volumes

# تحقق من حجم volumes
docker system df -v | grep loki

# تنظيف volumes غير المستخدمة
docker volume prune
```

### 4. تحديث Loki و Promtail

```bash
# تحديث إلى نسخة جديدة
# في docker-compose.yml:
# loki: image: grafana/loki:2.10.0  # نسخة جديدة
# promtail: image: grafana/promtail:2.10.0

# تحديث
docker-compose pull loki promtail
docker-compose up -d loki promtail

# تحقق من النسخة
docker exec aapanel_loki loki --version
docker exec aapanel_promtail promtail --version
```

### 5. Performance Tuning

إذا كان Loki بطيئاً، جرّب:

```yaml
# في loki-config.yml

# 1. زد cache size
chunk_store_config:
  chunk_cache_config:
    embedded_cache:
      max_size_mb: 500  # من 100

# 2. زد query parallelism
query_range:
  parallelise_shardable_queries: true
  max_retries: 5

# 3. قلل retention
limits_config:
  retention_period: 72h  # من 168h
```

---

## 📚 مراجع إضافية

### الوثائق الرسمية

- **Loki Documentation**: https://grafana.com/docs/loki/latest/
- **Promtail Documentation**: https://grafana.com/docs/loki/latest/clients/promtail/
- **LogQL Guide**: https://grafana.com/docs/loki/latest/logql/

### أدوات مفيدة

```bash
# logcli - CLI tool لـ Loki
docker run grafana/logcli:latest --addr=http://loki:3100 query '{job="aapanel"}'

# loki-canary - أداة testing
docker run grafana/loki-canary:latest -addr=http://loki:3100
```

### مثال Integration مع Python

```python
import logging
import requests

class LokiHandler(logging.Handler):
    def __init__(self, url, labels):
        super().__init__()
        self.url = url
        self.labels = labels
    
    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "streams": [{
                "stream": self.labels,
                "values": [[str(int(time.time() * 1e9)), log_entry]]
            }]
        }
        try:
            requests.post(self.url, json=payload)
        except:
            pass

# استخدام
handler = LokiHandler(
    url="http://localhost:3100/loki/api/v1/push",
    labels={"job": "myapp", "level": "info"}
)
logging.getLogger().addHandler(handler)
```

---

## ❓ الأسئلة الشائعة

**Q: هل يمكن استخدام Loki مع Elasticsearch؟**  
A: نعم، لكن Loki مصمم ليكون بديل أخف وأرخص من Elasticsearch للسجلات.

**Q: ما الفرق بين Loki و Elasticsearch؟**  
A: Loki يفهرس labels فقط (أسرع وأرخص)، بينما Elasticsearch يفهرس كل النص (أبطأ وأغلى).

**Q: هل Loki يدعم Full-Text Search؟**  
A: Loki يدعم grep-style search في النصوص، لكن ليس full-text indexing مثل Elasticsearch.

**Q: كم من المساحة يحتاج Loki؟**  
A: يعتمد على حجم السجلات. كقاعدة عامة: ~1GB لكل مليون سطر log.

**Q: هل يمكن استخدام Loki في Production؟**  
A: نعم، Loki مستقر ويستخدم في production من شركات كبيرة (Grafana Labs نفسها تستخدمه).

---

## 🎯 الخلاصة

نظام Centralized Logging الآن جاهز بالكامل:

✅ **Loki** - يخزن ويفهرس السجلات  
✅ **Promtail** - يجمع السجلات من Docker و Application  
✅ **Grafana** - يعرض ويحلل السجلات  
✅ **Structured Logging** - JSON logs من التطبيق  
✅ **Retention** - 7 أيام افتراضياً  
✅ **Dashboard** - جاهز للاستخدام  
✅ **Blue-Green** - يدعم نشر Blue-Green  

**الخطوات التالية:**

1. ✅ راجع Dashboard في Grafana
2. ✅ جرّب استعلامات LogQL
3. ✅ أنشئ alerts للأخطاء الحرجة
4. ✅ اضبط retention حسب احتياجاتك
5. ✅ أضف custom labels لتطبيقك

**للدعم:**
- راجع [Troubleshooting](#استكشاف-الأخطاء)
- راجع [Loki Documentation](https://grafana.com/docs/loki/latest/)
- راجع ملف `MONITORING_SETUP.md` للمراقبة

---

**تم إعداد هذا الدليل بتاريخ:** 2024-01-01  
**النسخة:** 1.0  
**المؤلف:** aaPanel DevOps Team
