# 🔧 دليل إعداد systemd Service - aaPanel

## 📋 نظرة عامة

هذا الدليل يشرح كيفية إعداد وتشغيل aaPanel كـ **systemd service** على خوادم الإنتاج (VPS/Dedicated). systemd service يوفر:

- ✅ **بدء تلقائي** عند إقلاع النظام
- ✅ **إعادة تشغيل تلقائية** عند الفشل
- ✅ **إدارة سجلات** متقدمة
- ✅ **أمان محسّن** مع resource limits
- ✅ **مراقبة وصيانة** سهلة

---

## 🚀 التثبيت السريع (الطريقة التلقائية)

### المتطلبات الأساسية:
- ✅ خادم Linux مع systemd (Ubuntu 18.04+, CentOS 7+, Debian 9+)
- ✅ Python 3.8+
- ✅ صلاحيات root
- ✅ aaPanel مثبت في `/www/server/panel`

### خطوات التثبيت:

```bash
# 1. الانتقال إلى مجلد المشروع
cd /www/server/panel

# 2. تشغيل سكريبت الإعداد
sudo ./setup_systemd.sh
```

السكريبت سيقوم بـ:
1. ✅ التحقق من المتطلبات
2. ✅ إنشاء المستخدم `www` إن لم يكن موجوداً
3. ✅ إنشاء المجلدات المطلوبة
4. ✅ ضبط الصلاحيات
5. ✅ تثبيت systemd service
6. ✅ بدء الخدمة تلقائياً

---

## ⚙️ التثبيت اليدوي (الطريقة التقليدية)

### 1. إنشاء المستخدم والمجموعة

```bash
# إنشاء مستخدم www إن لم يكن موجوداً
sudo groupadd -r www
sudo useradd -r -g www -s /sbin/nologin -d /www -M www
```

### 2. إعداد المجلدات والصلاحيات

```bash
# إنشاء المجلدات
sudo mkdir -p /www/server/panel/logs
sudo mkdir -p /www/server/panel/data
sudo mkdir -p /www/server/panel/BTPanel/static/upload

# ضبط الصلاحيات
sudo chown -R www:www /www/server/panel
sudo chmod -R 755 /www/server/panel
sudo chmod -R 775 /www/server/panel/logs
sudo chmod -R 775 /www/server/panel/data
sudo chmod 600 /www/server/panel/.env
```

### 3. إنشاء virtualenv وتثبيت الاعتماديات

```bash
# إنشاء virtualenv
python3 -m venv /www/server/panel/venv

# تفعيل virtualenv
source /www/server/panel/venv/bin/activate

# تحديث pip
pip install --upgrade pip

# تثبيت Gunicorn و gevent-websocket
pip install gunicorn gevent-websocket

# تثبيت باقي الاعتماديات من requirements.txt (إن وجد)
pip install -r /www/server/panel/requirements.txt

# إلغاء تفعيل virtualenv
deactivate

# ضبط صلاحيات virtualenv للمستخدم www
sudo chown -R www:www /www/server/panel/venv
```

**ملاحظة مهمة:** استخدام virtualenv ضروري لأن systemd service يعمل كمستخدم `www` ويحتاج صلاحيات على الملفات التنفيذية.

### 4. نسخ وتفعيل الخدمة

```bash
# نسخ ملف الخدمة
sudo cp aapanel.service /etc/systemd/system/

# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل البدء التلقائي
sudo systemctl enable aapanel.service

# بدء الخدمة
sudo systemctl start aapanel.service
```

### 5. التحقق من الحالة

```bash
# عرض حالة الخدمة
sudo systemctl status aapanel.service

# عرض السجلات
sudo journalctl -u aapanel.service -f
```

---

## 📄 شرح ملف aapanel.service

### القسم [Unit]
```ini
[Unit]
Description=aaPanel - Server Management Control Panel
Documentation=https://www.aapanel.com/
After=network.target postgresql.service mysql.service redis.service
Wants=network-online.target
```

- **Description**: وصف الخدمة
- **After**: تبدأ بعد الشبكة وقواعد البيانات
- **Wants**: تحتاج اتصال شبكة كامل

### القسم [Service]
```ini
[Service]
Type=simple
User=www
Group=www
WorkingDirectory=/www/server/panel
```

- **Type=simple**: خدمة بسيطة (foreground process)
- **User/Group**: تشغيل كمستخدم www (أمان)
- **WorkingDirectory**: مجلد العمل

**ملاحظة:** تم استخدام `Type=simple` بدلاً من `Type=notify` لأن Gunicorn لا يدعم systemd notify mode افتراضياً إلا مع flag `--systemd`.

