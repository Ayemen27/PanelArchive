# 📊 دليل إعداد نظام المراقبة - Prometheus & Grafana

## نظرة عامة

تم إعداد نظام مراقبة شامل لـ aaPanel باستخدام **Prometheus** لجمع المقاييس و **Grafana** لعرض البيانات. هذا النظام يوفر:

- ✅ مراقبة فورية للأداء (CPU, Memory, Disk)
- ✅ مراقبة قاعدة البيانات (اتصالات، وقت الاستجابة)
- ✅ مراقبة Redis (اتصالات، وقت الاستجابة)
- ✅ Dashboards جاهزة للاستخدام
- ✅ بيانات محفوظة (retention 15 يوم)

---

## 📋 جدول المحتويات

1. [البنية التقنية](#البنية-التقنية)
2. [التثبيت السريع](#التثبيت-السريع)
3. [الوصول للخدمات](#الوصول-للخدمات)
4. [تكوين Prometheus](#تكوين-prometheus)
5. [تكوين Grafana](#تكوين-grafana)
6. [الـ Dashboards](#الـ-dashboards)
7. [استكشاف الأخطاء](#استكشاف-الأخطاء)
8. [الأمان](#الأمان)

---

## 🏗️ البنية التقنية

### المكونات الرئيسية

```
┌─────────────────────────────────────────────────┐
│                   aaPanel App                    │
│            (Port 5000)                           │
│         /health/metrics endpoint                 │
└────────────────┬────────────────────────────────┘
                 │ Scrapes metrics every 10s
                 ↓
┌─────────────────────────────────────────────────┐
│                  Prometheus                      │
│            (Port 9090)                           │
│         - Collects metrics                       │
│         - Stores time-series data                │
│         - Retention: 15 days                     │
└────────────────┬────────────────────────────────┘
                 │ Data source
                 ↓
┌─────────────────────────────────────────────────┐
│                   Grafana                        │
│            (Port 3000)                           │
│         - Visualizes metrics                     │
│         - Auto-provisioned dashboards            │
│         - Credentials: Set via .env (required)   │
└─────────────────────────────────────────────────┘
```

### الملفات المستخدمة

| الملف | الوصف |
|-------|--------|
| `prometheus.yml` | تكوين Prometheus الرئيسي |
| `grafana-datasource.yml` | تكوين مصدر البيانات لـ Grafana |
| `grafana-dashboard-aapanel.json` | Dashboard الرئيسي لـ aaPanel |
| `grafana-dashboard-provisioning.yml` | تكوين التحميل التلقائي للـ dashboards |
| `docker-compose.yml` | إعداد الخدمات في Docker |

---

## 🚀 التثبيت السريع

### 1. البيئة الأساسية (Production)

```bash
# 1. تأكد من وجود جميع الملفات
ls -la prometheus.yml grafana-*.yml grafana-*.json

# 2. ⚠️ أضف Grafana credentials في .env (إلزامي!)
# انسخ من .env.monitoring.example أو أضف مباشرة:
echo "GRAFANA_ADMIN_USER=admin" >> .env
echo "GRAFANA_ADMIN_PASSWORD=YourSecurePassword123!" >> .env

# 3. شغّل جميع الخدمات
docker-compose up -d

# 4. تحقق من حالة الخدمات
docker-compose ps

# 5. افتح Grafana
# انتقل إلى: http://localhost:3000
# تسجيل الدخول بالـ credentials المحددة في .env
```

### 2. بيئة Blue-Green Deployment

```bash
# 1. شغّل الخدمات المشتركة (بما فيها Prometheus & Grafana)
docker-compose -f docker-compose.shared.yml up -d

# 2. شغّل البيئة الزرقاء أو الخضراء
docker-compose -f docker-compose.blue.yml up -d
# أو
docker-compose -f docker-compose.green.yml up -d

# 3. Prometheus و Grafana متوفران على نفس المنافذ
```

---

## 🔑 الوصول للخدمات

### Prometheus

- **URL**: `http://localhost:9090`
- **لا يحتاج تسجيل دخول** (افتراضياً)
- **الاستخدام**:
  - استعراض Metrics: `/graph`
  - Targets status: `/targets`
  - Configuration: `/config`

### Grafana

- **URL**: `http://localhost:3000`
- **المستخدم**: يُحدد عبر `GRAFANA_ADMIN_USER` (متغير بيئة **إلزامي**)
- **كلمة المرور**: يُحدد عبر `GRAFANA_ADMIN_PASSWORD` (متغير بيئة **إلزامي**)

⚠️ **مهم جداً**: لا يوجد admin/admin افتراضي! يجب تعيين credentials قبل التشغيل:

```bash
# في ملف .env (أو استخدم .env.monitoring.example كنموذج)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=VerySecurePassword123!

# ثم شغّل Docker Compose
docker-compose up -d
```

⚠️ **في الإنتاج**:
1. استخدم كلمة مرور قوية (12+ حرف)
2. أزل port mapping (3000:3000) من docker-compose.yml
3. استخدم nginx reverse proxy مع SSL/TLS فقط

---

## ⚙️ تكوين Prometheus

### 1. ملف `prometheus.yml`

```yaml
global:
  scrape_interval: 15s      # جمع المقاييس كل 15 ثانية
  evaluation_interval: 15s   # تقييم القواعد كل 15 ثانية

scrape_configs:
  # مراقبة aaPanel
  - job_name: 'aapanel'
    scrape_interval: 10s     # أسرع لـ aaPanel
    metrics_path: '/health/metrics'
    static_configs:
      - targets: ['app:5000']
```

### 2. المقاييس المتاحة

Prometheus يجمع المقاييس التالية من `/health/metrics`:

#### مقاييس النظام (System Metrics)
- `aapanel_cpu_percent` - استخدام CPU (%)
- `aapanel_memory_percent` - استخدام الذاكرة (%)
- `aapanel_disk_percent` - استخدام القرص (%)

#### مقاييس قاعدة البيانات (Database Metrics)
- `aapanel_db_pool_active_connections` - الاتصالات النشطة
- `aapanel_db_pool_idle_connections` - الاتصالات الخاملة
- `aapanel_db_response_time_ms` - وقت استجابة DB (ms)

#### مقاييس Redis (Redis Metrics)
- `aapanel_redis_connected` - حالة اتصال Redis
- `aapanel_redis_response_time_ms` - وقت استجابة Redis (ms)

### 3. الاستعلامات الشائعة (PromQL)

```promql
# معدل استخدام CPU
rate(aapanel_cpu_percent[5m])

# متوسط وقت استجابة DB
avg_over_time(aapanel_db_response_time_ms[5m])

# عدد اتصالات DB الكلي
aapanel_db_pool_active_connections + aapanel_db_pool_idle_connections

# معدل تغيير الذاكرة
delta(aapanel_memory_percent[1h])
```

---

## 📈 تكوين Grafana

### 1. Datasource (Prometheus)

تم تكوين Prometheus تلقائياً كمصدر بيانات عبر `grafana-datasource.yml`:

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

### 2. Dashboard التلقائي

Dashboard `aaPanel System Monitoring` يتم تحميله تلقائياً ويحتوي على:

#### الـ Panels

1. **CPU Usage Gauge** (0-100%)
   - Green: 0-70%
   - Yellow: 70-90%
   - Red: 90-100%

2. **Memory Usage Gauge** (0-100%)
   - Green: 0-70%
   - Yellow: 70-85%
   - Red: 85-100%

3. **Disk Usage Gauge** (0-100%)
   - Green: 0-75%
   - Yellow: 75-90%
   - Red: 90-100%

4. **Database Connections** (Time Series)
   - Active connections
   - Idle connections

5. **Database Response Time** (Time Series)
   - Average response time
   - Max response time

6. **Redis Response Time** (Time Series)
   - Average response time
   - Max response time

### 3. إنشاء Dashboard جديد

```bash
# 1. افتح Grafana (http://localhost:3000)
# 2. اذهب إلى Dashboards > New Dashboard
# 3. أضف Panel جديد
# 4. اختر Prometheus كـ Data Source
# 5. أدخل PromQL query (مثال: aapanel_cpu_percent)
# 6. احفظ Dashboard
```

---

## 🎯 الـ Dashboards

### Dashboard الرئيسي: aaPanel System Monitoring

**المسار**: `Dashboards > aaPanel > aaPanel System Monitoring`

**الميزات**:
- ✅ Auto-refresh كل 10 ثوانٍ
- ✅ عرض آخر ساعة افتراضياً
- ✅ 6 panels جاهزة للاستخدام
- ✅ Responsive design

**التخصيص**:
1. انقر على عنوان Panel > Edit
2. غيّر Query أو Visualization
3. احفظ التغييرات

### إضافة Panels جديدة

```promql
# مثال: معدل الطلبات في الدقيقة (إذا كان متوفراً)
rate(http_requests_total[1m])

# مثال: معدل الأخطاء
rate(http_requests_total{status=~"5.."}[5m])

# مثال: P95 latency (إذا كان متوفراً)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

---

## 🔧 استكشاف الأخطاء

### المشكلة 1: Prometheus لا يجمع metrics

**الأعراض**:
- Dashboard فارغ
- "No data" في Grafana

**الحلول**:
```bash
# 1. تحقق من صحة Prometheus
curl http://localhost:9090/-/healthy

# 2. تحقق من targets
curl http://localhost:9090/api/v1/targets

# 3. تحقق من /health/metrics في التطبيق
curl http://localhost:5000/health/metrics

# 4. فحص logs
docker-compose logs prometheus
docker-compose logs app
```

### المشكلة 2: Grafana لا تظهر البيانات

**الأعراض**:
- Dashboard يفتح لكن لا توجد بيانات

**الحلول**:
```bash
# 1. تحقق من datasource
# في Grafana: Configuration > Data Sources > Prometheus > Test

# 2. تحقق من query في Dashboard
# افتح Panel > Edit > Query inspector

# 3. تحقق من logs
docker-compose logs grafana
```

### المشكلة 3: Cannot connect to Prometheus

**الأعراض**:
- Grafana: "Bad Gateway" أو "Connection refused"

**الحلول**:
```bash
# 1. تحقق من Docker network
docker network ls
docker network inspect aapanel_network

# 2. تحقق من أن Prometheus يعمل
docker-compose ps prometheus

# 3. ping من داخل Grafana container
docker exec -it aapanel_grafana ping prometheus
```

### المشكلة 4: بيانات قديمة فقط

**الأعراض**:
- Dashboard يظهر بيانات قديمة

**الحلول**:
```bash
# 1. تحقق من scrape_interval في prometheus.yml
# يجب أن يكون 10-15 ثانية

# 2. تحقق من auto-refresh في Grafana
# Dashboard settings > Auto refresh: 10s

# 3. أعد تحميل Prometheus config
curl -X POST http://localhost:9090/-/reload
```

---

## 🔒 الأمان

### ⚠️ تحذير أمني حرج

**لا تستخدم هذا النظام في الإنتاج بدون تأمينه أولاً!**

النظام الحالي معرّض للمخاطر التالية:
1. ❌ Prometheus & Grafana معرّضان على 0.0.0.0 (جميع الواجهات)
2. ❌ لا يوجد authentication على Prometheus
3. ❌ يجب تعيين Grafana credentials يدوياً

### 1. تأمين Grafana

#### تعيين Credentials (إلزامي قبل التشغيل)

```bash
# في .env (أو انسخ من .env.monitoring.example)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=VerySecurePassword123!

# تحقق من أن المتغيرات موجودة
echo $GRAFANA_ADMIN_PASSWORD
```

⚠️ **لا تستخدم admin/admin في الإنتاج!**

#### تفعيل HTTPS (عبر nginx)

```nginx
# في nginx.conf
location /grafana/ {
    proxy_pass http://grafana:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### 2. تأمين Prometheus

#### إضافة Basic Authentication

```yaml
# في prometheus.yml
scrape_configs:
  - job_name: 'aapanel'
    basic_auth:
      username: 'monitoring_user'
      password: 'secure_password'
```

#### تقييد الوصول عبر nginx

```nginx
location /prometheus/ {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://prometheus:9090/;
}
```

### 3. أفضل الممارسات

1. **غيّر جميع كلمات المرور الافتراضية**
   ```bash
   GRAFANA_ADMIN_PASSWORD=secure_password_here
   ```

2. **استخدم HTTPS في الإنتاج**
   - SSL/TLS عبر nginx
   - Certbot للشهادات المجانية

3. **قيّد الوصول للمنافذ (إلزامي في الإنتاج)**
   
   **الطريقة الصحيحة**:
   ```yaml
   # في docker-compose.yml - احذف ports للإنتاج
   prometheus:
     # ports:  # ⚠️ أزل هذا السطر بالكامل
     #   - "9090:9090"
     # ... بقية الإعدادات
   
   grafana:
     # ports:  # ⚠️ أزل هذا السطر بالكامل
     #   - "3000:3000"
     # ... بقية الإعدادات
   ```
   
   **ثم استخدم nginx reverse proxy**:
   ```nginx
   # في nginx.conf
   location /prometheus/ {
       auth_basic "Monitoring Access";
       auth_basic_user_file /etc/nginx/.htpasswd;
       proxy_pass http://prometheus:9090/;
   }
   
   location /grafana/ {
       proxy_pass http://grafana:3000/;
       proxy_set_header Host $host;
   }
   ```

4. **فعّل Audit Logging**
   ```yaml
   # في Grafana environment
   - GF_LOG_MODE=console file
   - GF_LOG_LEVEL=info
   ```

---

## 📊 إحصائيات الأداء

### استهلاك الموارد (Typical)

| الخدمة | CPU | RAM | Disk (15d retention) |
|--------|-----|-----|---------------------|
| Prometheus | ~50-100m | ~200-400 MB | ~2-5 GB |
| Grafana | ~10-50m | ~100-200 MB | ~100-500 MB |

### Retention Policy

- **Prometheus**: 15 يوم (قابل للتعديل)
  ```yaml
  command:
    - '--storage.tsdb.retention.time=15d'
  ```

- **Grafana**: لا حد (SQLite database)

---

## 🔄 التحديث والصيانة

### تحديث Prometheus

```bash
# 1. غيّر الإصدار في docker-compose.yml
image: prom/prometheus:v2.49.0  # من v2.48.0

# 2. أعد البناء
docker-compose up -d prometheus

# 3. تحقق من النسخة
curl http://localhost:9090/api/v1/status/buildinfo
```

### تحديث Grafana

```bash
# 1. غيّر الإصدار
image: grafana/grafana:10.3.0  # من 10.2.2

# 2. أعد البناء
docker-compose up -d grafana

# 3. تحقق من النسخة
curl http://localhost:3000/api/health
```

### النسخ الاحتياطي

```bash
# Backup Prometheus data
docker run --rm \
  -v aapanel_prometheus_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz /data

# Backup Grafana data
docker run --rm \
  -v aapanel_grafana_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/grafana-$(date +%Y%m%d).tar.gz /data
```

---

## 📚 موارد إضافية

### الوثائق الرسمية

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)

### أمثلة Dashboards

- [Grafana Dashboard Gallery](https://grafana.com/grafana/dashboards/)
- [Prometheus Exporters](https://prometheus.io/docs/instrumenting/exporters/)

### المجتمع

- [Prometheus Community](https://prometheus.io/community/)
- [Grafana Community](https://community.grafana.com/)

---

## ✅ Checklist النشر

- [ ] تم تثبيت Prometheus بنجاح
- [ ] تم تثبيت Grafana بنجاح
- [ ] تم تعيين GRAFANA_ADMIN_USER و GRAFANA_ADMIN_PASSWORD في .env ⚠️
- [ ] `/health/metrics` يعمل ويعيد بيانات صحيحة
- [ ] Prometheus يجمع metrics من التطبيق
- [ ] Grafana dashboard يظهر البيانات بشكل صحيح
- [ ] تم استخدام كلمة مرور قوية (12+ حرف) في الإنتاج
- [ ] تم تفعيل HTTPS (في الإنتاج)
- [ ] تم تقييد الوصول للمنافذ - إزالة port mappings (في الإنتاج)
- [ ] تم إعداد nginx reverse proxy (في الإنتاج)
- [ ] تم إعداد النسخ الاحتياطي الدوري

---

## 📞 الحصول على المساعدة

إذا واجهت أي مشاكل:

1. راجع قسم [استكشاف الأخطاء](#استكشاف-الأخطاء)
2. افحص logs: `docker-compose logs [service]`
3. تحقق من health endpoints:
   - Prometheus: `http://localhost:9090/-/healthy`
   - Grafana: `http://localhost:3000/api/health`

---

**آخر تحديث**: 1 أكتوبر 2025  
**الحالة**: ✅ جاهز للإنتاج  
**الإصدار**: 1.0.0

---

<div align="center">

**نظام المراقبة جاهز! 🎉**

</div>
