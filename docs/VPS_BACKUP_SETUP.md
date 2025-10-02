# دليل إعداد النسخ الاحتياطي التلقائي على VPS
## Automated Backup Setup Guide for VPS

> **ملاحظة مهمة**: هذا الدليل مخصص لبيئة الإنتاج (VPS) فقط.  
> في بيئة Replit، لا يتوفر `crontab` أو `systemd`، لذا يُشغّل النسخ الاحتياطي يدوياً فقط.

---

## 📋 المتطلبات الأساسية | Prerequisites

### 1. البرمجيات المطلوبة
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python 3.9+
sudo apt install python3 python3-pip -y

# تثبيت التبعيات
pip3 install -r requirements.txt
```

### 2. ملف `.env` محدّث
تأكد من وجود `SECRET_KEY` **ثابت** في `.env`:

```bash
# مطلوب لـ HMAC verification
SECRET_KEY=your-secure-random-key-here-min-32-chars
```

> ⚠️ **تحذير**: بدون SECRET_KEY ثابت، ستفشل عملية استعادة النسخ v2 (SHA-256 + HMAC)!

---

## ⚙️ الطريقة 1: إعداد Cron (بسيط)

### الخطوة 1: إعداد السكريبت
```bash
# نقل setup_cron.sh إلى مجلد المشروع
cd /path/to/your/project

# منح صلاحيات التنفيذ
chmod +x backups/setup_cron.sh
```

### الخطوة 2: تشغيل السكريبت
```bash
# تشغيل إعداد Cron
./backups/setup_cron.sh
```

**الإخراج المتوقع**:
```
✅ تم إضافة Cron job بنجاح!
📋 جدولة النسخ الاحتياطي: 2:00 صباحاً يومياً

📝 لعرض Cron jobs الحالية:
   crontab -l

🔧 لتعديل الجدولة:
   crontab -e
```

### الخطوة 3: التحقق من Cron Job
```bash
# عرض جميع Cron jobs
crontab -l

# يجب أن ترى:
# 0 2 * * * cd /path/to/project && /usr/bin/python3 backups/backup_manager.py --backup >> /path/to/logs/backup_cron.log 2>&1
```

### الخطوة 4: اختبار يدوي
```bash
# تشغيل يدوي للتأكد
python3 backups/backup_manager.py --backup

# التحقق من الناتج
python3 backups/backup_manager.py --list
```

---

## 🔧 الطريقة 2: إعداد Systemd Timer (متقدّم)

### الخطوة 1: إنشاء Systemd Service
```bash
sudo nano /etc/systemd/system/aapanel-backup.service
```

**المحتوى**:
```ini
[Unit]
Description=aaPanel Backup Service
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 /path/to/your/project/backups/backup_manager.py --backup
StandardOutput=append:/var/log/aapanel-backup.log
StandardError=append:/var/log/aapanel-backup-error.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### الخطوة 2: إنشاء Systemd Timer
```bash
sudo nano /etc/systemd/system/aapanel-backup.timer
```

**المحتوى**:
```ini
[Unit]
Description=aaPanel Backup Timer - Daily at 2:00 AM
Requires=aapanel-backup.service

[Timer]
# تشغيل يومياً الساعة 2:00 صباحاً
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### الخطوة 3: تفعيل Timer
```bash
# إعادة تحميل Systemd
sudo systemctl daemon-reload

# تفعيل Timer (يبدأ تلقائياً عند الإقلاع)
sudo systemctl enable aapanel-backup.timer

# بدء Timer
sudo systemctl start aapanel-backup.timer

# التحقق من الحالة
sudo systemctl status aapanel-backup.timer
```

### الخطوة 4: اختبار Service يدوياً
```bash
# تشغيل يدوي للـ Service
sudo systemctl start aapanel-backup.service

# التحقق من السجلات
sudo journalctl -u aapanel-backup.service -n 50
```

---

## 📊 التحقق من التشغيل | Verification

### 1. فحص السجلات
```bash
# Cron logs
tail -f logs/backup_cron.log

# Systemd logs
sudo journalctl -u aapanel-backup.service -f
```

### 2. التحقق من النسخ الاحتياطية
```bash
# عرض قائمة النسخ
python3 backups/backup_manager.py --list

