#!/bin/bash

# ================================================================
# Fail2Ban Testing Script for aaPanel
# ================================================================
# هذا السكريبت يختبر إعدادات Fail2Ban بشكل شامل
#
# الاستخدام:
#   sudo ./test_fail2ban.sh
#
# الاختبارات:
#   1. ✅ Service status
#   2. ✅ Configuration validation
#   3. ✅ Jails status
#   4. ✅ Filters testing
#   5. ✅ Ban/Unban functionality
#   6. ✅ Logs verification
# ================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# ================================================================
# Helper Functions
# ================================================================

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

test_start() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${CYAN}🧪 اختبار $TESTS_TOTAL: $1${NC}"
}

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}   ✅ نجح: $1${NC}"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}   ❌ فشل: $1${NC}"
}

test_info() {
    echo -e "${BLUE}   ℹ️  $1${NC}"
}

test_warning() {
    echo -e "${YELLOW}   ⚠️  $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}❌ هذا السكريبت يجب تشغيله بصلاحيات root${NC}"
        echo -e "${BLUE}ℹ️  استخدم: sudo $0${NC}"
        exit 1
    fi
}

# ================================================================
# Tests
# ================================================================

check_root

print_header "🛡️  اختبار Fail2Ban لـ aaPanel"

# Test 1: Check if Fail2Ban is installed
test_start "التحقق من تثبيت Fail2Ban"
if command -v fail2ban-server &> /dev/null; then
    VERSION=$(fail2ban-server --version 2>&1 | head -n1)
    test_pass "Fail2Ban مثبت - $VERSION"
else
    test_fail "Fail2Ban غير مثبت"
    echo ""
    echo -e "${RED}الرجاء تشغيل setup_fail2ban.sh أولاً${NC}"
    exit 1
fi

# Test 2: Check if service is running
test_start "التحقق من حالة الخدمة"
if systemctl is-active --quiet fail2ban; then
    test_pass "خدمة Fail2Ban تعمل"
    
    # Check uptime
    UPTIME=$(systemctl show fail2ban --property=ActiveEnterTimestamp --value 2>/dev/null)
    if [ -n "$UPTIME" ]; then
        test_info "Uptime: $UPTIME"
    fi
else
    test_fail "خدمة Fail2Ban لا تعمل"
    test_info "حاول: systemctl start fail2ban"
fi

# Test 3: Check if service is enabled
test_start "التحقق من التفعيل التلقائي"
if systemctl is-enabled --quiet fail2ban 2>/dev/null; then
    test_pass "الخدمة مفعلة للتشغيل التلقائي"
else
    test_warning "الخدمة غير مفعلة للتشغيل التلقائي"
    test_info "حاول: systemctl enable fail2ban"
fi

# Test 4: Validate configuration
test_start "التحقق من صحة jail.local"
if fail2ban-client -t >/dev/null 2>&1; then
    test_pass "jail.local صالح"
else
    test_fail "خطأ في jail.local"
    fail2ban-client -t 2>&1 | head -10
fi

# Test 5: Check jail.local exists
test_start "التحقق من وجود jail.local"
if [ -f /etc/fail2ban/jail.local ]; then
    test_pass "jail.local موجود"
    SIZE=$(stat -c%s /etc/fail2ban/jail.local 2>/dev/null || stat -f%z /etc/fail2ban/jail.local 2>/dev/null)
    test_info "الحجم: $SIZE bytes"
else
    test_fail "jail.local غير موجود"
fi

# Test 6: Check custom filter
test_start "التحقق من custom filter لـ aaPanel"
if [ -f /etc/fail2ban/filter.d/aapanel.conf ]; then
    test_pass "aapanel.conf موجود"
    
    # Test filter with sample log
    SAMPLE_LOG="2025-01-01 12:00:00 [error] Login failed for user 'admin' from IP: 192.168.1.100"
    if echo "$SAMPLE_LOG" | fail2ban-regex - /etc/fail2ban/filter.d/aapanel.conf --print-all-matched >/dev/null 2>&1; then
        test_pass "filter يعمل بشكل صحيح"
    else
        test_warning "filter قد يحتاج مراجعة"
    fi
