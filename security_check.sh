#!/bin/bash

# ================================================================
# Comprehensive Security Check Script for aaPanel
# ================================================================
# هذا السكريبت يفحص النظام بحثاً عن المشاكل الأمنية والثغرات
#
# الاستخدام:
#   sudo ./security_check.sh
#   sudo ./security_check.sh --detailed
#   sudo ./security_check.sh --json
#
# الفحوصات:
#   1. System configuration
#   2. Network security
#   3. File permissions
#   4. User accounts
#   5. Services and processes
#   6. Installed packages
#   7. Logs and audit
#   8. Compliance checks
# ================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0
CHECKS_TOTAL=0

# Output mode
OUTPUT_MODE="normal"  # normal, detailed, json

# Parse arguments
for arg in "$@"; do
    case $arg in
        --detailed)
            OUTPUT_MODE="detailed"
            ;;
        --json)
            OUTPUT_MODE="json"
            ;;
        -h|--help)
            echo "Usage: sudo ./security_check.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --detailed    Show detailed output"
            echo "  --json        Output in JSON format"
            echo "  -h, --help    Show this help"
            exit 0
            ;;
    esac
done

# ================================================================
# Helper Functions
# ================================================================

print_header() {
    if [ "$OUTPUT_MODE" != "json" ]; then
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}  $1${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    fi
}

check_start() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if [ "$OUTPUT_MODE" = "normal" ] || [ "$OUTPUT_MODE" = "detailed" ]; then
        echo -e "${CYAN}🔍 فحص $CHECKS_TOTAL: $1${NC}"
    fi
}

check_pass() {
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    if [ "$OUTPUT_MODE" != "json" ]; then
        echo -e "${GREEN}   ✅ نجح: $1${NC}"
    fi
}

check_fail() {
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
    if [ "$OUTPUT_MODE" != "json" ]; then
        echo -e "${RED}   ❌ فشل: $1${NC}"
    fi
}

check_warning() {
    CHECKS_WARNING=$((CHECKS_WARNING + 1))
    if [ "$OUTPUT_MODE" != "json" ]; then
        echo -e "${YELLOW}   ⚠️  تحذير: $1${NC}"
    fi
}

check_info() {
    if [ "$OUTPUT_MODE" = "detailed" ]; then
        echo -e "${BLUE}      ℹ️  $1${NC}"
    fi
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}❌ هذا السكريبت يجب تشغيله بصلاحيات root${NC}"
        echo -e "${BLUE}ℹ️  استخدم: sudo $0${NC}"
        exit 1
    fi
}

# ================================================================
# Security Checks
# ================================================================

check_root

if [ "$OUTPUT_MODE" != "json" ]; then
    print_header "🔒 فحص أمان شامل لـ aaPanel"
fi

# ================================================================
# 1. System Configuration Checks
# ================================================================

print_header "1️⃣ فحص إعدادات النظام"

# Check 1.1: SELinux/AppArmor
check_start "التحقق من SELinux/AppArmor"
if command -v getenforce &> /dev/null; then
    SELINUX_STATUS=$(getenforce 2>/dev/null || echo "unknown")
    if [ "$SELINUX_STATUS" = "Enforcing" ]; then
        check_pass "SELinux enabled and enforcing"
    else
        check_warning "SELinux not enforcing (status: $SELINUX_STATUS)"
    fi
elif command -v aa-status &> /dev/null; then
    if aa-status --enabled 2>/dev/null; then
        check_pass "AppArmor enabled"
    else
        check_warning "AppArmor not enabled"
    fi
else
    check_warning "لا SELinux ولا AppArmor مثبت"
fi

# Check 1.2: Kernel parameters
check_start "التحقق من kernel hardening parameters"
SYSCTL_CHECKS=(
    "net.ipv4.tcp_syncookies=1"
    "net.ipv4.conf.all.accept_redirects=0"
    "net.ipv4.conf.all.accept_source_route=0"
    "kernel.randomize_va_space=2"
    "kernel.dmesg_restrict=1"
)

