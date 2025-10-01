import json
import os
import datetime
from typing import Dict, Any, List

class ServiceMapper:
    def __init__(self):
        self.results: Dict[str, List[Dict[str, Any]]] = {
            'messaging_services': [],
            'email_services': [],
            'cloud_storage': [],
            'databases': [],
            'api_integrations': []
        }
        self.scan_dir = 'فحص' # المجلد الجديد الذي سيتم نقل الملفات إليه
        os.makedirs(self.scan_dir, exist_ok=True) # إنشاء المجلد إذا لم يكن موجوداً

    def _load_service_data(self, service_type: str, filename: str) -> None:
        """تحميل بيانات خدمة من ملف JSON."""
        filepath = os.path.join(self.scan_dir, filename) # تحديد المسار داخل مجلد "فحص"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.results[service_type].extend(data)
                    else:
                        print(f"⚠️ تحذير: محتوى الملف {filename} ليس قائمة.")
            except json.JSONDecodeError:
                print(f"❌ خطأ في تحليل JSON للملف: {filename}")
            except Exception as e:
                print(f"❌ خطأ غير متوقع أثناء قراءة {filename}: {e}")
        else:
            print(f"⚠️ تحذير: الملف {filename} غير موجود في المجلد {self.scan_dir}.")

    def map_services(self) -> Dict[str, List[Dict[str, Any]]]:
        """تحليل أنواع مختلفة من الخدمات."""
        print("🔍 جاري تحليل خدمات المراسلة...")
        self._load_service_data('messaging_services', 'messaging_services.json')

        print("📧 جاري تحليل خدمات البريد الإلكتروني...")
        self._load_service_data('email_services', 'email_services.json')

        print("☁️ جاري تحليل خدمات التخزين السحابي...")
        self._load_service_data('cloud_storage', 'cloud_storage.json')

        print("🗄️ جاري تحليل قواعد البيانات...")
        self._load_service_data('databases', 'databases.json')

        print("🔌 جاري تحليل تكاملات API...")
        self._load_service_data('api_integrations', 'api_integrations.json')

        # نقل الملفات بعد التحليل (إذا كانت موجودة)
        for filename in ['messaging_services.json', 'email_services.json', 'cloud_storage.json', 'databases.json', 'api_integrations.json']:
            original_path = filename
            new_path = os.path.join(self.scan_dir, filename)
            if os.path.exists(original_path):
                try:
                    os.rename(original_path, new_path)
                    print(f"✅ تم نقل {filename} إلى المجلد {self.scan_dir}")
                except OSError as e:
                    print(f"❌ خطأ في نقل الملف {filename}: {e}")


        return self.results

    def generate_report(self) -> Dict[str, Any]:
        """إنشاء تقرير شامل للخدمات"""
        summary = {
            'total_services': sum(len(services) for services in self.results.values() if isinstance(services, list)),
            'messaging_services_count': len(self.results['messaging_services']),
            'email_services_count': len(self.results['email_services']),
            'cloud_storage_count': len(self.results['cloud_storage']),
            'databases_count': len(self.results['databases']),
            'api_integrations_count': len(self.results['api_integrations']),
            'scan_timestamp': datetime.datetime.now().isoformat()
        }

        return {
            'summary': summary,
            'services': self.results,
            'recommendations': self._get_service_recommendations()
        }

    def _get_service_recommendations(self) -> List[str]:
        """توصيات أمنية للخدمات"""
        recommendations = []

        if self.results['messaging_services']:
            recommendations.append("💬 تأمين خدمات الرسائل وحماية الرموز المميزة")

        if self.results['cloud_storage']:
            recommendations.append("☁️ مراجعة أذونات التخزين السحابي")

        if self.results['databases']:
            recommendations.append("🗄️ تأمين قواعد البيانات وتشفير البيانات الحساسة")

        recommendations.extend([
            "🔐 استخدام مصادقة ثنائية العامل",
            "📝 مراجعة أذونات الخدمات بانتظام",
            "🛡️ تحديث الخدمات والمكتبات"
        ])

        return recommendations

def main():
    mapper = ServiceMapper()
    print("🔍 بدء تحليل الخدمات المرتبطة...")

    results = mapper.map_services()
    report = mapper.generate_report()

    # حفظ التقرير داخل مجلد "فحص"
    report_filename = 'service_mapping_report.json'
    report_path = os.path.join('.', mapper.scan_dir, report_filename) # تحديد المسار داخل مجلد "فحص"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ تم إنشاء تقرير تحليل الخدمات: {report_path}")
    print(f"📊 النتائج: {report['summary']['total_services']} خدمة، {report['summary']['databases_count']} قاعدة بيانات")

    return report

if __name__ == "__main__":
    main()