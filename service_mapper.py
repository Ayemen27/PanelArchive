
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام تحليل الخدمات المرتبطة
Service Mapper - فحص وتحليل الخدمات المتصلة بالنظام
"""

import os
import re
import json
import sqlite3
import datetime
from typing import Dict, List, Any, Set
from pathlib import Path

class ServiceMapper:
    def __init__(self):
        self.results = {
            'messaging_services': [],
            'email_services': [],
            'cloud_storage': [],
            'databases': [],
            'api_integrations': [],
            'monitoring_services': [],
            'security_services': [],
            'backup_services': [],
            'cdn_services': [],
            'payment_services': []
        }
        
        # أنماط الخدمات المختلفة
        self.service_patterns = {
            # خدمات الرسائل
            'wechat': r'(?i)(wechat|weixin|wx_|微信)',
            'dingtalk': r'(?i)(dingtalk|dingding|钉钉)',
            'telegram': r'(?i)(telegram|tg_|bot_token)',
            'feishu': r'(?i)(feishu|lark|飞书)',
            'slack': r'(?i)(slack|slack_)',
            
            # خدمات البريد الإلكتروني
            'smtp': r'(?i)(smtp|mail_server|email_host)',
            'imap': r'(?i)(imap|mail_imap)',
            'pop3': r'(?i)(pop3|mail_pop)',
            'sendmail': r'(?i)(sendmail|mail_send)',
            
            # خدمات التخزين السحابي
            'aws_s3': r'(?i)(aws|s3|amazon)',
            'google_cloud': r'(?i)(google_cloud|gcp|googleapis)',
            'azure': r'(?i)(azure|microsoft_cloud)',
            'aliyun': r'(?i)(aliyun|阿里云|oss)',
            'tencent_cloud': r'(?i)(tencent|qcloud|腾讯云)',
            'baidu_cloud': r'(?i)(baidu|百度云|bce)',
            
            # قواعد البيانات
            'mysql': r'(?i)(mysql|mariadb)',
            'postgresql': r'(?i)(postgresql|postgres|pgsql)',
            'redis': r'(?i)(redis|redis_)',
            'mongodb': r'(?i)(mongodb|mongo)',
            'sqlite': r'(?i)(sqlite|sqlite3)',
            
            # خدمات API
            'github': r'(?i)(github|git_)',
            'gitlab': r'(?i)(gitlab)',
            'docker': r'(?i)(docker|container)',
            'kubernetes': r'(?i)(kubernetes|k8s)',
            
            # خدمات المراقبة
            'monitoring': r'(?i)(monitor|grafana|prometheus)',
            'logging': r'(?i)(log|syslog|logstash)',
            
            # خدمات الأمان
            'ssl_cert': r'(?i)(ssl|tls|certificate|cert)',
            'firewall': r'(?i)(firewall|iptables|ufw)',
            'security': r'(?i)(security|safe|scan)',
            
            # خدمات النسخ الاحتياطي
            'backup': r'(?i)(backup|restore|bak)',
            'sync': r'(?i)(sync|rsync)',
            
            # شبكات توصيل المحتوى
            'cloudflare': r'(?i)(cloudflare|cf_)',
            'cdn': r'(?i)(cdn|content_delivery)',
            
            # خدمات الدفع
            'payment': r'(?i)(payment|pay|alipay|wechatpay)'
        }
        
        # مسارات مهمة للفحص
        self.scan_paths = [
            'class/', 'class_v2/', 'plugin/', 'mod/', 'config/',
            'data/', 'BTPanel/', 'script/'
        ]
    
    def map_services(self) -> Dict[str, Any]:
        """فحص وتحليل جميع الخدمات المرتبطة"""
        print("🔍 بدء تحليل الخدمات المرتبطة...")
        
        self._scan_configuration_files()
        self._scan_code_files()
        self._scan_database_connections()
        self._scan_plugin_services()
        self._analyze_service_dependencies()
        
        return self.results
    
    def _scan_configuration_files(self):
        """فحص ملفات التكوين"""
        print("⚙️ فحص ملفات التكوين...")
        
        config_files = []
        for path in self.scan_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.json', '.conf', '.cfg', '.ini', '.yml', '.yaml')):
                            config_files.append(os.path.join(root, file))
        
        for config_file in config_files:
            self._analyze_config_file(config_file)
    
    def _analyze_config_file(self, filepath: str):
        """تحليل ملف تكوين محدد"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # فحص كل نمط خدمة
            for service_type, pattern in self.service_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    service_info = {
                        'service_type': service_type,
                        'file': filepath,
                        'matches': list(set(matches)),  # إزالة التكرارات
                        'match_count': len(matches),
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    
                    # تصنيف الخدمة
                    self._categorize_service(service_info)
                    
        except Exception as e:
            print(f"⚠️ خطأ في قراءة ملف التكوين {filepath}: {str(e)}")
    
    def _scan_code_files(self):
        """فحص ملفات الكود المصدري"""
        print("💻 فحص ملفات الكود المصدري...")
        
        code_files = []
        for path in self.scan_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.py', '.js', '.php')):
                            code_files.append(os.path.join(root, file))
        
        # فحص عينة من الملفات لتجنب البطء
        for code_file in code_files[:100]:
            self._analyze_code_file(code_file)
    
    def _analyze_code_file(self, filepath: str):
        """تحليل ملف كود مصدري"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # البحث عن imports وإعدادات الخدمات
            service_indicators = [
                r'import\s+(\w+)',
                r'from\s+(\w+)',
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'(\w+_api|api_\w+)',
                r'(\w+_service|service_\w+)',
                r'(\w+_client|client_\w+)'
            ]
            
            for pattern in service_indicators:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1]
                    
                    # فحص إذا كان المطابق يحتوي على خدمة معروفة
                    for service_type, service_pattern in self.service_patterns.items():
                        if re.search(service_pattern, match, re.IGNORECASE):
                            service_info = {
                                'service_type': service_type,
                                'file': filepath,
                                'indicator': match,
                                'context': 'code_import',
                                'timestamp': datetime.datetime.now().isoformat()
                            }
                            self._categorize_service(service_info)
                            
        except Exception as e:
            pass  # تجاهل الأخطاء في قراءة ملفات الكود
    
    def _scan_database_connections(self):
        """فحص اتصالات قواعد البيانات"""
        print("🗄️ فحص اتصالات قواعد البيانات...")
        
        # فحص ملفات قواعد البيانات
        db_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_files.append(os.path.join(root, file))
        
        for db_file in db_files:
            self._analyze_database_file(db_file)
    
    def _analyze_database_file(self, db_path: str):
        """تحليل ملف قاعدة بيانات"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # الحصول على أسماء الجداول
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            db_info = {
                'service_type': 'sqlite',
                'file': db_path,
                'tables': [table[0] for table in tables],
                'table_count': len(tables),
                'file_size': os.path.getsize(db_path),
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # فحص جداول الخدمات الخاصة
            service_tables = []
            for table_name in [table[0] for table in tables]:
                if any(service in table_name.lower() for service in 
                      ['mail', 'message', 'user', 'config', 'service', 'api', 'log']):
                    service_tables.append(table_name)
            
            if service_tables:
                db_info['service_tables'] = service_tables
            
            self.results['databases'].append(db_info)
            conn.close()
            
        except Exception as e:
            print(f"⚠️ خطأ في فحص قاعدة البيانات {db_path}: {str(e)}")
    
    def _scan_plugin_services(self):
        """فحص خدمات الإضافات"""
        print("🔌 فحص خدمات الإضافات...")
        
        plugin_dirs = ['plugin/', 'mod/']
        for plugin_dir in plugin_dirs:
            if os.path.exists(plugin_dir):
                for item in os.listdir(plugin_dir):
                    plugin_path = os.path.join(plugin_dir, item)
                    if os.path.isdir(plugin_path):
                        self._analyze_plugin_directory(plugin_path)
    
    def _analyze_plugin_directory(self, plugin_path: str):
        """تحليل مجلد إضافة محددة"""
        plugin_name = os.path.basename(plugin_path)
        
        # فحص ملفات الإضافة
        plugin_files = []
        for root, dirs, files in os.walk(plugin_path):
            for file in files:
                if file.endswith(('.py', '.json', '.conf', '.txt')):
                    plugin_files.append(os.path.join(root, file))
        
        services_found = []
        for file_path in plugin_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for service_type, pattern in self.service_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        services_found.append(service_type)
                        
            except:
                continue
        
        if services_found:
            plugin_info = {
                'plugin_name': plugin_name,
                'plugin_path': plugin_path,
                'services': list(set(services_found)),
                'service_count': len(set(services_found)),
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # تصنيف الخدمات حسب النوع
            for service in set(services_found):
                service_info = {
                    'service_type': service,
                    'source': 'plugin',
                    'plugin_name': plugin_name,
                    'file': plugin_path,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                self._categorize_service(service_info)
    
    def _categorize_service(self, service_info: Dict[str, Any]):
        """تصنيف الخدمة حسب نوعها"""
        service_type = service_info['service_type']
        
        # خدمات الرسائل
        if service_type in ['wechat', 'dingtalk', 'telegram', 'feishu', 'slack']:
            self.results['messaging_services'].append(service_info)
        
        # خدمات البريد الإلكتروني
        elif service_type in ['smtp', 'imap', 'pop3', 'sendmail']:
            self.results['email_services'].append(service_info)
        
        # خدمات التخزين السحابي
        elif service_type in ['aws_s3', 'google_cloud', 'azure', 'aliyun', 'tencent_cloud', 'baidu_cloud']:
            self.results['cloud_storage'].append(service_info)
        
        # قواعد البيانات
        elif service_type in ['mysql', 'postgresql', 'redis', 'mongodb', 'sqlite']:
            self.results['databases'].append(service_info)
        
        # تكاملات API
        elif service_type in ['github', 'gitlab', 'docker', 'kubernetes']:
            self.results['api_integrations'].append(service_info)
        
        # خدمات المراقبة
        elif service_type in ['monitoring', 'logging']:
            self.results['monitoring_services'].append(service_info)
        
        # خدمات الأمان
        elif service_type in ['ssl_cert', 'firewall', 'security']:
            self.results['security_services'].append(service_info)
        
        # خدمات النسخ الاحتياطي
        elif service_type in ['backup', 'sync']:
            self.results['backup_services'].append(service_info)
        
        # شبكات توصيل المحتوى
        elif service_type in ['cloudflare', 'cdn']:
            self.results['cdn_services'].append(service_info)
        
        # خدمات الدفع
        elif service_type in ['payment']:
            self.results['payment_services'].append(service_info)
    
    def _analyze_service_dependencies(self):
        """تحليل اعتماديات الخدمات"""
        print("🔗 تحليل اعتماديات الخدمات...")
        
        # حساب إحصائيات الخدمات
        service_stats = {}
        for category, services in self.results.items():
            if isinstance(services, list):
                service_types = [s.get('service_type', 'unknown') for s in services]
                for service_type in service_types:
                    service_stats[service_type] = service_stats.get(service_type, 0) + 1
        
        # إضافة الإحصائيات إلى النتائج
        self.results['service_statistics'] = service_stats
    
    def generate_report(self) -> Dict[str, Any]:
        """إنشاء تقرير الخدمات"""
        summary = {
            'messaging_services_count': len(self.results['messaging_services']),
            'email_services_count': len(self.results['email_services']),
            'cloud_storage_count': len(self.results['cloud_storage']),
            'databases_count': len(self.results['databases']),
            'api_integrations_count': len(self.results['api_integrations']),
            'monitoring_services_count': len(self.results['monitoring_services']),
            'security_services_count': len(self.results['security_services']),
            'backup_services_count': len(self.results['backup_services']),
            'cdn_services_count': len(self.results['cdn_services']),
            'payment_services_count': len(self.results['payment_services']),
            'total_services': sum([
                len(services) for services in self.results.values() 
                if isinstance(services, list)
            ]) - len(self.results.get('service_statistics', {})),
            'scan_timestamp': datetime.datetime.now().isoformat()
        }
        
        return {
            'summary': summary,
            'services': self.results,
            'recommendations': self._get_service_recommendations()
        }
    
    def _get_service_recommendations(self) -> List[str]:
        """توصيات إدارة الخدمات"""
        recommendations = []
        
        if self.results['messaging_services']:
            recommendations.append("📱 مراجعة إعدادات خدمات الرسائل وتأمينها")
        
        if self.results['email_services']:
            recommendations.append("📧 تشفير اتصالات البريد الإلكتروني")
        
        if self.results['cloud_storage']:
            recommendations.append("☁️ مراجعة أذونات التخزين السحابي")
        
        if len(self.results['databases']) > 5:
            recommendations.append("🗄️ توحيد قواعد البيانات وتحسين الأداء")
        
        recommendations.extend([
            "🔐 استخدام مفاتيح API آمنة",
            "📊 مراقبة استخدام الخدمات",
            "🔄 تحديث الخدمات بانتظام",
            "📝 توثيق جميع الخدمات المستخدمة"
        ])
        
        return recommendations

def main():
    mapper = ServiceMapper()
    print("🔍 بدء تحليل الخدمات المرتبطة...")
    
    results = mapper.map_services()
    report = mapper.generate_report()
    
    # حفظ التقرير
    with open('service_mapping_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم إنشاء تقرير الخدمات المرتبطة: service_mapping_report.json")
    print(f"📊 النتائج: {report['summary']['total_services']} خدمة مكتشفة")
    
    return report

if __name__ == "__main__":
    main()