SYSCTL_PASS=0
for check in "${SYSCTL_CHECKS[@]}"; do
    param=$(echo "$check" | cut -d= -f1)
    expected=$(echo "$check" | cut -d= -f2)
    actual=$(sysctl -n "$param" 2>/dev/null || echo "notset")
    
    if [ "$actual" = "$expected" ]; then
        SYSCTL_PASS=$((SYSCTL_PASS + 1))
        check_info "$param = $expected ✓"
    else
        check_info "$param = $actual (expected: $expected) ✗"
    fi
done

if [ $SYSCTL_PASS -ge 4 ]; then
    check_pass "Kernel hardening parameters configured ($SYSCTL_PASS/5)"
else
    check_warning "Some kernel parameters not configured ($SYSCTL_PASS/5)"
fi

# Check 1.3: Core dumps
check_start "التحقق من core dumps"
if [ "$(sysctl -n fs.suid_dumpable 2>/dev/null)" = "0" ]; then
    check_pass "Core dumps disabled (fs.suid_dumpable=0)"
else
    check_warning "Core dumps enabled - security risk"
fi

# ================================================================
# 2. Network Security Checks
# ================================================================

print_header "2️⃣ فحص أمان الشبكة"

# Check 2.1: Firewall status
check_start "التحقق من Firewall"
if systemctl is-active --quiet ufw; then
    check_pass "UFW firewall active"
    
    # Check default policies
    UFW_STATUS=$(ufw status verbose 2>/dev/null)
    if echo "$UFW_STATUS" | grep -q "Default: deny (incoming)"; then
        check_info "Default policy: deny incoming ✓"
    else
        check_warning "Default policy not set to deny incoming"
    fi
elif systemctl is-active --quiet firewalld; then
    check_pass "firewalld active"
else
    check_fail "No active firewall detected"
fi

# Check 2.2: Open ports
check_start "فحص المنافذ المفتوحة"
OPEN_PORTS=$(ss -tuln | grep LISTEN | awk '{print $5}' | sed 's/.*://' | sort -u | wc -l)
if [ "$OPEN_PORTS" -le 10 ]; then
    check_pass "عدد المنافذ المفتوحة معقول ($OPEN_PORTS)"
    if [ "$OUTPUT_MODE" = "detailed" ]; then
        ss -tuln | grep LISTEN | awk '{print $5}' | sed 's/.*://' | sort -u | while read port; do
            check_info "Port $port"
        done
    fi
else
    check_warning "عدد كبير من المنافذ المفتوحة ($OPEN_PORTS)"
fi

# Check 2.3: IP forwarding
check_start "التحقق من IP forwarding"
if [ "$(sysctl -n net.ipv4.ip_forward)" = "0" ]; then
    check_pass "IP forwarding disabled"
else
    check_warning "IP forwarding enabled - قد يكون خطر أمني"
fi

# ================================================================
# 3. SSH Security Checks
# ================================================================

print_header "3️⃣ فحص أمان SSH"

SSH_CONFIG="/etc/ssh/sshd_config"

if [ -f "$SSH_CONFIG" ]; then
    # Check 3.1: Root login
    check_start "التحقق من SSH root login"
    ROOT_LOGIN=$(grep "^PermitRootLogin" "$SSH_CONFIG" | awk '{print $2}')
    if [ "$ROOT_LOGIN" = "no" ]; then
        check_pass "Root login disabled"
    else
        check_fail "Root login enabled - خطر أمني!"
    fi
    
    # Check 3.2: Password authentication
    check_start "التحقق من SSH password authentication"
    PASS_AUTH=$(grep "^PasswordAuthentication" "$SSH_CONFIG" | awk '{print $2}')
    if [ "$PASS_AUTH" = "no" ]; then
        check_pass "Password authentication disabled (key-based only)"
    else
        check_warning "Password authentication enabled"
    fi
    
    # Check 3.3: Protocol version
    check_start "التحقق من SSH protocol version"
    if grep -q "^Protocol 2" "$SSH_CONFIG"; then
        check_pass "SSH Protocol 2 enforced"
    else
        check_warning "SSH Protocol version not explicitly set to 2"
    fi
    
    # Check 3.4: Max auth tries
    check_start "التحقق من SSH MaxAuthTries"
    MAX_TRIES=$(grep "^MaxAuthTries" "$SSH_CONFIG" | awk '{print $2}')
    if [ -n "$MAX_TRIES" ] && [ "$MAX_TRIES" -le 3 ]; then
        check_pass "MaxAuthTries set to $MAX_TRIES (good)"
    else
        check_warning "MaxAuthTries not set or too high (current: ${MAX_TRIES:-default})"
    fi
