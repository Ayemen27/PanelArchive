#!/bin/bash

# ================================================================
# SSL/TLS Configuration Check Script
# ================================================================
# هذا السكريبت يتحقق من صحة إعداد SSL/TLS ويعطي تقريراً شاملاً
#
# الاستخدام:
#   ./ssl_check.sh example.com
#
# المتطلبات:
#   - openssl
#   - curl
#   - نطاق مُفعّل مع SSL
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ================================================================
# Helper Functions
# ================================================================

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_item() {
    local item="$1"
    local status="$2"
    
    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✅ ${item}${NC}"
    elif [ "$status" = "warn" ]; then
        echo -e "${YELLOW}⚠️  ${item}${NC}"
    else
        echo -e "${RED}❌ ${item}${NC}"
    fi
}

# ================================================================
# Validation
# ================================================================

if [ $# -eq 0 ]; then
    print_error "يرجى تحديد اسم النطاق"
    echo "الاستخدام: $0 example.com"
    exit 1
fi

DOMAIN=$1
PORT=${2:-443}

# Check if required tools are installed
for tool in openssl curl; do
    if ! command -v $tool &> /dev/null; then
        print_error "$tool غير مثبت. يرجى تثبيته أولاً"
        exit 1
    fi
done

# ================================================================
# SSL Certificate Check
# ================================================================

print_header "فحص شهادة SSL"

# Get certificate info
CERT_INFO=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:$PORT" 2>/dev/null | openssl x509 -noout -dates -subject -issuer 2>/dev/null)

if [ -z "$CERT_INFO" ]; then
    print_error "فشل الاتصال بـ $DOMAIN:$PORT"
    print_info "تأكد من أن:"
    echo "  1. النطاق يعمل وصحيح"
    echo "  2. SSL مفعّل على المنفذ $PORT"
    echo "  3. الخادم يستجيب للطلبات"
    exit 1
fi

# Extract certificate details
ISSUER=$(echo "$CERT_INFO" | grep "issuer=" | cut -d'=' -f2-)
NOT_BEFORE=$(echo "$CERT_INFO" | grep "notBefore=" | cut -d'=' -f2-)
NOT_AFTER=$(echo "$CERT_INFO" | grep "notAfter=" | cut -d'=' -f2-)

print_info "الجهة المُصدِرة: $ISSUER"
print_info "صالحة من: $NOT_BEFORE"
print_info "صالحة حتى: $NOT_AFTER"

# Check expiration
EXPIRY_DATE=$(date -d "$NOT_AFTER" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$NOT_AFTER" +%s 2>/dev/null)
CURRENT_DATE=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_DATE - $CURRENT_DATE) / 86400 ))

if [ $DAYS_LEFT -lt 0 ]; then
    check_item "الشهادة منتهية الصلاحية!" "fail"
elif [ $DAYS_LEFT -lt 30 ]; then
    check_item "الشهادة ستنتهي خلال $DAYS_LEFT يوم - يجب التجديد!" "warn"
else
    check_item "الشهادة صالحة لمدة $DAYS_LEFT يوم" "pass"
fi

# ================================================================
# Protocol Check
# ================================================================

print_header "فحص البروتوكولات"

# Check TLS versions
for protocol in ssl3 tls1 tls1_1 tls1_2 tls1_3; do
    # Map protocol name to OpenSSL format (e.g., tls1_2 -> TLSv1.2)
    case $protocol in
        ssl3) PROTOCOL_PATTERN="SSLv3" ;;
        tls1) PROTOCOL_PATTERN="TLSv1" ;;
        tls1_1) PROTOCOL_PATTERN="TLSv1.1" ;;
        tls1_2) PROTOCOL_PATTERN="TLSv1.2" ;;
        tls1_3) PROTOCOL_PATTERN="TLSv1.3" ;;
    esac
    
    if echo | openssl s_client -"$protocol" -servername "$DOMAIN" -connect "$DOMAIN:$PORT" 2>/dev/null | grep -qi "Protocol.*$PROTOCOL_PATTERN"; then
        case $protocol in
            ssl3|tls1|tls1_1)
                check_item "$protocol مُفعّل (غير آمن!)" "fail"
                ;;
            tls1_2)
                check_item "$protocol مُفعّل (جيد)" "pass"
                ;;
            tls1_3)
                check_item "$protocol مُفعّل (ممتاز!)" "pass"
                ;;
        esac
    else
        case $protocol in
            ssl3|tls1|tls1_1)
                check_item "$protocol مُعطّل (ممتاز!)" "pass"
                ;;
            tls1_2|tls1_3)
                check_item "$protocol غير مُفعّل (يُنصح بتفعيله)" "warn"
                ;;
        esac
    fi
done

# ================================================================
# Cipher Suites Check
# ================================================================

print_header "فحص Cipher Suites"

CIPHERS=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:$PORT" -cipher 'ALL' 2>/dev/null | grep "Cipher" | awk '{print $3}')

if [ -n "$CIPHERS" ]; then
    print_info "Cipher المستخدم: $CIPHERS"
    
    # Check for strong ciphers
    if echo "$CIPHERS" | grep -qE "ECDHE|GCM|CHACHA20"; then
        check_item "يستخدم cipher قوي وآمن" "pass"
    else
        check_item "Cipher ضعيف - يُنصح بتحسينه" "warn"
    fi
else
    check_item "فشل التحقق من cipher" "fail"
