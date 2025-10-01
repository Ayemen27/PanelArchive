#!/usr/bin/env python3
"""
Comprehensive Fail2Ban Filter Test - Final Verification
Tests all 17 true positives and 10 false positives
"""

import re
import sys

# Complete regex patterns from setup_fail2ban.sh
PATTERNS = [
    # Login failed patterns - CRITICAL: Order matters!
    r'^.*[Ll]ogin [Ff]ailed[^,]*[Ff]rom\s+[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed[^,]*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed.*username:[^,]+,\s*ip:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ll]ogin [Ff]ailed.*username:[^,]+,\s*ip\((?P<host>[^)]+)\)',
    r'^.*[Ll]ogin [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Error: Login failed
    r'^.*[Ee]rror:\s*[Ll]ogin [Ff]ailed.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ee]rror:\s*[Ll]ogin [Ff]ailed.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ee]rror:\s*[Ll]ogin [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # [error] Login failed
    r'^.*\[error\].*[Ll]ogin.*[Ff]ailed.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*\[error\].*[Ll]ogin.*[Ff]ailed.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*\[error\].*[Ll]ogin.*[Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Authentication failed
    r'^.*[Aa]uthentication [Ff]ailed.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Aa]uthentication [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Aa]uthentication [Ff]ailed.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Auth failed
    r'^.*[Aa]uth [Ff]ailed.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Aa]uth [Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Aa]uth [Ff]ailed.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # [error] Auth failed
    r'^.*\[error\].*[Aa]uth.*[Ff]ailed.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*\[error\].*[Aa]uth.*[Ff]ailed.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*\[error\].*[Aa]uth.*[Ff]ailed.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Failed password
    r'^.*[Ff]ailed [Pp]assword.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ff]ailed [Pp]assword.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ff]ailed [Pp]assword.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Invalid user
    r'^.*[Ii]nvalid [Uu]ser.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ii]nvalid [Uu]ser.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Ii]nvalid [Uu]ser.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Unauthorized access
    r'^.*[Uu]nauthorized [Aa]ccess.*[Ff]rom\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Uu]nauthorized [Aa]ccess.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Uu]nauthorized [Aa]ccess.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    
    # Access denied
    r'^.*[Aa]ccess [Dd]enied.*[Ff]or\s+(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Aa]ccess [Dd]enied.*,\s*[Ii][Pp]:\s*(?P<host>\S+?)(?:\s|$|,|;)',
    r'^.*[Aa]ccess [Dd]enied.*client:\s*(?P<host>\S+?)(?:\s|$|,|;)',
]

def extract_ip(log_line):
    """Extract IP from log line using all patterns"""
    for pattern in PATTERNS:
        match = re.search(pattern, log_line)
        if match:
            return match.group('host')
    return None

# TRUE POSITIVES - Must detect (17 total)
TRUE_POSITIVES = [
    # Standard formats
    ("2025-01-01 12:00:00 [error] Login failed for user 'admin' from IP: 192.168.1.100", "192.168.1.100"),
    ("2025-01-01 12:00:00 [notice] Authentication failed from 192.168.1.100", "192.168.1.100"),
    ("2025-01-01 12:00:00 [error] Failed password for admin from 192.168.1.100 port 12345", "192.168.1.100"),
    ("2025-01-01 12:00:00 [error] Invalid user test from 192.168.1.50", "192.168.1.50"),
    ("2025-01-01 12:00:00 [error] Unauthorized access attempt from 10.0.0.5", "10.0.0.5"),
    
    # aaPanel-specific formats (username:, ip:, ip())
    ("2025-01-01 12:00:00 [error] Login failed, username: admin, ip: 192.168.1.100", "192.168.1.100"),
    ("2025-01-01 12:00:00 [error] Login failed, username: admin, ip(192.168.1.100)", "192.168.1.100"),
    ("2025-01-01 12:00:00 Error: login failed; client: 192.168.1.100", "192.168.1.100"),
    ("2025-01-01 12:00:00 [error] Authentication failed, client: 192.168.1.101", "192.168.1.101"),
    ("2025-01-01 12:00:00 [error] Failed password for admin, client: 192.168.1.102", "192.168.1.102"),
    
    # CRITICAL: Multi-IP scenarios (must match correct IP)
    ("2025-01-01 12:00:00 [error] Login failed, username: admin, last login IP: 10.0.0.5, IP: 192.168.1.100", "192.168.1.100"),
    ("2025-01-01 12:00:00 [error] Login failed from 192.168.1.100, previous login was from 10.0.0.5", "192.168.1.100"),
    
    # Variations
    ("2025-01-01 12:00:00 [error] login failed from IP: 10.20.30.40", "10.20.30.40"),
    ("2025-01-01 12:00:00 [error] Auth failed from 172.16.0.1", "172.16.0.1"),
    ("2025-01-01 12:00:00 [error] Auth failed, client: 172.16.0.2", "172.16.0.2"),
    ("2025-01-01 12:00:00 [error] Access denied for 192.168.1.99", "192.168.1.99"),
    ("2025-01-01 12:00:00 [error] Access denied, client: 192.168.1.98", "192.168.1.98"),
]