else
    check_warning "SSH config file not found"
fi

# ================================================================
# 4. User Account Security
# ================================================================

print_header "4️⃣ فحص أمان حسابات المستخدمين"

# Check 4.1: Password aging
check_start "التحقق من password aging policies"
if grep -q "^PASS_MAX_DAYS.*90" /etc/login.defs && \
   grep -q "^PASS_MIN_DAYS.*1" /etc/login.defs; then
    check_pass "Password aging policies configured"
else
    check_warning "Password aging policies not optimal"
fi

# Check 4.2: Empty passwords
check_start "البحث عن حسابات بدون كلمات مرور"
EMPTY_PASS=$(awk -F: '($2 == "" ) { print $1 }' /etc/shadow 2>/dev/null | wc -l)
if [ "$EMPTY_PASS" -eq 0 ]; then
    check_pass "No accounts with empty passwords"
else
    check_fail "$EMPTY_PASS accounts with empty passwords found!"
fi

# Check 4.3: UID 0 accounts
check_start "البحث عن حسابات بـ UID 0 (غير root)"
UID_0=$(awk -F: '($3 == "0") {print $1}' /etc/passwd | grep -v "^root$" | wc -l)
if [ "$UID_0" -eq 0 ]; then
    check_pass "No non-root accounts with UID 0"
else
    check_fail "$UID_0 non-root accounts with UID 0 found!"
fi

# Check 4.4: Sudo configuration
check_start "التحقق من sudo configuration"
if [ -f /etc/sudoers ]; then
    if grep -q "^Defaults.*requiretty" /etc/sudoers 2>/dev/null; then
        check_info "sudo requiretty enabled ✓"
    fi
    check_pass "sudoers file exists"
else
    check_warning "sudoers file not found"
fi

# ================================================================
# 5. File Permission Checks
# ================================================================

print_header "5️⃣ فحص صلاحيات الملفات الحساسة"

# Check 5.1: Critical file permissions
check_start "التحقق من صلاحيات الملفات الحرجة"
FILES_TO_CHECK=(
    "/etc/passwd:644"
    "/etc/shadow:600"
    "/etc/group:644"
    "/etc/gshadow:600"
    "/etc/ssh/sshd_config:600"
)

FILES_OK=0
for file_perm in "${FILES_TO_CHECK[@]}"; do
    file=$(echo "$file_perm" | cut -d: -f1)
    expected=$(echo "$file_perm" | cut -d: -f2)
    
    if [ -f "$file" ]; then
        actual=$(stat -c "%a" "$file" 2>/dev/null || stat -f "%Lp" "$file" 2>/dev/null)
        if [ "$actual" = "$expected" ]; then
            FILES_OK=$((FILES_OK + 1))
            check_info "$file: $actual ✓"
        else
            check_info "$file: $actual (expected: $expected) ✗"
        fi
    fi
done

if [ $FILES_OK -ge 4 ]; then
    check_pass "Critical file permissions OK ($FILES_OK/5)"
else
    check_warning "Some file permissions incorrect ($FILES_OK/5)"
fi

# Check 5.2: World-writable files
check_start "البحث عن ملفات world-writable"
WORLD_WRITABLE=$(find / -xdev -type f -perm -002 ! -path "/proc/*" ! -path "/sys/*" 2>/dev/null | wc -l)
if [ "$WORLD_WRITABLE" -eq 0 ]; then
    check_pass "No world-writable files found"
else
    check_warning "$WORLD_WRITABLE world-writable files found"
fi

