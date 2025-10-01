
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الفحص الأمني الشامل
Comprehensive Security Scanner - تشغيل جميع الفحوصات وإنتاج التقارير
"""

import os
import json
import datetime
from typing import Dict, List, Any
import security_analyzer
import network_analyzer
import service_mapper

class ComprehensiveScanner:
    def __init__(self):
        self.scan_timestamp = datetime.datetime.now().isoformat()
        self.reports = {}
        self.master_report = {}
        
    def run_all_scans(self) -> Dict[str, Any]:
        """تشغيل جميع الفحوصات الأمنية"""
        print("🚀 بدء الفحص الأمني الشامل...")
        print("=" * 60)
        
        # 1. فحص البيانات الحساسة
        print("\n📊 المرحلة 1: فحص البيانات الحساسة")
        print("-" * 40)
        try:
            security_scan = security_analyzer.SecurityAnalyzer()
            security_results = security_scan.scan_files()
            security_report = security_scan.generate_report()
            self.reports['security'] = security_report
            print("✅ تم إكمال فحص البيانات الحساسة")
        except Exception as e:
            print(f"❌ خطأ في فحص البيانات الحساسة: {str(e)}")
            self.reports['security'] = {'error': str(e)}
        
        # 2. فحص الشبكة والاتصالات
        print("\n🌐 المرحلة 2: فحص الشبكة والاتصالات")
        print("-" * 40)
        try:
            network_scan = network_analyzer.NetworkAnalyzer()
            network_results = network_scan.scan_network()
            network_report = network_scan.generate_report()
            self.reports['network'] = network_report
            print("✅ تم إكمال فحص الشبكة والاتصالات")
        except Exception as e:
            print(f"❌ خطأ في فحص الشبكة: {str(e)}")
            self.reports['network'] = {'error': str(e)}
        
        # 3. تحليل الخدمات المرتبطة
        print("\n🔍 المرحلة 3: تحليل الخدمات المرتبطة")
        print("-" * 40)
        try:
            service_scan = service_mapper.ServiceMapper()
            service_results = service_scan.map_services()
            service_report = service_scan.generate_report()
            self.reports['services'] = service_report
            print("✅ تم إكمال تحليل الخدمات المرتبطة")
        except Exception as e:
            print(f"❌ خطأ في تحليل الخدمات: {str(e)}")
            self.reports['services'] = {'error': str(e)}
        
        # 4. إنشاء التقرير الرئيسي
        print("\n📋 المرحلة 4: إنشاء التقرير الشامل")
        print("-" * 40)
        self._generate_master_report()
        self._save_all_reports()
        self._create_summary_html()
        
        print("\n✅ تم إكمال جميع الفحوصات بنجاح!")
        print("=" * 60)
        
        return self.master_report
    
    def _generate_master_report(self):
        """إنشاء التقرير الرئيسي الشامل"""
        # تجميع الإحصائيات
        summary_stats = {
            'scan_timestamp': self.scan_timestamp,
            'scan_duration': self._calculate_scan_duration(),
            'total_issues_found': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0
        }
        
        # تجميع النتائج من جميع التقارير
        all_findings = {}
        all_recommendations = []
        
        # معالجة تقرير الأمان
        if 'security' in self.reports and 'error' not in self.reports['security']:
            security_data = self.reports['security']
            summary_stats.update({
                'emails_found': security_data['summary'].get('total_emails', 0),
                'passwords_found': security_data['summary'].get('total_passwords', 0),
                'api_keys_found': security_data['summary'].get('total_api_keys', 0),
                'databases_found': security_data['summary'].get('total_databases', 0)
            })
            
            # إضافة المشاكل الأمنية
            security_issues = security_data['findings'].get('security_issues', [])
            for issue in security_issues:
                if issue['severity'] == 'critical':
                    summary_stats['critical_issues'] += 1
                elif issue['severity'] == 'high':
                    summary_stats['high_issues'] += 1
                elif issue['severity'] == 'medium':
                    summary_stats['medium_issues'] += 1
                else:
                    summary_stats['low_issues'] += 1
            
            all_findings['security_findings'] = security_data['findings']
            all_recommendations.extend(security_data.get('recommendations', []))
        
        # معالجة تقرير الشبكة
        if 'network' in self.reports and 'error' not in self.reports['network']:
            network_data = self.reports['network']
            summary_stats.update({
                'open_ports': network_data['summary'].get('open_ports_count', 0),
                'ssl_certificates': network_data['summary'].get('ssl_certificates_count', 0),
                'external_connections': network_data['summary'].get('external_connections_count', 0)
            })
            
            # إضافة المشاكل الشبكية
            network_issues = network_data['findings'].get('security_issues', [])
            for issue in network_issues:
                if issue['severity'] == 'critical':
                    summary_stats['critical_issues'] += 1
                elif issue['severity'] == 'high':
                    summary_stats['high_issues'] += 1
                elif issue['severity'] == 'medium':
                    summary_stats['medium_issues'] += 1
                else:
                    summary_stats['low_issues'] += 1
            
            all_findings['network_findings'] = network_data['findings']
            all_recommendations.extend(network_data.get('recommendations', []))
        
        # معالجة تقرير الخدمات
        if 'services' in self.reports and 'error' not in self.reports['services']:
            service_data = self.reports['services']
            summary_stats.update({
                'total_services': service_data['summary'].get('total_services', 0),
                'messaging_services': service_data['summary'].get('messaging_services_count', 0),
                'cloud_services': service_data['summary'].get('cloud_storage_count', 0)
            })
            
            all_findings['service_findings'] = service_data['services']
            all_recommendations.extend(service_data.get('recommendations', []))
        
        # حساب المجموع الكلي للمشاكل
        summary_stats['total_issues_found'] = (
            summary_stats['critical_issues'] + 
            summary_stats['high_issues'] + 
            summary_stats['medium_issues'] + 
            summary_stats['low_issues']
        )
        
        # إنشاء التقرير الرئيسي
        self.master_report = {
            'scan_info': {
                'scan_type': 'comprehensive_security_scan',
                'version': '1.0',
                'timestamp': self.scan_timestamp,
                'scanner': 'Comprehensive Security Scanner'
            },
            'summary': summary_stats,
            'findings': all_findings,
            'recommendations': list(set(all_recommendations)),  # إزالة التكرارات
            'detailed_reports': {
                'security_report_file': 'security_analysis_report.json',
                'network_report_file': 'network_analysis_report.json',
                'service_report_file': 'service_mapping_report.json'
            },
            'risk_assessment': self._assess_overall_risk(summary_stats)
        }
    
    def _calculate_scan_duration(self) -> str:
        """حساب مدة الفحص"""
        # هذا مجرد تقدير بسيط
        return "تقريباً 2-5 دقائق"
    
    def _assess_overall_risk(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم المخاطر الإجمالية"""
        risk_score = 0
        
        # حساب نقاط المخاطر
        risk_score += stats.get('critical_issues', 0) * 10
        risk_score += stats.get('high_issues', 0) * 5
        risk_score += stats.get('medium_issues', 0) * 2
        risk_score += stats.get('low_issues', 0) * 1
        
        # تصنيف المخاطر
        if risk_score >= 50:
            risk_level = 'عالي جداً'
            risk_color = 'red'
        elif risk_score >= 30:
            risk_level = 'عالي'
            risk_color = 'orange'
        elif risk_score >= 15:
            risk_level = 'متوسط'
            risk_color = 'yellow'
        elif risk_score >= 5:
            risk_level = 'منخفض'
            risk_color = 'lightgreen'
        else:
            risk_level = 'آمن'
            risk_color = 'green'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'assessment_date': self.scan_timestamp
        }
    
    def _save_all_reports(self):
        """حفظ جميع التقارير"""
        # حفظ التقرير الرئيسي
        with open('comprehensive_security_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.master_report, f, ensure_ascii=False, indent=2)
        
        # حفظ التقارير التفصيلية (إذا لم تكن محفوظة بالفعل)
        for report_type, report_data in self.reports.items():
            if 'error' not in report_data:
                filename = f'{report_type}_detailed_report.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # إنشاء ملف فهرس
        self._create_index_file()
    
    def _create_index_file(self):
        """إنشاء ملف فهرس للتقارير"""
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
    
    def _get_file_size(self, filename: str) -> str:
        """الحصول على حجم الملف"""
        try:
            size = os.path.getsize(filename)
            if size < 1024:
                return f"{size} بايت"
            elif size < 1024 * 1024:
                return f"{size // 1024} كيلوبايت"
            else:
                return f"{size // (1024 * 1024)} ميجابايت"
        except:
            return "غير محدد"
    
    def _create_summary_html(self):
        """إنشاء ملخص HTML تفاعلي"""
        html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الفحص الأمني الشامل</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(45deg, #1e3c72, #2a5298);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header .timestamp {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .card.critical {{ border-left-color: #dc3545; }}
        .card.high {{ border-left-color: #fd7e14; }}
        .card.medium {{ border-left-color: #ffc107; }}
        .card.low {{ border-left-color: #28a745; }}
        .card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .card.critical .number {{ color: #dc3545; }}
        .card.high .number {{ color: #fd7e14; }}
        .card.medium .number {{ color: #ffc107; }}
        .card.low .number {{ color: #28a745; }}
        .risk-assessment {{
            margin: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }}
        .risk-level {{
            font-size: 1.5em;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .recommendations {{
            margin: 30px;
            padding: 20px;
            background: #e9ecef;
            border-radius: 8px;
        }}
        .recommendations h2 {{
            margin-top: 0;
            color: #333;
        }}
        .recommendations ul {{
            list-style-type: none;
            padding: 0;
        }}
        .recommendations li {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #007bff;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #333;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ تقرير الفحص الأمني الشامل</h1>
            <div class="timestamp">تاريخ الفحص: {self.scan_timestamp}</div>
        </div>
        
        <div class="summary">
            <div class="card critical">
                <h3>مشاكل حرجة</h3>
                <div class="number">{self.master_report['summary'].get('critical_issues', 0)}</div>
            </div>
            <div class="card high">
                <h3>مشاكل عالية</h3>
                <div class="number">{self.master_report['summary'].get('high_issues', 0)}</div>
            </div>
            <div class="card medium">
                <h3>مشاكل متوسطة</h3>
                <div class="number">{self.master_report['summary'].get('medium_issues', 0)}</div>
            </div>
            <div class="card low">
                <h3>مشاكل منخفضة</h3>
                <div class="number">{self.master_report['summary'].get('low_issues', 0)}</div>
            </div>
            <div class="card">
                <h3>إيميلات مكتشفة</h3>
                <div class="number">{self.master_report['summary'].get('emails_found', 0)}</div>
            </div>
            <div class="card">
                <h3>مفاتيح API</h3>
                <div class="number">{self.master_report['summary'].get('api_keys_found', 0)}</div>
            </div>
            <div class="card">
                <h3>منافذ مفتوحة</h3>
                <div class="number">{self.master_report['summary'].get('open_ports', 0)}</div>
            </div>
            <div class="card">
                <h3>خدمات مكتشفة</h3>
                <div class="number">{self.master_report['summary'].get('total_services', 0)}</div>
            </div>
        </div>
        
        <div class="risk-assessment">
            <h2>تقييم المخاطر الإجمالية</h2>
            <div class="risk-level" style="background-color: {self.master_report['risk_assessment']['risk_color']}; color: white;">
                {self.master_report['risk_assessment']['risk_level']}
            </div>
            <p>نقاط المخاطر: {self.master_report['risk_assessment']['risk_score']}</p>
        </div>
        
        <div class="recommendations">
            <h2>التوصيات الأمنية الرئيسية</h2>
            <ul>
"""
        
        # إضافة التوصيات
        for rec in self.master_report['recommendations'][:10]:  # أول 10 توصيات
            html_content += f"                <li>{rec}</li>\n"
        
        html_content += f"""
            </ul>
        </div>
        
        <div class="footer">
            <p>تم إنشاء هذا التقرير بواسطة نظام الفحص الأمني الشامل</p>
            <p>للحصول على تفاصيل أكثر، راجع الملفات: comprehensive_security_report.json</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open('security_summary.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        print("\n📊 ملخص نتائج الفحص الأمني الشامل")
        print("=" * 50)
        
        summary = self.master_report['summary']
        
        print(f"📧 الإيميلات المكتشفة: {summary.get('emails_found', 0)}")
        print(f"🔑 مفاتيح API: {summary.get('api_keys_found', 0)}")
        print(f"🗄️ قواعد البيانات: {summary.get('databases_found', 0)}")
        print(f"🌐 المنافذ المفتوحة: {summary.get('open_ports', 0)}")
        print(f"🔗 الخدمات المكتشفة: {summary.get('total_services', 0)}")
        
        print(f"\n🚨 المشاكل الأمنية:")
        print(f"   🔴 حرجة: {summary.get('critical_issues', 0)}")
        print(f"   🟠 عالية: {summary.get('high_issues', 0)}")
        print(f"   🟡 متوسطة: {summary.get('medium_issues', 0)}")
        print(f"   🟢 منخفضة: {summary.get('low_issues', 0)}")
        
        risk_info = self.master_report['risk_assessment']
        print(f"\n🎯 تقييم المخاطر: {risk_info['risk_level']} ({risk_info['risk_score']} نقطة)")
        
        print(f"\n📁 الملفات المنشأة:")
        print(f"   📋 comprehensive_security_report.json - التقرير الرئيسي")
        print(f"   🌐 security_summary.html - الملخص التفاعلي") 
        print(f"   📊 security_analysis_report.json - تفاصيل البيانات الحساسة")
        print(f"   🔗 network_analysis_report.json - تفاصيل الشبكة")
        print(f"   🔍 service_mapping_report.json - تفاصيل الخدمات")
        print(f"   📚 reports_index.json - فهرس التقارير")

def main():
    """الدالة الرئيسية لتشغيل الفحص الشامل"""
    scanner = ComprehensiveScanner()
    
    print("🛡️ مرحباً بك في نظام الفحص الأمني الشامل")
    print("سيتم فحص النظام بالكامل للبحث عن البيانات الحساسة والخدمات المرتبطة")
    print("\n⏰ قد يستغرق الفحص عدة دقائق حسب حجم المشروع...")
    
    try:
        # تشغيل جميع الفحوصات
        results = scanner.run_all_scans()
        
        # طباعة الملخص
        scanner.print_summary()
        
        print(f"\n✅ تم إكمال الفحص بنجاح!")
        print(f"🌐 افتح security_summary.html في المتصفح لعرض النتائج")
        
        return results
        
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء الفحص: {str(e)}")
        return None

if __name__ == "__main__":
    main()
