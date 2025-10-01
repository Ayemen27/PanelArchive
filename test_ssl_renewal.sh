#!/bin/bash

# ================================================================
# SSL Auto-Renewal Test Script
# ================================================================
# هذا السكريبت يختبر عمل التجديد التلقائي لشهادات SSL
#
# الاستخدام:
#   sudo ./test_ssl_renewal.sh
#
# المتطلبات:
#   - certbot مثبت
#   - صلاحيات root
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

# ================================================================
# Validation
# ================================================================

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "يجب تشغيل هذا السكريبت بصلاحيات root"
    print_info "استخدم: sudo ./test_ssl_renewal.sh"
    exit 1
fi

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    print_error "certbot غير مثبت"
    print_info "قم بتثبيته أولاً: sudo apt install -y certbot python3-certbot-nginx"
    exit 1
fi

# ================================================================
# Check Certbot Installation
# ================================================================

print_header "فحص تثبيت Certbot"

CERTBOT_VERSION=$(certbot --version 2>&1 | head -n1)
print_info "الإصدار: $CERTBOT_VERSION"
print_success "certbot مثبت بنجاح"

# ================================================================
# Check Certificates
# ================================================================

print_header "فحص الشهادات المثبتة"

CERT_LIST=$(certbot certificates 2>&1)

if echo "$CERT_LIST" | grep -q "No certificates found"; then
    print_warning "لا توجد شهادات مثبتة"
    print_info "قم بإعداد شهادة أولاً باستخدام setup_nginx.sh"
    exit 0
else
    echo "$CERT_LIST"
    print_success "تم العثور على شهادات"
fi

# Extract certificate details
DOMAINS=$(echo "$CERT_LIST" | grep -A 5 "Certificate Name:" | grep "Domains:" | cut -d':' -f2- | xargs)
EXPIRY=$(echo "$CERT_LIST" | grep "Expiry Date:" | cut -d':' -f2- | xargs)

print_info "النطاقات: $DOMAINS"
print_info "تاريخ الانتهاء: $EXPIRY"

# ================================================================
# Check Cron Job
# ================================================================

print_header "فحص Cron Job للتجديد التلقائي"

# Check if renewal cron exists
if crontab -l 2>/dev/null | grep -q "certbot renew"; then
    print_success "Cron job موجود"
    CRON_LINE=$(crontab -l 2>/dev/null | grep "certbot renew")
    print_info "الإعداد: $CRON_LINE"
    
    # Parse cron schedule
    CRON_SCHEDULE=$(echo "$CRON_LINE" | awk '{print $1, $2, $3, $4, $5}')
    print_info "الجدول الزمني: $CRON_SCHEDULE"
    
    if echo "$CRON_SCHEDULE" | grep -q "0 0,12 \* \* \*"; then
        print_success "يعمل مرتين يومياً (00:00 و 12:00) - إعداد ممتاز!"
    elif echo "$CRON_SCHEDULE" | grep -q "@daily"; then
        print_success "يعمل يومياً - إعداد جيد"
    else
        print_warning "جدول زمني مخصص: $CRON_SCHEDULE"
    fi