else
    test_warning "aapanel.conf غير موجود"
fi

# Test 7: List active jails
test_start "التحقق من الـ jails النشطة"
JAILS_OUTPUT=$(fail2ban-client status 2>/dev/null)
if [ -n "$JAILS_OUTPUT" ]; then
    JAILS_LIST=$(echo "$JAILS_OUTPUT" | grep "Jail list:" | sed 's/.*://; s/,/ /g' | xargs)
    
    if [ -n "$JAILS_LIST" ]; then
        test_pass "Jails نشطة: $JAILS_LIST"
        
        # Count jails
        JAIL_COUNT=$(echo "$JAILS_LIST" | wc -w)
        test_info "عدد الـ jails: $JAIL_COUNT"
    else
        test_warning "لا توجد jails نشطة"
    fi
else
    test_fail "لا يمكن الحصول على حالة الـ jails"
fi

# Test 8: Check each jail status
test_start "التحقق من حالة كل jail"
if [ -n "$JAILS_LIST" ]; then
    for jail in $JAILS_LIST; do
        JAIL_STATUS=$(fail2ban-client status "$jail" 2>/dev/null)
        
        if [ -n "$JAIL_STATUS" ]; then
            BANNED=$(echo "$JAIL_STATUS" | grep "Currently banned:" | awk '{print $4}')
            TOTAL=$(echo "$JAIL_STATUS" | grep "Total banned:" | awk '{print $4}')
            
            if [ "$BANNED" -gt 0 ]; then
                test_info "  $jail: $BANNED banned حالياً (إجمالي: $TOTAL)"
            else
                test_pass "  $jail: يعمل (banned: 0, total: $TOTAL)"
            fi
        else
            test_warning "  $jail: لا يمكن الحصول على الحالة"
        fi
    done
else
    test_warning "لا توجد jails للفحص"
fi

# Test 9: Check log files
test_start "التحقق من ملفات السجلات"

# SSH logs
SSH_LOGS_FOUND=false
for log in /var/log/auth.log /var/log/secure; do
    if [ -f "$log" ] && [ -r "$log" ]; then
        test_pass "  $log موجود وقابل للقراءة"
        SSH_LOGS_FOUND=true
        break
    fi
done

if [ "$SSH_LOGS_FOUND" = false ]; then
    test_warning "  لم يتم العثور على سجلات SSH"
fi

# Nginx logs
if [ -f /var/log/nginx/error.log ]; then
    test_pass "  /var/log/nginx/error.log موجود"
elif [ -f /var/log/nginx/access.log ]; then
    test_pass "  /var/log/nginx/access.log موجود"
else
    test_warning "  سجلات Nginx غير موجودة"
fi

# aaPanel logs
if [ -f /www/server/panel/logs/error.log ]; then
    test_pass "  /www/server/panel/logs/error.log موجود"
else
    test_warning "  سجلات aaPanel غير موجودة"
fi

# Test 10: Check Fail2Ban logs
test_start "التحقق من سجلات Fail2Ban"
if journalctl -u fail2ban -n 1 --no-pager >/dev/null 2>&1; then
    test_pass "سجلات Fail2Ban متاحة (journalctl)"
    
    # Check for recent activity
    RECENT_LOGS=$(journalctl -u fail2ban --since "5 minutes ago" --no-pager 2>/dev/null | wc -l)
    test_info "  سجلات آخر 5 دقائق: $RECENT_LOGS سطر"
elif [ -f /var/log/fail2ban.log ]; then
    test_pass "سجلات Fail2Ban متاحة (/var/log/fail2ban.log)"
else
    test_warning "لا يمكن الوصول إلى سجلات Fail2Ban"
fi

# Test 11: Test ban/unban functionality (safe test)
test_start "اختبار وظيفة Ban/Unban"
TEST_IP="192.0.2.1"  # TEST-NET-1 (RFC 5737 - safe to use)

