import os
import json
import socket
import subprocess
import psutil
import platform
import datetime
from typing import Dict, List, Any

class NetworkAnalyzer:
    def __init__(self):
        self.results: Dict[str, Any] = {
            'open_ports': [],
            'active_connections': [],
            'ssl_certificates': [],
            'external_connections': [],
            'network_interfaces': [],
            'security_issues': []
        }
        self.scan_directory = "فحص"
        os.makedirs(self.scan_directory, exist_ok=True)

    def _run_command(self, command: List[str]) -> str:
        """تشغيل أمر في النظام والحصول على المخرجات"""
        try:
            return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore')
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e.output}"
        except FileNotFoundError:
            return "Error: Command not found. Ensure necessary tools are installed."

    def scan_open_ports(self, ip_address: str = '127.0.0.1', start_port: int = 1, end_port: int = 1024) -> None:
        """فحص المنافذ المفتوحة على عنوان IP معين"""
        print(f"🔎 فحص المنافذ المفتوحة على {ip_address}...")
        for port in range(start_port, end_port + 1):
            try:
                with socket.create_connection((ip_address, port), timeout=0.5) as sock:
                    self.results['open_ports'].append({'ip': ip_address, 'port': port, 'status': 'open'})
            except (socket.timeout, ConnectionRefusedError):
                pass
            except Exception as e:
                print(f"An unexpected error occurred while scanning port {port}: {e}")
        print(f"✅ اكتمل فحص المنافذ. تم العثور على {len(self.results['open_ports'])} منافذ مفتوحة.")

    def scan_active_connections(self) -> None:
        """الحصول على قائمة بالاتصالات النشطة"""
        print("🔌 فحص الاتصالات النشطة...")
        try:
            if platform.system() == "Windows":
                command = ['netstat', '-an']
            else:
                command = ['netstat', '-tunap'] # -t: TCP, -u: UDP, -n: numeric, -a: all, -p: program
            
            output = self._run_command(command)
            
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 4 and (parts[0].startswith('tcp') or parts[0].startswith('udp')):
                    local_address = parts[3]
                    remote_address = parts[4]
                    
                    if local_address != '0.0.0.0:0' and remote_address != '0.0.0.0:*':
                        try:
                            local_ip, local_port = local_address.rsplit(':', 1)
                            remote_ip, remote_port = remote_address.rsplit(':', 1)
                            
                            if local_ip != '127.0.0.1' and remote_ip != '127.0.0.1':
                                self.results['active_connections'].append({
                                    'protocol': parts[0],
                                    'local_address': local_address,
                                    'remote_address': remote_address,
                                    'state': parts[5] if len(parts) > 5 else 'N/A'
                                })
                        except ValueError:
                            continue # Skip lines with unexpected address formats
            print(f"✅ اكتمل فحص الاتصالات النشطة. تم العثور على {len(self.results['active_connections'])} اتصال نشط.")
        except Exception as e:
            print(f"An error occurred during active connections scan: {e}")

    def scan_external_connections(self) -> None:
        """تحديد الاتصالات الخارجية"""
        print("🌍 فحص الاتصالات الخارجية...")
        for conn in self.results['active_connections']:
            try:
                remote_ip = conn['remote_address'].split(':')[0]
                # A very basic check: if the IP doesn't start with '192.168.', '10.', or '172.16.' to '172.31.'
                # this is a simplification and might not be accurate for all private networks.
                if not (remote_ip.startswith('192.168.') or remote_ip.startswith('10.') or 
                        (remote_ip.startswith('172.') and 16 <= int(remote_ip.split('.')[1]) <= 31)):
                    self.results['external_connections'].append(conn)
            except IndexError:
                continue # Skip if remote address format is unexpected
        print(f"✅ اكتمل فحص الاتصالات الخارجية. تم العثور على {len(self.results['external_connections'])} اتصال خارجي.")

    def scan_network_interfaces(self) -> None:
        """الحصول على معلومات واجهات الشبكة"""
        print("💻 فحص واجهات الشبكة...")
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        self.results['network_interfaces'].append({
                            'interface': interface,
                            'ip_address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast_ip': addr.broadcast
                        })
            print(f"✅ اكتمل فحص واجهات الشبكة. تم العثور على {len(self.results['network_interfaces'])} واجهة شبكة.")
        except Exception as e:
            print(f"An error occurred during network interfaces scan: {e}")

    def scan_ssl_certificates(self, ip_address: str = '127.0.0.1') -> None:
        """فحص شهادات SSL (بشكل أساسي للتحقق من وجود خدمة HTTPS)"""
        # This is a simplified check. A full SSL certificate scan is complex.
        # We'll check if common HTTPS ports are open and attempt a basic connection.
        print("🔒 فحص شهادات SSL (التحقق من وجود HTTPS)...")
        https_ports = [443, 8443, 8080] # Common HTTPS ports
        for port in https_ports:
            try:
                with socket.create_connection((ip_address, port), timeout=1) as sock:
                    # Attempt to perform an SSL handshake (very basic)
                    context = None
                    if hasattr(ssl, 'create_default_context'):
                        context = ssl.create_default_context()
                    
                    if context:
                        with context.wrap_socket(sock, server_hostname=ip_address) as ssock:
                            cert = ssock.getpeercert()
                            if cert:
                                self.results['ssl_certificates'].append({
                                    'ip': ip_address,
                                    'port': port,
                                    'subject': cert.get('subject'),
                                    'issuer': cert.get('issuer'),
                                    'expiry_date': cert.get('notAfter')
                                })
                                print(f"  ✅ تم العثور على اتصال HTTPS على المنفذ {port}.")
                    else: # Fallback for older Python versions or environments without ssl context
                         self.results['ssl_certificates'].append({'ip': ip_address, 'port': port, 'status': 'HTTPS might be available'})
                         print(f"  ⚠️ تم العثور على اتصال على المنفذ {port}, لكن التحقق من SSL غير مدعوم بالكامل.")

            except (socket.timeout, ConnectionRefusedError, ssl.SSLError):
                pass # Port not open or SSL error, expected
            except Exception as e:
                print(f"An unexpected error occurred during SSL scan on port {port}: {e}")
        print(f"✅ اكتمل فحص SSL. تم العثور على {len(self.results['ssl_certificates'])} شهادة SSL محتملة.")

    def scan_security_issues(self) -> None:
        """فحص قضايا أمنية بسيطة"""
        print("🛡️ فحص القضايا الأمنية...")
        # 1. Check for known insecure ports
        insecure_ports = [21, 23, 135, 137, 138, 139, 445]
        for port_info in self.results['open_ports']:
            if port_info['port'] in insecure_ports:
                self.results['security_issues'].append({
                    'issue': f"منفذ غير آمن مفتوح: {port_info['port']}",
                    'recommendation': "إغلاق المنافذ غير الضرورية أو تأمينها."
                })

        # 2. Check for default credentials (highly simplified and not exhaustive)
        # This part is difficult to implement reliably without specific service checks.
        # We'll add a placeholder recommendation.
        self.results['security_issues'].append({
            'issue': "استخدام كلمات مرور افتراضية أو ضعيفة محتمل",
            'recommendation': "تغيير جميع كلمات المرور الافتراضية وتطبيق سياسات كلمات مرور قوية."
        })
        
        # 3. Check for missing SSL on sensitive ports (e.g., if 443 is open but no SSL found)
        if any(p['port'] == 80 for p in self.results['open_ports']) and not any(s['port'] == 443 for s in self.results['ssl_certificates']):
             self.results['security_issues'].append({
                'issue': "خدمة HTTP تعمل على المنفذ 80 بدون HTTPS مطابق على المنفذ 443.",
                'recommendation': "تطبيق HTTPS على المنفذ 443 لتشفير الاتصالات."
            })

        print(f"✅ اكتمل فحص القضايا الأمنية. تم العثور على {len(self.results['security_issues'])} قضية أمنية محتملة.")
        
    def scan_network(self) -> Dict[str, Any]:
        """تنفيذ جميع عمليات فحص الشبكة"""
        print("\n" + "="*50)
        print("🚀 بدء تحليل شامل للشبكة 🚀")
        print("="*50)
        
        local_ip = socket.gethostbyname(socket.gethostname())
        
        self.scan_open_ports(local_ip)
        self.scan_active_connections()
        self.scan_network_interfaces()
        self.scan_external_connections() # Depends on active_connections
        self.scan_ssl_certificates(local_ip) # Depends on open ports for HTTPS
        self.scan_security_issues() # Depends on open_ports and ssl_certificates

        # Add results to the main results dictionary
        # The individual scan methods already populate self.results

        print("\n" + "="*50)
        print("✅ اكتمل تحليل الشبكة!")
        print("="*50)
        
        # The generate_report and main function will be handled separately or called after this.
        return self.results


    def generate_report(self) -> Dict[str, Any]:
        """إنشاء تقرير شامل للشبكة"""
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
        """توصيات أمنية للشبكة"""
        recommendations = []

        if any(p['port'] in [21, 23] for p in self.results['open_ports']):
            recommendations.append("🚫 إغلاق المنافذ غير الآمنة (FTP, Telnet)")

        if self.results['ssl_certificates']:
            recommendations.append("🔐 مراجعة شهادات SSL وتجديد المنتهية الصلاحية")

        if len(self.results['external_connections']) > 10:
            recommendations.append("🌐 مراجعة الاتصالات الخارجية والتأكد من ضرورتها")

        recommendations.extend([
            "🛡️ تفعيل الجدار الناري",
            "🔒 استخدام SSH بدلاً من Telnet",
            "📊 مراقبة حركة الشبكة بانتظام"
        ])

        return recommendations


# Ensure json and ssl are imported if not already
import json
import ssl

def main():
    analyzer = NetworkAnalyzer()
    print("🌐 بدء فحص الشبكة والاتصالات...")

    results = analyzer.scan_network()
    report = analyzer.generate_report()

    # حفظ التقرير داخل مجلد 'فحص'
    report_filename = 'network_analysis_report.json'
    report_path = os.path.join(analyzer.scan_directory, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ تم إنشاء تقرير فحص الشبكة في المسار: {report_path}")
    print(f"📊 النتائج: {report['summary']['open_ports_count']} منفذ مفتوح، {report['summary']['ssl_certificates_count']} شهادة SSL")

    return report

if __name__ == "__main__":
    main()