### Environment Variables
```ini
EnvironmentFile=/www/server/panel/.env
Environment="PYTHONUNBUFFERED=1"
Environment="ENVIRONMENT=production"
```

- **EnvironmentFile**: تحميل متغيرات من `.env`
- **PYTHONUNBUFFERED**: لضمان ظهور السجلات فوراً
- **ENVIRONMENT**: فرض بيئة الإنتاج

### ExecStart - أمر التشغيل

**الطريقة الموصى بها (مع virtualenv و gunicorn_config.py):**
```ini
ExecStart=/www/server/panel/venv/bin/gunicorn -c gunicorn_config.py BTPanel:app
```

**أو الطريقة اليدوية (مع أوامر مباشرة):**
```ini
ExecStart=/www/server/panel/venv/bin/gunicorn \
    --bind 0.0.0.0:${PORT:-8888} \
    --workers ${WORKERS:-4} \
    --threads ${THREADS:-3} \
    --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    --timeout 7200 \
    --keepalive 60 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --graceful-timeout 30 \
    --access-logfile /www/server/panel/logs/access.log \
    --error-logfile /www/server/panel/logs/error.log \
    --log-level info \
    --pid /www/server/panel/logs/panel.pid \
    --capture-output \
    --enable-stdio-inheritance \
    BTPanel:app
```

**لماذا virtualenv (`/www/server/panel/venv/bin/gunicorn`)؟**
- يعزل اعتماديات Python عن النظام
- يسمح للمستخدم `www` بتشغيل Gunicorn بدون صلاحيات root
- يتجنب تعارضات الإصدارات
- يسهل التحديثات والصيانة
- **مهم**: المسار المباشر للـ virtualenv يضمن أن systemd يجد الملف التنفيذي الصحيح المملوك للمستخدم `www`

**الخيارات المهمة:**
- `--workers 4`: عدد العمليات (عادة: CPU cores × 2-4)
- `--threads 3`: عدد الخيوط لكل عامل
- `--worker-class`: دعم WebSocket
- `--timeout 7200`: 2 ساعة (للعمليات الطويلة)
- `--max-requests 1000`: إعادة تشغيل العامل كل 1000 طلب (لمنع تسرب الذاكرة)
- `--graceful-timeout 30`: 30 ثانية للإغلاق الرشيق

### Restart Policy - سياسة إعادة التشغيل
```ini
Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3
```

- **Restart=always**: إعادة تشغيل دائماً عند الفشل
- **RestartSec=5**: انتظر 5 ثوان قبل إعادة التشغيل
- **StartLimitBurst=3**: حاول 3 مرات كحد أقصى
- **StartLimitInterval=60**: في 60 ثانية

### Resource Limits - حدود الموارد
```ini
LimitNOFILE=65535
LimitNPROC=4096
```

- **LimitNOFILE**: 65535 ملف مفتوح (للاتصالات المتزامنة)
- **LimitNPROC**: 4096 عملية كحد أقصى

### Security Hardening - تحصين الأمان
```ini
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/www/server/panel/data /www/server/panel/logs
ReadOnlyPaths=/www/server/panel
```

- **NoNewPrivileges**: منع التصعيد
- **PrivateTmp**: مجلد /tmp خاص
- **ProtectSystem**: حماية النظام
- **ReadWritePaths**: مجلدات الكتابة فقط

### Process Management - إدارة العمليات
```ini
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
```

- **KillMode=mixed**: إرسال SIGTERM للعملية الرئيسية و SIGKILL للباقي
- **KillSignal=SIGTERM**: إغلاق رشيق
- **TimeoutStopSec=30**: انتظر 30 ثانية قبل القتل القسري

---

## 🔧 إدارة الخدمة

### الأوامر الأساسية

```bash
# بدء الخدمة
sudo systemctl start aapanel

# إيقاف الخدمة
sudo systemctl stop aapanel

# إعادة تشغيل الخدمة
sudo systemctl restart aapanel

# إعادة تحميل الإعدادات (بدون downtime)
sudo systemctl reload aapanel

# عرض الحالة
sudo systemctl status aapanel

# تفعيل البدء التلقائي
sudo systemctl enable aapanel

# تعطيل البدء التلقائي
sudo systemctl disable aapanel
```

### مراقبة السجلات

```bash
# عرض السجلات الحية
sudo journalctl -u aapanel -f

# عرض آخر 100 سطر
sudo journalctl -u aapanel -n 100

# عرض سجلات اليوم
sudo journalctl -u aapanel --since today

# عرض سجلات آخر ساعة
sudo journalctl -u aapanel --since "1 hour ago"

# عرض سجلات مع أولوية الخطأ فقط
sudo journalctl -u aapanel -p err

# تصفية بكلمة مفتاحية
sudo journalctl -u aapanel | grep "ERROR"
```

