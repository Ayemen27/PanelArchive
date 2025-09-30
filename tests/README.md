# دليل الاختبارات - Tests Guide

## 📋 نظرة عامة

هذا المجلد يحتوي على جميع اختبارات المشروع باستخدام إطار عمل pytest. الاختبارات منظمة ومحولة من الاختبارات المدمجة في الملفات الأصلية إلى pytest format.

## 🗂️ هيكل الملفات

```
tests/
├── __init__.py                      # ملف تهيئة المجلد
├── test_environment_detector.py     # اختبارات كاشف البيئة (14 اختبار)
├── test_config_factory.py           # اختبارات مصنع الإعدادات (54 اختبار)
└── test_env_validator.py            # اختبارات مدقق المتغيرات (19 اختبار)
```

**إجمالي الاختبارات:** 87 اختبار

## 🚀 تشغيل الاختبارات

### المتطلبات الأساسية

قم بتثبيت حزم التطوير:

```bash
pip install -r requirements-dev.txt
```

أو تثبيت الحزم الأساسية فقط:

```bash
pip install pytest pytest-cov
```

### تشغيل جميع الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest

# تشغيل مع عرض تفصيلي
pytest -v

# تشغيل مع تغطية الكود
pytest --cov=. --cov-report=term-missing
```

### تشغيل اختبارات محددة

```bash
# اختبارات ملف معين
pytest tests/test_environment_detector.py

# اختبار فئة معينة
pytest tests/test_config_factory.py::TestBaseConfig

# اختبار دالة معينة
pytest tests/test_environment_detector.py::TestDetectEnvironment::test_returns_valid_environment
```

### تقارير التغطية

```bash
# تقرير HTML تفاعلي
pytest --cov=. --cov-report=html
# افتح htmlcov/index.html في المتصفح

# تقرير XML (لـ CI/CD)
pytest --cov=. --cov-report=xml
```

## 📊 نتائج الاختبارات

### test_environment_detector.py
- ✅ 14 اختبار لكاشف البيئة
- اختبارات detect_environment()
- اختبارات is_replit()
- اختبارات is_production()
- اختبارات get_environment_info()

### test_config_factory.py
- ✅ 54 اختبار لمصنع الإعدادات
- اختبارات BaseConfig
- اختبارات DevelopmentConfig
- اختبارات ProductionConfig
- اختبارات get_config() و get_config_for_environment()

### test_env_validator.py
- ✅ 19 اختبار لمدقق المتغيرات
- اختبارات ValidationResult
- اختبارات EnvValidator
- اختبارات validate_production_env()
- اختبارات validate_development_env()

## 🔧 إعدادات pytest

الإعدادات موجودة في `pytest.ini` في جذر المشروع:

- **testpaths:** tests/
- **python_files:** test_*.py
- **Coverage:** مفعل مع استثناء المجلدات غير الضرورية
- **Markers:** unit, integration, slow, security

## 🔍 CI/CD Integration

الاختبارات تُشغل تلقائياً في GitHub Actions:

### Workflow: Tests & Security (test.yml)
- يشتغل على Python 3.11 و 3.12
- يشغل جميع الاختبارات
- ينشئ تقرير تغطية
- يرفع النتائج إلى Codecov
- يشغل Bandit و Safety للأمان

### Workflow: Lint & Format (lint.yml)
- فحص الكود بـ flake8
- فحص التنسيق بـ black
- فحص ترتيب الـ imports بـ isort

## 📝 ملاحظات مهمة

1. **الاختبارات الأصلية محفوظة:** الاختبارات في الملفات الأصلية (`if __name__ == "__main__"`) لا تزال موجودة ولم تُحذف.

2. **pytest format:** تم تحويل جميع الاختبارات إلى pytest format باستخدام:
   - Classes: `class Test*`
   - Functions: `def test_*()`
   - Fixtures: `@pytest.fixture`
   - Monkeypatch: لتعديل متغيرات البيئة

3. **Coverage:** تغطية الكود تستثني:
   - مجلد tests/
   - مجلدات BTPanel, class, class_v2, pyenv, etc.

## 🛠️ كتابة اختبارات جديدة

عند إضافة اختبارات جديدة:

1. أنشئ ملف جديد بنمط `test_*.py`
2. استخدم فئات بنمط `class Test*`
3. استخدم دوال بنمط `def test_*()`
4. استخدم fixtures عند الحاجة
5. أضف docstrings بالعربية

مثال:

```python
class TestMyFeature:
    """اختبارات لميزة معينة"""
    
    def test_basic_functionality(self):
        """الاختبار: الوظيفة الأساسية تعمل"""
        assert True
    
    @pytest.fixture
    def setup_data(self):
        """إعداد البيانات للاختبار"""
        return {"key": "value"}
```

## 🔗 روابط مفيدة

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [GitHub Actions Workflows](../.github/workflows/)
