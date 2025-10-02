# 🔧 دليل استكشاف الأخطاء وإصلاحها - aaPanel

## 📋 جدول المحتويات
1. [مشاكل التشغيل الأساسية](#مشاكل-التشغيل-الأساسية)
2. [مشاكل البيئة والإعدادات](#مشاكل-البيئة-والإعدادات)
3. [مشاكل قاعدة البيانات](#مشاكل-قاعدة-البيانات)
4. [مشاكل Docker](#مشاكل-docker)
5. [مشاكل النشر](#مشاكل-النشر)
6. [مشاكل الأداء](#مشاكل-الأداء)
7. [مشاكل الأمان](#مشاكل-الأمان)
8. [مشاكل المراقبة](#مشاكل-المراقبة)
9. [مشاكل Logging](#مشاكل-logging)
10. [مشاكل التنبيهات](#مشاكل-التنبيهات)
11. [مشاكل Blue-Green Deployment](#مشاكل-blue-green-deployment)

---

## 🚨 مشاكل التشغيل الأساسية

### المشكلة: التطبيق لا يبدأ

**الأعراض**:
```
Error: [Errno 98] Address already in use
```

**الحل**:
```bash
# 1. تحقق من المنفذ المستخدم
cat data/port.pl

# 2. ابحث عن العملية المستخدمة للمنفذ
sudo lsof -i :5000

# 3. أوقف العملية
sudo kill -9 <PID>

# أو استخدم منفذ آخر
echo "5001" > data/port.pl
python runserver.py
```

---

### المشكلة: خطأ في الاستيراد (Import Error)

**الأعراض**:
```
ModuleNotFoundError: No module named 'BTPanel'
```

**الحل**:
```bash
# 1. تحقق من المسار الحالي
pwd
# يجب أن يكون في مجلد المشروع

# 2. تحقق من وجود المجلد
ls -la BTPanel/

# 3. تحقق من sys.path في Python
python -c "import sys; print('\n'.join(sys.path))"

# 4. أضف المسار يدوياً إن لزم
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python runserver.py
```

---

### المشكلة: خطأ في الأذونات (Permission Denied)

**الأعراض**:
```
PermissionError: [Errno 13] Permission denied: 'data/port.pl'
```

**الحل**:
```bash
# 1. تحقق من الأذونات
ls -la data/

# 2. غيّر الملكية
sudo chown -R $USER:$USER .

# 3. غيّر الأذونات
chmod -R 755 .
chmod 644 data/*

# 4. لا تشغل كـ root!
python runserver.py  # ليس sudo python
```

---

## ⚙️ مشاكل البيئة والإعدادات

### المشكلة: المتغيرات البيئية لا تُقرأ

**الأعراض**:
```python
KeyError: 'DATABASE_URL'
```

**الحل**:
```bash
# 1. تحقق من وجود .env
ls -la .env

# 2. تحقق من المحتوى
cat .env

# 3. حمّل المتغيرات يدوياً
export $(cat .env | xargs)

# 4. تحقق من التحميل
echo $DATABASE_URL

# 5. أو استخدم python-dotenv
pip install python-dotenv
```

```python
# في بداية runserver.py
from dotenv import load_dotenv
load_dotenv()
```

---

### المشكلة: البيئة الخاطئة مُكتشفة

**الأعراض**:
- Replit يُكتشف كـ production
- VPS يُكتشف كـ development

**الحل**:
```bash
# 1. تحقق من environment_detector.py
python environment_detector.py

# 2. اضبط المتغير يدوياً
export ENVIRONMENT=development
# أو
export ENVIRONMENT=production

# 3. أضف للـ .env
echo "ENVIRONMENT=development" >> .env

# 4. أعد التشغيل
python runserver.py
```

---

### المشكلة: الإعدادات الخاطئة تُحمّل

**الأعراض**:
- التطبيق يستخدم قاعدة بيانات خاطئة
- المنفذ خاطئ

**الحل**:
```python
# 1. افحص config_factory.py
from config_factory import get_config

config = get_config()
print(f"Environment: {config.ENVIRONMENT}")
print(f"Database: {config.SQLALCHEMY_DATABASE_URI}")
print(f"Port: {config.PORT}")

# 2. تحقق من الأولوية
# المتغير البيئي > الإعدادات الافتراضية

# 3. أعد بناء التطبيق
python runserver.py
```

---

## 💾 مشاكل قاعدة البيانات

### المشكلة: فشل الاتصال بقاعدة البيانات

**الأعراض**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**الحل**:
```bash
# للـ PostgreSQL
# 1. تحقق من DATABASE_URL
echo $DATABASE_URL

# 2. اختبر الاتصال
psql $DATABASE_URL -c "SELECT version();"

# 3. تحقق من الخادم
pg_isready -h <host> -p <port>

# 4. تحقق من الأذونات
# تأكد أن المستخدم له صلاحيات

# للـ SQLite
# 1. تحقق من المسار
ls -la dev.db

# 2. تحقق من الأذونات
chmod 644 dev.db

# 3. أنشئ قاعدة جديدة إن لزم
python -c "from BTPanel import db; db.create_all()"
```

---

### المشكلة: فشل Migration

**الأعراض**:
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxx'
```

**الحل**:
```bash
# 1. تحقق من حالة migrations
alembic current

# 2. راجع سجل migrations
alembic history

# 3. ارجع للإصدار السابق
alembic downgrade -1

# 4. أو ابدأ من الصفر (خطر!)
# احذف جداول alembic_version
psql $DATABASE_URL -c "DROP TABLE IF EXISTS alembic_version;"

# 5. أعد الـ migrations
alembic stamp head
alembic upgrade head
```

---

### المشكلة: بيانات تالفة

**الأعراض**:
- نتائج غير متوقعة
- أخطاء في القراءة/الكتابة

**الحل**:
```bash
# 1. خذ نسخة احتياطية فوراً! (SHA-256 + HMAC)
python backups/backup_manager.py

# أو استخدام pg_dump
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. تحقق من سلامة DB
# للـ PostgreSQL
psql $DATABASE_URL -c "VACUUM ANALYZE;"

# 3. استعد من آخر نسخة احتياطية صحيحة
python backups/backup_manager.py --restore backup_latest.tar.gz
# أو
psql $DATABASE_URL < backup_20250930_120000.sql

# 4. راجع الكود الذي سبب المشكلة
```

---

## 🐳 مشاكل Docker

### المشكلة: فشل بناء الصورة

**الأعراض**:
```
ERROR [5/5] RUN pip install -r requirements.txt
```

**الحل**:
```bash
# 1. نظف الـ cache
docker system prune -a

# 2. استخدم --no-cache
docker build --no-cache -t aapanel:latest .

# 3. تحقق من requirements.txt
cat requirements.txt

# 4. اختبر التثبيت محلياً
pip install -r requirements.txt

# 5. راجع Dockerfile
cat Dockerfile
```

---

### المشكلة: الحاوية تتوقف فوراً

**الأعراض**:
```bash
docker ps -a
# الحالة: Exited (1) 2 seconds ago
```

**الحل**:
```bash
# 1. افحص السجلات
docker logs <container-id>

# 2. شغل بوضع interactive للتشخيص
docker run -it aapanel:latest /bin/bash

# 3. تحقق من CMD/ENTRYPOINT
docker inspect aapanel:latest | grep -A5 Cmd

# 4. اختبر الأمر يدوياً
docker run -it aapanel:latest python runserver.py
```

---

### المشكلة: الحاوية لا تتصل بالشبكة

**الأعراض**:
- لا يمكن الوصول للتطبيق من المتصفح
- الحاوية لا تتصل بـ DB

**الحل**:
```bash
# 1. تحقق من المنافذ
docker ps
# تأكد من PORTS column

# 2. تحقق من port mapping
docker run -p 5000:5000 aapanel:latest

# 3. افحص الشبكة
docker network ls
docker network inspect bridge

# 4. في docker-compose
# تأكد من ports section
docker-compose config
```

---

## 🚀 مشاكل النشر

### المشكلة: فشل SSH في GitHub Actions

**الأعراض**:
```
Permission denied (publickey)
```

**الحل**:
```bash
# 1. تحقق من SSH key في GitHub Secrets
# Settings > Secrets > VPS_SSH_KEY

# 2. تأكد من صحة المفتاح
ssh-keygen -l -f ~/.ssh/id_rsa.pub

# 3. تحقق من authorized_keys على VPS
cat ~/.ssh/authorized_keys

# 4. أضف المفتاح العام للـ VPS
ssh-copy-id user@vps-ip

# 5. اختبر الاتصال
ssh -i ~/.ssh/id_rsa user@vps-ip
```

---

### المشكلة: فشل Health Check

**الأعراض**:
```
Health check failed: GET /health returned 500
```

**الحل**:
```bash
# 1. اختبر endpoint محلياً
curl http://localhost:5000/health

# 2. افحص السجلات
tail -f logs/error.log

# 3. تحقق من /health/live و /health/ready
curl http://localhost:5000/health/live
curl http://localhost:5000/health/ready

# 4. راجع الكود
# تأكد من endpoints موجودة وتعمل
```

---

### المشكلة: Rollback لا يعمل

**الأعراض**:
- النسخة القديمة لا تعود
- خطأ في Blue-Green switch

**الحل**:
```bash
# 1. تحقق من النسخ المتاحة
docker images | grep aapanel

# 2. شغل النسخة القديمة يدوياً
docker run -p 5000:5000 aapanel:v1.0.0

# 3. راجع سكريبت rollback
cat scripts/rollback.sh

# 4. اختبر التبديل يدوياً
./scripts/switch_version.sh v1.0.0
```

---

## ⚡ مشاكل الأداء

### المشكلة: التطبيق بطيء

**الأعراض**:
- وقت استجابة طويل
- استهلاك CPU/Memory عالي

**الحل**:
```bash
# 1. راقب الموارد
top
htop
docker stats

# 2. افحص اتصالات DB
# تحقق من connection pooling
python -c "from sqlalchemy import create_engine; 
engine = create_engine('$DATABASE_URL'); 
print(engine.pool.status())"

# 3. راجع Gunicorn workers
cat runconfig.py
# زد عدد workers

# 4. استخدم profiling
pip install py-spy
py-spy record -o profile.svg -- python runserver.py

# 5. راجع nginx caching
cat /etc/nginx/sites-available/aapanel
```

---

### المشكلة: استهلاك ذاكرة عالي

**الأعراض**:
```
MemoryError: out of memory
```

**الحل**:
```bash
# 1. راقب الذاكرة
free -h
docker stats

# 2. قلل workers
# في runconfig.py
workers = 2  # بدلاً من 4

# 3. أضف limits في Docker
docker run -m 512m aapanel:latest

# 4. في docker-compose.yml
services:
  app:
    mem_limit: 512m
    
# 5. راجع memory leaks
pip install memory_profiler
python -m memory_profiler runserver.py
```

---

## 🔒 مشاكل الأمان

### المشكلة: SSL لا يعمل

**الأعراض**:
```
SSL certificate problem: unable to get local issuer certificate
```

**الحل**:
```bash
# 1. تحقق من الشهادة
sudo certbot certificates

# 2. جدد الشهادة
sudo certbot renew --dry-run
sudo certbot renew

# 3. تحقق من nginx config
sudo nginx -t
cat /etc/nginx/sites-available/aapanel

# 4. راجع المسارات
ls -la /etc/letsencrypt/live/yourdomain.com/

# 5. أعد تشغيل nginx
sudo systemctl restart nginx
```

---

### المشكلة: تحذيرات أمنية

**الأعراض**:
```
Security vulnerability detected in package X
```

**الحل**:
```bash
# 1. افحص الثغرات
pip-audit
# أو
safety check

# 2. حدّث الحزم
pip install --upgrade package-name

# 3. راجع requirements.txt
cat requirements.txt

# 4. ثبّت إصدارات آمنة
pip install package-name==safe-version

# 5. أعد بناء Docker image
docker build -t aapanel:latest .
```

---

### المشكلة: Fail2Ban لا يحمي

**الأعراض**:
- هجمات brute force مستمرة
- لا يتم حظر IPs

**الحل**:
```bash
# 1. تحقق من حالة Fail2Ban
sudo systemctl status fail2ban

# 2. راجع jails
sudo fail2ban-client status

# 3. افحص السجلات
sudo tail -f /var/log/fail2ban.log

# 4. اختبر القواعد
sudo fail2ban-client set sshd banip 192.168.1.100

# 5. راجع التكوين
cat /etc/fail2ban/jail.local
```

---

## 📊 مشاكل المراقبة

### المشكلة: Prometheus لا يجمع metrics

**الأعراض**:
- Dashboard في Grafana فارغ
- "No data" في Prometheus
- Targets تظهر "DOWN"

**الحل**:
```bash
# 1. تحقق من صحة Prometheus
curl http://localhost:9090/-/healthy

# 2. تحقق من targets
curl http://localhost:9090/api/v1/targets

# 3. تحقق من /health/metrics في التطبيق
curl http://localhost:5000/health/metrics

# 4. افحص prometheus.yml
cat prometheus.yml

# 5. تحقق من logs
docker-compose logs prometheus

# 6. أعد تشغيل Prometheus
docker-compose restart prometheus

# 7. تحقق من Docker network
docker network inspect aapanel_network
```

---

### المشكلة: Grafana لا تعرض البيانات

**الأعراض**:
- Dashboard يفتح لكن بدون بيانات
- "Bad Gateway" أو "Connection refused"

**الحل**:
```bash
# 1. تحقق من datasource في Grafana
# افتح: Configuration > Data Sources > Prometheus > Test

# 2. تحقق من اتصال Prometheus
docker exec -it aapanel_grafana ping prometheus

# 3. تحقق من URL datasource
# يجب أن يكون: http://prometheus:9090

# 4. افحص logs
docker-compose logs grafana

# 5. تحقق من credentials
echo $GRAFANA_ADMIN_USER
echo $GRAFANA_ADMIN_PASSWORD

# 6. أعد تشغيل Grafana
docker-compose restart grafana
```

---

### المشكلة: Health endpoints لا تعمل

**الأعراض**:
```
curl: (7) Failed to connect to localhost port 5000
```

**الحل**:
```bash
# 1. تحقق من أن التطبيق يعمل
docker-compose ps app

# 2. اختبر endpoints
curl http://localhost:5000/health
curl http://localhost:5000/health/live
curl http://localhost:5000/health/ready
curl http://localhost:5000/health/metrics

# 3. تحقق من port mapping
docker port aapanel_app

# 4. افحص logs التطبيق
docker-compose logs app | grep -i "health"

# 5. تحقق من الكود
# تأكد من وجود health_routes في التطبيق
```

---

### المشكلة: مشاكل في Dashboards

**الأعراض**:
- Dashboard لا يحمل
- Panels فارغة
- أخطاء في queries

**الحل**:
```bash
# 1. تحقق من Dashboard provisioning
docker-compose exec grafana ls -la /etc/grafana/provisioning/dashboards/

# 2. تحقق من Dashboard JSON
cat grafana-dashboard-aapanel.json

# 3. اختبر PromQL queries يدوياً
curl -g 'http://localhost:9090/api/v1/query?query=aapanel_cpu_percent'

# 4. أعد تحميل Dashboard
# في Grafana: Dashboard Settings > JSON Model > Save

# 5. تحقق من logs
docker-compose logs grafana | grep -i "dashboard"

# 6. أعد إنشاء Dashboard من الملف
# احذف Dashboard القديم وأعد تشغيل Grafana
docker-compose restart grafana
```

---

## 📝 مشاكل Logging

### المشكلة: Loki لا يستقبل logs

**الأعراض**:
- لا توجد logs في Grafana Explore
- Promtail يعمل لكن لا بيانات

**الحل**:
```bash
# 1. تحقق من صحة Loki
docker-compose ps loki

# 2. اختبر Loki API
curl http://loki:3100/ready
# من داخل container:
docker exec -it aapanel_app curl http://loki:3100/ready

# 3. تحقق من logs
docker-compose logs loki | tail -50

# 4. افحص التكوين
docker-compose exec loki cat /etc/loki/local-config.yaml

# 5. تحقق من retention policy
# في loki-config.yml:
# retention_period: 168h

# 6. أعد تشغيل Loki
docker-compose restart loki

# 7. تحقق من Docker volumes
docker volume inspect aapanel_loki_data
```

---

### المشكلة: Promtail لا يرسل logs

**الأعراض**:
- Promtail targets فارغة
- "failed to get docker container info"

**الحل**:
```bash
# 1. تحقق من حالة Promtail
docker-compose ps promtail

# 2. تحقق من targets
curl http://localhost:9080/targets

# 3. افحص logs
docker-compose logs promtail | tail -50

# 4. تحقق من Docker socket mount
docker inspect aapanel_promtail | grep -A 5 "docker.sock"

# يجب أن ترى:
# /var/run/docker.sock:/var/run/docker.sock:ro

# 5. تحقق من volumes
docker inspect aapanel_promtail | grep -A 10 Mounts

# 6. تحقق من صلاحيات logs/
ls -la logs/

# 7. أعد تشغيل Promtail
docker-compose restart promtail

# 8. تحقق من promtail-config.yml
cat promtail-config.yml
```

---

### المشكلة: مشاكل في البحث في logs

**الأعراض**:
- استعلامات LogQL لا تعيد نتائج
- "No data" في Grafana Explore

**الحل**:
```bash
# 1. اختبر LogQL query بسيطة
# في Grafana Explore:
{job="aapanel"}

# 2. تحقق من labels المتاحة
curl -G -s "http://loki:3100/loki/api/v1/label/job/values"
# من داخل container:
docker exec -it aapanel_app curl -G -s "http://loki:3100/loki/api/v1/label/job/values"

# 3. تحقق من JSON formatting في logs
tail -f logs/app.log
# يجب أن ترى JSON مثل:
# {"timestamp": "...", "level": "INFO", ...}

# 4. تحقق من متغيرات البيئة
docker-compose exec app env | grep LOG_

# يجب أن تكون:
# LOG_FORMAT=json
# LOG_LEVEL=INFO

# 5. اختبر query مع time range
# في Explore: {job="aapanel"} [5m]

# 6. راجع Dashboard queries
# Dashboard > Panel > Edit > Query
```

---

### المشكلة: Log retention issues

**الأعراض**:
- السجلات تُحذف بسرعة
- أو السجلات القديمة لا تُحذف

**الحل**:
```bash
# 1. تحقق من retention policy في loki-config.yml
cat loki-config.yml | grep -A 5 "retention_period"

# 2. تعديل retention (مثال: 7 أيام)
# في loki-config.yml:
# limits_config:
#   retention_period: 168h  # 7 days

# 3. تحقق من مساحة القرص
df -h /var/lib/docker/volumes

# 4. تحقق من حجم Loki data
docker system df -v | grep loki

# 5. تنظيف يدوي (حذر!)
docker exec -it aapanel_loki sh
find /tmp/loki -type f -mtime +7 -delete
exit

# 6. أعد تشغيل Loki بعد التغييرات
docker-compose restart loki

# 7. تحقق من compactor
# في loki-config.yml:
# compactor:
#   compaction_interval: 10m
```

---

## 🔔 مشاكل التنبيهات

### المشكلة: Alertmanager لا يرسل تنبيهات

**الأعراض**:
- التنبيهات نشطة في Prometheus
- لكن لا تصل إشعارات

**الحل**:
```bash
# 1. تحقق من اتصال Alertmanager بـ Prometheus
curl http://localhost:9090/api/v1/alertmanagers | jq

# 2. تحقق من حالة Alertmanager
curl http://localhost:9093/-/healthy

# 3. افحص logs
docker-compose logs alertmanager | tail -50

# 4. تحقق من التكوين
curl http://localhost:9093/api/v1/status | jq '.data.config'

# 5. تحقق من متغيرات البيئة
docker-compose exec alertmanager env | grep -E "SLACK|SMTP|EMAIL"

# 6. تحقق من expand-env flag
docker-compose logs alertmanager | grep "expand-env"

# 7. اختبر إرسال تنبيه يدوي
curl -X POST http://localhost:9093/api/v1/alerts -H "Content-Type: application/json" -d '[
  {
    "labels": {"alertname": "TestAlert", "severity": "warning"},
    "annotations": {"summary": "Test alert"}
  }
]'

# 8. أعد تشغيل Alertmanager
docker-compose restart alertmanager
```

---

### المشكلة: مشاكل Slack notifications

**الأعراض**:
- التنبيهات لا تصل إلى Slack
- خطأ "invalid webhook URL"

**الحل**:
```bash
# 1. تحقق من SLACK_WEBHOOK_URL في .env
cat .env | grep SLACK_WEBHOOK_URL

# يجب أن يبدأ بـ: https://hooks.slack.com/services/

# 2. اختبر webhook يدوياً
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test from aaPanel"}' \
  $SLACK_WEBHOOK_URL

# 3. تحقق من alertmanager.yml
cat alertmanager.yml | grep -A 5 "slack_configs"

# 4. تحقق من expand-env في docker-compose
cat docker-compose.yml | grep -A 3 "alertmanager:" | grep "expand-env"

# يجب أن ترى:
# - '--config.expand-env=true'

# 5. افحص logs للأخطاء
docker-compose logs alertmanager | grep -i "slack"

# 6. أعد إنشاء webhook في Slack
# راجع ALERTING_SETUP.md للتفاصيل

# 7. أعد تشغيل Alertmanager بعد التغيير
docker-compose down alertmanager
docker-compose up -d alertmanager
```

---

### المشكلة: مشاكل Email notifications

**الأعراض**:
- emails لا تصل
- خطأ في SMTP authentication

**الحل**:
```bash
# 1. تحقق من SMTP credentials في .env
cat .env | grep SMTP_

# 2. اختبر SMTP يدوياً
python3 << 'EOF'
import smtplib
from email.mime.text import MIMEText
import os

msg = MIMEText("Test from aaPanel Alertmanager")
msg['Subject'] = "Test Alert"
msg['From'] = os.getenv('ALERT_EMAIL_FROM')
msg['To'] = os.getenv('ALERT_EMAIL_TO')

server = smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT')))
server.starttls()
server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
server.send_message(msg)
server.quit()
print("✅ Email sent!")
EOF

# 3. للـ Gmail: تحقق من App Password
# لا تستخدم كلمة المرور العادية!
# راجع: https://myaccount.google.com/apppasswords

# 4. تحقق من alertmanager.yml
cat alertmanager.yml | grep -A 10 "email_configs"

# 5. افحص logs
docker-compose logs alertmanager | grep -i "email\|smtp"

# 6. تحقق من firewall/ports
# Port 587 (STARTTLS) يجب أن يكون مفتوحاً

# 7. أعد تشغيل Alertmanager
docker-compose restart alertmanager
```

---

### المشكلة: Alert fatigue (كثرة التنبيهات)

**الأعراض**:
- تنبيهات كثيرة جداً
- إشعارات متكررة
- تجاهل التنبيهات المهمة

**الحل**:
```bash
# 1. زيادة repeat_interval في alertmanager.yml
# غيّر من:
# repeat_interval: 4h
# إلى:
# repeat_interval: 12h  # أو 24h

# 2. زيادة thresholds في prometheus-rules.yml
# مثلاً للـ CPU:
# من: aapanel_cpu_percent > 80
# إلى: aapanel_cpu_percent > 85

# 3. زيادة for duration
# من: for: 5m
# إلى: for: 10m

# 4. استخدام inhibition rules
# في alertmanager.yml:
# inhibit_rules:
#   - source_match:
#       severity: 'critical'
#     target_match:
#       severity: 'warning'
#     equal: ['alertname']

# 5. تجميع التنبيهات
# في alertmanager.yml:
# group_by: ['alertname', 'severity']
# group_wait: 30s
# group_interval: 10m

# 6. إنشاء routes مختلفة حسب severity
# critical → Slack + Email
# warning → Slack فقط
# info → لا شيء

# 7. أعد تشغيل بعد التغييرات
docker-compose restart alertmanager prometheus
```

---

## 🔄 مشاكل Blue-Green Deployment

### المشكلة: فشل التبديل بين البيئات

**الأعراض**:
- nginx لا يوجه للبيئة الجديدة
- المستخدمون يرون الإصدار القديم

**الحل**:
```bash
# 1. تحقق من البيئة النشطة حالياً
cat /etc/nginx/conf.d/upstream.conf

# 2. تحقق من nginx configuration
sudo nginx -t

# 3. اختبر البيئات يدوياً
curl http://localhost:5001/health  # Blue
curl http://localhost:5002/health  # Green

# 4. تحقق من سكريبت التبديل
cat scripts/switch_blue_green.sh

# 5. شغّل التبديل يدوياً
sudo ./scripts/switch_blue_green.sh green

# 6. تحقق من nginx reload
sudo systemctl status nginx

# 7. افحص nginx error log
sudo tail -f /var/log/nginx/error.log

# 8. أعد تحميل nginx يدوياً
sudo nginx -s reload
# أو
sudo systemctl reload nginx
```

---

### المشكلة: مشاكل health checks

**الأعراض**:
- health check يفشل رغم أن الخدمة تعمل
- Deployment يتوقف عند health check

**الحل**:
```bash
# 1. اختبر health endpoint يدوياً
curl -v http://localhost:5002/health/ready

# 2. تحقق من الـ response
# يجب أن يكون: {"status": "healthy"}

# 3. تحقق من الكود
# في health_routes.py:
# @health_bp.route('/ready')

# 4. زد timeout في سكريبت التبديل
# في switch_blue_green.sh:
# HEALTH_CHECK_TIMEOUT=60  # من 30

# 5. تحقق من dependencies (DB, Redis)
docker-compose ps postgres redis

# 6. افحص logs التطبيق
docker-compose logs green_app | grep -i "health"

# 7. تحقق من DB migrations
# قد يكون health check يفشل بسبب migrations غير مطبقة

# 8. اختبر في حاوية مؤقتة
docker run --rm --network aapanel_network alpine/curl \
  curl http://green_app:5000/health/ready
```

---

### المشكلة: مشاكل nginx switching

**الأعراض**:
- nginx لا يتعرف على البيئة الجديدة
- خطأ "upstream not found"

**الحل**:
```bash
# 1. تحقق من upstream configuration
cat /etc/nginx/conf.d/upstream.conf

# يجب أن يحتوي على:
# upstream aapanel_backend {
#     server blue_app:5000;  # أو green_app:5000
# }

# 2. تحقق من Docker network
docker network inspect aapanel_network

# 3. تحقق من أسماء containers
docker-compose ps | grep app

# 4. اختبر DNS resolution من nginx
docker exec -it nginx ping blue_app
docker exec -it nginx ping green_app

# 5. تحقق من nginx.conf
cat /etc/nginx/sites-available/aapanel

# 6. أعد بناء upstream.conf
echo "upstream aapanel_backend {
    server green_app:5000;
}" | sudo tee /etc/nginx/conf.d/upstream.conf

# 7. اختبر nginx config
sudo nginx -t

# 8. أعد تحميل nginx
sudo systemctl reload nginx
```

---

### المشكلة: Rollback issues

**الأعراض**:
- rollback لا يعمل
- لا يمكن العودة للإصدار السابق

**الحل**:
```bash
# 1. تحقق من البيئة النشطة
cat /etc/nginx/conf.d/upstream.conf

# 2. تحقق من أن البيئة القديمة لا تزال تعمل
docker-compose ps blue_app green_app

# 3. rollback يدوي
# إذا كنت على green، ارجع إلى blue:
sudo ./scripts/switch_blue_green.sh blue

# 4. تحقق من docker images
docker images | grep aapanel

# يجب أن ترى versions متعددة

# 5. شغّل الإصدار القديم يدوياً
docker-compose -f docker-compose.blue.yml up -d

# 6. اختبر قبل التبديل
curl http://localhost:5001/health

# 7. بدّل nginx
sudo ./scripts/switch_blue_green.sh blue

# 8. إذا فشل كل شيء، استخدم backup
# استعد من آخر نسخة احتياطية:
python backups/backup_manager.py --restore backup_latest.tar.gz

# 9. وثّق السبب
# أضف ملاحظات في logs حول سبب الـ rollback
```

---

## 📞 الحصول على مساعدة إضافية

### خطوات استكشاف الأخطاء العامة:

1. **اجمع المعلومات**:
   ```bash
   # معلومات النظام
   uname -a
   python --version
   docker --version
   
   # حالة الخدمات
   systemctl status aapanel
   docker ps -a
   
   # السجلات
   tail -100 logs/error.log
   journalctl -u aapanel -n 100
   ```

2. **عزل المشكلة**:
   - هل المشكلة في Development أم Production؟
   - هل بدأت بعد تغيير معين؟
   - هل يمكن إعادة إنتاج المشكلة؟

3. **ابحث في التوثيق**:
   - `replit.md` - نظرة عامة
   - `خطة_التطوير.md` - تفاصيل تقنية
   - `دليل_البدء_السريع.md` - أساسيات

4. **استشر الفريق**:
   - وثّق المشكلة بالتفصيل
   - أرفق السجلات ذات الصلة
   - اذكر ما جربت من حلول

5. **وثّق الحل**:
   - أضف المشكلة والحل لهذا الملف
   - حدّث الملفات ذات الصلة
   - شارك مع الفريق

---

## 🆘 أوامر طوارئ سريعة

### إعادة تشغيل كاملة:
```bash
# أوقف كل شيء
sudo systemctl stop aapanel
docker-compose down

# نظف
docker system prune -a
rm -rf __pycache__

# ابدأ من جديد
docker-compose up --build -d
sudo systemctl start aapanel
```

### استعادة من backup:
```bash
# باستخدام نظام النسخ الاحتياطي المدمج (SHA-256 + HMAC - موصى به)
python backups/backup_manager.py --restore backup_file.tar.gz

# للنسخ القديمة (MD5)
python backups/backup_manager.py --restore backup_file.tar.gz --skip-md5

# قاعدة البيانات مباشرة
psql $DATABASE_URL < backup_latest.sql

# الملفات
tar -xzf backup_files.tar.gz -C /www/server/panel

# الإعدادات
cp backup/.env .env
cp backup/runconfig.py runconfig.py
```

> **📚 ملاحظة:** النسخ الجديدة تستخدم SHA-256 + HMAC للتحقق من السلامة. راجع [DEPLOYMENT_SECRETS.md](./DEPLOYMENT_SECRETS.md) لتفاصيل عن SECRET_KEY وتأثيره على النسخ الاحتياطية.

### فحص شامل:
```bash
# صحة النظام
./scripts/health_check.sh

# اختبارات
pytest tests/

# أمان
./scripts/security_audit.sh
```

---

**آخر تحديث**: 30 سبتمبر 2025

**ملاحظة**: هذا الملف يجب أن يُحدّث باستمرار مع اكتشاف مشاكل جديدة وحلولها.
