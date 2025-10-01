import json
import os
import datetime

class SecurityScanner:
    def __init__(self):
        self.master_report = {}
        self.reports = {}
        self.scan_timestamp = datetime.datetime.now().isoformat()

    def add_report(self, report_type, report_data):
        """إضافة تقرير إلى الماسح"""
        self.reports[report_type] = report_data
        # دمج التقرير في التقرير الرئيسي (كمثال بسيط)
        self.master_report[report_type] = report_data.get('summary', 'لا يوجد ملخص')

    def _get_file_size(self, filename):
        """الحصول على حجم الملف بالبايت"""
        try:
            return os.path.getsize(filename)
        except FileNotFoundError:
            return 0

    def _create_index_file(self):
        """إنشاء ملف فهرس للتقارير"""
        import os

        index_content = {
            'scan_info': {
                'timestamp': self.scan_timestamp,
                'total_reports': len(self.reports) + 1
            },
            'available_reports': {
                'comprehensive_report': {
                    'file': 'comprehensive_security_report.json',
                    'description': 'التقرير الرئيسي الشامل',
                    'size': self._get_file_size('comprehensive_security_report.json')
                },
                'security_report': {
                    'file': 'security_analysis_report.json',
                    'description': 'تقرير فحص البيانات الحساسة',
                    'size': self._get_file_size('security_analysis_report.json')
                },
                'network_report': {
                    'file': 'network_analysis_report.json',
                    'description': 'تقرير فحص الشبكة والاتصالات',
                    'size': self._get_file_size('network_analysis_report.json')
                },
                'service_report': {
                    'file': 'service_mapping_report.json',
                    'description': 'تقرير تحليل الخدمات المرتبطة',
                    'size': self._get_file_size('service_mapping_report.json')
                },
                'html_summary': {
                    'file': 'security_summary.html',
                    'description': 'ملخص بصري تفاعلي',
                    'size': self._get_file_size('security_summary.html')
                }
            },
            'instructions': {
                'view_main_report': 'افتح comprehensive_security_report.json',
                'view_html_summary': 'افتح security_summary.html في المتصفح',
                'access_detailed_reports': 'افتح التقارير التفصيلية حسب الحاجة'
            }
        }

        with open('reports_index.json', 'w', encoding='utf-8') as f:
            json.dump(index_content, f, ensure_ascii=False, indent=2)

    def _generate_html_summary(self):
        """إنشاء ملخص HTML للتقارير"""
        html_content = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ملخص فحص الأمان</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 20px; background-color: #f4f4f4; color: #333; }
                .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;}
                h2 { color: #34495e; margin-top: 20px;}
                table { width: 100%; border-collapse: collapse; margin-top: 15px; }
                th, td { border: 1px solid #ddd; padding: 10px; text-align: right; }
                th { background-color: #ecf0f1; color: #2c3e50; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .report-link { color: #3498db; text-decoration: none; }
                .report-link:hover { text-decoration: underline; }
                .summary-section { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>ملخص فحص الأمان الشامل</h1>
                <p><strong>وقت الفحص:</strong> {scan_timestamp}</p>
                <div class="summary-section">
                    <h2>التقرير الرئيسي</h2>
                    <p>يحتوي هذا التقرير على ملخص لجميع النتائج.</p>
                    <p><a href="comprehensive_security_report.json" class="report-link">فتح التقرير الرئيسي</a></p>
                </div>
        """.format(scan_timestamp=self.scan_timestamp)

        # إضافة التقارير التفصيلية
        html_content += """
                <div class="summary-section">
                    <h2>التقارير التفصيلية</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>نوع التقرير</th>
                                <th>اسم الملف</th>
                                <th>حجم الملف</th>
                                <th>الوصف</th>
                            </tr>
                        </thead>
                        <tbody>
        """

        for report_type, report_data in self.reports.items():
            if 'error' not in report_data:
                filename = f'{report_type}_detailed_report.json'
                description = report_data.get('description', f'تقرير تفصيلي لـ {report_type}')
                size = self._get_file_size(filename)
                html_content += f"""
                            <tr>
                                <td>{report_type.capitalize()}</td>
                                <td><a href="{filename}" class="report-link">{filename}</a></td>
                                <td>{size} بايت</td>
                                <td>{description}</td>
                            </tr>
                """

        html_content += """
                        </tbody>
                    </table>
                </div>
        """

        # إضافة تعليمات الوصول
        html_content += """
                <div class="summary-section">
                    <h2>تعليمات الوصول</h2>
                    <ul>
                        <li>يمكنك فتح التقرير الرئيسي <a href="comprehensive_security_report.json" class="report-link">هنا</a>.</li>
                        <li>يمكنك الوصول إلى التقارير التفصيلية المذكورة أعلاه بالنقر على روابطها.</li>
                        <li>يمكنك فتح هذا الملف (security_summary.html) في متصفحك لرؤية هذا الملخص.</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """

        # حفظ الملف
        import os
        with open(os.path.join('.', 'security_summary.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)


    def _save_all_reports(self):
        """حفظ جميع التقارير"""
        # التأكد من وجود مجلد التقارير
        import os
        reports_dir = '.'

        # حفظ التقرير الرئيسي
        with open(os.path.join(reports_dir, 'comprehensive_security_report.json'), 'w', encoding='utf-8') as f:
            json.dump(self.master_report, f, ensure_ascii=False, indent=2)

        # حفظ التقارير التفصيلية (إذا لم تكن محفوظة بالفعل)
        for report_type, report_data in self.reports.items():
            if 'error' not in report_data:
                filename = os.path.join(reports_dir, f'{report_type}_detailed_report.json')
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2)

        # إنشاء ملف فهرس
        self._create_index_file()

    def run_all_scans(self):
        """تشغيل جميع عمليات الفحص وحفظ التقارير"""
        print("بدء عمليات الفحص الأمني...")

        # مثال: إضافة تقرير فحص أمني
        security_data = {
            'summary': 'تم العثور على بعض الثغرات المحتملة.',
            'vulnerabilities': [
                {'name': 'SQL Injection', 'severity': 'عالية', 'details': '...'},
                {'name': 'XSS', 'severity': 'متوسطة', 'details': '...'}
            ],
            'description': 'تقرير تفصيلي لنتائج فحص الثغرات الأمنية.'
        }
        self.add_report('security_analysis', security_data)

        # مثال: إضافة تقرير فحص شبكة
        network_data = {
            'summary': 'تم اكتشاف منافذ مفتوحة غير متوقعة.',
            'open_ports': ['80', '443', '2222'],
            'description': 'تقرير تفصيلي لنتائج فحص الشبكة.'
        }
        self.add_report('network_analysis', network_data)

        # مثال: إضافة تقرير فحص خدمات
        service_data = {
            'summary': 'تم تحديد الخدمات قيد التشغيل.',
            'services': [{'name': 'Apache', 'version': '2.4.41'}, {'name': 'SSH', 'version': 'OpenSSH 8.2p1'}],
            'description': 'تقرير تفصيلي لتحليل الخدمات المرتبطة.'
        }
        self.add_report('service_mapping', service_data)

        print("تم الانتهاء من عمليات الفحص.")

        # إنشاء ملخص HTML
        self._generate_html_summary()

        # حفظ جميع التقارير
        self._save_all_reports()
        print("تم حفظ جميع التقارير بنجاح.")

if __name__ == "__main__":
    scanner = SecurityScanner()
    scanner.run_all_scans()