# FALSE POSITIVES - Must NOT detect (10 total)
FALSE_POSITIVES = [
    # Normal errors
    "2025-01-01 12:00:00 [error] 404 Not Found: /api/users from 192.168.1.200",
    "2025-01-01 12:00:00 [error] 500 Internal Server Error from 192.168.1.201",
    "2025-01-01 12:00:00 [notice] 10.0.0.10 \"GET /api/data\" 404",
    "2025-01-01 12:00:00 [notice] 10.0.0.11 \"POST /api/submit\" 500",
    "2025-01-01 12:00:00 [error] client: 192.168.1.202 - Database connection failed",
    "2025-01-01 12:00:00 [error] client: 192.168.1.203 - File not found: /tmp/data.txt",
    
    # CRITICAL: Multi-IP scenarios that should NOT match (successful logins)
    "2025-01-01 12:00:00 [info] Login succeeded from 192.168.1.10, last failed IP: 10.0.0.5",
    "2025-01-01 12:00:00 [notice] User logged in from 192.168.1.20, previous login 192.168.1.21",
    "2025-01-01 12:00:00 [info] Session established for 192.168.1.30, referred by 192.168.1.31",
    "2025-01-01 12:00:00 [notice] Connection from 192.168.1.40 successful (last IP: 192.168.1.41)",
]

def run_tests():
    print("=" * 80)
    print("COMPREHENSIVE FAIL2BAN FILTER TEST")
    print("=" * 80)
    print()
    
    tp_passed = 0
    tp_failed = 0
    fp_passed = 0
    fp_failed = 0
    
    # Test True Positives
    print("📋 Testing TRUE POSITIVES (17 total - must ALL be detected)")
    print("-" * 80)
    for i, (log_line, expected_ip) in enumerate(TRUE_POSITIVES, 1):
        extracted_ip = extract_ip(log_line)
        if extracted_ip == expected_ip:
            print(f"✅ TP {i:2d}/17: PASS - Extracted {expected_ip}")
            tp_passed += 1
        else:
            print(f"❌ TP {i:2d}/17: FAIL - Expected {expected_ip}, got {extracted_ip}")
            print(f"         Log: {log_line[:70]}...")
            tp_failed += 1
    
    print()
    print("📋 Testing FALSE POSITIVES (10 total - must ALL be ignored)")
    print("-" * 80)
    for i, log_line in enumerate(FALSE_POSITIVES, 1):
        extracted_ip = extract_ip(log_line)
        if extracted_ip is None:
            print(f"✅ FP {i:2d}/10: PASS - Correctly ignored")
            fp_passed += 1
        else:
            print(f"❌ FP {i:2d}/10: FAIL - Incorrectly matched {extracted_ip}")
            print(f"         Log: {log_line[:70]}...")
            fp_failed += 1
    
    print()
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"True Positives:  {tp_passed}/17 passed, {tp_failed}/17 failed")
    print(f"False Positives: {fp_passed}/10 passed, {fp_failed}/10 failed")
    print()
    
    total_tests = 27
    total_passed = tp_passed + fp_passed
    total_failed = tp_failed + fp_failed
    
    success_rate = (total_passed / total_tests) * 100
    print(f"Overall: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
    print()
    
    if total_failed == 0:
        print("🎉 ✅ SUCCESS! All tests passed!")
        print()
        print("✓ All 17 true positives detected correctly")
        print("✓ All 10 false positives ignored correctly")
        print("✓ Critical multi-IP scenarios extract correct IP")
        print()
        print("The Fail2Ban filter is ready for production! 🛡️")
        return 0
    else:
        print("❌ FAILURE! Some tests failed.")
        print()
        print(f"✗ {tp_failed} true positive(s) failed (missed detections)")
        print(f"✗ {fp_failed} false positive(s) failed (wrong detections)")
        print()
        print("⚠️  DO NOT deploy until all tests pass!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