### فحص الأداء

```bash
# عرض استخدام الموارد
sudo systemctl show aapanel --property=MainPID
ps aux | grep <PID>

# عرض عدد الاتصالات
sudo ss -tlnp | grep :8888

# عرض استخدام الذاكرة
sudo systemd-cgtop -1
```

---

## 🔄 التحديث والصيانة

### تحديث الكود

```bash
# 1. إيقاف الخدمة
sudo systemctl stop aapanel

# 2. تحديث الكود
cd /www/server/panel
git pull origin main

# 3. تحديث الاعتماديات في virtualenv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# أو بدون تفعيل:
# /www/server/panel/venv/bin/pip install -r requirements.txt

# 4. بدء الخدمة
sudo systemctl start aapanel
```

**ملاحظة:** تأكد دائماً من تثبيت الاعتماديات **داخل virtualenv** لضمان عمل الخدمة بشكل صحيح.

### تحديث ملف الخدمة

```bash
# 1. تعديل الملف
sudo nano /etc/systemd/system/aapanel.service

# 2. إعادة تحميل systemd
sudo systemctl daemon-reload

# 3. إعادة تشغيل الخدمة
sudo systemctl restart aapanel
```

### Rolling Update (بدون downtime)

```bash
# 1. تحديث الكود
cd /www/server/panel
git pull origin main

# تحديث الاعتماديات في virtualenv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# أو بدون تفعيل:
# /www/server/panel/venv/bin/pip install -r requirements.txt

# 2. إعادة تحميل Gunicorn بلطف
sudo systemctl reload aapanel

# أو إرسال إشارة USR2
sudo kill -USR2 $(cat /www/server/panel/logs/panel.pid)
```

**ملاحظة:** حتى في Rolling Update، يجب تثبيت الاعتماديات داخل virtualenv.

---

## 🐛 استكشاف الأخطاء

### المشكلة 1: الخدمة لا تبدأ

**الأعراض:**
```
sudo systemctl status aapanel
● aapanel.service - failed
```

**الحلول:**

1. **فحص السجلات:**
```bash
sudo journalctl -u aapanel -n 50 --no-pager
```

2. **التحقق من المتغيرات:**
```bash
cat /www/server/panel/.env
```

3. **التحقق من الصلاحيات:**
```bash
ls -la /www/server/panel
```

4. **اختبار يدوي:**
```bash
cd /www/server/panel
# استخدام gunicorn من virtualenv
sudo -u www venv/bin/gunicorn --bind 0.0.0.0:8888 BTPanel:app
```

### المشكلة 2: الخدمة تتوقف بشكل متكرر

**الأسباب المحتملة:**
- تسرب ذاكرة (memory leak)
- أخطاء في الكود
- موارد غير كافية

**الحلول:**

1. **زيادة max-requests:**
```ini
# في aapanel.service
--max-requests 500
--max-requests-jitter 50
```

2. **زيادة الذاكرة:**
```bash
# إضافة memory limit
[Service]
MemoryMax=2G
```

3. **فحص الأخطاء:**
```bash
sudo journalctl -u aapanel -p err -n 100
```

### المشكلة 3: البدء التلقائي لا يعمل

**الحل:**
```bash
# التأكد من التفعيل
sudo systemctl enable aapanel

# التحقق من الحالة
sudo systemctl is-enabled aapanel

# التحقق من التبعيات
sudo systemctl list-dependencies aapanel
```

### المشكلة 4: أداء ضعيف

**الحلول:**

1. **زيادة عدد العمال:**
```bash
# حساب العدد المثالي
# Workers = (2 x CPU cores) + 1
nproc  # عدد CPU cores
```

2. **تعديل .env:**
```env
WORKERS=9  # لـ 4 cores
THREADS=4
```

3. **تفعيل preload:**
```ini
# في Gunicorn config
--preload-app
```

### المشكلة 5: السجلات لا تظهر

**الحلول:**

1. **التحقق من rsyslog:**
```bash
sudo systemctl status rsyslog
```

2. **فحص صلاحيات المجلد:**
```bash
sudo chmod 775 /www/server/panel/logs
sudo chown -R www:www /www/server/panel/logs
```

3. **إعادة تشغيل journald:**
```bash
sudo systemctl restart systemd-journald
```

---

## ⚡ أفضل الممارسات

### 1. الأمان

✅ **استخدم مستخدم غير root:**
```ini
User=www
Group=www
```

✅ **فعّل security hardening:**
```ini
NoNewPrivileges=true
ProtectSystem=strict
PrivateTmp=true
```