# Check 5.3: Unowned files
check_start "البحث عن ملفات بدون مالك"
UNOWNED=$(find / -xdev -nouser -o -nogroup ! -path "/proc/*" ! -path "/sys/*" 2>/dev/null | wc -l)
if [ "$UNOWNED" -eq 0 ]; then
    check_pass "No unowned files found"
else
    check_warning "$UNOWNED unowned files found"
fi

# ================================================================
# 6. Service Security Checks
# ================================================================

print_header "6️⃣ فحص أمان الخدمات"

# Check 6.1: Fail2Ban
check_start "التحقق من Fail2Ban"
if systemctl is-active --quiet fail2ban; then
    JAILS=$(fail2ban-client status 2>/dev/null | grep "Jail list:" | sed 's/.*://; s/,/ /g' | wc -w)
    check_pass "Fail2Ban active with $JAILS jails"
else
    check_warning "Fail2Ban not active"
fi

# Check 6.2: Audit daemon
check_start "التحقق من audit daemon"
if systemctl is-active --quiet auditd; then
    RULES=$(auditctl -l 2>/dev/null | grep -v "No rules" | wc -l)
    check_pass "auditd active with $RULES rules"
else
    check_warning "auditd not active"
fi

# Check 6.3: Unnecessary services
check_start "فحص الخدمات غير الضرورية"
UNNECESSARY_SERVICES=(
    "telnet"
    "rsh"
    "rlogin"
    "ftp"
    "tftp"
)

UNNECESSARY_FOUND=0
for service in "${UNNECESSARY_SERVICES[@]}"; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        UNNECESSARY_FOUND=$((UNNECESSARY_FOUND + 1))
        check_info "$service running (should be disabled)"
    fi
done

if [ $UNNECESSARY_FOUND -eq 0 ]; then
    check_pass "No unnecessary services running"
else
    check_warning "$UNNECESSARY_FOUND unnecessary services found"
fi

# ================================================================
# 7. Package & Update Checks
# ================================================================

print_header "7️⃣ فحص الحزم والتحديثات"

# Check 7.1: Automatic updates
check_start "التحقق من automatic updates"
if command -v unattended-upgrades &> /dev/null; then
    if [ -f /etc/apt/apt.conf.d/20auto-upgrades ]; then
        check_pass "Automatic updates configured (Ubuntu/Debian)"
    else
        check_warning "unattended-upgrades installed but not configured"
    fi
elif systemctl is-active --quiet yum-cron 2>/dev/null; then
    check_pass "Automatic updates active (CentOS/RHEL)"
else
    check_warning "Automatic updates not configured"
fi

# Check 7.2: Available updates
check_start "التحقق من التحديثات المتاحة"
if command -v apt &> /dev/null; then
    UPDATES=$(apt list --upgradable 2>/dev/null | grep -c upgradable || echo "0")
    if [ "$UPDATES" -eq 0 ]; then
        check_pass "System up to date"
    else
        check_warning "$UPDATES updates available"
    fi
elif command -v yum &> /dev/null; then
    UPDATES=$(yum check-update --quiet 2>/dev/null | grep -v "^$" | wc -l || echo "0")
    if [ "$UPDATES" -eq 0 ]; then
        check_pass "System up to date"
    else
        check_warning "$UPDATES updates available"
    fi
fi

# ================================================================
# 8. Log & Audit Checks
# ================================================================

print_header "8️⃣ فحص السجلات"

# Check 8.1: Failed login attempts
check_start "فحص محاولات تسجيل الدخول الفاشلة"
FAILED_LOGINS=$(grep "Failed password" /var/log/auth.log 2>/dev/null | tail -100 | wc -l || \
                grep "Failed password" /var/log/secure 2>/dev/null | tail -100 | wc -l || echo "0")
if [ "$FAILED_LOGINS" -lt 10 ]; then
    check_pass "Low number of failed login attempts ($FAILED_LOGINS in last 100)"
else
    check_warning "High number of failed login attempts ($FAILED_LOGINS in last 100)"
fi

# Check 8.2: Last logins
check_start "فحص آخر عمليات تسجيل الدخول"
if command -v last &> /dev/null; then
    RECENT_LOGINS=$(last -n 5 | grep -v "^$" | wc -l)
    check_pass "Last $RECENT_LOGINS logins recorded"
