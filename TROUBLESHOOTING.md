# 🔧 دليل استكشاف الأخطاء وإصلاحها - aaPanel

## 📋 جدول المحتويات
1. [مشاكل التشغيل الأساسية](#مشاكل-التشغيل-الأساسية)
2. [مشاكل البيئة والإعدادات](#مشاكل-البيئة-والإعدادات)
3. [مشاكل قاعدة البيانات](#مشاكل-قاعدة-البيانات)
4. [مشاكل Docker](#مشاكل-docker)
5. [مشاكل النشر](#مشاكل-النشر)
6. [مشاكل الأداء](#مشاكل-الأداء)
7. [مشاكل الأمان](#مشاكل-الأمان)

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
# 1. خذ نسخة احتياطية فوراً!
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. تحقق من سلامة DB
# للـ PostgreSQL
psql $DATABASE_URL -c "VACUUM ANALYZE;"

# 3. استعد من آخر نسخة احتياطية صحيحة
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
# قاعدة البيانات
psql $DATABASE_URL < backup_latest.sql

# الملفات
tar -xzf backup_files.tar.gz -C /www/server/panel

# الإعدادات
cp backup/.env .env
cp backup/runconfig.py runconfig.py
```

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