# Try to ban test IP
if fail2ban-client set sshd banip "$TEST_IP" >/dev/null 2>&1; then
    test_pass "  تم حظر IP اختباري: $TEST_IP"
    
    # Verify ban
    if fail2ban-client status sshd 2>/dev/null | grep -q "$TEST_IP"; then
        test_pass "  تأكيد: IP موجود في قائمة الحظر"
        
        # Unban
        if fail2ban-client set sshd unbanip "$TEST_IP" >/dev/null 2>&1; then
            test_pass "  تم إلغاء الحظر بنجاح"
        else
            test_warning "  فشل إلغاء الحظر"
        fi
    else
        test_warning "  IP غير موجود في قائمة الحظر"
    fi
else
    test_warning "  فشل حظر IP اختباري (قد يكون jail sshd غير نشط)"
fi

# Test 12: Check iptables rules
test_start "التحقق من قواعد iptables"
if command -v iptables &> /dev/null; then
    F2B_CHAINS=$(iptables -L -n 2>/dev/null | grep -c "f2b-" || echo "0")
    
    if [ "$F2B_CHAINS" -gt 0 ]; then
        test_pass "قواعد Fail2Ban موجودة في iptables ($F2B_CHAINS chain)"
    else
        test_warning "لا توجد قواعد Fail2Ban في iptables"
    fi
else
    test_warning "iptables غير متاح"
fi

# Test 13: Check database
test_start "التحقق من قاعدة بيانات Fail2Ban"
if [ -f /var/lib/fail2ban/fail2ban.sqlite3 ]; then
    test_pass "قاعدة البيانات موجودة"
    SIZE=$(stat -c%s /var/lib/fail2ban/fail2ban.sqlite3 2>/dev/null || stat -f%z /var/lib/fail2ban/fail2ban.sqlite3 2>/dev/null)
    test_info "  الحجم: $SIZE bytes"
else
    test_warning "قاعدة البيانات غير موجودة"
fi

# Test 14: Check management script
test_start "التحقق من سكريبت الإدارة"
if [ -f /usr/local/bin/fail2ban-check ] && [ -x /usr/local/bin/fail2ban-check ]; then
    test_pass "fail2ban-check موجود وقابل للتنفيذ"
else
    test_warning "fail2ban-check غير موجود"
fi

# ================================================================
# Summary
# ================================================================

print_header "📊 ملخص الاختبارات"

echo ""
echo -e "${CYAN}النتائج:${NC}"
echo -e "  ${GREEN}✅ نجح: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "  ${RED}❌ فشل: $TESTS_FAILED${NC}"
fi
TESTS_WARNING=$((TESTS_TOTAL - TESTS_PASSED - TESTS_FAILED))
if [ $TESTS_WARNING -gt 0 ]; then
    echo -e "  ${YELLOW}⚠️  تحذير: $TESTS_WARNING${NC}"
fi
echo -e "  ${BLUE}📝 الإجمالي: $TESTS_TOTAL${NC}"
echo ""

# Calculate success rate
SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))

if [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${GREEN}🎉 ممتاز! Fail2Ban يعمل بشكل مثالي (نسبة النجاح: $SUCCESS_RATE%)${NC}"
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo -e "${YELLOW}⚠️  جيد، لكن هناك بعض المشاكل البسيطة (نسبة النجاح: $SUCCESS_RATE%)${NC}"
else
    echo -e "${RED}❌ يحتاج إلى إصلاح (نسبة النجاح: $SUCCESS_RATE%)${NC}"
fi

echo ""
echo -e "${CYAN}الأوامر المفيدة:${NC}"
echo "  • fail2ban-check                    - فحص سريع"
echo "  • fail2ban-client status            - حالة جميع الـ jails"
echo "  • fail2ban-client status <jail>     - حالة jail معين"
echo "  • journalctl -u fail2ban -f         - متابعة السجلات"
echo "  • fail2ban-client unban <IP>        - إلغاء حظر IP"
echo ""

# Exit with appropriate code
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi
