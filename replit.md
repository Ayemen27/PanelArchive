# aaPanel - لوحة تحكم الخادم

## نظرة عامة على المشروع

**aaPanel** هو لوحة تحكم قوية لإدارة الخوادم مكتوبة بلغة Python/Flask. يتيح للمستخدمين إدارة الخوادم بسهولة من خلال واجهة ويب رسومية.

### المعلومات الأساسية
- **اللغة الأساسية**: Python 3.12
- **الإطار**: Flask مع Gunicorn
- **قاعدة البيانات**: SQLite (محلياً) / MySQL/PostgreSQL (إنتاج)
- **المنفذ الافتراضي**: 5000
- **المسار الافتراضي للإنتاج**: `/www/server/panel`

---

## الوضع الحالي للمشروع (آخر تحديث: 30 سبتمبر 2025)

### ✅ ما تم إنجازه
1. **نظام اكتشاف البيئة**: ✅ مكتمل (نسبة الإنجاز: 100%)
   - ملف `environment_detector.py` يكتشف البيئة تلقائياً
   - يميز بين Replit و VPS بدقة عالية
   - دعم التحكم اليدوي عبر متغير ENVIRONMENT
   - 14 اختبار ناجح بنسبة 100%

2. **Factory Pattern للإعدادات**: ✅ مكتمل (نسبة الإنجاز: 100%)
   - ملف `config_factory.py` يوفر نظام إعدادات موحد
   - BaseConfig، DevelopmentConfig، ProductionConfig
   - دالة `get_config()` للحصول على الإعدادات تلقائياً
   - 54 اختبار ناجح بنسبة 100%
   - إلزام SECRET_KEY في الإنتاج
   - دعم MySQL+PyMySQL و PostgreSQL

3. **إدارة المتغيرات البيئية**: ✅ مكتمل (نسبة الإنجاز: 100%)
   - ملف `.env.example` يوثق 18 متغير بيئة
   - ملف `env_validator.py` للتحقق من صحة المتغيرات
   - 19 اختبار ناجح بنسبة 100%
   - تصنيف واضح للمتغيرات (إلزامية/اختيارية)
   - حماية الأسرار الحساسة

3. **البنية الأساسية**: 
   - التطبيق يعمل على Replit
   - ملف `.env` تم إعداده مع المتغيرات الأساسية
   - `runserver.py` جاهز ويعمل

4. **قاعدة البيانات**:
   - دعم متعدد لقواعد البيانات (SQLite, MySQL, PostgreSQL)
   - نظام migrations متقدم

5. **الأمان**:
   - نظام مراقبة أمني متقدم
   - دعم SSL/HTTPS
   - جدار حماية

### ⚠️ ما يحتاج تطوير
1. **CI/CD Pipeline**: غير موجود (نسبة الإنجاز: 0%)
2. **نظام المراقبة والتنبيهات**: غير موجود (نسبة الإنجاز: 0%)
3. **Docker/Containerization**: غير موجود (نسبة الإنجاز: 0%)

---

## البيئات المستهدفة

### 1. بيئة التطوير (Replit)
- المنفذ: ديناميكي من متغير `PORT`
- قاعدة البيانات: SQLite محلية
- بدون nginx
- وضع DEBUG مفعّل

### 2. بيئة الإنتاج (VPS)
- المنفذ: 5000 (خلف nginx)
- قاعدة البيانات: MySQL/PostgreSQL خارجية
- nginx كـ reverse proxy مع SSL
- systemd لإدارة العمليات

---

## البنية التقنية الحالية

### الملفات الرئيسية
- `runserver.py` - نقطة دخول التطبيق
- `runconfig.py` - إعدادات Gunicorn
- `environment_detector.py` - ✨ اكتشاف البيئة التلقائي
- `config_factory.py` - ✨ نظام الإعدادات الموحد (Factory Pattern)
- `.env.example` - ✨ **جديد**: توثيق متغيرات البيئة (18 متغير)
- `env_validator.py` - ✨ **جديد**: التحقق من صحة المتغيرات البيئية
- `BTPanel/__init__.py` - تهيئة Flask
- `class/config.py` - إعدادات قديمة
- `class_v2/config_v2.py` - إعدادات محدثة