fi

# ================================================================
# Security Headers Check
# ================================================================

print_header "فحص Security Headers"

HEADERS=$(curl -sI "https://$DOMAIN" 2>/dev/null)

# Check HSTS
if echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
    HSTS_VALUE=$(echo "$HEADERS" | grep -i "Strict-Transport-Security" | cut -d':' -f2- | xargs)
    check_item "HSTS: $HSTS_VALUE" "pass"
else
    check_item "HSTS غير مُفعّل (يُنصح بتفعيله)" "warn"
fi

# Check X-Frame-Options
if echo "$HEADERS" | grep -qi "X-Frame-Options"; then
    XFO_VALUE=$(echo "$HEADERS" | grep -i "X-Frame-Options" | cut -d':' -f2- | xargs)
    check_item "X-Frame-Options: $XFO_VALUE" "pass"
else
    check_item "X-Frame-Options غير مُفعّل" "warn"
fi

# Check X-Content-Type-Options
if echo "$HEADERS" | grep -qi "X-Content-Type-Options"; then
    check_item "X-Content-Type-Options مُفعّل" "pass"
else
    check_item "X-Content-Type-Options غير مُفعّل" "warn"
fi

# Check CSP
if echo "$HEADERS" | grep -qi "Content-Security-Policy"; then
    check_item "Content-Security-Policy مُفعّل" "pass"
else
    check_item "Content-Security-Policy غير مُفعّل" "warn"
fi

# ================================================================
# OCSP Stapling Check
# ================================================================

print_header "فحص OCSP Stapling"

OCSP_RESPONSE=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:$PORT" -status 2>/dev/null | grep -A 17 "OCSP response:")

if echo "$OCSP_RESPONSE" | grep -q "OCSP Response Status: successful"; then
    check_item "OCSP Stapling مُفعّل (ممتاز!)" "pass"
else
    check_item "OCSP Stapling غير مُفعّل (يُنصح بتفعيله)" "warn"
fi

# ================================================================
# Certificate Chain Check
# ================================================================

print_header "فحص سلسلة الشهادات"

CHAIN_INFO=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:$PORT" -showcerts 2>/dev/null)

CERT_COUNT=$(echo "$CHAIN_INFO" | grep -c "BEGIN CERTIFICATE")

if [ $CERT_COUNT -ge 2 ]; then
    check_item "سلسلة الشهادات كاملة ($CERT_COUNT شهادات)" "pass"
else
    check_item "سلسلة الشهادات قد تكون ناقصة ($CERT_COUNT شهادة)" "warn"
fi

# ================================================================
# SSL Labs Rating Estimate
# ================================================================

print_header "تقدير التصنيف"

SCORE=100
GRADE="A+"

# Deduct points for issues
if echo "$CERT_INFO" | grep -q "Let's Encrypt"; then
    print_info "شهادة من Let's Encrypt (مجانية وموثوقة)"
fi

# Check TLS versions
if echo | openssl s_client -tls1 -servername "$DOMAIN" -connect "$DOMAIN:$PORT" 2>/dev/null | grep -q "Protocol.*tls1"; then
    SCORE=$((SCORE - 20))
    GRADE="B"
fi

# Check HSTS
if ! echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
    SCORE=$((SCORE - 10))
    if [ "$GRADE" = "A+" ]; then GRADE="A"; fi
fi

# Check protocols
TLS13_ENABLED=$(echo | openssl s_client -tls1_3 -servername "$DOMAIN" -connect "$DOMAIN:$PORT" 2>/dev/null | grep -c "Protocol.*TLSv1.3" || echo 0)

if [ "$TLS13_ENABLED" -gt 0 ]; then
    print_success "TLS 1.3 مُفعّل - أعلى درجة أمان!"
else
    print_warning "TLS 1.3 غير مُفعّل - يُنصح بتفعيله"
    if [ "$GRADE" = "A+" ]; then GRADE="A"; fi
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  التقييم المُقدَّر: ${GREEN}$GRADE${CYAN} (النتيجة: $SCORE/100)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ================================================================
# Recommendations
# ================================================================

print_header "التوصيات"

if [ "$GRADE" = "A+" ]; then
    print_success "الإعداد ممتاز! لا حاجة لتحسينات"
else
    print_warning "يمكن تحسين التصنيف باتباع التوصيات:"
    echo ""
    
    if echo | openssl s_client -tls1 -servername "$DOMAIN" -connect "$DOMAIN:$PORT" 2>/dev/null | grep -q "Protocol.*tls1"; then
        echo "  1. تعطيل TLS 1.0 و TLS 1.1 (غير آمنين)"
    fi
    
    if ! echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
        echo "  2. تفعيل HSTS header"
    fi
    
    if [ "$TLS13_ENABLED" -eq 0 ]; then
        echo "  3. تفعيل TLS 1.3 لأعلى درجة أمان"
    fi
    
    if ! echo "$OCSP_RESPONSE" | grep -q "OCSP Response Status: successful"; then
        echo "  4. تفعيل OCSP Stapling"
    fi
fi

# ================================================================
# Online Tools Suggestion
# ================================================================

echo ""
print_info "للحصول على تحليل أكثر تفصيلاً، استخدم:"
echo "  • SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "  • Security Headers: https://securityheaders.com/?q=https://$DOMAIN"
echo ""

print_success "انتهى الفحص!"
