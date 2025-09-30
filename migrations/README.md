# aaPanel Database Migrations

## نظرة عامة

هذا المجلد يحتوي على نظام إدارة migrations لقاعدة بيانات aaPanel باستخدام Alembic.

## الملفات الرئيسية

- `env.py` - بيئة Alembic التي تتكامل مع config_factory
- `script.py.mako` - Template لإنشاء migrations جديدة
- `migrate.py` - سكريبت إدارة migrations (واجهة سهلة)
- `versions/` - مجلد يحتوي على جميع migrations

## الاستخدام

### 1. عرض الحالة الحالية
```bash
python migrations/migrate.py current
```

### 2. عرض سجل Migrations
```bash
python migrations/migrate.py history
```

### 3. إنشاء Migration جديد
```bash
python migrations/migrate.py create "وصف التغيير"
```

### 4. تطبيق Migrations
```bash
# ترقية إلى آخر إصدار
python migrations/migrate.py upgrade

# ترقية إلى إصدار معين
python migrations/migrate.py upgrade --revision <revision_id>
```

### 5. التراجع عن Migration
```bash
# التراجع خطوة واحدة
python migrations/migrate.py downgrade

# التراجع إلى إصدار معين
python migrations/migrate.py downgrade --revision <revision_id>
```

## البنية الحالية (Baseline)

Migration `001_initial_baseline` يوثق البنية الحالية للقاعدة دون تغييرها:

### الجداول الرئيسية:
- `backup` - إدارة النسخ الاحتياطية
- `binding` - ربط النطاقات
- `config` - إعدادات النظام
- `crontab` - المهام المجدولة
- `databases` - إدارة قواعد البيانات
- `firewall` - قواعد الجدار الناري
- `ftps` - حسابات FTP
- `logs` - سجلات النظام
- `sites` - إدارة المواقع
- `domain` - سجلات النطاقات
- `users` - حسابات المستخدمين
- `tasks` - قائمة المهام
- و15 جدول آخر للميزات المختلفة

## أمثلة Migrations

### مثال 1: إضافة عمود جديد
```python
def upgrade():
    with op.batch_alter_table('sites') as batch_op:
        batch_op.add_column(sa.Column('ssl_enabled', sa.Boolean(), nullable=True))

def downgrade():
    with op.batch_alter_table('sites') as batch_op:
        batch_op.drop_column('ssl_enabled')
```

### مثال 2: إنشاء جدول جديد
```python
def upgrade():
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('api_keys')
```

### مثال 3: تعديل عمود
```python
def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('email', nullable=False)

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('email', nullable=True)
```

## ملاحظات مهمة

### SQLite و batch_alter_table
عند العمل مع SQLite، استخدم دائماً `batch_alter_table`:
```python
with op.batch_alter_table('table_name') as batch_op:
    batch_op.add_column(...)
```

### التكامل مع config_factory
يستخدم النظام `config_factory.get_config()` للحصول على DATABASE_URI تلقائياً:
- في التطوير: SQLite (`data/dev_database.db`)
- في الإنتاج: PostgreSQL أو MySQL

### الاختبار قبل الإنتاج
**دائماً** اختبر migrations في بيئة التطوير قبل تطبيقها في الإنتاج:
```bash
# في التطوير
ENVIRONMENT=development python migrations/migrate.py upgrade

# بعد التأكد، في الإنتاج
ENVIRONMENT=production python migrations/migrate.py upgrade
```

## استكشاف الأخطاء

### خطأ: "Could not determine current revision"
```bash
# أنشئ جدول alembic_version يدوياً
alembic stamp head
```

### خطأ: "Target database is not up to date"
```bash
# عرض الحالة الحالية
python migrations/migrate.py current

# الترقية إلى آخر إصدار
python migrations/migrate.py upgrade
```

### خطأ: "Can't locate revision"
```bash
# تحقق من سجل migrations
python migrations/migrate.py history
```

## الاختبارات

لاختبار نظام migrations:
```bash
pytest tests/test_migrations.py -v
```

## المساهمة

عند إنشاء migration جديد:
1. ✅ استخدم أسماء وصفية
2. ✅ اكتب دالتي upgrade و downgrade
3. ✅ اختبر Migration في بيئة التطوير
4. ✅ وثق التغييرات في docstring
5. ✅ تأكد من rollback يعمل بشكل صحيح

---

**تاريخ الإنشاء**: 30 سبتمبر 2025  
**المسؤول**: الوكيل رقم 9  
**الحالة**: ✅ جاهز للاستخدام