### المجلدات المهمة
- `BTPanel/` - التطبيق الأساسي
- `class/` & `class_v2/` - المنطق البرمجي
- `data/` - ملفات البيانات والإعدادات
- `config/` - ملفات الإعدادات
- `vhost/` - إعدادات nginx/apache

---

## طريقة استخدام نظام اكتشاف البيئة

### الاستيراد والاستخدام الأساسي
```python
# استيراد الدوال الأساسية
from environment_detector import detect_environment, is_replit, is_production, get_environment_info

# اكتشاف البيئة الحالية
env = detect_environment()
print(f"البيئة الحالية: {env}")  # 'development' أو 'production'

# التحقق من نوع البيئة
if is_replit():
    print("نحن في بيئة Replit")
    
if is_production():
    print("نحن في بيئة الإنتاج")
```

### الحصول على معلومات تفصيلية
```python
# الحصول على معلومات شاملة عن البيئة
info = get_environment_info()
print(f"البيئة: {info['environment']}")
print(f"Replit: {info['is_replit']}")
print(f"إنتاج: {info['is_production']}")
print(f"نسخة Python: {info['python_version']}")
```

### التحكم اليدوي بالبيئة
يمكنك التحكم يدوياً بالبيئة عبر متغير `ENVIRONMENT`:

```bash
# في ملف .env أو terminal
ENVIRONMENT=development  # لفرض بيئة التطوير
ENVIRONMENT=production   # لفرض بيئة الإنتاج
```

**ملاحظة**: التحكم اليدوي له الأولوية على الاكتشاف التلقائي.

---

## طريقة استخدام نظام الإعدادات الموحد (Config Factory)

### الاستيراد والاستخدام الأساسي
```python
# استيراد دالة get_config
from config_factory import get_config

# الحصول على الإعدادات المناسبة للبيئة الحالية
config = get_config()

# استخدام الإعدادات في التطبيق
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT)
```

### الحصول على إعدادات بيئة محددة
```python
from config_factory import get_config_for_environment

# الحصول على إعدادات بيئة التطوير
dev_config = get_config_for_environment('development')

# الحصول على إعدادات بيئة الإنتاج
prod_config = get_config_for_environment('production')
```

### الإعدادات المتاحة

#### إعدادات مشتركة (BaseConfig):
- `SECRET_KEY` - مفتاح الأمان (يتم توليده تلقائياً في التطوير)
- `DATABASE_URI` - رابط قاعدة البيانات
- `PORT` - منفذ التطبيق
- `HOST` - عنوان الخادم

#### إعدادات التطوير (DevelopmentConfig):
- `DEBUG = True`
- قاعدة بيانات SQLite محلية
- `LOG_LEVEL = 'DEBUG'`
- `CORS` مفعّل
- `AUTO_RELOAD = True`

#### إعدادات الإنتاج (ProductionConfig):
- `DEBUG = False`
- قاعدة بيانات MySQL/PostgreSQL خارجية
- **SECRET_KEY إلزامي** (يرفع خطأ إذا لم يكن موجوداً)
- `FORCE_HTTPS = True`
- `SESSION_COOKIE_SECURE = True`
- دعم SSL/TLS

### متغيرات البيئة المطلوبة