fi

# ================================================================
# 9. aaPanel Specific Checks
# ================================================================

print_header "9️⃣ فحص أمان aaPanel"

# Check 9.1: aaPanel directory permissions
check_start "التحقق من صلاحيات مجلد aaPanel"
if [ -d /www/server/panel ]; then
    PANEL_PERMS=$(stat -c "%a" /www/server/panel 2>/dev/null || stat -f "%Lp" /www/server/panel 2>/dev/null)
    if [ "$PANEL_PERMS" = "750" ] || [ "$PANEL_PERMS" = "755" ]; then
        check_pass "aaPanel directory permissions OK ($PANEL_PERMS)"
    else
        check_warning "aaPanel directory permissions: $PANEL_PERMS (recommended: 750)"
    fi
else
    check_info "aaPanel directory not found"
fi

# Check 9.2: aaPanel logs
check_start "التحقق من سجلات aaPanel"
if [ -f /www/server/panel/logs/error.log ]; then
    ERROR_COUNT=$(tail -100 /www/server/panel/logs/error.log 2>/dev/null | grep -i "error" | wc -l || echo "0")
    if [ "$ERROR_COUNT" -lt 10 ]; then
        check_pass "Low error count in aaPanel logs ($ERROR_COUNT)"
    else
        check_warning "High error count in aaPanel logs ($ERROR_COUNT)"
    fi
fi

# ================================================================
# Summary
# ================================================================

print_header "📊 ملخص الفحص الأمني"

echo ""
if [ "$OUTPUT_MODE" != "json" ]; then
    echo -e "${CYAN}النتائج:${NC}"
    echo -e "  ${GREEN}✅ نجح: $CHECKS_PASSED${NC}"
    if [ $CHECKS_FAILED -gt 0 ]; then
        echo -e "  ${RED}❌ فشل: $CHECKS_FAILED${NC}"
    fi
    if [ $CHECKS_WARNING -gt 0 ]; then
        echo -e "  ${YELLOW}⚠️  تحذير: $CHECKS_WARNING${NC}"
    fi
    echo -e "  ${BLUE}📝 الإجمالي: $CHECKS_TOTAL${NC}"
    echo ""
fi

# Calculate security score
SCORE=$(( (CHECKS_PASSED * 100) / CHECKS_TOTAL ))

if [ "$OUTPUT_MODE" = "json" ]; then
    # JSON output
    cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks_total": $CHECKS_TOTAL,
  "checks_passed": $CHECKS_PASSED,
  "checks_failed": $CHECKS_FAILED,
  "checks_warning": $CHECKS_WARNING,
  "security_score": $SCORE
}
EOF
else
    # Normal output
    if [ $SCORE -ge 90 ]; then
        echo -e "${GREEN}🎉 ممتاز! النظام آمن جداً (نسبة الأمان: $SCORE%)${NC}"
    elif [ $SCORE -ge 70 ]; then
        echo -e "${YELLOW}⚠️  جيد، لكن يحتاج بعض التحسينات (نسبة الأمان: $SCORE%)${NC}"
    else
        echo -e "${RED}❌ يحتاج إلى تحسينات أمنية عاجلة (نسبة الأمان: $SCORE%)${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}التوصيات:${NC}"
    if [ $CHECKS_FAILED -gt 0 ]; then
        echo "  • أصلح المشاكل الحرجة (❌) فوراً"
    fi
    if [ $CHECKS_WARNING -gt 0 ]; then
        echo "  • راجع التحذيرات (⚠️) وحسّنها"
    fi
    echo "  • شغّل setup_security_hardening.sh لتطبيق التحسينات"
    echo "  • فعّل Fail2Ban و auditd إن لم يكونا نشطين"
    echo "  • راجع السجلات بانتظام"
    echo ""
fi

# Exit with appropriate code
if [ $CHECKS_FAILED -gt 0 ]; then
    exit 1
elif [ $CHECKS_WARNING -gt 0 ]; then
    exit 2
else
    exit 0
fi
