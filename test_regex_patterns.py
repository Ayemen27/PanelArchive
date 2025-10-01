#!/usr/bin/env python3
"""
Test Fail2Ban regex patterns for aaPanel filter
Simulates fail2ban-regex behavior to verify IP extraction
"""

import re
import sys

# Regex patterns from setup_fail2ban.sh (converted to Python)
PATTERNS = [
    # Login failed patterns - CRITICAL: Order matters! More specific patterns first
    # "from IP:" must come before "from <HOST>" to avoid matching "IP:" as host
    r'^.*[Ll]ogin [Ff]ailed[^,]*[Ff]rom\s+[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed[^,]*[Ff]rom\s+(?P<host>(?:(?!from)[0-9]{1,3}\.){3}[0-9]{1,3})(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed.*username:[^,]+,\s*ip:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed.*username:[^,]+,\s*ip\((?P<host>[^)]+)\)',
    r'^.*[Ll]ogin [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Error: Login failed
    r'^.*[Ee]rror:\s*[Ll]ogin [Ff]ailed.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Ee]rror:\s*[Ll]ogin [Ff]ailed.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Ee]rror:\s*[Ll]ogin [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # [error] Login failed
    r'^.*\[error\].*[Ll]ogin.*[Ff]ailed.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*\[error\].*[Ll]ogin.*[Ff]ailed.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*\[error\].*[Ll]ogin.*[Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # Authentication failed
    r'^.*[Aa]uthentication [Ff]ailed.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Aa]uthentication [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Aa]uthentication [Ff]ailed.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # Auth failed
    r'^.*[Aa]uth [Ff]ailed.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Aa]uth [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Aa]uth [Ff]ailed.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # [error] Auth failed
    r'^.*\[error\].*[Aa]uth.*[Ff]ailed.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*\[error\].*[Aa]uth.*[Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*\[error\].*[Aa]uth.*[Ff]ailed.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # Failed password
    r'^.*[Ff]ailed [Pp]assword.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Ff]ailed [Pp]assword.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Ff]ailed [Pp]assword.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # Invalid user
    r'^.*[Ii]nvalid [Uu]ser.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Ii]nvalid [Uu]ser.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Ii]nvalid [Uu]ser.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # Unauthorized access
    r'^.*[Uu]nauthorized [Aa]ccess.*[Ff]rom\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Uu]nauthorized [Aa]ccess.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Uu]nauthorized [Aa]ccess.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
    
    # Access denied
    r'^.*[Aa]ccess [Dd]enied.*[Ff]or\s+(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Aa]ccess [Dd]enied.*,\s*[Ii][Pp]:\s*(?P<host>\S+)(?:\s|$|,|;)',
    r'^.*[Aa]ccess [Dd]enied.*client:\s*(?P<host>\S+)(?:\s|$|,|;)',
]

def extract_ip(log_line):
    """Extract IP from log line using all patterns"""
    for pattern in PATTERNS:
        match = re.search(pattern, log_line)
        if match:
            return match.group('host')
    return None

def test_cases():
    """Test critical scenarios"""
    test_data = [
        # (log_line, expected_ip, description)
        ("2025-01-01 12:00:00 [error] Login failed, username: admin, last login IP: 10.0.0.5, IP: 192.168.1.100", 
         "192.168.1.100", "Multi-IP: should extract attack IP, not last login IP"),
        
        ("2025-01-01 12:00:00 [error] Login failed from 192.168.1.100, previous login was from 10.0.0.5", 
         "192.168.1.100", "Multi-IP: should extract first IP (attack), not historical"),
        
        ("2025-01-01 12:00:00 [error] Login failed, username: admin, ip: 192.168.1.100", 
         "192.168.1.100", "Standard format with username, ip:"),
        
        ("2025-01-01 12:00:00 Error: login failed; client: 172.16.0.1", 
         "172.16.0.1", "Client format"),
        
        ("2025-01-01 12:00:00 [error] login failed from IP: 10.20.30.40", 
         "10.20.30.40", "From IP: format"),
        
        ("2025-01-01 12:00:00 [error] Login failed for user 'admin' from IP: 192.168.1.100", 
         "192.168.1.100", "Standard format with from IP:"),
        
        ("2025-01-01 12:00:00 [notice] Authentication failed from 192.168.1.100", 
         "192.168.1.100", "Authentication failed from"),
        
        ("2025-01-01 12:00:00 [error] Failed password for admin from 192.168.1.100 port 12345", 
         "192.168.1.100", "Failed password from"),
        
        ("2025-01-01 12:00:00 [error] Invalid user test from 192.168.1.50", 
         "192.168.1.50", "Invalid user from"),
        
        ("2025-01-01 12:00:00 [error] Unauthorized access attempt from 10.0.0.5", 
         "10.0.0.5", "Unauthorized access from"),
        
        # Should NOT match
        ("2025-01-01 12:00:00 [error] 404 Not Found: /api/users from 192.168.1.200", 
         None, "False positive: 404 error (no auth failure)"),
        
        ("2025-01-01 12:00:00 [error] 500 Internal Server Error from 192.168.1.201", 
         None, "False positive: 500 error (no auth failure)"),
        
        ("2025-01-01 12:00:00 [info] Login succeeded from 192.168.1.10, last failed IP: 10.0.0.5", 
         None, "False positive: successful login"),
    ]
    
    print("=" * 80)
    print("Testing Fail2Ban Regex Patterns for aaPanel")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for log_line, expected_ip, description in test_data:
        extracted_ip = extract_ip(log_line)
        
        if expected_ip is None:
            # Should NOT match
            if extracted_ip is None:
                print(f"✅ PASS: {description}")
                print(f"   Log: {log_line[:80]}...")
                print(f"   Expected: No match | Got: No match")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Log: {log_line[:80]}...")
                print(f"   Expected: No match | Got: {extracted_ip} (FALSE POSITIVE!)")
                failed += 1
        else:
            # Should match specific IP
            if extracted_ip == expected_ip:
                print(f"✅ PASS: {description}")
                print(f"   Log: {log_line[:80]}...")
                print(f"   Expected: {expected_ip} | Got: {extracted_ip}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Log: {log_line[:80]}...")
                print(f"   Expected: {expected_ip} | Got: {extracted_ip}")
                failed += 1
        
        print()
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 80)
    
    if failed > 0:
        print("❌ CRITICAL: Some tests failed! Fix the regex patterns.")
        sys.exit(1)
    else:
        print("✅ SUCCESS: All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    test_cases()
