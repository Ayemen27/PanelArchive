
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام فحص الشبكة والاتصالات
Network Security Analyzer - فحص شامل للشبكة والخدمات
"""

import os
import re
import json
import socket
import subprocess
import datetime
import ssl
import requests
from typing import Dict, List, Any, Optional

class NetworkAnalyzer:
    def __init__(self):
        self.results = {
            'open_ports': [],
            'active_connections': [],
            'dns_settings': [],
            'ssl_certificates': [],
            'external_connections': [],
            'firewall_rules': [],
            'network_interfaces': [],
            'security_issues': []
        }
        
        # منافذ مهمة للفحص
        self.important_ports = [
            21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995,
            3306, 5432, 6379, 27017, 3000, 5000, 8000, 8080, 8443
        ]
        
        # خدمات معروفة
        self.port_services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
            443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
            3306: 'MySQL', 5432: 'PostgreSQL', 6379: 'Redis',
            27017: 'MongoDB', 3000: 'Node.js', 5000: 'Flask',
            8000: 'HTTP Alt', 8080: 'HTTP Proxy', 8443: 'HTTPS Alt'
        }
    
    def scan_network(self) -> Dict[str, Any]:
        """فحص شامل للشبكة"""
        print("🌐 بدء فحص الشبكة والاتصالات...")
        
        self._scan_open_ports()
        self._scan_active_connections()
        self._check_dns_settings()
        self._scan_ssl_certificates()
        self._check_external_connections()
        self._check_firewall_status()
        self._scan_network_interfaces()
        self._analyze_network_security()
        
        return self.results
    
    def _scan_open_ports(self):
        """فحص المنافذ المفتوحة"""
        print("🔍 فحص المنافذ المفتوحة...")
        
        for port in self.important_ports:
            if self._is_port_open('127.0.0.1', port):
                service = self.port_services.get(port, 'Unknown')
                port_info = {
                    'port': port,
                    'service': service,
                    'status': 'open',
                    'protocol': 'tcp',
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                # فحص إضافي للخدمة
                service_info = self._get_service_info(port)
                if service_info:
                    port_info.update(service_info)
                
                self.results['open_ports'].append(port_info)
    
    def _is_port_open(self, host: str, port: int, timeout: int = 3) -> bool:
        """فحص ما إذا كان المنفذ مفتوح"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _get_service_info(self, port: int) -> Optional[Dict[str, Any]]:
        """الحصول على معلومات إضافية عن الخدمة"""
        try:
            if port == 80:
                response = requests.get('http://127.0.0.1', timeout=5)
                return {
                    'server': response.headers.get('Server', 'Unknown'),
                    'status_code': response.status_code
                }
            elif port == 443:
                response = requests.get('https://127.0.0.1', timeout=5, verify=False)
                return {
                    'server': response.headers.get('Server', 'Unknown'),
                    'status_code': response.status_code,
                    'ssl_enabled': True
                }
        except:
            pass
        return None
    
    def _scan_active_connections(self):
        """فحص الاتصالات النشطة"""
        print("🔗 فحص الاتصالات النشطة...")
        
        try:
            # استخدام netstat لفحص الاتصالات
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # تجاهل العناوين
                    parts = line.split()
                    if len(parts) >= 4:
                        connection = {
                            'protocol': parts[0],
                            'local_address': parts[3],
                            'state': parts[5] if len(parts) > 5 else 'LISTEN',
                            'timestamp': datetime.datetime.now().isoformat()
                        }
                        self.results['active_connections'].append(connection)
        except Exception as e:
            print(f"⚠️ خطأ في فحص الاتصالات: {str(e)}")
    
    def _check_dns_settings(self):
        """فحص إعدادات DNS"""
        print("🌍 فحص إعدادات DNS...")
        
        try:
            # قراءة ملف resolv.conf
            resolv_conf = '/etc/resolv.conf'
            if os.path.exists(resolv_conf):
                with open(resolv_conf, 'r') as f:
                    content = f.read()
                
                dns_servers = re.findall(r'nameserver\s+(\S+)', content)
                for dns in dns_servers:
                    self.results['dns_settings'].append({
                        'server': dns,
                        'type': 'nameserver',
                        'source': resolv_conf
                    })
        except Exception as e:
            print(f"⚠️ خطأ في فحص DNS: {str(e)}")
    
    def _scan_ssl_certificates(self):
        """فحص شهادات SSL"""
        print("🔐 فحص شهادات SSL...")
        
        ssl_dirs = ['ssl/', 'ssl_init/', 'data/']
        for ssl_dir in ssl_dirs:
            if os.path.exists(ssl_dir):
                for root, dirs, files in os.walk(ssl_dir):
                    for file in files:
                        if file.endswith(('.pem', '.crt', '.cert')):
                            cert_path = os.path.join(root, file)
                            cert_info = self._analyze_ssl_certificate(cert_path)
                            if cert_info:
                                self.results['ssl_certificates'].append(cert_info)
    
    def _analyze_ssl_certificate(self, cert_path: str) -> Optional[Dict[str, Any]]:
        """تحليل شهادة SSL"""
        try:
            # قراءة الشهادة
            with open(cert_path, 'r') as f:
                cert_content = f.read()
            
            # استخراج معلومات أساسية
            cert_info = {
                'path': cert_path,
                'type': 'ssl_certificate',
                'file_size': os.path.getsize(cert_path),
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # فحص إضافي باستخدام openssl إذا كان متوفر
            try:
                result = subprocess.run([
                    'openssl', 'x509', '-in', cert_path, '-text', '-noout'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    output = result.stdout
                    
                    # استخراج معلومات الشهادة
                    if 'Subject:' in output:
                        subject_match = re.search(r'Subject:(.+)', output)
                        if subject_match:
                            cert_info['subject'] = subject_match.group(1).strip()
                    
                    if 'Issuer:' in output:
                        issuer_match = re.search(r'Issuer:(.+)', output)
                        if issuer_match:
                            cert_info['issuer'] = issuer_match.group(1).strip()
                    
                    # فحص تاريخ انتهاء الصلاحية
                    not_after_match = re.search(r'Not After : (.+)', output)
                    if not_after_match:
                        cert_info['expires'] = not_after_match.group(1).strip()
            except:
                pass
            
            return cert_info
            
        except Exception as e:
            print(f"⚠️ خطأ في تحليل الشهادة {cert_path}: {str(e)}")
            return None
    
    def _check_external_connections(self):
        """فحص الاتصالات الخارجية"""
        print("🌐 فحص الاتصالات الخارجية...")
        
        # فحص ملفات التكوين للبحث عن URLs خارجية
        config_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.conf', '.cfg', '.json', '.py')):
                    config_files.append(os.path.join(root, file))
        
        url_pattern = r'https?://[^\s"\'\]>)]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        for config_file in config_files[:50]:  # حد أقصى 50 ملف
            try:
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                urls = re.findall(url_pattern, content)
                for url in urls:
                    if not url.startswith(('127.0.0.1', 'localhost', '192.168.', '10.')):
                        self.results['external_connections'].append({
                            'url': url,
                            'source_file': config_file,
                            'type': 'external_url',
                            'timestamp': datetime.datetime.now().isoformat()
                        })
            except:
                continue
    
    def _check_firewall_status(self):
        """فحص حالة الجدار الناري"""
        print("🛡️ فحص الجدار الناري...")
        
        try:
            # فحص iptables
            result = subprocess.run(['iptables', '-L'], capture_output=True, text=True)
            if result.returncode == 0:
                rules = result.stdout.strip().split('\n')
                for rule in rules:
                    if rule.strip() and not rule.startswith('Chain'):
                        self.results['firewall_rules'].append({
                            'rule': rule.strip(),
                            'type': 'iptables',
                            'timestamp': datetime.datetime.now().isoformat()
                        })
        except:
            pass
        
        try:
            # فحص ufw
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
            if result.returncode == 0:
                self.results['firewall_rules'].append({
                    'rule': result.stdout.strip(),
                    'type': 'ufw',
                    'timestamp': datetime.datetime.now().isoformat()
                })
        except:
            pass
    
    def _scan_network_interfaces(self):
        """فحص واجهات الشبكة"""
        print("🔌 فحص واجهات الشبكة...")
        
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                interfaces = result.stdout.strip()
                
                # استخراج معلومات الواجهات
                interface_blocks = re.split(r'\n(?=\d+:)', interfaces)
                for block in interface_blocks:
                    if block.strip():
                        lines = block.strip().split('\n')
                        if lines:
                            interface_line = lines[0]
                            interface_name = re.search(r'\d+:\s+(\w+):', interface_line)
                            if interface_name:
                                name = interface_name.group(1)
                                
                                # استخراج عناوين IP
                                ip_addresses = re.findall(r'inet\s+(\S+)', block)
                                
                                self.results['network_interfaces'].append({
                                    'name': name,
                                    'ip_addresses': ip_addresses,
                                    'status': 'UP' if 'UP' in interface_line else 'DOWN',
                                    'timestamp': datetime.datetime.now().isoformat()
                                })
        except Exception as e:
            print(f"⚠️ خطأ في فحص واجهات الشبكة: {str(e)}")
    
    def _analyze_network_security(self):
        """تحليل الأمان الشبكي"""
        issues = []
        
        # فحص المنافذ المفتوحة الخطيرة
        dangerous_ports = [21, 23, 3306, 5432, 6379, 27017]
        open_dangerous = [p for p in self.results['open_ports'] if p['port'] in dangerous_ports]
        
        if open_dangerous:
            issues.append({
                'severity': 'high',
                'type': 'dangerous_ports_open',
                'count': len(open_dangerous),
                'description': 'منافذ خطيرة مفتوحة',
                'ports': [p['port'] for p in open_dangerous]
            })
        
        # فحص الاتصالات الخارجية المشبوهة
        external_count = len(self.results['external_connections'])
        if external_count > 20:
            issues.append({
                'severity': 'medium',
                'type': 'too_many_external_connections',
                'count': external_count,
                'description': 'عدد كبير من الاتصالات الخارجية'
            })
        
        # فحص شهادات SSL منتهية الصلاحية
        expired_certs = []
        for cert in self.results['ssl_certificates']:
            if 'expires' in cert:
                # فحص بسيط لتواريخ منتهية
                if 'expired' in cert['expires'].lower():
                    expired_certs.append(cert)
        
        if expired_certs:
            issues.append({
                'severity': 'medium',
                'type': 'expired_ssl_certificates',
                'count': len(expired_certs),
                'description': 'شهادات SSL منتهية الصلاحية'
            })
        
        self.results['security_issues'] = issues
    
    def generate_report(self) -> Dict[str, Any]:
        """إنشاء تقرير الشبكة"""
        summary = {
            'open_ports_count': len(self.results['open_ports']),
            'active_connections_count': len(self.results['active_connections']),
            'ssl_certificates_count': len(self.results['ssl_certificates']),
            'external_connections_count': len(self.results['external_connections']),
            'network_interfaces_count': len(self.results['network_interfaces']),
            'security_issues_count': len(self.results['security_issues']),
            'scan_timestamp': datetime.datetime.now().isoformat()
        }
        
        return {
            'summary': summary,
            'findings': self.results,
            'recommendations': self._get_network_recommendations()
        }
    
    def _get_network_recommendations(self) -> List[str]:
        """توصيات أمان الشبكة"""
        recommendations = []
        
        if any(p['port'] in [21, 23] for p in self.results['open_ports']):
            recommendations.append("🚫 إغلاق خدمات FTP و Telnet غير الآمنة")
        
        if any(p['port'] in [3306, 5432, 6379] for p in self.results['open_ports']):
            recommendations.append("🔒 تأمين قواعد البيانات وتقييد الوصول")
        
        if not self.results['firewall_rules']:
            recommendations.append("🛡️ تفعيل وتكوين الجدار الناري")
        
        recommendations.extend([
            "🔐 استخدام شهادات SSL صالحة",
            "🌐 مراقبة الاتصالات الخارجية",
            "📊 مراجعة المنافذ المفتوحة بانتظام",
            "🔄 تحديث النظام والخدمات"
        ])
        
        return recommendations

def main():
    analyzer = NetworkAnalyzer()
    print("🌐 بدء فحص الشبكة والاتصالات...")
    
    results = analyzer.scan_network()
    report = analyzer.generate_report()
    
    # حفظ التقرير
    with open('network_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم إنشاء تقرير فحص الشبكة: network_analysis_report.json")
    print(f"📊 النتائج: {report['summary']['open_ports_count']} منفذ مفتوح، {report['summary']['external_connections_count']} اتصال خارجي")
    
    return report

if __name__ == "__main__":
    main()