else
    print_warning "Cron job غير موجود!"
    print_info "إعداد Cron job للتجديد التلقائي..."
    
    echo -n "هل تريد إعداد التجديد التلقائي الآن؟ (y/n) [y]: "
    read SETUP_CRON
    SETUP_CRON=${SETUP_CRON:-y}
    
    if [ "$SETUP_CRON" = "y" ]; then
        (crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
        print_success "تم إعداد Cron job بنجاح"
        print_info "سيتم التحقق من التجديد مرتين يومياً (00:00 و 12:00)"
    fi
fi

# ================================================================
# Check Systemd Timer (Alternative)
# ================================================================

print_header "فحص Systemd Timer"

if systemctl list-timers --all 2>/dev/null | grep -q "certbot"; then
    print_success "Systemd timer موجود"
    systemctl status certbot.timer --no-pager 2>/dev/null | head -5
else
    print_info "Systemd timer غير مُعد (اختياري - Cron موجود)"
fi

# ================================================================
# Test Dry Run Renewal
# ================================================================

print_header "اختبار التجديد (Dry Run)"

print_info "جاري اختبار عملية التجديد (بدون تطبيق فعلي)..."

DRY_RUN_OUTPUT=$(certbot renew --dry-run 2>&1)
DRY_RUN_EXIT_CODE=$?

if [ $DRY_RUN_EXIT_CODE -eq 0 ]; then
    print_success "اختبار التجديد نجح!"
    
    # Check if certificates would be renewed
    if echo "$DRY_RUN_OUTPUT" | grep -q "The dry run was successful"; then
        print_success "جميع الشهادات جاهزة للتجديد التلقائي"
    fi
    
    # Show summary
    if echo "$DRY_RUN_OUTPUT" | grep -q "simulated renewal"; then
        RENEWED_COUNT=$(echo "$DRY_RUN_OUTPUT" | grep -c "simulated renewal" || echo "0")
        print_info "عدد الشهادات التي تم اختبار تجديدها: $RENEWED_COUNT"
    fi
else
    print_error "فشل اختبار التجديد!"
    echo ""
    echo "تفاصيل الخطأ:"
    echo "$DRY_RUN_OUTPUT"
    echo ""
    print_info "يرجى مراجعة الأخطاء أعلاه وإصلاحها"
    exit 1
fi

# ================================================================
# Check Renewal Configuration
# ================================================================

print_header "فحص إعدادات التجديد"

RENEWAL_CONF_DIR="/etc/letsencrypt/renewal"

if [ -d "$RENEWAL_CONF_DIR" ]; then
    CONF_FILES=$(ls -1 "$RENEWAL_CONF_DIR"/*.conf 2>/dev/null | wc -l)
    print_info "ملفات إعداد التجديد: $CONF_FILES"
    
    # Check each config file
    for conf in "$RENEWAL_CONF_DIR"/*.conf; do
        if [ -f "$conf" ]; then
            CERT_NAME=$(basename "$conf" .conf)
            print_info "  • $CERT_NAME"
            
            # Check if auto-renew is disabled
            if grep -q "autorenew = False" "$conf"; then
                print_warning "    تحذير: التجديد التلقائي مُعطّل لهذه الشهادة!"
            fi
        fi
    done
else
    print_warning "مجلد إعدادات التجديد غير موجود"
fi

# ================================================================
# Check Post-Renewal Hooks
# ================================================================

print_header "فحص Post-Renewal Hooks"

HOOKS_DIR="/etc/letsencrypt/renewal-hooks/post"

if [ -d "$HOOKS_DIR" ]; then
    HOOK_FILES=$(ls -1 "$HOOKS_DIR" 2>/dev/null | wc -l)
    
    if [ $HOOK_FILES -gt 0 ]; then
        print_success "تم العثور على $HOOK_FILES hook(s)"
        ls -l "$HOOKS_DIR"
    else
        print_info "لا توجد hooks مُعدّة"
    fi
else
    print_info "مجلد hooks غير موجود"
fi

# Check if nginx reload is configured
if crontab -l 2>/dev/null | grep "certbot renew" | grep -q "nginx"; then
    print_success "إعادة تحميل nginx مُعدّة في Cron"
elif [ -f "$HOOKS_DIR/reload-nginx.sh" ] || [ -f "$HOOKS_DIR/reload-nginx" ]; then
    print_success "إعادة تحميل nginx مُعدّة في hooks"
else
    print_warning "لم يتم العثور على إعداد لإعادة تحميل nginx بعد التجديد"
    print_info "يُنصح بإضافة --post-hook 'systemctl reload nginx' إلى أمر التجديد"
fi

# ================================================================
# Check Certificate Age
# ================================================================

print_header "فحص عمر الشهادة"

# Extract expiry date from certbot certificates
CERT_EXPIRY=$(echo "$CERT_LIST" | grep "Expiry Date:" | head -1 | cut -d':' -f2- | xargs)

if [ -n "$CERT_EXPIRY" ]; then
    # Calculate days until expiry
    EXPIRY_TIMESTAMP=$(date -d "$CERT_EXPIRY" +%s 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S%z" "$CERT_EXPIRY" +%s 2>/dev/null)
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_TIMESTAMP - $CURRENT_TIMESTAMP) / 86400 ))
    
    if [ $DAYS_UNTIL_EXPIRY -lt 0 ]; then
        print_error "الشهادة منتهية الصلاحية!"
        print_info "يجب التجديد فوراً: sudo certbot renew"
    elif [ $DAYS_UNTIL_EXPIRY -lt 30 ]; then
        print_warning "الشهادة ستنتهي خلال $DAYS_UNTIL_EXPIRY يوم"
        print_info "سيتم التجديد التلقائي قريباً (certbot يجدد قبل 30 يوم من الانتهاء)"
    else
        print_success "الشهادة صالحة لمدة $DAYS_UNTIL_EXPIRY يوم"
        
        # Calculate when renewal will occur
        RENEWAL_DAYS=$(( $DAYS_UNTIL_EXPIRY - 30 ))
        if [ $RENEWAL_DAYS -gt 0 ]; then
            print_info "سيتم التجديد التلقائي بعد $RENEWAL_DAYS يوم تقريباً"
        else
            print_info "الشهادة في فترة التجديد (آخر 30 يوم)"
        fi
    fi
fi

# ================================================================
# Final Summary
# ================================================================

print_header "ملخص النتائج"

echo ""
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Certbot installed
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if command -v certbot &> /dev/null; then
    print_success "Certbot مثبت"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Certificates exist
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if ! echo "$CERT_LIST" | grep -q "No certificates found"; then
    print_success "الشهادات موجودة"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Cron job configured
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if crontab -l 2>/dev/null | grep -q "certbot renew"; then
    print_success "Cron job مُعد"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Dry run successful
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ $DRY_RUN_EXIT_CODE -eq 0 ]; then
    print_success "اختبار التجديد نجح"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Certificate valid
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ $DAYS_UNTIL_EXPIRY -gt 0 ]; then
    print_success "الشهادة صالحة"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  النتيجة: ${GREEN}$PASSED_CHECKS${CYAN}/${TOTAL_CHECKS} فحوصات نجحت${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    print_success "جميع الفحوصات نجحت! التجديد التلقائي يعمل بشكل صحيح ✨"
else
    print_warning "بعض الفحوصات فشلت. يرجى مراجعة التفاصيل أعلاه"
fi

# ================================================================
# Additional Recommendations
# ================================================================

echo ""
print_header "نصائح إضافية"

echo "1. للتحقق يدوياً من التجديد:"
echo "   sudo certbot renew --dry-run"
echo ""
echo "2. للتجديد الفوري (إن لزم):"
echo "   sudo certbot renew --force-renewal"
echo ""
echo "3. لمشاهدة سجلات certbot:"
echo "   sudo tail -f /var/log/letsencrypt/letsencrypt.log"
echo ""
echo "4. للتحقق من جدول Cron:"
echo "   crontab -l | grep certbot"
echo ""

print_success "انتهى الفحص!"
