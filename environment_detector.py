# coding: utf-8
"""
كاشف البيئة التلقائي - Environment Detector
يكتشف تلقائياً البيئة التي يعمل فيها التطبيق (Replit أو VPS)
"""

import os
import sys


def detect_environment():
    """
    تكتشف البيئة الحالية تلقائياً
    
    الأولويات:
    1. متغير ENVIRONMENT (للتحكم اليدوي)
    2. فحص متغيرات Replit (REPL_ID, REPL_OWNER)
    3. فحص وجود /etc/systemd/system (للكشف عن VPS)
    
    Returns:
        str: "development" للبيئة التطويرية (Replit)
             "production" للبيئة الإنتاجية (VPS)
    """
    # أولاً: فحص التحكم اليدوي عبر متغير ENVIRONMENT
    manual_env = os.environ.get('ENVIRONMENT', '').lower()
    if manual_env in ['development', 'production']:
        return manual_env
    
    # ثانياً: فحص متغيرات Replit
    repl_id = os.environ.get('REPL_ID')
    repl_owner = os.environ.get('REPL_OWNER')
    
    if repl_id or repl_owner:
        return 'development'
    
    # ثالثاً: فحص وجود /etc/systemd/system للكشف عن VPS
    if os.path.exists('/etc/systemd/system'):
        return 'production'
    
    # افتراضياً: بيئة تطويرية
    return 'development'


def is_replit():
    """
    تتحقق إذا كانت البيئة الحالية هي Replit
    
    Returns:
        bool: True إذا كانت البيئة Replit، False خلاف ذلك
    """
    repl_id = os.environ.get('REPL_ID')
    repl_owner = os.environ.get('REPL_OWNER')
    return bool(repl_id or repl_owner)


def is_production():
    """
    تتحقق إذا كانت البيئة الحالية هي بيئة إنتاجية
    
    Returns:
        bool: True إذا كانت بيئة إنتاجية، False خلاف ذلك
    """
    return detect_environment() == 'production'


def get_environment_info():
    """
    ترجع معلومات تفصيلية عن البيئة الحالية
    
    Returns:
        dict: قاموس يحتوي على معلومات البيئة
            - environment: البيئة الحالية (development/production)
            - is_replit: هل البيئة Replit
            - is_production: هل البيئة إنتاجية
            - repl_id: معرف Replit (إن وجد)
            - repl_owner: مالك Replit (إن وجد)
            - has_systemd: وجود systemd (للـ VPS)
            - manual_override: التحكم اليدوي مفعل
            - python_version: إصدار Python
            - os_name: اسم نظام التشغيل
    """
    env = detect_environment()
    manual_override = os.environ.get('ENVIRONMENT', '').lower() in ['development', 'production']
    
    info = {
        'environment': env,
        'is_replit': is_replit(),
        'is_production': is_production(),
        'repl_id': os.environ.get('REPL_ID'),
        'repl_owner': os.environ.get('REPL_OWNER'),
        'has_systemd': os.path.exists('/etc/systemd/system'),
        'manual_override': manual_override,
        'python_version': sys.version.split()[0],
        'os_name': os.name
    }
    
    return info


# ==================== الاختبارات - Unit Tests ====================