✅ **حدد الصلاحيات:**
```ini
ReadWritePaths=/www/server/panel/data /www/server/panel/logs
ReadOnlyPaths=/www/server/panel
```

### 2. الأداء

✅ **اضبط عدد العمال حسب CPU:**
```bash
# قاعدة عامة: (2 × CPU cores) + 1
WORKERS=$(( 2 * $(nproc) + 1 ))
```

✅ **فعّل max-requests لمنع memory leak:**
```ini
--max-requests 1000
--max-requests-jitter 50
```

✅ **استخدم preload في الإنتاج:**
```ini
--preload-app
```

### 3. الموثوقية

✅ **إعادة التشغيل التلقائي:**
```ini
Restart=always
RestartSec=5
```

✅ **timeout مناسب:**
```ini
--timeout 7200  # 2 ساعة للعمليات الطويلة
--graceful-timeout 30
```

✅ **مراقبة السجلات:**
```bash
# إعداد تنبيه تلقائي
sudo journalctl -u aapanel -p err -f | mail -s "aaPanel Error" admin@example.com
```

### 4. الصيانة

✅ **نسخ احتياطية منتظمة:**
```bash
# Backup service file
sudo cp /etc/systemd/system/aapanel.service /root/backups/
```

✅ **تدوير السجلات:**
```bash
# في /etc/logrotate.d/aapanel
/www/server/panel/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    postrotate
        systemctl reload aapanel > /dev/null 2>&1 || true
    endscript
}
```

✅ **مراقبة دورية:**
```bash
# Cron job للمراقبة
*/5 * * * * systemctl is-active --quiet aapanel || systemctl restart aapanel
```

---

## 📊 المراقبة والتنبيهات

### Prometheus Integration

```bash
# تثبيت prometheus_client في virtualenv
source /www/server/panel/venv/bin/activate
pip install prometheus-client
deactivate

# أو بدون تفعيل:
# /www/server/panel/venv/bin/pip install prometheus-client

# في BTPanel/__init__.py
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})
```

### Health Check Endpoint

```python
# في BTPanel/routes.py
@app.route('/health/live')
def health_live():
    return {'status': 'ok'}, 200

@app.route('/health/ready')
def health_ready():
    # فحص DB، Redis، etc.
    return {'status': 'ready'}, 200
```

### Systemd Health Check

```ini
# في aapanel.service
[Service]
# Health check كل 30 ثانية
ExecStartPost=/usr/bin/curl -f http://localhost:8888/health/live || exit 1
```

---

## 🔗 التكامل مع Nginx

### Nginx Configuration

```nginx
upstream aapanel_backend {
    server 127.0.0.1:8888;
    keepalive 64;
}

server {
    listen 80;
    server_name panel.example.com;
    
    location / {
        proxy_pass http://aapanel_backend;
        include /etc/nginx/proxy_params;
    }
}
```

### تفعيل systemd socket activation

```ini
# aapanel.socket
[Unit]
Description=aaPanel Socket

[Socket]
ListenStream=8888
Accept=no

[Install]
WantedBy=sockets.target
```

---

## 📝 ملاحظات مهمة

### ⚠️ تحذيرات

1. **لا تشغل كـ root** - دائماً استخدم مستخدم محدود الصلاحيات
2. **لا تنسَ تحديث .env** - الإعدادات الخاطئة قد تسبب فشل
3. **راقب السجلات** - تحقق من journalctl بانتظام
4. **اختبر قبل الإنتاج** - جرب التحديثات في بيئة staging أولاً

### ✅ نصائح

1. **استخدم السكريبت التلقائي** - `setup_systemd.sh` يوفر الوقت
2. **وثّق التغييرات** - احفظ نسخة من كل تعديل
3. **راقب الأداء** - استخدم htop، systemd-cgtop
4. **حدّث باستمرار** - ابقَ على اطلاع بآخر التحديثات

---

## 🎓 موارد إضافية

### الوثائق الرسمية:
- [systemd.service man page](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

### مراجع مفيدة:
- [systemd by example](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Best practices for systemd services](https://www.digitalocean.com/community/tutorials/systemd-essentials-working-with-services-units-and-the-journal)

---

## 📞 الدعم

### في حالة المشاكل:

1. 📖 راجع قسم "استكشاف الأخطاء" في هذا الدليل
2. 🔍 افحص السجلات: `sudo journalctl -u aapanel -n 100`
3. 📝 راجع TROUBLESHOOTING.md
4. 💬 استشر الفريق الفني

---

**آخر تحديث:** 30 سبتمبر 2025  
**الإصدار:** 1.0  
**المؤلف:** الوكيل رقم 6  
**الحالة:** ✅ جاهز للإنتاج
