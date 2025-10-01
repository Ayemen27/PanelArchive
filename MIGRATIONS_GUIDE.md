# دليل نظام Migrations الشامل - aaPanel

## 📋 نظرة عامة

تم إنشاء نظام migrations متكامل لإدارة تغييرات قاعدة البيانات بشكل آمن ومنظم باستخدام **Alembic**.

## ✅ ما تم إنجازه

### 1. البنية الأساسية
- ✅ `alembic.ini` - ملف التكوين الرئيسي
- ✅ `migrations/env.py` - بيئة Alembic متكاملة مع config_factory
- ✅ `migrations/script.py.mako` - Template للـ migrations
- ✅ `migrations/migrate.py` - أداة إدارة سهلة الاستخدام
- ✅ `migrations/versions/` - مجلد للـ migrations

### 2. Baseline Migration
- ✅ `001_initial_baseline.py` - توثيق البنية الحالية (27 جدول)
- ✅ لا يعدل البيانات، فقط يوثق ما موجود

### 3. التوثيق
- ✅ `migrations/README.md` - دليل شامل بالعربية
- ✅ أمثلة عملية لجميع العمليات
- ✅ استكشاف أخطاء شامل

### 4. الاختبارات
- ✅ `tests/test_migrations.py` - 13 اختبار شامل
- ✅ **نسبة النجاح: 100%**
- ✅ يغطي جميع الجوانب

## 🚀 الاستخدام السريع

### عرض الحالة
```bash
python migrations/migrate.py current
```

### عرض السجل
```bash
python migrations/migrate.py history
```

### إنشاء migration جديد
```bash
python migrations/migrate.py create "Add SSL column to sites table"
```

### تطبيق migrations
```bash
python migrations/migrate.py upgrade
```

### التراجع
```bash
python migrations/migrate.py downgrade
```

## 🎯 الميزات الرئيسية

### 1. التكامل مع config_factory
- يستخدم `get_config()` للحصول على DATABASE_URI تلقائياً
- دعم بيئات متعددة (Development/Production)
- SQLite في التطوير، PostgreSQL/MySQL في الإنتاج

### 2. دعم SQLite الكامل
- استخدام `batch_alter_table` تلقائياً
- يتعامل مع قيود SQLite بشكل صحيح

### 3. Rollback آمن
- كل migration لها upgrade و downgrade
- يمكن التراجع لأي نقطة

### 4. Baseline واضح
- توثيق البنية الحالية (27 جدول)
- نقطة انطلاق موثوقة

## 📊 البنية الحالية

### الجداول الموجودة (27 جدول):
1. **backup** - إدارة النسخ الاحتياطية
2. **binding** - ربط النطاقات
3. **config** - إعدادات النظام
4. **crontab** - المهام المجدولة
5. **databases** - إدارة قواعد البيانات
6. **firewall** - قواعد الجدار الناري
7. **ftps** - حسابات FTP
8. **logs** - سجلات النظام
9. **sites** - إدارة المواقع
10. **domain** - سجلات النطاقات
11. **users** - حسابات المستخدمين
12. **tasks** - قائمة المهام
13-27. جداول إضافية للميزات المختلفة

## 🧪 الاختبارات

### تشغيل الاختبارات
```bash
pytest tests/test_migrations.py -v
```

### ما يتم اختباره:
- ✅ وجود الملفات الأساسية
- ✅ صحة التكوين
- ✅ baseline migration
- ✅ integration مع config_factory
- ✅ batch mode لـ SQLite
- ✅ البنية الصحيحة للـ migrations

### النتائج:
```
13 passed in 1.92s - 100% ✅
```

## 📝 أمثلة عملية

### مثال 1: إضافة عمود SSL
```python
def upgrade():
    with op.batch_alter_table('sites') as batch_op:
        batch_op.add_column(
            sa.Column('ssl_enabled', sa.Boolean(), 
                     server_default='0', nullable=False)
        )

def downgrade():
    with op.batch_alter_table('sites') as batch_op:
        batch_op.drop_column('ssl_enabled')
```

### مثال 2: إنشاء جدول API Keys
```python
def upgrade():
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(64), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permissions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True)
    )

def downgrade():
    op.drop_table('api_keys')
```

## ⚠️ ملاحظات مهمة

### 1. SQLite Constraints
استخدم دائماً `batch_alter_table` مع SQLite:
```python
with op.batch_alter_table('table_name') as batch_op:
    # التعديلات هنا
```

### 2. الاختبار قبل الإنتاج
```bash
# اختبر في التطوير
ENVIRONMENT=development python migrations/migrate.py upgrade

# ثم في الإنتاج
ENVIRONMENT=production python migrations/migrate.py upgrade
```

### 3. النسخ الاحتياطي
**دائماً** خذ نسخة احتياطية قبل تطبيق migrations في الإنتاج:
```bash
sqlite3 data/default.db ".backup data/default_backup_$(date +%Y%m%d).db"
```

## 🔧 استكشاف الأخطاء

### "Could not determine current revision"
```bash
alembic stamp head
```

### "Target database is not up to date"
```bash
python migrations/migrate.py current
python migrations/migrate.py upgrade
```

### "Can't locate revision"
```bash
python migrations/migrate.py history
```

## 📈 الخطوات التالية

### المرحلة 4.2: استراتيجية النسخ الاحتياطي
- [ ] نسخ احتياطية تلقائية
- [ ] جدولة يومية
- [ ] رفع إلى السحابة

### المرحلة 4.3: Connection Pooling
- [ ] تحسين اتصالات DB
- [ ] connection pool
- [ ] retry logic

## 👥 المساهمون

**الوكيل رقم 9**
- تاريخ الإنشاء: 30 سبتمبر 2025
- المهمة: 4.1 - تحسين نظام Migrations
- الحالة: ✅ مكتمل

---

**آخر تحديث**: 30 سبتمبر 2025  
**النسخة**: 1.0.0  
**الحالة**: ✅ جاهز للاستخدام في الإنتاج
