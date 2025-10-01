import json
import os
import subprocess

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تنفيذ الأمر {command}: {e}")
        print(f"   الخطأ القياسي: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print(f"❌ الأمر غير موجود: {command[0]}")
        return None

def get_git_repo_info():
    info = {}
    info['branch'] = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    info['commit_hash'] = run_command(['git', 'rev-parse', '--short', 'HEAD'])
    info['last_commit_author'] = run_command(['git', 'log', '-1', '--pretty=format:%an'])
    info['last_commit_date'] = run_command(['git', 'log', '-1', '--pretty=format:%cd'])
    info['remote_url'] = run_command(['git', 'config', '--get', 'remote.origin.url'])
    return info

def check_dependencies(dependencies):
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    return missing

def perform_security_checks(repo_path='.'):
    report = {}
    report['git_info'] = get_git_repo_info()
    report['dependencies'] = {}

    # قائمة بالاعتمادات التي يجب التحقق منها
    dependencies_to_check = ['requests', 'beautifulsoup4', 'json', 'os', 'subprocess']
    missing_deps = check_dependencies(dependencies_to_check)
    report['dependencies']['missing'] = missing_deps
    report['dependencies']['all_checked'] = dependencies_to_check

    # التحقق من وجود ملفات حساسة محتملة
    sensitive_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(ext in file.lower() for ext in ['.env', '.config', '.pem', '.key', '.yml', '.yaml', '.json', '.xml']):
                sensitive_files.append(os.path.join(root, file))
    report['potential_sensitive_files'] = sensitive_files

    # التحقق من الأوامر الخطرة المحتملة في السكربتات
    dangerous_commands = []
    scripts_to_check = ['run_all_scans.py'] # أضف ملفات أخرى إذا لزم الأمر
    for script in scripts_to_check:
        script_path = os.path.join(repo_path, script)
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "subprocess.run(" in content or "os.system(" in content:
                    # تحليل أكثر تفصيلاً لتحديد الأوامر الخطرة
                    # هذا مجرد مثال بسيط
                    if "shell=True" in content:
                         dangerous_commands.append(f"{script}: يستخدم subprocess/os.system مع shell=True")
    report['dangerous_commands_in_scripts'] = dangerous_commands

    # يمكنك إضافة المزيد من التحققات هنا
    # مثال: التحقق من صلاحيات الملفات، البحث عن كلمات مرور في الكود، إلخ.

    return report

def create_report_directory():
    report_dir = "فحص"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        print(f"✅ تم إنشاء المجلد: {report_dir}")
    return report_dir

def main():
    report_dir = create_report_directory()

    print("🚀 بدء عمليات الفحص الأمني...")
    security_report_data = perform_security_checks()

    # حفظ التقرير داخل مجلد "فحص"
    report_filename = 'security_analysis_report.json'
    report_path = os.path.join(report_dir, report_filename)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(security_report_data, f, ensure_ascii=False, indent=2)

    print(f"✅ تم إنشاء تقرير الفحص الأمني: {report_path}")
    print("\n--- ملخص التقرير ---")
    print(json.dumps(security_report_data, ensure_ascii=False, indent=2))
    print("\n🎉 اكتملت عمليات الفحص الأمني.")

if __name__ == "__main__":
    main()