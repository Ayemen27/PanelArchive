# نظام النسخ الاحتياطي الشامل
# Comprehensive Backup Manager

نظام نسخ احتياطي متكامل لقواعد البيانات والملفات الهامة مع دعم SQLite و PostgreSQL و MySQL.

## المميزات الرئيسية

✅ دعم قواعد بيانات متعددة (SQLite, PostgreSQL, MySQL)
✅ نسخ احتياطي للمجلدات والملفات الهامة
✅ ضغط tar.gz مع تسمية زمنية
✅ الاحتفاظ التلقائي بعدد محدد من النسخ
✅ **التحقق من السلامة والأصالة (SHA-256 + HMAC - v2)**
✅ **التوافق الرجعي** مع النسخ القديمة (MD5 v1 - للاستعادة فقط)
✅ CLI متقدم مع ألوان ANSI
✅ سجل شامل للعمليات

## الاستخدام السريع

### إنشاء نسخة احتياطية جديدة
```bash
python backups/backup_manager.py
```

### عرض قائمة النسخ الاحتياطية
```bash
python backups/backup_manager.py --list
```

### تنظيف النسخ القديمة
```bash
python backups/backup_manager.py --cleanup
```

### تغيير عدد النسخ المحفوظة
```bash
python backups/backup_manager.py --keep 10
```

### استرجاع نسخة احتياطية
```bash
# استرجاع نسخة v2 (SHA-256 + HMAC)
python backups/backup_manager.py --restore backups/backup_YYYYMMDD_HHMMSS.tar.gz

# استرجاع نسخة v1 قديمة (MD5) - غير آمن
python backups/backup_manager.py --restore backups/legacy_backup.tar.gz --skip-md5
```

> **⚠️ تحذير:** النسخ القديمة (MD5 v1) غير آمنة. استخدم --skip-md5 فقط للنسخ القديمة الضرورية.

## المتغيرات البيئية

- `BACKUP_RETENTION`: عدد النسخ الاحتياطية المحفوظة (الافتراضي: 7)

## الملفات المنسوخة

- `data/` - جميع قواعد البيانات والإعدادات
- `logs/` - السجلات
- `.env` - متغيرات البيئة (نسخة آمنة مع إخفاء كلمات المرور)
- `alembic.ini` - إعدادات migrations

## الأمان

⚠️ ملف `.env` يتم نسخه بشكل آمن مع إخفاء جميع القيم الحساسة (PASSWORD, SECRET, KEY, TOKEN)

🔐 **النسخ الاحتياطية الجديدة (v2):**
- تستخدم **SHA-256 + HMAC** للتحقق من السلامة والأصالة
- تتطلب **SECRET_KEY** من `.env` - تغييره يبطل جميع النسخ v2
- حماية متقدمة ضد التلاعب والهجمات

⚠️ **النسخ القديمة (v1 - MD5):**
- مدعومة للاستعادة فقط (باستخدام --skip-md5)
- غير آمنة - MD5 ضعيف ضد الهجمات
- يُوصى بشدة بإعادة إنشائها بـ SHA-256 + HMAC

📚 **لمزيد من التفاصيل:** راجع [DEPLOYMENT_SECRETS.md](../DEPLOYMENT_SECRETS.md)

## السجلات

جميع العمليات مسجلة في: `backups/backup.log`
