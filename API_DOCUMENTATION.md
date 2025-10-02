# 📚 aaPanel API Documentation

## نظرة عامة

توثيق شامل لـ Health & Monitoring API الخاص بـ aaPanel.

---

## 📋 جدول المحتويات

1. [مقدمة](#مقدمة)
2. [البدء السريع](#البدء-السريع)
3. [نقاط النهاية (Endpoints)](#نقاط-النهاية-endpoints)
4. [أمثلة عملية](#أمثلة-عملية)
5. [التكامل مع Kubernetes](#التكامل-مع-kubernetes)
6. [Swagger UI](#swagger-ui)
7. [خطط مستقبلية](#خطط-مستقبلية)

---

## 🎯 مقدمة

### ما هو aaPanel Health API؟

aaPanel Health API يوفر **3 نقاط نهاية (endpoints) للمراقبة والصحة**:

| Endpoint | الوصف | الحالة |
|----------|--------|--------|
| `/health/live` | Liveness probe | ✅ متاح |
| `/health/ready` | Readiness probe | ✅ متاح |
| `/health/metrics` | Prometheus metrics | ✅ متاح |

### الميزات الحالية

✅ **Liveness Check**: التحقق من أن التطبيق يعمل  
✅ **Readiness Check**: التحقق من جاهزية التطبيق (Database + Redis)  
✅ **Metrics Export**: إحصائيات النظام وقاعدة البيانات  
✅ **Kubernetes Compatible**: متوافق مع Kubernetes probes  
✅ **Prometheus Compatible**: متوافق مع Prometheus scraping  

### التنفيذ الفني

جميع نقاط النهاية مُنفذة في **`health_endpoints.py`**:

```python
from health_endpoints import register_health_routes

# تسجيل health routes مع Flask app
register_health_routes(app)
```

---

## 🚀 البدء السريع

### 1. الوصول إلى التوثيق التفاعلي (Swagger UI)

افتح المتصفح وانتقل إلى:

```
http://localhost:5000/api/docs/
```

**في الإنتاج:**
```
https://your-domain.com/api/docs/
```

### 2. أول طلب API

#### مثال: فحص صحة التطبيق (Liveness)

```bash
curl http://localhost:5000/health/live
```

**الاستجابة:**
```json
{
  "status": "alive",
  "timestamp": "2025-10-02T12:00:00.000000",
  "uptime_seconds": 3600.5
}
```

#### مثال: فحص جاهزية التطبيق (Readiness)

```bash
curl http://localhost:5000/health/ready
```

**الاستجابة (جاهز):**
```json
{
  "status": "ready",
  "timestamp": "2025-10-02T12:00:00.000000",
  "uptime_seconds": 3600.5,
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connected"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connected"
    }
  }
}
```

#### مثال: الحصول على Metrics

```bash
curl http://localhost:5000/health/metrics
```

**الاستجابة:**
```json
{
  "uptime_seconds": 3600.5,
  "timestamp": "2025-10-02T12:00:00.000000",
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_percent": 68.7
  },
  "database": {
    "connections_created": 150,
    "connections_closed": 145,
    "total_queries": 5000,
    "failed_queries": 5,
    "success_rate": 99.9,
    "status": "up"
  },
  "redis": {
    "status": "up"
  }
}
```

---

## 🌐 نقاط النهاية (Endpoints)

### 1. GET /health/live

**Liveness Probe** - يتحقق من أن التطبيق يعمل

#### معلومات الـ Endpoint

| المعلومة | القيمة |
|----------|--------|
| **Method** | `GET` |
| **Path** | `/health/live` |
| **Authentication** | لا يتطلب ❌ |
| **Rate Limit** | غير محدود |
| **Response Format** | JSON |

#### الوصف

يرجع دائماً `200 OK` إذا كان التطبيق قيد التشغيل. يُستخدم من قبل Kubernetes و monitoring systems للتحقق من أن العملية (process) نشطة.

#### الاستجابة

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "status": "alive",
  "timestamp": "2025-10-02T12:00:00.000000",
  "uptime_seconds": 3600.5
}
```

**Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | دائماً `"alive"` |
| `timestamp` | string (ISO 8601) | وقت الاستجابة بتوقيت UTC |
| `uptime_seconds` | number | مدة تشغيل التطبيق بالثواني |

#### مثال cURL

```bash
curl -X GET http://localhost:5000/health/live
```

#### مثال Python

```python
import requests

response = requests.get('http://localhost:5000/health/live')
print(response.json())

# Output:
# {
#   "status": "alive",
#   "timestamp": "2025-10-02T12:00:00.000000",
#   "uptime_seconds": 3600.5
# }
```

#### استخدام Kubernetes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

---

### 2. GET /health/ready

**Readiness Probe** - يتحقق من جاهزية التطبيق لاستقبال الطلبات

#### معلومات الـ Endpoint

| المعلومة | القيمة |
|----------|--------|
| **Method** | `GET` |
| **Path** | `/health/ready` |
| **Authentication** | لا يتطلب ❌ |
| **Rate Limit** | غير محدود |
| **Response Format** | JSON |

#### الوصف

يتحقق من اتصال قاعدة البيانات و Redis قبل إرجاع الاستجابة:
- ✅ يرجع `200 OK` إذا كانت جميع الخدمات سليمة
- ❌ يرجع `503 Service Unavailable` إذا فشل أي فحص

يُستخدم من قبل Kubernetes و load balancers لمعرفة متى يمكن إرسال traffic للتطبيق.

#### الفحوصات المُنفذة

1. **Database Check**: يستدعي `db_pool.health_check()`
2. **Redis Check**: يتصل بـ Redis ويرسل `PING`

#### الاستجابة - حالة جاهز

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "status": "ready",
  "timestamp": "2025-10-02T12:00:00.000000",
  "uptime_seconds": 3600.5,
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connected"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connected"
    }
  }
}
```

#### الاستجابة - حالة غير جاهز

**Status Code**: `503 Service Unavailable`

**Response Body**:
```json
{
  "status": "not_ready",
  "timestamp": "2025-10-02T12:00:00.000000",
  "uptime_seconds": 3600.5,
  "checks": {
    "database": {
      "status": "unhealthy",
      "message": "Database connection failed"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connected"
    }
  }
}
```

#### Schema

**Root Object**:
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"ready"` أو `"not_ready"` |
| `timestamp` | string (ISO 8601) | وقت الاستجابة |
| `uptime_seconds` | number | مدة التشغيل |
| `checks` | object | نتائج الفحوصات |

**checks.database / checks.redis**:
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"healthy"` أو `"unhealthy"` |
| `message` | string | رسالة توضيحية |

#### مثال cURL

```bash
# الاستدعاء العادي
curl -X GET http://localhost:5000/health/ready

# مع عرض status code
curl -w "\nHTTP Status: %{http_code}\n" http://localhost:5000/health/ready
```

#### مثال Python

```python
import requests

response = requests.get('http://localhost:5000/health/ready')

if response.status_code == 200:
    print("✅ Application is ready!")
    print(response.json())
elif response.status_code == 503:
    print("❌ Application is NOT ready!")
    data = response.json()
    
    # طباعة الفحوصات الفاشلة
    for service, check in data['checks'].items():
        if check['status'] == 'unhealthy':
            print(f"  - {service}: {check['message']}")
```

#### استخدام Kubernetes

```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

---

### 3. GET /health/metrics

**Prometheus Metrics** - إحصائيات ومقاييس التطبيق

#### معلومات الـ Endpoint

| المعلومة | القيمة |
|----------|--------|
| **Method** | `GET` |
| **Path** | `/health/metrics` |
| **Authentication** | لا يتطلب ❌ |
| **Rate Limit** | غير محدود |
| **Response Format** | JSON |
| **Prometheus Compatible** | ✅ (عبر json_exporter) |

#### الوصف

يرجع إحصائيات شاملة عن التطبيق والنظام، بما في ذلك:
- معلومات النظام (CPU, Memory, Disk)
- إحصائيات قاعدة البيانات
- حالة Redis
- مدة التشغيل

#### الاستجابة

**Status Code**: `200 OK`

**Response Body (كامل - مع database stats)**:
```json
{
  "uptime_seconds": 3600.5,
  "timestamp": "2025-10-02T12:00:00.000000",
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_percent": 68.7
  },
  "database": {
    "connections_created": 150,
    "connections_closed": 145,
    "total_queries": 5000,
    "failed_queries": 5,
    "success_rate": 99.9,
    "status": "up"
  },
  "redis": {
    "status": "up"
  }
}
```

**Response Body (بدون database - إذا لم يكن db_pool متاحاً)**:
```json
{
  "uptime_seconds": 1200.0,
  "timestamp": "2025-10-02T12:20:00.000000",
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 38.5,
    "disk_percent": 55.3
  },
  "redis": {
    "status": "down"
  }
}
```

#### Schema

**Root Object**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uptime_seconds` | number | ✅ | مدة التشغيل |
| `timestamp` | string | ✅ | وقت الاستجابة |
| `system` | object | ✅ | معلومات النظام |
| `database` | object | ❌ | إحصائيات DB (إن وُجد) |
| `redis` | object | ✅ | حالة Redis |

**system object**:
| Field | Type | Description | Range |
|-------|------|-------------|-------|
| `cpu_percent` | number | استخدام CPU | 0-100 |
| `memory_percent` | number | استخدام الذاكرة | 0-100 |
| `disk_percent` | number | استخدام القرص | 0-100 |

**database object** (optional):
| Field | Type | Description |
|-------|------|-------------|
| `connections_created` | integer | إجمالي الاتصالات المُنشأة |
| `connections_closed` | integer | إجمالي الاتصالات المُغلقة |
| `total_queries` | integer | إجمالي الاستعلامات |
| `failed_queries` | integer | الاستعلامات الفاشلة |
| `success_rate` | number | نسبة النجاح (0-100) |
| `status` | string | `"up"` أو `"down"` |

**redis object**:
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"up"` أو `"down"` |

#### مثال cURL

```bash
curl -X GET http://localhost:5000/health/metrics | jq .
```

#### مثال Python - مراقبة مستمرة

```python
import requests
import time

def monitor_metrics(interval=30):
    """مراقبة metrics كل interval ثانية"""
    while True:
        try:
            response = requests.get('http://localhost:5000/health/metrics')
            metrics = response.json()
            
            cpu = metrics['system']['cpu_percent']
            memory = metrics['system']['memory_percent']
            disk = metrics['system']['disk_percent']
            
            print(f"[{metrics['timestamp']}]")
            print(f"  CPU: {cpu:.1f}%")
            print(f"  Memory: {memory:.1f}%")
            print(f"  Disk: {disk:.1f}%")
            
            if 'database' in metrics:
                db = metrics['database']
                print(f"  DB Queries: {db['total_queries']} (Success: {db['success_rate']:.2f}%)")
            
            # تنبيه إذا تجاوز CPU 80%
            if cpu > 80:
                print("  ⚠️  WARNING: High CPU usage!")
            
            print()
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(interval)

# بدء المراقبة
monitor_metrics(interval=30)
```

#### التكامل مع Prometheus

##### prometheus.yml

```yaml
scrape_configs:
  - job_name: 'aapanel'
    scrape_interval: 15s
    metrics_path: '/health/metrics'
    static_configs:
      - targets: ['localhost:5000']
```

**ملاحظة**: `/health/metrics` يرجع JSON، لذلك تحتاج إلى:
- استخدام `prometheus-json-exporter` لتحويل JSON إلى Prometheus format
- أو استخدام endpoint منفصل يرجع Prometheus text format

---

## 💡 أمثلة عملية

### مثال 1: سكريبت مراقبة صحة التطبيق

```bash
#!/bin/bash
# health_monitor.sh - مراقبة صحة التطبيق

ENDPOINT="http://localhost:5000/health/ready"
LOG_FILE="/var/log/aapanel/health_monitor.log"

while true; do
    RESPONSE=$(curl -s -w "\n%{http_code}" "$ENDPOINT")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | head -n -1)
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "[$TIMESTAMP] ✅ Application is ready" | tee -a "$LOG_FILE"
    else
        echo "[$TIMESTAMP] ❌ Application is NOT ready (HTTP $HTTP_CODE)" | tee -a "$LOG_FILE"
        echo "$BODY" | jq . | tee -a "$LOG_FILE"
    fi
    
    sleep 60
done
```

### مثال 2: جمع Metrics وحفظها

```python
#!/usr/bin/env python3
# metrics_collector.py

import requests
import json
import time
from datetime import datetime

METRICS_URL = 'http://localhost:5000/health/metrics'
OUTPUT_FILE = '/var/log/aapanel/metrics.jsonl'

def collect_and_save():
    """جمع وحفظ metrics"""
    try:
        response = requests.get(METRICS_URL)
        if response.status_code == 200:
            metrics = response.json()
            
            # إضافة timestamp للسجل
            log_entry = {
                'collected_at': datetime.utcnow().isoformat(),
                'metrics': metrics
            }
            
            # حفظ في ملف JSONL (JSON Lines)
            with open(OUTPUT_FILE, 'a') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            print(f"✅ Metrics collected at {log_entry['collected_at']}")
            
            # تنبيه إذا كان CPU أو Memory عالي
            if metrics['system']['cpu_percent'] > 80:
                print("⚠️  WARNING: High CPU usage!")
            if metrics['system']['memory_percent'] > 85:
                print("⚠️  WARNING: High memory usage!")
        else:
            print(f"❌ Failed to fetch metrics: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

# جمع كل 30 ثانية
if __name__ == '__main__':
    while True:
        collect_and_save()
        time.sleep(30)
```

### مثال 3: Integration مع Alerting System

```python
#!/usr/bin/env python3
# alerting.py

import requests
import time

def send_slack_alert(message):
    """إرسال تنبيه إلى Slack"""
    webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    payload = {
        'text': message,
        'username': 'aaPanel Monitor',
        'icon_emoji': ':warning:'
    }
    requests.post(webhook_url, json=payload)

def check_health():
    """فحص صحة التطبيق وإرسال تنبيهات"""
    try:
        # فحص readiness
        ready = requests.get('http://localhost:5000/health/ready')
        
        if ready.status_code != 200:
            data = ready.json()
            
            # فحص الخدمات الفاشلة
            for service, check in data['checks'].items():
                if check['status'] == 'unhealthy':
                    message = f"🚨 *{service}* is unhealthy: {check['message']}"
                    send_slack_alert(message)
        
        # فحص metrics
        metrics_resp = requests.get('http://localhost:5000/health/metrics')
        if metrics_resp.status_code == 200:
            metrics = metrics_resp.json()
            
            # تنبيهات CPU/Memory
            if metrics['system']['cpu_percent'] > 90:
                send_slack_alert(f"🔥 Critical: CPU usage at {metrics['system']['cpu_percent']:.1f}%")
            
            if metrics['system']['memory_percent'] > 95:
                send_slack_alert(f"🔥 Critical: Memory usage at {metrics['system']['memory_percent']:.1f}%")
            
            # تنبيه Database
            if 'database' in metrics and metrics['database']['status'] == 'down':
                send_slack_alert("🔴 Database is DOWN!")
    
    except Exception as e:
        send_slack_alert(f"❌ Monitoring script error: {str(e)}")

# تشغيل الفحص كل دقيقة
if __name__ == '__main__':
    while True:
        check_health()
        time.sleep(60)
```

---

## ☸️ التكامل مع Kubernetes

### Deployment مع Health Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aapanel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aapanel
  template:
    metadata:
      labels:
        app: aapanel
    spec:
      containers:
      - name: aapanel
        image: ghcr.io/your-org/aapanel:latest
        ports:
        - containerPort: 5000
          name: http
        
        # Liveness Probe
        livenessProbe:
          httpGet:
            path: /health/live
            port: 5000
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
        
        # Readiness Probe
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 5000
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
        
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### ServiceMonitor للـ Prometheus Operator

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: aapanel-metrics
spec:
  selector:
    matchLabels:
      app: aapanel
  endpoints:
  - port: http
    path: /health/metrics
    interval: 30s
```

---

## 📖 Swagger UI

### الوصول

افتح المتصفح:

```
http://localhost:5000/api/docs/
```

### الميزات

✅ **واجهة تفاعلية** - جرب APIs مباشرة  
✅ **توثيق مرئي** - schemas و examples واضحة  
✅ **Try it out** - اختبر endpoints من المتصفح  
✅ **Export** - حمّل OpenAPI spec (YAML/JSON)  

### التفعيل

في `runserver.py` أو `BTPanel/__init__.py`:

```python
from swagger_ui import register_swagger_ui

# بعد إنشاء Flask app
app = Flask(__name__)

# تسجيل Swagger UI
register_swagger_ui(app)
```

### الملفات المطلوبة

```
project/
├── openapi.yaml              # OpenAPI 3.0 specification
├── swagger_ui.py             # Swagger UI integration
└── API_DOCUMENTATION.md      # هذا الدليل
```

---

## 🔮 خطط مستقبلية

### Endpoints مخطط لها (قيد التطوير)

التوثيق الحالي يغطي **فقط Health Endpoints الموجودة فعلياً**.

في المستقبل، سيتم إضافة:

#### 🔐 Authentication API
- `POST /api/login` - تسجيل الدخول
- `POST /api/logout` - تسجيل الخروج
- `GET /api/user/profile` - معلومات المستخدم

#### 💻 System Management API
- `GET /api/system/info` - معلومات النظام
- `GET /api/system/processes` - قائمة العمليات
- `POST /api/system/restart` - إعادة تشغيل خدمات

#### 🗄️ Database Management API
- `GET /api/databases` - قائمة قواعد البيانات
- `POST /api/databases` - إنشاء قاعدة بيانات
- `DELETE /api/databases/{id}` - حذف قاعدة بيانات

#### 📁 File Management API
- `GET /api/files` - تصفح الملفات
- `POST /api/files/upload` - رفع ملفات
- `GET /api/files/download` - تنزيل ملفات

#### 🔒 Security API
- `GET /api/firewall/rules` - قواعد جدار الحماية
- `POST /api/ssl/certificates` - إدارة SSL certificates

**سيتم تحديث هذا التوثيق عند إضافة هذه الـ endpoints.**

---

## 🔧 التثبيت والإعداد

### 1. المتطلبات

```bash
pip install flask pyyaml psutil
```

### 2. تفعيل Health Endpoints

في `BTPanel/__init__.py` أو `runserver.py`:

```python
from health_endpoints import register_health_routes

# تسجيل health routes
register_health_routes(app)
```

### 3. تفعيل Swagger UI (اختياري)

```python
from swagger_ui import register_swagger_ui

# تسجيل Swagger UI
register_swagger_ui(app)
```

### 4. التحقق

```bash
# بدء التطبيق
python runserver.py

# اختبار endpoints
curl http://localhost:5000/health/live
curl http://localhost:5000/health/ready
curl http://localhost:5000/health/metrics

# Swagger UI
# افتح: http://localhost:5000/api/docs/
```

---

## 📞 الدعم والمساعدة

### الموارد

- **Swagger UI**: `http://localhost:5000/api/docs/`
- **OpenAPI Spec**: `openapi.yaml`
- **Source Code**: `health_endpoints.py`

### استكشاف الأخطاء الشائعة

#### المشكلة: `/health/ready` يرجع 503

**السبب**: Database أو Redis غير متصل

**الحل**:
1. افحص `/health/ready` للتفاصيل
2. تحقق من اتصال Database
3. تحقق من اتصال Redis (إن كان مُفعّل)

```bash
curl http://localhost:5000/health/ready | jq .
```

#### المشكلة: Swagger UI لا يعمل

**الحل**:
1. تأكد من تسجيل `swagger_ui` blueprint
2. تحقق من وجود `openapi.yaml`
3. افتح console في المتصفح لرؤية الأخطاء

#### المشكلة: Metrics لا تظهر database stats

**السبب**: `db_pool` غير متاح أو لم يُهيأ

**الحل**:
1. تأكد من تهيئة `DatabaseConnectionPool`
2. تحقق من import في `health_endpoints.py`

---

## 📝 ملاحظات تقنية

### التنفيذ

- **File**: `health_endpoints.py`
- **Blueprint**: `health_bp` (prefix: `/health`)
- **Dependencies**: `psutil`, `config_factory`, `db_pool`

### الأداء

- ⚡ **Liveness**: < 5ms (بدون I/O)
- ⚡ **Readiness**: < 50ms (مع DB + Redis checks)
- ⚡ **Metrics**: < 100ms (مع جمع system stats)

### الأمان

- 🔓 **لا يتطلب authentication** - endpoints عامة للمراقبة
- 🔒 **في الإنتاج**: يمكن تقييد الوصول عبر firewall/nginx
- ⚠️ **لا تحتوي على معلومات حساسة** - آمنة للعرض

---

## 🎉 الخلاصة

الآن لديك:

✅ **3 Health Endpoints** موثقة بالكامل  
✅ **OpenAPI 3.0 Specification** دقيقة  
✅ **Swagger UI** تفاعلي  
✅ **أمثلة عملية** جاهزة  
✅ **تكامل Kubernetes** محدد  

**ابدأ الآن!** 🚀

```bash
curl http://localhost:5000/health/live
```

---

**آخر تحديث**: 2 أكتوبر 2025  
**الإصدار**: 1.0.0  
**الحالة**: ✅ يوثق فقط Endpoints الموجودة فعلياً  
**المصدر**: `health_endpoints.py`