#### للإنتاج (Production):
```bash
# إلزامية
SECRET_KEY=your-secret-key-here

# قاعدة البيانات
DATABASE_TYPE=mysql  # أو postgresql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=production_db
DB_DRIVER=pymysql  # اختياري (افتراضي: pymysql - قيم مقبولة: pymysql, mysqldb, mysqlconnector)

# SSL (اختياري)
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

#### للتطوير (Development):
```bash
# كل شيء اختياري - يتم استخدام القيم الافتراضية
PORT=5000  # اختياري
```

**ملاحظة مهمة**: في الإنتاج، يجب تعيين `SECRET_KEY` وإلا سيتم رفع خطأ `RuntimeError`.

---

## تفضيلات المستخدم والفريق

### متطلبات التوثيق
- يجب تحديث حالة كل مهمة فور إنجازها
- توثيق واضح لما تم إنجازه وما تبقى
- تمكين الفريق من معرفة نقطة التوقف ونقطة الاستكمال

### التواصل
- **اللغة المفضلة**: العربية فقط في جميع الردود
- التوثيق يجب أن يكون واضح ومفصل

---

## القرارات المعمارية

### القرار 1: استخدام Factory Pattern للإعدادات
- **التاريخ**: 30 سبتمبر 2025
- **السبب**: لتسهيل التبديل بين بيئات مختلفة والحفاظ على نظافة الكود
- **الحالة**: ✅ تم التنفيذ
- **الملفات**: `config_factory.py`

### القرار 2: اعتماد Docker للنقل
- **التاريخ**: 30 سبتمبر 2025
- **السبب**: ضمان توافق البيئات
- **الحالة**: قيد التخطيط

---

## المشاكل المعروفة

1. **التعقيد**: البنية معقدة ومصممة للـ VPS أكثر من التطوير المحلي
2. **الاعتماديات**: بعض الميزات تتطلب root access وخدمات نظام
3. **التوافق**: بعض الميزات قد لا تعمل في Replit

---

## الملاحظات الفنية

### نقاط مهمة للمطورين
- التطبيق يستخدم Gunicorn مع GeventWebSocketWorker
- المسار الافتراضي محدد في الكود: `/www/server/panel`
- المنفذ يُقرأ من ملف `data/port.pl`
- دعم WebSocket موجود

### تحذيرات
- لا تشغل التطبيق كـ root
- تأكد من وجود المجلدات المطلوبة قبل التشغيل
- بعض الميزات تحتاج صلاحيات نظام

---

## آخر التغييرات (السجل)

### 30 سبتمبر 2025 - المساء
- ✅ **المهمة 1.3 مكتملة**: تم إنشاء `.env.example` و `env_validator.py`
  - ملف `.env.example` يوثق 18 متغير بيئة بشكل شامل
  - ملف `env_validator.py` للتحقق من صحة المتغيرات
  - 19 اختبار ناجح بنسبة 100%
  - إصلاح 4 مشاكل حرجة حددها Architect:
    * إصلاح ENVIRONMENT validation (يقبل فقط development/production)
    * إصلاح MySQL driver validation (pymysql, mysqldb, mysqlconnector)
    * إصلاح فحص SSL files الافتراضية
    * تحسين رسائل الخطأ وال validation logic
  - تصنيف واضح للمتغيرات (إلزامية/اختيارية/حساسة)
  - توثيق ثنائي اللغة (عربي/إنجليزي)
  - تحديث التوثيق الكامل
  - رفع التقدم الإجمالي من 60% إلى 64%

- ✅ **المهمة 1.2 مكتملة**: تم إنشاء ملف `config_factory.py`
  - نظام إعدادات موحد (Factory Pattern)
  - BaseConfig، DevelopmentConfig، ProductionConfig
  - دالة `get_config()` للحصول على الإعدادات تلقائياً
  - 54 اختبار ناجح بنسبة 100%
  - إلزام SECRET_KEY في الإنتاج للأمان
  - دعم MySQL+PyMySQL و PostgreSQL
  - إصلاح 3 مشاكل حرجة حددها Architect
  - تحديث التوثيق الكامل (replit.md، خطة_التطوير.md، قائمة_التحقق.md)
  - رفع التقدم الإجمالي من 51% إلى 60%

- ✅ **المهمة 1.1 مكتملة**: تم إنشاء ملف `environment_detector.py`
  - نظام اكتشاف بيئة متقدم (Replit/VPS)
  - 14 اختبار ناجح بنسبة 100%
  - يكتشف البيئة بدقة عالية
  - يدعم التحكم اليدوي عبر متغير ENVIRONMENT
  - توثيق شامل بالعربية

- ⚠️ **تنبيه أمني**: تم رصد أسرار حساسة في .env (سيتم معالجتها في المهمة 1.3)

### 30 سبتمبر 2025
- تم إنشاء ملف التوثيق الأولي
- تم فحص البنية الحالية
- تم تحديد نقاط الضعف والقوة