if __name__ == "__main__":
    print("=" * 70)
    print("بدء اختبار كاشف البيئة - Environment Detector Tests")
    print("=" * 70)
    print()
    
    # حفظ المتغيرات الأصلية
    original_env = os.environ.get('ENVIRONMENT')
    original_repl_id = os.environ.get('REPL_ID')
    original_repl_owner = os.environ.get('REPL_OWNER')
    
    # متغير لحساب الاختبارات
    tests_passed = 0
    tests_failed = 0
    total_tests = 0
    
    def run_test(test_name, condition, expected=True):
        """دالة مساعدة لتشغيل الاختبار"""
        global tests_passed, tests_failed, total_tests
        total_tests += 1
        
        result = condition == expected
        status = "✓ نجح" if result else "✗ فشل"
        
        if result:
            tests_passed += 1
            print(f"[{status}] {test_name}")
        else:
            tests_failed += 1
            print(f"[{status}] {test_name} - القيمة: {condition}, المتوقع: {expected}")
        
        return result
    
    # ==================== الاختبار 1: البيئة الحالية ====================
    print("\n--- الاختبار 1: الكشف عن البيئة الحالية ---")
    current_env = detect_environment()
    print(f"البيئة الحالية المكتشفة: {current_env}")
    run_test("الاختبار: البيئة المكتشفة إما development أو production", 
             current_env in ['development', 'production'])
    
    # ==================== الاختبار 2: كشف Replit ====================
    print("\n--- الاختبار 2: كشف بيئة Replit ---")
    is_repl = is_replit()
    print(f"هل البيئة Replit؟ {is_repl}")
    has_repl_vars = bool(os.environ.get('REPL_ID') or os.environ.get('REPL_OWNER'))
    run_test("الاختبار: is_replit() يطابق وجود متغيرات Replit", 
             is_repl, has_repl_vars)
    
    # ==================== الاختبار 3: كشف بيئة الإنتاج ====================
    print("\n--- الاختبار 3: كشف بيئة الإنتاج ---")
    is_prod = is_production()
    print(f"هل البيئة إنتاجية؟ {is_prod}")
    run_test("الاختبار: is_production() يطابق detect_environment()", 
             is_prod, current_env == 'production')
    
    # ==================== الاختبار 4: معلومات البيئة ====================
    print("\n--- الاختبار 4: الحصول على معلومات البيئة التفصيلية ---")
    env_info = get_environment_info()
    print("المعلومات التفصيلية:")
    for key, value in env_info.items():
        print(f"  - {key}: {value}")
    
    run_test("الاختبار: environment_info يحتوي على environment", 
             'environment' in env_info)
    run_test("الاختبار: environment_info يحتوي على is_replit", 
             'is_replit' in env_info)
    run_test("الاختبار: environment_info يحتوي على is_production", 
             'is_production' in env_info)
    run_test("الاختبار: environment_info يحتوي على python_version", 
             'python_version' in env_info)
    run_test("الاختبار: قيمة environment في المعلومات صحيحة", 
             env_info['environment'] == current_env)
    
    # ==================== الاختبار 5: التحكم اليدوي ====================
    print("\n--- الاختبار 5: اختبار التحكم اليدوي عبر ENVIRONMENT ---")
    
    # اختبار: فرض development
    os.environ['ENVIRONMENT'] = 'development'
    forced_dev = detect_environment()
    run_test("الاختبار: ENVIRONMENT=development يفرض development", 
             forced_dev == 'development')
    
    # اختبار: فرض production
    os.environ['ENVIRONMENT'] = 'production'
    forced_prod = detect_environment()
    run_test("الاختبار: ENVIRONMENT=production يفرض production", 
             forced_prod == 'production')
    
    # اختبار: قيمة غير صالحة
    os.environ['ENVIRONMENT'] = 'invalid_value'
    auto_detect = detect_environment()
    run_test("الاختبار: ENVIRONMENT بقيمة غير صالحة يعود للكشف التلقائي", 
             auto_detect in ['development', 'production'])
    
    # ==================== الاختبار 6: محاكاة بيئات مختلفة ====================
    print("\n--- الاختبار 6: محاكاة بيئات مختلفة ---")
    
    # إزالة التحكم اليدوي
    if 'ENVIRONMENT' in os.environ:
        del os.environ['ENVIRONMENT']
    
    # محاكاة Replit (حفظ المتغيرات الأصلية)
    os.environ['REPL_ID'] = 'test-repl-id-12345'
    simulated_repl = detect_environment()
    run_test("الاختبار: وجود REPL_ID يكشف development", 
             simulated_repl == 'development')
    run_test("الاختبار: is_replit() يعود True مع REPL_ID", 
             is_replit(), True)
    
    # إزالة متغيرات Replit
    if 'REPL_ID' in os.environ:
        del os.environ['REPL_ID']
    if 'REPL_OWNER' in os.environ:
        del os.environ['REPL_OWNER']
    
    # اختبار بدون متغيرات Replit
    no_repl_env = detect_environment()
    run_test("الاختبار: is_replit() يعود False بدون متغيرات Replit", 
             is_replit(), False)
    
    # ==================== استعادة المتغيرات الأصلية ====================
    if original_env:
        os.environ['ENVIRONMENT'] = original_env
    elif 'ENVIRONMENT' in os.environ:
        del os.environ['ENVIRONMENT']
    
    if original_repl_id:
        os.environ['REPL_ID'] = original_repl_id
    elif 'REPL_ID' in os.environ:
        del os.environ['REPL_ID']
    
    if original_repl_owner:
        os.environ['REPL_OWNER'] = original_repl_owner
    elif 'REPL_OWNER' in os.environ:
        del os.environ['REPL_OWNER']
    
    # ==================== ملخص النتائج ====================
    print("\n" + "=" * 70)
    print("ملخص نتائج الاختبار - Test Summary")
    print("=" * 70)
    print(f"إجمالي الاختبارات: {total_tests}")
    print(f"الاختبارات الناجحة: {tests_passed} ✓")
    print(f"الاختبارات الفاشلة: {tests_failed} ✗")
    
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"نسبة النجاح: {success_rate:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 جميع الاختبارات نجحت!")
        sys.exit(0)
    else:
        print(f"\n⚠️ هناك {tests_failed} اختبار(ات) فشل(ت)")
        sys.exit(1)