# يجب أن ترى نسخة جديدة كل يوم
```

### 3. اختبار الاستعادة
```bash
# اختبار استعادة أحدث نسخة
python3 backups/backup_manager.py --restore backups/backup_YYYYMMDD_HHMMSS.tar.gz --skip-md5
```

---

## 🔐 الأمان | Security

### 1. صلاحيات الملفات
```bash
# حماية مجلد backups
chmod 700 backups/
chmod 600 backups/*.tar.gz

# حماية .env
chmod 600 .env
```

### 2. التشفير (اختياري - مستقبلاً)
```bash
# تشفير النسخة الاحتياطية باستخدام GPG
gpg --symmetric --cipher-algo AES256 backups/backup_YYYYMMDD_HHMMSS.tar.gz

# فك التشفير
gpg --decrypt backups/backup_YYYYMMDD_HHMMSS.tar.gz.gpg > backup_restored.tar.gz
```

---

## 🗑️ تنظيف النسخ القديمة | Cleanup

### تلقائياً (مدمج في backup_manager.py)
```python
# في backup_manager.py
# الافتراضي: الاحتفاظ بـ 7 نسخ فقط
BACKUP_RETENTION = 7
```

### يدوياً
```bash
# عرض وحذف النسخ القديمة
python3 backups/backup_manager.py --cleanup

# حذف يدوي
rm backups/backup_YYYYMMDD_HHMMSS.tar.gz*
```

---

## 🐛 استكشاف الأخطاء | Troubleshooting

### 1. فشل HMAC Verification
**المشكلة**: `❌ فشل التحقق من HMAC!`

**الحل**:
```bash
# 1. تأكد من وجود SECRET_KEY ثابت في .env
echo $SECRET_KEY

# 2. إذا كان فارغاً، أضفه:
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# 3. أعد إنشاء النسخة الاحتياطية
python3 backups/backup_manager.py --backup
```

### 2. Cron لا يعمل
**التحقق**:
```bash
# 1. تحقق من حالة cron
sudo systemctl status cron

# 2. تحقق من السجلات
grep CRON /var/log/syslog

# 3. تحقق من الصلاحيات
ls -la backups/backup_manager.py
```

### 3. مساحة التخزين ممتلئة
**الحل**:
```bash
# 1. فحص المساحة
df -h

# 2. تنظيف النسخ القديمة
python3 backups/backup_manager.py --cleanup

# 3. ضبط retention
# في backup_manager.py: BACKUP_RETENTION = 3
```

---

## 📅 جداول زمنية مقترحة | Recommended Schedules

### 1. يومياً الساعة 2:00 صباحاً (افتراضي)
```cron
0 2 * * * cd /path/to/project && python3 backups/backup_manager.py --backup
```

### 2. كل 6 ساعات
```cron
0 */6 * * * cd /path/to/project && python3 backups/backup_manager.py --backup
```

### 3. أسبوعياً يوم الأحد
```cron
0 3 * * 0 cd /path/to/project && python3 backups/backup_manager.py --backup
```

### 4. شهرياً (أول يوم من الشهر)
```cron
0 4 1 * * cd /path/to/project && python3 backups/backup_manager.py --backup
```

---

## 📝 ملاحظات إضافية | Additional Notes

### 1. النسخ الاحتياطي عن بُعد
```bash
# نسخ إلى خادم بعيد باستخدام rsync
rsync -avz --delete backups/ user@remote-server:/backups/aapanel/

# أو استخدام AWS S3
aws s3 sync backups/ s3://your-bucket/aapanel-backups/
```

### 2. إشعارات البريد الإلكتروني
```bash
# إضافة إلى cron job
0 2 * * * cd /path/to/project && python3 backups/backup_manager.py --backup 2>&1 | mail -s "aaPanel Backup Status" admin@example.com
```

### 3. مراقبة الأداء
```bash
# استخدام systemd timer مع OnFailure
[Unit]
OnFailure=backup-failed-notify@%n.service
```

---

## ✅ قائمة التحقق النهائية | Final Checklist

- [ ] تثبيت Python 3.9+ والتبعيات
- [ ] إعداد `SECRET_KEY` ثابت في `.env`
- [ ] إعداد Cron أو Systemd Timer
- [ ] اختبار النسخ الاحتياطي اليدوي بنجاح
- [ ] التحقق من السجلات (logs)
- [ ] اختبار الاستعادة (restore) بنجاح
- [ ] ضبط صلاحيات الملفات (permissions)
- [ ] إعداد تنظيف تلقائي للنسخ القديمة
- [ ] (اختياري) إعداد النسخ الاحتياطي عن بُعد
- [ ] (اختياري) إعداد إشعارات البريد الإلكتروني

---

## 📚 مراجع إضافية | Additional Resources

- [Cron Best Practices](https://man7.org/linux/man-pages/man5/crontab.5.html)
- [Systemd Timer Documentation](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)

---

**آخر تحديث**: 2025-10-02  
**الحالة**: ✅ جاهز للإنتاج
