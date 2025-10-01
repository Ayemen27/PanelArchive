# نظام النسخ الاحتياطي الشامل
# Comprehensive Backup Manager

نظام نسخ احتياطي متكامل لقواعد البيانات والملفات الهامة مع دعم SQLite و PostgreSQL و MySQL.

## المميزات الرئيسية

✅ دعم قواعد بيانات متعددة (SQLite, PostgreSQL, MySQL)
✅ نسخ احتياطي للمجلدات والملفات الهامة
✅ ضغط tar.gz مع تسمية زمنية
✅ الاحتفاظ التلقائي بعدد محدد من النسخ
✅ التحقق من سلامة النسخ (MD5 checksum)
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
python backups/backup_manager.py --restore backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

## المتغيرات البيئية

- `BACKUP_RETENTION`: عدد النسخ الاحتياطية المحفوظة (الافتراضي: 7)

## الملفات المنسوخة

- `data/` - جميع قواعد البيانات والإعدادات
- `logs/` - السجلات
- `.env` - متغيرات البيئة (نسخة آمنة مع إخفاء كلمات المرور)
- `alembic.ini` - إعدادات migrations

## الأمان

⚠️ ملف `.env` يتم نسخه بشكل آمن مع إخفاء جميع القيم الحساسة (PASSWORD, SECRET, KEY, TOKEN)

## السجلات

جميع العمليات مسجلة في: `backups/backup.log`
