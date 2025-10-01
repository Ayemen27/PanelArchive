
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام فحص البيانات الحساسة
Security Data Analyzer - فحص شامل للبيانات الحساسة في النظام
"""

import os
import re
import json
import sqlite3
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Any, Set

class SecurityAnalyzer:
    def __init__(self):
        self.results = {
            'emails': [],
            'passwords': [],
            'api_keys': [],
            'tokens': [],
            'user_ids': [],
            'ip_addresses': [],
            'database_info': [],
            'config_files': [],
            'sensitive_patterns': [],
            'security_issues': []
        }
        
        # أنماط البحث عن البيانات الحساسة
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'password': r'(?i)(password|pwd|pass|secret)\s*[:=]\s*["\']?([^"\'\s\n,;}]+)',
            'api_key': r'(?i)(api[_-]?key|apikey|access[_-]?key)\s*[:=]\s*["\']?([A-Za-z0-9]{20,})',
            'jwt_token': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            'github_token': r'gh[pousr]_[A-Za-z0-9_]{36}',
            'google_api': r'AIza[0-9A-Za-z_-]{35}',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'private_key': r'-----BEGIN\s+(?:RSA\s+|EC\s+)?PRIVATE\s+KEY-----',
            'database_url': r'(?i)(database_url|db_url|mongodb_uri)\s*[:=]\s*["\']?([^"\'\s\n,;}]+)',
            'secret_key': r'(?i)(secret[_-]?key|encryption[_-]?key)\s*[:=]\s*["\']?([^"\'\s\n,;}]+)'
        }
        
        # مسارات مهمة للفحص
        self.important_paths = [
            'data/', 'config/', 'class/', 'class_v2/', 'BTPanel/',
            'plugin/', 'mod/', 'ssl/', 'script/', 'logs/'
        ]
        
        # ملفات قواعد البيانات
        self.db_extensions = ['.db', '.sqlite', '.sqlite3']
        
    def scan_files(self, directory: str = '.') -> Dict[str, Any]:
        """فحص جميع الملفات في المجلد المحدد"""
        print(f"🔍 بدء فحص المجلد: {directory}")
        
        for root, dirs, files in os.walk(directory):
            # تجاهل المجلدات غير المهمة
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # فحص قواعد البيانات
                if any(file.endswith(ext) for ext in self.db_extensions):
                    self._scan_database(file_path)
                
                # فحص الملفات النصية
                elif self._is_text_file(file):
                    self._scan_text_file(file_path)
        
        self._analyze_findings()
        return self.results
    
    def _is_text_file(self, filepath: str) -> bool:
        """تحديد ما إذا كان الملف نصي قابل للقراءة"""
        text_extensions = ['.py', '.js', '.json', '.conf', '.cfg', '.ini', '.txt', '.log', '.md', '.yml', '.yaml', '.xml', '.html']
        return any(filepath.endswith(ext) for ext in text_extensions)
    
    def _scan_text_file(self, filepath: str):
        """فحص ملف نصي للبحث عن البيانات الحساسة"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern_name, pattern in self.patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    for match in matches:
                        self._add_finding(pattern_name, match, filepath)
                        
        except Exception as e:
            print(f"⚠️ خطأ في قراءة الملف {filepath}: {str(e)}")
    
    def _scan_database(self, db_path: str):
        """فحص قاعدة بيانات SQLite"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # الحصول على أسماء الجداول
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            db_info = {
                'path': db_path,
                'tables': [],
                'sensitive_data': []
            }
            
            for table in tables:
                table_name = table[0]
                db_info['tables'].append(table_name)
                
                # فحص محتويات الجدول للبحث عن بيانات حساسة
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
                    rows = cursor.fetchall()
                    
                    # الحصول على أسماء الأعمدة
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    for row in rows:
                        for i, value in enumerate(row):
                            if value and isinstance(value, str):
                                # فحص القيم للبحث عن أنماط حساسة
                                for pattern_name, pattern in self.patterns.items():
                                    if re.search(pattern, str(value)):
                                        db_info['sensitive_data'].append({
                                            'table': table_name,
                                            'column': columns[i] if i < len(columns) else f'col_{i}',
                                            'pattern': pattern_name,
                                            'value_hash': hashlib.md5(str(value).encode()).hexdigest()[:8]
                                        })
                                        
                except Exception as e:
                    print(f"⚠️ خطأ في فحص الجدول {table_name}: {str(e)}")
            
            self.results['database_info'].append(db_info)
            conn.close()
            
        except Exception as e:
            print(f"⚠️ خطأ في فحص قاعدة البيانات {db_path}: {str(e)}")
    
    def _add_finding(self, pattern_name: str, match, filepath: str):
        """إضافة نتيجة فحص جديدة"""
        if isinstance(match, tuple):
            # للأنماط التي تعيد مجموعات
            if len(match) >= 2:
                key, value = match[0], match[1]
            else:
                key, value = pattern_name, match[0]
        else:
            key, value = pattern_name, match
        
        finding = {
            'type': pattern_name,
            'key': key,
            'value_hash': hashlib.md5(str(value).encode()).hexdigest()[:8],
            'file': filepath,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # تصنيف النتائج
        if pattern_name == 'email':
            self.results['emails'].append({**finding, 'email': value, 'verified': self._check_email_validity(value)})
        elif pattern_name == 'password':
            self.results['passwords'].append({**finding, 'strength': self._check_password_strength(value)})
        elif 'api' in pattern_name or 'key' in pattern_name:
            self.results['api_keys'].append(finding)
        elif 'token' in pattern_name:
            self.results['tokens'].append(finding)
        elif pattern_name == 'ip_address':
            self.results['ip_addresses'].append({**finding, 'ip': value, 'type': self._classify_ip(value)})
        else:
            self.results['sensitive_patterns'].append(finding)
    
    def _check_email_validity(self, email: str) -> str:
        """فحص صحة الإيميل"""
        if '@' not in email:
            return 'invalid'
        
        domain = email.split('@')[1]
        common_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
        
        if domain in common_domains:
            return 'public'
        elif domain.endswith('.com') or domain.endswith('.org'):
            return 'corporate'
        else:
            return 'unknown'
    
    def _check_password_strength(self, password: str) -> str:
        """تقييم قوة كلمة المرور"""
        score = 0
        if len(password) >= 8:
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        
        if score <= 2:
            return 'weak'
        elif score <= 3:
            return 'medium'
        else:
            return 'strong'
    
    def _classify_ip(self, ip: str) -> str:
        """تصنيف عنوان IP"""
        if ip.startswith('127.'):
            return 'localhost'
        elif ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            return 'private'
        elif ip == '0.0.0.0':
            return 'any'
        else:
            return 'public'
    
    def _analyze_findings(self):
        """تحليل النتائج وإنشاء تقرير المشاكل الأمنية"""
        issues = []
        
        # فحص كلمات المرور الضعيفة
        weak_passwords = [p for p in self.results['passwords'] if p.get('strength') == 'weak']
        if weak_passwords:
            issues.append({
                'severity': 'high',
                'type': 'weak_passwords',
                'count': len(weak_passwords),
                'description': 'تم العثور على كلمات مرور ضعيفة'
            })
        
        # فحص مفاتيح API المكشوفة
        if self.results['api_keys']:
            issues.append({
                'severity': 'critical',
                'type': 'exposed_api_keys',
                'count': len(self.results['api_keys']),
                'description': 'مفاتيح API مكشوفة في الملفات'
            })
        
        # فحص عناوين IP العامة
        public_ips = [ip for ip in self.results['ip_addresses'] if ip.get('type') == 'public']
        if public_ips:
            issues.append({
                'severity': 'medium',
                'type': 'public_ips',
                'count': len(public_ips),
                'description': 'عناوين IP عامة مكشوفة'
            })
        
        self.results['security_issues'] = issues
    
    def generate_report(self) -> Dict[str, Any]:
        """إنشاء تقرير شامل"""
        summary = {
            'total_emails': len(self.results['emails']),
            'total_passwords': len(self.results['passwords']),
            'total_api_keys': len(self.results['api_keys']),
            'total_tokens': len(self.results['tokens']),
            'total_ips': len(self.results['ip_addresses']),
            'total_databases': len(self.results['database_info']),
            'security_issues_count': len(self.results['security_issues']),
            'scan_timestamp': datetime.datetime.now().isoformat()
        }
        
        return {
            'summary': summary,
            'findings': self.results,
            'recommendations': self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """توصيات أمنية"""
        recommendations = []
        
        if self.results['api_keys']:
            recommendations.append("🔑 استخدم متغيرات البيئة لتخزين مفاتيح API")
        
        if any(p.get('strength') == 'weak' for p in self.results['passwords']):
            recommendations.append("🔒 استخدم كلمات مرور قوية (8+ أحرف، أرقام، رموز)")
        
        if self.results['database_info']:
            recommendations.append("🗄️ تشفير قواعد البيانات الحساسة")
        
        recommendations.extend([
            "🔐 تفعيل التشفير للاتصالات",
            "📝 مراجعة ملفات السجلات بانتظام",
            "🚫 عدم تخزين البيانات الحساسة في الكود المصدري"
        ])
        
        return recommendations

def main():
    analyzer = SecurityAnalyzer()
    print("🔍 بدء الفحص الأمني الشامل...")
    
    results = analyzer.scan_files()
    report = analyzer.generate_report()
    
    # حفظ التقرير
    with open('security_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم إنشاء تقرير الفحص الأمني: security_analysis_report.json")
    print(f"📊 النتائج: {report['summary']['total_emails']} إيميل، {report['summary']['total_passwords']} كلمة مرور، {report['summary']['total_api_keys']} مفتاح API")
    
    return report

if __name__ == "__main__":
    main()
