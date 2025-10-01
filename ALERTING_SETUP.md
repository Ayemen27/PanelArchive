# 🔔 دليل إعداد نظام التنبيهات - Alertmanager Setup Guide

## نظرة عامة - Overview

تم إعداد نظام تنبيهات شامل لـ aaPanel باستخدام **Prometheus Alertmanager**. هذا النظام يوفر:

- ✅ تنبيهات فورية عند حدوث مشاكل (CPU, Memory, Disk, Database, Redis)
- ✅ إشعارات عبر Slack و Email
- ✅ قواعد تنبيه قابلة للتخصيص
- ✅ تجميع وتنظيم التنبيهات لتجنب الإزعاج
- ✅ حل تلقائي للتنبيهات عند عودة الأمور للطبيعي

---

## 📋 جدول المحتويات - Table of Contents

1. [البنية التقنية](#البنية-التقنية---architecture)
2. [قائمة Alert Rules](#قائمة-alert-rules---alert-rules-list)
3. [تكوين Slack Integration](#تكوين-slack-integration)
4. [تكوين Email/SMTP](#تكوين-emailsmtp)
5. [خطوات التثبيت](#خطوات-التثبيت---installation-steps)
6. [اختبار التنبيهات](#اختبار-التنبيهات---testing-alerts)
7. [استكشاف الأخطاء](#استكشاف-الأخطاء---troubleshooting)
8. [Best Practices](#best-practices---أفضل الممارسات)
9. [الأمان](#الأمان---security)

---

## 🏗️ البنية التقنية - Architecture

### مخطط النظام - System Diagram

```
┌─────────────────────────────────────────────────┐
│                   aaPanel App                    │
│            (Port 5000)                           │
│         /health/metrics endpoint                 │
│         - CPU, Memory, Disk                      │
│         - Database health                        │
│         - Redis health                           │
└────────────────┬────────────────────────────────┘
                 │ Scrapes metrics every 10s
                 ↓
┌─────────────────────────────────────────────────┐
│                  Prometheus                      │
│            (Port 9090)                           │
│         - Collects metrics                       │
│         - Evaluates alert rules                  │
│         - Stores time-series data                │
└────────────────┬────────────────────────────────┘
                 │ Sends alerts when rules match
                 ↓
┌─────────────────────────────────────────────────┐
│                 Alertmanager                     │
│            (Port 9093)                           │
│         - Groups alerts                          │
│         - Routes to receivers                    │
│         - Manages alert lifecycle                │
└────────┬───────────────────────┬─────────────────┘
         │                       │
         │ Slack                 │ Email
         ↓                       ↓
┌──────────────────┐   ┌──────────────────┐
│  Slack Channel   │   │  Email Inbox     │
│   #alerts        │   │  admin@domain    │
└──────────────────┘   └──────────────────┘
```

### المكونات الرئيسية - Main Components

1. **prometheus-rules.yml**: ملف قواعد التنبيه (10 قواعد)
2. **alertmanager.yml**: تكوين Alertmanager (routing, receivers, inhibition)
3. **Prometheus**: محرك التنبيهات (يقيّم القواعد كل 30 ثانية)
4. **Alertmanager**: مدير التنبيهات (يرسل الإشعارات)

### ملاحظات مهمة - Important Notes

#### Environment Variable Expansion - توسيع متغيرات البيئة

**⚠️ Critical Configuration:**

Alertmanager يستخدم العلم `--config.expand-env=true` لتوسيع متغيرات البيئة في ملف التكوين. هذا ضروري للأسباب التالية:

- **Slack Webhook URL**: متغير `${SLACK_WEBHOOK_URL}` يتم توسيعه من ملف `.env`
- **SMTP Credentials**: متغيرات SMTP (`${SMTP_HOST}`, `${SMTP_USERNAME}`, `${SMTP_PASSWORD}`) يتم توسيعها من ملف `.env`
- **Email Addresses**: متغيرات `${ALERT_EMAIL_FROM}` و `${ALERT_EMAIL_TO}` يتم توسيعها من ملف `.env`

**بدون هذا العلم:**
- سيظهر Alertmanager الأخطاء مثل: `invalid webhook URL: ${SLACK_WEBHOOK_URL}`
- لن يستطيع إرسال الإشعارات إلى Slack أو Email
- ستبقى المتغيرات كنصوص literal بدلاً من توسيعها إلى القيم الفعلية

**التكوين في docker-compose.yml:**
```yaml
alertmanager:
  command:
    - '--config.file=/etc/alertmanager/alertmanager.yml'
    - '--config.expand-env=true'  # ← ضروري لتوسيع متغيرات البيئة
    - '--storage.path=/alertmanager'
```

**التحقق من التكوين:**
```bash
# التأكد من أن Alertmanager يستخدم expand-env
docker-compose logs alertmanager | grep "expand-env"
```

---

## 📊 قائمة Alert Rules - Alert Rules List

### 1. Resource Usage Alerts - تنبيهات استخدام الموارد

| Alert Name | Condition | Duration | Severity | Description |
|------------|-----------|----------|----------|-------------|
| **HighCPUUsage** | CPU > 80% | 5 minutes | warning | استخدام CPU مرتفع |
| **CriticalCPUUsage** | CPU > 95% | 5 minutes | critical | استخدام CPU حرج |
| **HighMemoryUsage** | Memory > 90% | 5 minutes | warning | استخدام ذاكرة مرتفع |
| **CriticalMemoryUsage** | Memory > 95% | 5 minutes | critical | استخدام ذاكرة حرج |
| **HighDiskUsage** | Disk > 85% | 1 minute | warning | مساحة القرص منخفضة |
| **CriticalDiskUsage** | Disk > 95% | 1 minute | critical | مساحة القرص حرجة |

### 2. Service Availability Alerts - تنبيهات توفر الخدمة

| Alert Name | Condition | Duration | Severity | Description |
|------------|-----------|----------|----------|-------------|
| **ApplicationDown** | up{job="aapanel"} == 0 | 1 minute | critical | التطبيق متوقف |
| **DatabaseUnhealthy** | aapanel_db_healthy == 0 | 2 minutes | critical | قاعدة البيانات غير متاحة |
| **RedisUnhealthy** | aapanel_redis_healthy == 0 | 2 minutes | critical | Redis غير متاح |

### 3. Performance Alerts - تنبيهات الأداء

| Alert Name | Condition | Duration | Severity | Description |
|------------|-----------|----------|----------|-------------|
| **HighDatabaseResponseTime** | response_time > 5s | 5 minutes | warning | وقت استجابة DB بطيء |

### Alert States - حالات التنبيه

- **Pending** (معلق): الشرط متحقق لكن لم تمر المدة المطلوبة (for duration)
- **Firing** (نشط): الشرط متحقق وتم إرسال التنبيه
- **Resolved** (محلول): المشكلة تم حلها وعادت الأمور للطبيعي

---

## 💬 تكوين Slack Integration

### الخطوة 1: إنشاء Slack App

1. اذهب إلى **Slack API Console**: https://api.slack.com/apps
2. انقر على **"Create New App"**
3. اختر **"From scratch"**
4. أدخل:
   - **App Name**: `aaPanel Alerts` (أو أي اسم تريده)
   - **Workspace**: اختر workspace الخاص بك
5. انقر **"Create App"**

### الخطوة 2: تفعيل Incoming Webhooks

1. في القائمة الجانبية، اختر **"Incoming Webhooks"**
2. قم بتفعيل **"Activate Incoming Webhooks"** (التبديل إلى ON)
3. انتقل لأسفل وانقر على **"Add New Webhook to Workspace"**
4. اختر القناة التي تريد إرسال التنبيهات إليها (مثال: `#alerts`)
5. انقر **"Allow"**

### الخطوة 3: نسخ Webhook URL

1. ستظهر لك قائمة بـ Webhook URLs
2. انسخ الـ URL (يبدأ بـ `https://hooks.slack.com/services/...`)
3. احتفظ به للخطوة التالية

### الخطوة 4: إضافة Webhook إلى .env

```bash
# في ملف .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

### اختبار Slack Webhook

```bash
# اختبار يدوي للـ webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🔔 Test alert from aaPanel!"}' \
  YOUR_SLACK_WEBHOOK_URL
```

إذا ظهرت الرسالة في قناة Slack، فإن التكوين صحيح! ✅

---

## 📧 تكوين Email/SMTP

### خيارات SMTP - SMTP Options

يدعم Alertmanager أي خادم SMTP. إليك أمثلة لأشهر الخدمات:

### 1. Gmail Configuration

```bash
# في ملف .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # ليس كلمة المرور العادية!
SMTP_STARTTLS_ENABLE=true
ALERT_EMAIL_FROM=your-email@gmail.com
ALERT_EMAIL_TO=admin@yourdomain.com
```

#### خطوات الحصول على Gmail App Password:

1. اذهب إلى **Google Account Security**: https://myaccount.google.com/security
2. قم بتفعيل **2-Step Verification** (إذا لم يكن مفعلاً)
3. اذهب إلى **App Passwords**: https://myaccount.google.com/apppasswords
4. اختر:
   - **App**: `Mail`
   - **Device**: `Other (Custom name)` → اكتب `aaPanel Alerts`
5. انقر **"Generate"**
6. انسخ كلمة المرور المكونة من 16 حرف (بدون مسافات)
7. استخدمها كـ `SMTP_PASSWORD` في `.env`

⚠️ **مهم**: لا تستخدم كلمة مرور حسابك العادية! استخدم App Password فقط.

### 2. SendGrid Configuration

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_STARTTLS_ENABLE=true
ALERT_EMAIL_FROM=alerts@yourdomain.com
ALERT_EMAIL_TO=admin@yourdomain.com
```

**خطوات الحصول على SendGrid API Key:**
1. سجل في https://sendgrid.com (Free tier: 100 emails/day)
2. اذهب إلى **Settings** → **API Keys**
3. انقر **"Create API Key"**
4. اختر **"Full Access"** أو **"Mail Send"**
5. انسخ API Key واستخدمه كـ `SMTP_PASSWORD`

### 3. Mailgun Configuration

```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@mg.yourdomain.com
SMTP_PASSWORD=your-mailgun-smtp-password
SMTP_STARTTLS_ENABLE=true
ALERT_EMAIL_FROM=alerts@yourdomain.com
ALERT_EMAIL_TO=admin@yourdomain.com
```

**خطوات الحصول على Mailgun Credentials:**
1. سجل في https://www.mailgun.com (Free tier: 100 emails/day)
2. أضف domain أو استخدم sandbox domain
3. اذهب إلى **Sending** → **Domain Settings** → **SMTP Credentials**
4. استخدم Username و Password الظاهرين

### 4. Outlook/Office365 Configuration

```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_STARTTLS_ENABLE=true
ALERT_EMAIL_FROM=your-email@outlook.com
ALERT_EMAIL_TO=admin@yourdomain.com
```

### اختبار SMTP

```bash
# اختبار SMTP باستخدام Python
python3 << EOF
import smtplib
from email.mime.text import MIMEText

smtp_host = "smtp.gmail.com"
smtp_port = 587
username = "your-email@gmail.com"
password = "your-app-password"

msg = MIMEText("Test email from aaPanel Alertmanager")
msg['Subject'] = "Test Alert"
msg['From'] = username
msg['To'] = "admin@yourdomain.com"

server = smtplib.SMTP(smtp_host, smtp_port)
server.starttls()
server.login(username, password)
server.send_message(msg)
server.quit()
print("✅ Email sent successfully!")
EOF
```

---

## 🚀 خطوات التثبيت - Installation Steps

### 1. إعداد ملف .env

```bash
# نسخ ملف المثال
cp .env.alerting.example .env

# تحرير الملف وإضافة القيم الحقيقية
nano .env
# أو
vim .env
```

### 2. التحقق من الملفات المطلوبة

تأكد من وجود الملفات التالية:

```bash
ls -la | grep -E "(prometheus-rules|alertmanager\.yml)"
```

يجب أن تشاهد:
- ✅ `prometheus-rules.yml`
- ✅ `alertmanager.yml`
- ✅ `prometheus.yml` (محدّث)
- ✅ `docker-compose.yml` (محدّث)
- ✅ `.env`

### 3. التحقق من صحة YAML Syntax

```bash
# التحقق من prometheus-rules.yml
docker run --rm -v $(pwd):/workspace prom/prometheus:latest \
  promtool check rules /workspace/prometheus-rules.yml

# التحقق من prometheus.yml
docker run --rm -v $(pwd):/workspace prom/prometheus:latest \
  promtool check config /workspace/prometheus.yml

# التحقق من alertmanager.yml
docker run --rm -v $(pwd):/workspace prom/alertmanager:latest \
  amtool check-config /workspace/alertmanager.yml
```

### 4. تشغيل النظام

```bash
# إيقاف الخدمات الحالية (إذا كانت تعمل)
docker-compose down

# إعادة بناء وتشغيل جميع الخدمات
docker-compose up -d

# مشاهدة السجلات
docker-compose logs -f alertmanager prometheus
```

### 5. التحقق من الخدمات

```bash
# التحقق من حالة الخدمات
docker-compose ps

# يجب أن تشاهد:
# - aapanel_app (healthy)
# - aapanel_prometheus (healthy)
# - aapanel_alertmanager (healthy)
# - aapanel_grafana (healthy)
# - aapanel_postgres (healthy)
# - aapanel_redis (healthy)
```

### 6. الوصول للواجهات

- **Prometheus**: http://localhost:9090
  - اذهب إلى **Status** → **Rules** لرؤية قواعد التنبيه
  - اذهب إلى **Alerts** لرؤية التنبيهات النشطة
  
- **Alertmanager**: http://localhost:9093
  - اذهب إلى **Status** لرؤية التكوين
  - اذهب إلى **Alerts** لرؤية التنبيهات المرسلة

- **Grafana**: http://localhost:3000
  - يمكنك إضافة Alertmanager كـ datasource لعرض التنبيهات

---

## 🧪 اختبار التنبيهات - Testing Alerts

### 1. التحقق من تحميل القواعد

```bash
# عرض قواعد التنبيه في Prometheus
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | {alert: .name, state: .state}'
```

### 2. إجبار تنبيه CPU (للاختبار)

```bash
# إنشاء حمل CPU عالٍ لمدة 6 دقائق (يكفي لتفعيل التنبيه)
docker exec -it aapanel_app bash -c "
for i in {1..6}; do
  stress --cpu 4 --timeout 60s &
  echo 'Minute $i of 6...'
  sleep 60
done
"
```

⚠️ **ملاحظة**: هذا للاختبار فقط! لا تستخدمه في الإنتاج.

### 3. محاكاة توقف التطبيق

```bash
# إيقاف التطبيق مؤقتاً
docker-compose stop app

# انتظر دقيقة واحدة ثم تحقق من Alertmanager
# يجب أن يظهر تنبيه "ApplicationDown"

# إعادة تشغيل التطبيق
docker-compose start app
```

### 4. إرسال تنبيه يدوي إلى Alertmanager

```bash
# إرسال تنبيه اختباري مباشرة
curl -X POST http://localhost:9093/api/v1/alerts -H "Content-Type: application/json" -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "service": "aapanel",
      "instance": "test"
    },
    "annotations": {
      "summary": "This is a test alert",
      "description": "Testing Alertmanager integration"
    },
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "endsAt": "'$(date -u -d '+5 minutes' +%Y-%m-%dT%H:%M:%SZ)'"
  }
]'
```

### 5. التحقق من وصول الإشعارات

- **Slack**: تحقق من قناة #alerts (أو القناة التي اخترتها)
- **Email**: تحقق من inbox للبريد المحدد في `ALERT_EMAIL_TO`

---

## 🔧 استكشاف الأخطاء - Troubleshooting

### المشكلة 1: التنبيهات لا تُفعّل (Alerts Not Firing)

#### الأعراض:
- لا تظهر تنبيهات في Prometheus → Alerts
- الشروط متحققة لكن لا يوجد تنبيه

#### الحلول:

**1. تحقق من تحميل القواعد:**
```bash
# عرض القواعد المحملة
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].file'

# يجب أن تشاهد: /etc/prometheus/rules/prometheus-rules.yml
```

**2. تحقق من وجود الـ metrics:**
```bash
# تحقق من metrics التطبيق
curl http://localhost:5000/health/metrics | jq

# تحقق من metrics في Prometheus
curl -g 'http://localhost:9090/api/v1/query?query=up{job="aapanel"}'
```

**3. تحقق من سجلات Prometheus:**
```bash
docker-compose logs prometheus | grep -i "error\|warn"
```

**4. تحقق من syntax القواعد:**
```bash
docker exec -it aapanel_prometheus promtool check rules /etc/prometheus/rules/prometheus-rules.yml
```

### المشكلة 2: الإشعارات لا ترسل (Notifications Not Sent)

#### الأعراض:
- التنبيهات نشطة في Prometheus
- لكن لا تصل إشعارات في Slack أو Email

#### الحلول:

**1. تحقق من اتصال Alertmanager بـ Prometheus:**
```bash
# عرض حالة Alertmanager في Prometheus
curl http://localhost:9090/api/v1/alertmanagers | jq
```

**2. تحقق من سجلات Alertmanager:**
```bash
docker-compose logs alertmanager | tail -50
```

**3. تحقق من تكوين Alertmanager:**
```bash
# عرض التكوين
curl http://localhost:9093/api/v1/status | jq '.data.config'
```

**4. اختبار Slack Webhook يدوياً:**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test from Alertmanager"}' \
  $SLACK_WEBHOOK_URL
```

**5. اختبار SMTP:**
```bash
# استخدم swaks (SMTP test tool)
docker run --rm --network aapanel_network \
  catatnight/postfix \
  swaks --to $ALERT_EMAIL_TO \
        --from $ALERT_EMAIL_FROM \
        --server $SMTP_HOST:$SMTP_PORT \
        --auth LOGIN \
        --auth-user $SMTP_USERNAME \
        --auth-password $SMTP_PASSWORD \
        --tls
```

### المشكلة 3: متغيرات البيئة غير محملة

#### الأعراض:
- تظهر أخطاء مثل `${SLACK_WEBHOOK_URL}` في السجلات
- Alertmanager لا يستطيع قراءة المتغيرات

#### الحلول:

**1. تحقق من وجود .env:**
```bash
ls -la .env
```

**2. تحقق من تحميل .env في docker-compose:**
```bash
# يجب أن يحتوي على:
# env_file:
#   - .env
cat docker-compose.yml | grep -A2 "alertmanager:" | grep "env_file"
```

**3. أعد تشغيل Alertmanager:**
```bash
docker-compose restart alertmanager
docker-compose logs alertmanager
```

### المشكلة 4: الإشعارات متكررة جداً

#### الأعراض:
- تصل إشعارات كل دقيقة أو أقل
- إزعاج من كثرة التنبيهات

#### الحلول:

**1. زيادة `repeat_interval` في alertmanager.yml:**
```yaml
route:
  repeat_interval: 12h  # زد هذه القيمة (مثلاً: 24h)
```

**2. زيادة `group_interval`:**
```yaml
route:
  group_interval: 10m  # زد هذه القيمة
```

**3. تعديل thresholds في prometheus-rules.yml:**
```yaml
# مثلاً: زيادة CPU threshold
expr: aapanel_cpu_percent > 85  # بدلاً من 80
```

### المشكلة 5: التنبيهات لا تُحَل (Alerts Don't Resolve)

#### الأعراض:
- التنبيهات تظل نشطة حتى بعد حل المشكلة

#### الحلول:

**1. تحقق من `resolve_timeout`:**
```yaml
# في alertmanager.yml
global:
  resolve_timeout: 5m  # يمكن زيادتها إذا لزم الأمر
```

**2. تحقق من `send_resolved`:**
```yaml
# في alertmanager.yml → receivers
slack_configs:
  - send_resolved: true  # تأكد أنها true
```

**3. أعد تشغيل Prometheus:**
```bash
docker-compose restart prometheus
```

### المشكلة 6: Healthcheck فشل

#### الأعراض:
- `docker-compose ps` يظهر unhealthy

#### الحلول:

```bash
# تحقق من healthcheck يدوياً
docker exec -it aapanel_alertmanager wget --spider -q http://localhost:9093/-/healthy
echo $?  # يجب أن يكون 0

# إذا فشل، تحقق من السجلات
docker-compose logs alertmanager
```

---

## ✅ Best Practices - أفضل الممارسات

### 1. تخصيص Thresholds - Tuning Thresholds

**لا تستخدم القيم الافتراضية بشكل أعمى!** قم بتخصيصها حسب بيئتك:

```yaml
# ❌ سيء: استخدام نفس القيم لكل البيئات
expr: aapanel_cpu_percent > 80

# ✅ جيد: تخصيص حسب البيئة
# Production: 85%
# Staging: 90%
# Development: 95%
expr: aapanel_cpu_percent > 85
```

**كيف تحدد Thresholds المناسبة:**
1. راقب النظام لمدة أسبوع على الأقل
2. احسب p95 و p99 للمقاييس
3. ضع thresholds أعلى قليلاً من p95

### 2. تجنب Alert Fatigue - تجنب الإزعاج من التنبيهات

**المشكلة**: كثرة التنبيهات تؤدي إلى تجاهلها.

**الحلول**:

```yaml
# ✅ استخدم `for` duration مناسب
# لا تنبه على ارتفاع مؤقت لمدة ثواني
- alert: HighCPUUsage
  expr: aapanel_cpu_percent > 80
  for: 5m  # انتظر 5 دقائق قبل التنبيه

# ✅ استخدم inhibition rules
# لا ترسل warning إذا كان هناك critical
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
```

### 3. تنظيم القنوات - Channel Organization

**افصل التنبيهات حسب الأهمية:**

```yaml
routes:
  # Critical → قناة #critical-alerts + Email
  - match:
      severity: critical
    receiver: 'critical-team'
  
  # Warning → قناة #warnings
  - match:
      severity: warning
    receiver: 'warnings-channel'
  
  # Info → قناة #info (optional)
  - match:
      severity: info
    receiver: 'info-channel'
```

### 4. Annotations الوصفية - Descriptive Annotations

```yaml
# ❌ سيء: annotations غير واضحة
annotations:
  summary: "High CPU"
  description: "CPU is high"

# ✅ جيد: annotations واضحة وقابلة للتنفيذ
annotations:
  summary: "High CPU usage detected on aaPanel"
  description: "CPU usage is {{ $value }}% (threshold: 80%) for more than 5 minutes on {{ $labels.instance }}"
  impact: "Application performance may be degraded"
  action: "Check running processes with 'top' or 'htop', consider scaling resources"
  runbook: "https://wiki.company.com/runbooks/high-cpu"
```

### 5. Alert Labels - تسميات التنبيه

**استخدم labels منطقية للتجميع:**

```yaml
labels:
  severity: warning       # الأهمية
  service: aapanel       # الخدمة
  category: resources    # الفئة (resources, database, cache)
  team: platform         # الفريق المسؤول
  environment: production # البيئة
```

### 6. Testing in Staging - الاختبار في بيئة التطوير

**لا تختبر التنبيهات في الإنتاج مباشرة!**

1. اختبر في بيئة staging أولاً
2. تأكد من وصول الإشعارات
3. راجع مع الفريق قبل النشر

### 7. Documentation - التوثيق

**وثّق كل تنبيه:**

```markdown
# Alert: HighCPUUsage

## Description
يُفعّل عندما يتجاوز استخدام CPU نسبة 80% لمدة 5 دقائق.

## Impact
- أداء التطبيق قد يتدهور
- زمن الاستجابة قد يزيد
- قد يؤدي إلى timeout في الطلبات

## Actions
1. تحقق من العمليات الجارية: `top` أو `htop`
2. تحقق من السجلات: `docker-compose logs app`
3. إذا كان الحمل مشروعاً، قم بـ scale up
4. إذا كان هناك process عالق، قم بـ restart

## False Positives
- Backup jobs (يومياً الساعة 2 صباحاً)
- Data migration tasks
```

### 8. Regular Review - المراجعة الدورية

**راجع التنبيهات شهرياً:**

- ✅ هل هناك تنبيهات لم تُفعّل أبداً؟ (قد تكون thresholds عالية جداً)
- ✅ هل هناك تنبيهات تُفعّل كثيراً؟ (قد تكون thresholds منخفضة جداً)
- ✅ هل التنبيهات مفيدة؟ (actionable)
- ✅ هل الفريق يستجيب للتنبيهات؟

---

## 🔒 الأمان - Security

### 1. حماية Webhook URLs

```bash
# ❌ لا تشارك webhook URLs في:
# - Git repositories
# - Chat messages
# - Documentation عامة

# ✅ استخدم environment variables
# ✅ قيّد الوصول للـ .env file
chmod 600 .env

# ✅ استخدم secrets management في الإنتاج
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

### 2. حماية SMTP Credentials

```bash
# ❌ لا تستخدم كلمة مرور حسابك الرئيسي
# ✅ استخدم App Passwords (Gmail, Outlook)
# ✅ استخدم API Keys (SendGrid, Mailgun)

# ✅ قم بتدوير credentials دورياً
# - كل 90 يوم على الأقل
```

### 3. Restrict Access - تقييد الوصول

```nginx
# في nginx reverse proxy
location /prometheus/ {
    auth_basic "Prometheus";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:9090/;
}

location /alertmanager/ {
    auth_basic "Alertmanager";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:9093/;
}
```

### 4. Network Isolation - عزل الشبكة

```yaml
# في docker-compose.yml
networks:
  aapanel_network:
    driver: bridge
    internal: false  # أو true للعزل الكامل

# في الإنتاج، استخدم:
# - Private subnets
# - Security groups
# - Firewalls
```

### 5. Audit Logging - سجلات المراجعة

```bash
# تفعيل logging في Alertmanager
docker-compose logs alertmanager > alertmanager_audit.log

# مراجعة دورية للسجلات
grep "notification" alertmanager_audit.log
grep "silenced" alertmanager_audit.log
```

### 6. Backup Configuration - نسخ احتياطي للتكوين

```bash
# نسخ احتياطي للملفات الحساسة
tar -czf alerting-backup-$(date +%Y%m%d).tar.gz \
  prometheus-rules.yml \
  alertmanager.yml \
  prometheus.yml

# تخزين في مكان آمن
# - S3 bucket (encrypted)
# - Encrypted USB drive
# - Password-protected archive
```

### 7. Security Checklist - قائمة التحقق الأمنية

قبل النشر في الإنتاج، تأكد من:

- [ ] `.env` في `.gitignore`
- [ ] SMTP passwords مشفرة
- [ ] Webhook URLs سرية
- [ ] File permissions محدودة (600)
- [ ] Basic auth مفعّل للواجهات
- [ ] TLS/SSL مفعّل للـ SMTP
- [ ] Network isolated
- [ ] Audit logging مفعّل
- [ ] Backup strategy موجودة

---

## 📚 موارد إضافية - Additional Resources

### Official Documentation

- **Prometheus Alerting**: https://prometheus.io/docs/alerting/latest/overview/
- **Alertmanager**: https://prometheus.io/docs/alerting/latest/alertmanager/
- **PromQL**: https://prometheus.io/docs/prometheus/latest/querying/basics/

### Tools

- **Prometheus**: https://prometheus.io/
- **Alertmanager**: https://github.com/prometheus/alertmanager
- **amtool**: https://github.com/prometheus/alertmanager#amtool
- **promtool**: https://prometheus.io/docs/prometheus/latest/command-line/promtool/

### Community

- **Prometheus Community**: https://prometheus.io/community/
- **Slack**: https://slack.cncf.io (channel: #prometheus)

---

## 🤝 الدعم - Support

إذا واجهت مشاكل:

1. راجع قسم [استكشاف الأخطاء](#استكشاف-الأخطاء---troubleshooting)
2. تحقق من السجلات: `docker-compose logs alertmanager prometheus`
3. راجع التوثيق الرسمي
4. افتح issue في GitHub repository

---

## 📝 Changelog

### Version 1.0.0 (2025-10-01)
- ✅ إعداد أولي لنظام التنبيهات
- ✅ 10 alert rules (CPU, Memory, Disk, Database, Redis)
- ✅ Slack و Email integration
- ✅ Inhibition rules
- ✅ توثيق شامل

---

**تم إعداد هذا النظام بعناية لضمان موثوقية عالية وسهولة في الاستخدام. 🚀**
