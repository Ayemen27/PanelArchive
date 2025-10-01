#!/bin/bash

# ================================================================
# UFW Firewall Setup Script for aaPanel - ULTRA SECURE VERSION
# ================================================================
# هذا السكريبت يقوم بإعداد UFW firewall للإنتاج تلقائياً بطريقة آمنة 100%
# 
# الاستخدام:
#   sudo ./setup_firewall.sh                  # تفاعلي (يسأل أسئلة)
#   sudo ./setup_firewall.sh -y               # تلقائي (بدون أسئلة)
#   sudo ./setup_firewall.sh --non-interactive  # تلقائي (بدون أسئلة)
#
# الميزات:
#   - 🔍 اكتشاف تلقائي لمنفذ SSH النشط (من عدة مصادر)
#   - 🛡️ حماية كاملة من SSH lockout
#   - 🤖 non-interactive mode للـ CI/CD
#   - 💾 backup/restore تلقائي للقواعد
#   - ⚡ UFW يبقى مُفعّلاً دائماً - لا يتم تعطيله أبداً
#   - 🔒 safeguards متعددة ضد الأخطاء
#   - ✅ idempotent حقيقي (يمكن تشغيله عدة مرات بأمان)
# ================================================================

set -e  # Exit on error

# ================================================================
# Parse Arguments
# ================================================================

NON_INTERACTIVE=false

for arg in "$@"; do
    case $arg in
        -y|--non-interactive|--yes)
            NON_INTERACTIVE=true
            shift
            ;;
        -h|--help)
            echo "Usage: sudo ./setup_firewall.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -y, --non-interactive    Run in non-interactive mode (no prompts)"
            echo "  --yes                    Same as --non-interactive"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  sudo ./setup_firewall.sh              # Interactive mode"
            echo "  sudo ./setup_firewall.sh -y           # Non-interactive mode"
            exit 0
            ;;
        *)
            ;;
    esac
done

# ================================================================
# CRITICAL SECURITY: Trap Handler
# ================================================================
# هذا يضمن بقاء UFW مُفعّلاً حتى لو فشل السكريبت أو تمت مقاطعته
cleanup_on_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}⚠️  حدث خطأ! جاري التأكد من أن UFW لا يزال مُفعّلاً...${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        # Make sure UFW is enabled (critical for security)
        if command -v ufw &> /dev/null; then
            if ! ufw status | grep -q "Status: active"; then
                echo -e "${YELLOW}⚠️  UFW كان معطلاً! جاري إعادة تفعيله فوراً...${NC}"
                echo "y" | ufw enable > /dev/null 2>&1
                echo -e "${GREEN}✅ تم إعادة تفعيل UFW - الخادم محمي${NC}"
            else
                echo -e "${GREEN}✅ UFW لا يزال مُفعّلاً - الخادم محمي${NC}"
            fi
            
            # Restore SSH access if we have backup
            if [ -n "$DETECTED_SSH_PORT" ] && [ "$DETECTED_SSH_PORT" -gt 0 ]; then
                echo -e "${YELLOW}⚠️  استعادة الوصول إلى SSH على المنفذ المكتشف: $DETECTED_SSH_PORT${NC}"
                ufw limit ${DETECTED_SSH_PORT}/tcp comment 'SSH - auto restored' > /dev/null 2>&1 || true
                ufw reload > /dev/null 2>&1 || true
                echo -e "${GREEN}✅ تم استعادة قاعدة SSH - الوصول محمي${NC}"
            fi
        fi
        
        echo -e "${RED}❌ السكريبت فشل لكن UFW لا يزال مُفعّلاً للحماية${NC}"
        echo ""
    fi
}

trap cleanup_on_error EXIT ERR INT TERM

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

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

print_step() {
    echo -e "${MAGENTA}▶️  $1${NC}"
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
# SSH Port Detection Functions
# ================================================================

detect_ssh_port_from_active_connections() {
    # Detect from active SSH connections using ss or netstat
    local port=""
    
    # Try ss first (modern tool)
    if command -v ss &> /dev/null; then
        # Get the port of current SSH connection
        port=$(ss -tnp 2>/dev/null | grep 'sshd' | grep -oP ':\K[0-9]+' | head -n1)
    fi
    
    # Fallback to netstat if ss failed
    if [ -z "$port" ] && command -v netstat &> /dev/null; then
        port=$(netstat -tnp 2>/dev/null | grep 'sshd' | grep -oP ':\K[0-9]+' | head -n1)
    fi
    
    echo "$port"
}

detect_ssh_port_from_sshd_config() {
    # Detect from /etc/ssh/sshd_config
    local port=""
    
    if [ -f /etc/ssh/sshd_config ]; then
        # Look for Port directive (uncommented)
        port=$(grep -E "^Port " /etc/ssh/sshd_config | awk '{print $2}' | head -n1)
    fi
    
    echo "$port"
}

detect_ssh_port_from_ufw_rules() {
    # Detect from existing UFW rules
    local port=""
    
    if command -v ufw &> /dev/null; then
        # Look for SSH-related rules
        port=$(ufw status | grep -E '(22|2222|SSH|ssh)' | grep -oP '\d+(?=/tcp)' | head -n1)
    fi
    
    echo "$port"
}

detect_ssh_port_from_listening_ports() {
    # Detect from listening ports
    local port=""
    
    if command -v ss &> /dev/null; then
        # Find sshd listening port
        port=$(ss -tln 2>/dev/null | grep 'sshd' | grep -oP ':\K[0-9]+' | head -n1)
        
        # If not found, check for common SSH ports
        if [ -z "$port" ]; then
            for p in 22 2222 22222; do
                if ss -tln 2>/dev/null | grep -q ":$p "; then
                    port=$p
                    break
                fi
            done
        fi
    fi
    
    echo "$port"
}

detect_active_ssh_port() {
    # Smart detection: try multiple methods and validate
    print_step "اكتشاف منفذ SSH النشط من مصادر متعددة..."
    
    local port_from_connections=$(detect_ssh_port_from_active_connections)
    local port_from_config=$(detect_ssh_port_from_sshd_config)
    local port_from_ufw=$(detect_ssh_port_from_ufw_rules)
    local port_from_listening=$(detect_ssh_port_from_listening_ports)
    
    print_info "🔍 نتائج الفحص:"
    [ -n "$port_from_connections" ] && echo -e "  ${BLUE}•${NC} من الاتصالات النشطة: ${GREEN}$port_from_connections${NC}" || echo -e "  ${BLUE}•${NC} من الاتصالات النشطة: ${YELLOW}غير متاح${NC}"
    [ -n "$port_from_config" ] && echo -e "  ${BLUE}•${NC} من sshd_config: ${GREEN}$port_from_config${NC}" || echo -e "  ${BLUE}•${NC} من sshd_config: ${YELLOW}غير متاح${NC}"
    [ -n "$port_from_ufw" ] && echo -e "  ${BLUE}•${NC} من قواعد UFW: ${GREEN}$port_from_ufw${NC}" || echo -e "  ${BLUE}•${NC} من قواعد UFW: ${YELLOW}غير متاح${NC}"
    [ -n "$port_from_listening" ] && echo -e "  ${BLUE}•${NC} من المنافذ المستمعة: ${GREEN}$port_from_listening${NC}" || echo -e "  ${BLUE}•${NC} من المنافذ المستمعة: ${YELLOW}غير متاح${NC}"
    
    # Priority: Active connections > sshd_config > UFW rules > Listening ports
    local detected_port=""
    
    if [ -n "$port_from_connections" ] && [ "$port_from_connections" -gt 0 ] 2>/dev/null; then
        detected_port=$port_from_connections
        print_success "تم اكتشاف المنفذ من الاتصالات النشطة: $detected_port"
    elif [ -n "$port_from_config" ] && [ "$port_from_config" -gt 0 ] 2>/dev/null; then
        detected_port=$port_from_config
        print_success "تم اكتشاف المنفذ من sshd_config: $detected_port"
    elif [ -n "$port_from_listening" ] && [ "$port_from_listening" -gt 0 ] 2>/dev/null; then
        detected_port=$port_from_listening
        print_success "تم اكتشاف المنفذ من المنافذ المستمعة: $detected_port"
    elif [ -n "$port_from_ufw" ] && [ "$port_from_ufw" -gt 0 ] 2>/dev/null; then
        detected_port=$port_from_ufw
        print_success "تم اكتشاف المنفذ من قواعد UFW: $detected_port"
    else
        detected_port=22
        print_warning "لم يتم اكتشاف منفذ SSH - سيتم استخدام المنفذ الافتراضي: 22"
    fi
    
    echo "$detected_port"
}

check_active_ssh_sessions() {
    # Check for active SSH sessions
    local session_count=0
    
    if command -v who &> /dev/null; then
        session_count=$(who | wc -l)
    elif command -v w &> /dev/null; then
        session_count=$(w -h | wc -l)
    fi
    
    echo "$session_count"
}

# ================================================================
# Check Requirements
# ================================================================

print_header "🔒 UFW Firewall Setup - Ultra Secure Mode"
print_info "إعداد جدار الحماية مع حماية كاملة من SSH lockout"

if [ "$NON_INTERACTIVE" = true ]; then
    print_success "🤖 الوضع التلقائي (Non-Interactive Mode) - بدون أسئلة"
else
    print_info "💬 الوضع التفاعلي (Interactive Mode) - سيتم طرح أسئلة"
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "يجب تشغيل هذا السكريبت بصلاحيات root"
    print_info "استخدم: sudo ./setup_firewall.sh"
    exit 1
fi

print_success "صلاحيات root متوفرة"

# ================================================================
# Detect OS
# ================================================================

print_header "فحص نظام التشغيل"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
    print_info "نظام التشغيل: $PRETTY_NAME"
else
    print_error "لا يمكن تحديد نظام التشغيل"
    exit 1
fi

# Check if OS is supported
case "$OS" in
    ubuntu|debian)
        print_success "نظام التشغيل مدعوم"
        ;;
    centos|rhel|fedora)
        print_warning "نظام التشغيل مدعوم جزئياً - قد تحتاج لاستخدام firewalld بدلاً من UFW"
        ;;
    *)
        print_warning "نظام التشغيل غير مختبر - قد تواجه مشاكل"
        ;;
esac

# ================================================================
# Install UFW
# ================================================================

print_header "تثبيت UFW"

if command -v ufw &> /dev/null; then
    UFW_VERSION=$(ufw version | head -n1)
    print_success "UFW مثبت بالفعل: $UFW_VERSION"
else
    print_step "جاري تثبيت UFW..."
    
    case "$OS" in
        ubuntu|debian)
            apt-get update -qq
            apt-get install -y ufw
            ;;
        centos|rhel|fedora)
            yum install -y ufw || dnf install -y ufw
            ;;
        *)
            print_error "لا يمكن تثبيت UFW تلقائياً على هذا النظام"
            exit 1
            ;;
    esac
    
    if command -v ufw &> /dev/null; then
        print_success "تم تثبيت UFW بنجاح"
    else
        print_error "فشل تثبيت UFW"
        exit 1
    fi
fi

# ================================================================
# Check Current Status
# ================================================================

print_header "فحص الحالة الحالية"

UFW_STATUS=$(ufw status | head -n1)
print_info "حالة UFW: $UFW_STATUS"

if echo "$UFW_STATUS" | grep -q "Status: active"; then
    print_success "UFW مُفعّل بالفعل - سيتم تحديث القواعد بأمان"
    UFW_WAS_ACTIVE=true
else
    print_info "UFW غير مُفعّل - سيتم تفعيله بعد إعداد القواعد الأساسية"
    UFW_WAS_ACTIVE=false
fi

# ================================================================
# CRITICAL: Detect Active SSH Port
# ================================================================

print_header "🔍 اكتشاف منفذ SSH النشط (حرج!)"

DETECTED_SSH_PORT=$(detect_active_ssh_port)

echo ""
print_success "المنفذ المكتشف: $DETECTED_SSH_PORT"

# Check active SSH sessions
ACTIVE_SESSIONS=$(check_active_ssh_sessions)
if [ "$ACTIVE_SESSIONS" -gt 0 ]; then
    print_info "عدد جلسات SSH النشطة: $ACTIVE_SESSIONS"
else
    print_warning "لم يتم اكتشاف جلسات SSH نشطة (قد يكون هذا الجهاز local console)"
fi

# ================================================================
# Backup Current Rules
# ================================================================

print_header "نسخ احتياطي للقواعد الحالية"

BACKUP_DIR="/root/ufw_backups"
BACKUP_FILE="$BACKUP_DIR/ufw_rules_$(date +%Y%m%d_%H%M%S).txt"
BACKUP_RAW_FILE="$BACKUP_DIR/ufw_raw_$(date +%Y%m%d_%H%M%S).txt"

mkdir -p "$BACKUP_DIR"

if [ "$UFW_WAS_ACTIVE" = true ]; then
    print_step "حفظ القواعد الحالية..."
    ufw status numbered > "$BACKUP_FILE" 2>/dev/null || echo "No rules" > "$BACKUP_FILE"
    ufw status verbose > "$BACKUP_RAW_FILE" 2>/dev/null || echo "No rules" > "$BACKUP_RAW_FILE"
    print_success "تم حفظ النسخة الاحتياطية:"
    print_info "  • $BACKUP_FILE"
    print_info "  • $BACKUP_RAW_FILE"
else
    echo "UFW was not active" > "$BACKUP_FILE"
    print_info "لا توجد قواعد لنسخها احتياطياً"
fi

# ================================================================
# Configuration
# ================================================================

print_header "تكوين الإعدادات"

# SSH Port Configuration
SSH_PORT=$DETECTED_SSH_PORT

if [ "$NON_INTERACTIVE" = false ]; then
    echo ""
    echo -e "${CYAN}المنفذ المكتشف حالياً: ${GREEN}$DETECTED_SSH_PORT${NC}"
    echo ""
    echo -n "هل تريد استخدام منفذ SSH مختلف؟ (الافتراضي: استخدام المكتشف) [y/n]: "
    read CHANGE_SSH_PORT
    
    if [ "$CHANGE_SSH_PORT" = "y" ] || [ "$CHANGE_SSH_PORT" = "yes" ]; then
        echo ""
        print_warning "⚠️  تحذير: تغيير منفذ SSH قد يؤدي لفقدان الاتصال إذا لم يكن مطابقاً لتكوين sshd!"
        echo ""
        echo -n "أدخل رقم منفذ SSH الجديد: "
        read CUSTOM_SSH_PORT
        
        if [ -n "$CUSTOM_SSH_PORT" ] && [ "$CUSTOM_SSH_PORT" -gt 0 ] 2>/dev/null; then
            if [ "$CUSTOM_SSH_PORT" != "$DETECTED_SSH_PORT" ]; then
                echo ""
                print_warning "🚨 المنفذ المطلوب ($CUSTOM_SSH_PORT) يختلف عن المكتشف ($DETECTED_SSH_PORT)!"
                echo ""
                echo -e "${YELLOW}هل أنت متأكد 100% أن sshd يعمل على المنفذ $CUSTOM_SSH_PORT؟${NC}"
                echo -e "${RED}إذا كان الجواب لا، ستفقد الوصول إلى الخادم!${NC}"
                echo ""
                echo -n "اكتب 'YES' بالأحرف الكبيرة للتأكيد: "
                read CONFIRM_DANGEROUS_CHANGE
                
                if [ "$CONFIRM_DANGEROUS_CHANGE" = "YES" ]; then
                    SSH_PORT=$CUSTOM_SSH_PORT
                    print_warning "تم قبول المنفذ: $SSH_PORT (على مسؤوليتك!)"
                else
                    print_info "تم إلغاء التغيير - سيتم استخدام المنفذ المكتشف: $DETECTED_SSH_PORT"
                    SSH_PORT=$DETECTED_SSH_PORT
                fi
            else
                SSH_PORT=$CUSTOM_SSH_PORT
                print_info "سيتم استخدام المنفذ: $SSH_PORT"
            fi
        else
            print_warning "رقم منفذ غير صالح - سيتم استخدام المنفذ المكتشف: $DETECTED_SSH_PORT"
            SSH_PORT=$DETECTED_SSH_PORT
        fi
    else
        print_info "سيتم استخدام المنفذ المكتشف: $SSH_PORT"
    fi
    
    # Ask for additional ports
    echo ""
    echo -n "هل تريد فتح منافذ إضافية؟ (مثال: 3000, 8080) [y/n]: "
    read ADD_CUSTOM_PORTS
    CUSTOM_PORTS=()
    if [ "$ADD_CUSTOM_PORTS" = "y" ] || [ "$ADD_CUSTOM_PORTS" = "yes" ]; then
        echo -n "أدخل أرقام المنافذ مفصولة بمسافات (مثال: 3000 8080): "
        read -a CUSTOM_PORTS
        if [ ${#CUSTOM_PORTS[@]} -gt 0 ]; then
            print_info "المنافذ الإضافية: ${CUSTOM_PORTS[*]}"
        fi
    fi
    
    # Ask for logging level
    echo ""
    echo "مستوى التسجيل (Logging):"
    echo "  1) off    - بدون تسجيل"
    echo "  2) low    - منخفض (الحد الأدنى)"
    echo "  3) medium - متوسط (موصى به)"
    echo "  4) high   - عالي (تفصيلي)"
    echo "  5) full   - كامل (كل شيء)"
    echo -n "اختر مستوى التسجيل [3]: "
    read LOG_LEVEL_CHOICE
    LOG_LEVEL_CHOICE=${LOG_LEVEL_CHOICE:-3}
    
    case "$LOG_LEVEL_CHOICE" in
        1) LOG_LEVEL="off" ;;
        2) LOG_LEVEL="low" ;;
        3) LOG_LEVEL="medium" ;;
        4) LOG_LEVEL="high" ;;
        5) LOG_LEVEL="full" ;;
        *) LOG_LEVEL="medium" ;;
    esac
else
    # Non-interactive mode: use safe defaults
    print_info "استخدام الإعدادات الآمنة الافتراضية..."
    print_success "منفذ SSH: $SSH_PORT (مكتشف تلقائياً)"
    CUSTOM_PORTS=()
    LOG_LEVEL="medium"
fi

print_info "مستوى التسجيل: $LOG_LEVEL"

# ================================================================
# Confirm Configuration
# ================================================================

if [ "$NON_INTERACTIVE" = false ]; then
    print_header "تأكيد التهيئة"
    
    echo ""
    echo -e "${CYAN}الإعدادات التي سيتم تطبيقها:${NC}"
    echo -e "  ${BLUE}•${NC} السياسة الافتراضية: رفض جميع الاتصالات الواردة، السماح بالصادرة"
    echo -e "  ${BLUE}•${NC} منفذ SSH: ${GREEN}$SSH_PORT${NC} (مع rate limiting)"
    echo -e "  ${BLUE}•${NC} منفذ HTTP: ${GREEN}80${NC}"
    echo -e "  ${BLUE}•${NC} منفذ HTTPS: ${GREEN}443${NC}"
    if [ ${#CUSTOM_PORTS[@]} -gt 0 ]; then
        echo -e "  ${BLUE}•${NC} منافذ إضافية: ${GREEN}${CUSTOM_PORTS[*]}${NC}"
    fi
    echo -e "  ${BLUE}•${NC} مستوى التسجيل: ${GREEN}$LOG_LEVEL${NC}"
    echo ""
    echo -e "${GREEN}🛡️  ضمان الأمان: UFW لن يتم تعطيله أبداً خلال هذه العملية${NC}"
    echo -e "${GREEN}🔒 حماية SSH: القاعدة القديمة ستبقى حتى يتم تأكيد الجديدة${NC}"
    echo ""
    
    echo -n "هل تريد المتابعة؟ [y/n]: "
    read CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "yes" ]; then
        print_warning "تم الإلغاء من قبل المستخدم"
        exit 0
    fi
else
    print_header "تطبيق الإعدادات (Non-Interactive Mode)"
    echo ""
    echo -e "${CYAN}الإعدادات التي سيتم تطبيقها:${NC}"
    echo -e "  ${BLUE}•${NC} منفذ SSH: ${GREEN}$SSH_PORT${NC} (مكتشف تلقائياً + rate limiting)"
    echo -e "  ${BLUE}•${NC} منفذ HTTP: ${GREEN}80${NC}"
    echo -e "  ${BLUE}•${NC} منفذ HTTPS: ${GREEN}443${NC}"
    echo -e "  ${BLUE}•${NC} مستوى التسجيل: ${GREEN}$LOG_LEVEL${NC}"
    echo ""
fi

# ================================================================
# Configure Default Policies (Safe Mode)
# ================================================================

print_header "تكوين السياسات الافتراضية - الوضع الآمن"

print_step "تعيين السياسات الافتراضية..."

# Default: deny all incoming
ufw default deny incoming > /dev/null 2>&1
check_item "رفض جميع الاتصالات الواردة (default)" "pass"

# Default: allow all outgoing
ufw default allow outgoing > /dev/null 2>&1
check_item "السماح بجميع الاتصالات الصادرة (default)" "pass"

# Default: deny all routed
ufw default deny routed > /dev/null 2>&1
check_item "رفض جميع الاتصالات الموجهة (routed)" "pass"

# ================================================================
# Smart Rule Management - Check and Update (NOT Reset!)
# ================================================================

print_header "إدارة القواعد الذكية - بدون إعادة تعيين"

print_info "فحص القواعد الموجودة وتحديثها بدلاً من حذفها..."

# Function to check if a rule exists
rule_exists() {
    local port=$1
    local proto=${2:-tcp}
    ufw status | grep -q "${port}/${proto}"
}

# Function to safely add or update a rule
add_or_update_rule() {
    local port=$1
    local proto=${2:-tcp}
    local action=${3:-allow}
    local comment=${4:-""}
    
    if rule_exists $port $proto; then
        print_info "القاعدة موجودة بالفعل: ${port}/${proto}"
    else
        if [ -n "$comment" ]; then
            ufw $action ${port}/${proto} comment "$comment" > /dev/null 2>&1
        else
            ufw $action ${port}/${proto} > /dev/null 2>&1
        fi
        print_success "تمت إضافة: ${port}/${proto}"
    fi
}

# ================================================================
# CRITICAL: Ensure SSH is Always Accessible - SAFE METHOD
# ================================================================

print_header "🔒 ضمان الوصول إلى SSH - حرج! (طريقة آمنة)"

print_step "التأكد من أن SSH متاح دائماً..."

# SAFE METHOD: Add new rule BEFORE removing old one
if rule_exists $SSH_PORT tcp; then
    print_info "قاعدة SSH موجودة بالفعل على المنفذ $SSH_PORT"
    
    # Check if it's a LIMIT rule (rate limiting) or just ALLOW
    if ufw status | grep "${SSH_PORT}/tcp" | grep -q "LIMIT"; then
        print_success "قاعدة SSH مع rate limiting موجودة - ممتاز!"
    else
        print_warning "قاعدة SSH موجودة لكن بدون rate limiting"
        print_step "تحديث إلى rate limiting..."
        
        # Add new LIMIT rule first (safe!)
        ufw limit ${SSH_PORT}/tcp comment 'SSH with rate limiting' > /dev/null 2>&1 || true
        
        # Now safe to delete old ALLOW rule
        ufw delete allow ${SSH_PORT}/tcp > /dev/null 2>&1 || true
        
        print_success "تم التحديث إلى rate limiting"
    fi
else
    print_step "إضافة قاعدة SSH جديدة على المنفذ $SSH_PORT..."
    ufw limit ${SSH_PORT}/tcp comment 'SSH with rate limiting' > /dev/null 2>&1
    print_success "تمت إضافة قاعدة SSH بنجاح"
fi

# Verify SSH rule exists
if rule_exists $SSH_PORT tcp; then
    check_item "SSH (منفذ $SSH_PORT) مع rate limiting" "pass"
    print_info "Rate limiting: يسمح بـ 6 محاولات اتصال خلال 30 ثانية"
else
    print_error "فشل إضافة قاعدة SSH! هذا خطر جداً!"
    print_error "جاري المحاولة مرة أخرى..."
    
    # Try again with force
    ufw limit ${SSH_PORT}/tcp comment 'SSH with rate limiting - recovery' > /dev/null 2>&1
    
    if rule_exists $SSH_PORT tcp; then
        print_success "نجحت المحاولة الثانية - SSH محمي"
    else
        print_error "فشلت جميع المحاولات! يجب التدخل اليدوي!"
        exit 1
    fi
fi

# Clean up old SSH rules on different ports (if we changed the port)
if [ "$SSH_PORT" != "$DETECTED_SSH_PORT" ] && [ "$DETECTED_SSH_PORT" -gt 0 ]; then
    print_step "تنظيف قاعدة SSH القديمة على المنفذ $DETECTED_SSH_PORT..."
    ufw delete allow ${DETECTED_SSH_PORT}/tcp > /dev/null 2>&1 || true
    ufw delete limit ${DETECTED_SSH_PORT}/tcp > /dev/null 2>&1 || true
    print_info "تم تنظيف القواعد القديمة"
fi

echo ""
print_warning "⚠️  تأكد من أنك تستطيع الاتصال بـ SSH على المنفذ: $SSH_PORT"
print_info "💡 اختبر الاتصال من نافذة terminal أخرى قبل إغلاق هذه النافذة!"

# ================================================================
# Allow HTTP and HTTPS
# ================================================================

print_header "تكوين HTTP و HTTPS"

print_step "إضافة/تحديث قواعد HTTP و HTTPS..."

add_or_update_rule 80 tcp allow "HTTP"
add_or_update_rule 443 tcp allow "HTTPS"

check_item "HTTP (منفذ 80)" "pass"
check_item "HTTPS (منفذ 443)" "pass"

# ================================================================
# Allow Custom Ports
# ================================================================

if [ ${#CUSTOM_PORTS[@]} -gt 0 ]; then
    print_header "تكوين المنافذ الإضافية"
    
    for port in "${CUSTOM_PORTS[@]}"; do
        if [ "$port" -gt 0 ] 2>/dev/null; then
            print_step "إضافة/تحديث منفذ $port..."
            add_or_update_rule $port tcp allow "Custom port $port"
            check_item "منفذ مخصص ($port)" "pass"
        else
            print_warning "تخطي منفذ غير صالح: $port"
        fi
    done
fi

# ================================================================
# Configure Logging
# ================================================================

print_header "تكوين التسجيل (Logging)"

print_step "تعيين مستوى التسجيل إلى: $LOG_LEVEL..."
ufw logging $LOG_LEVEL > /dev/null 2>&1
check_item "Logging level: $LOG_LEVEL" "pass"

print_info "السجلات ستكون في: /var/log/ufw.log"

# ================================================================
# Enable UFW (if not already enabled)
# ================================================================

print_header "التحقق من تفعيل UFW"

if ufw status | grep -q "Status: active"; then
    print_success "UFW مُفعّل بالفعل ويعمل"
    print_step "إعادة تحميل القواعد..."
    ufw reload > /dev/null 2>&1
    check_item "تم إعادة تحميل القواعد بنجاح" "pass"
else
    print_step "تفعيل UFW للمرة الأولى..."
    # Enable UFW (with automatic yes, non-interactive)
    echo "y" | ufw --force enable > /dev/null 2>&1
    check_item "UFW مُفعّل ويعمل" "pass"
fi

# Verify UFW is active
if ufw status | grep -q "Status: active"; then
    print_success "✅ UFW مُفعّل ومحمي"
else
    print_error "فشل تفعيل UFW - يجب التحقق يدوياً!"
    exit 1
fi

# ================================================================
# Enable UFW on Boot
# ================================================================

print_header "تفعيل البدء التلقائي"

print_step "تفعيل UFW عند بدء التشغيل..."

# Enable UFW service
if command -v systemctl &> /dev/null; then
    systemctl enable ufw > /dev/null 2>&1
    check_item "UFW سيبدأ تلقائياً عند إعادة التشغيل" "pass"
else
    print_warning "systemctl غير متوفر - تحقق من إعدادات البدء التلقائي يدوياً"
fi

# ================================================================
# Final Status Verification
# ================================================================

print_header "التحقق النهائي من الحالة"

echo ""
ufw status verbose
echo ""

# Final security check
if ufw status | grep -q "Status: active"; then
    print_success "🎉 تم إعداد UFW بنجاح والخادم محمي!"
else
    print_error "تحذير: UFW غير مُفعّل! يجب التحقق فوراً"
    exit 1
fi

# Verify SSH rule one last time
if rule_exists $SSH_PORT tcp; then
    print_success "✅ قاعدة SSH موجودة ومحمية على المنفذ: $SSH_PORT"
else
    print_error "⚠️  تحذير: قاعدة SSH غير موجودة! قد تفقد الاتصال!"
    print_error "جاري إضافة قاعدة الطوارئ..."
    ufw limit ${SSH_PORT}/tcp comment 'SSH - emergency recovery' > /dev/null 2>&1
    ufw reload > /dev/null 2>&1
    print_success "تمت إضافة قاعدة الطوارئ"
fi

# ================================================================
# Additional Information
# ================================================================

print_header "معلومات مهمة"

echo ""
echo -e "${CYAN}الأوامر المفيدة:${NC}"
echo -e "  ${BLUE}•${NC} عرض الحالة:        ${GREEN}sudo ufw status verbose${NC}"
echo -e "  ${BLUE}•${NC} عرض القواعد:       ${GREEN}sudo ufw status numbered${NC}"
echo -e "  ${BLUE}•${NC} إضافة قاعدة:       ${GREEN}sudo ufw allow <port>${NC}"
echo -e "  ${BLUE}•${NC} حذف قاعدة:         ${GREEN}sudo ufw delete <rule_number>${NC}"
echo -e "  ${BLUE}•${NC} إعادة تحميل:       ${GREEN}sudo ufw reload${NC}"
echo -e "  ${BLUE}•${NC} عرض السجلات:       ${GREEN}sudo tail -f /var/log/ufw.log${NC}"
echo ""

echo -e "${YELLOW}⚠️  تحذيرات مهمة:${NC}"
echo -e "  ${RED}•${NC} ${YELLOW}تأكد من قدرتك على الاتصال عبر SSH قبل قطع الاتصال!${NC}"
echo -e "  ${RED}•${NC} اختبر الاتصال من terminal آخر: ${GREEN}ssh -p $SSH_PORT user@server${NC}"
echo -e "  ${RED}•${NC} إذا غيّرت منفذ SSH، تأكد من تحديث /etc/ssh/sshd_config"
echo -e "  ${RED}•${NC} النسخة الاحتياطية للقواعد القديمة في: ${GREEN}$BACKUP_FILE${NC}"
echo -e "  ${RED}•${NC} ${YELLOW}لا تستخدم 'ufw reset' أبداً في الإنتاج - خطر أمني حرج!${NC}"
echo ""

echo -e "${CYAN}📚 للمزيد من المعلومات:${NC}"
echo -e "  ${BLUE}•${NC} راجع ملف: ${GREEN}FIREWALL_SETUP.md${NC}"
echo -e "  ${BLUE}•${NC} لاستعادة من backup: راجع $BACKUP_DIR"
echo ""

# ================================================================
# Security Recommendations
# ================================================================

print_header "توصيات الأمان"

echo ""
echo -e "${CYAN}لتحسين الأمان:${NC}"
echo -e "  ${BLUE}1.${NC} استخدم SSH keys بدلاً من كلمات المرور"
echo -e "  ${BLUE}2.${NC} غيّر منفذ SSH الافتراضي (22) إلى منفذ آخر"
echo -e "  ${BLUE}3.${NC} عطّل root login عبر SSH"
echo -e "  ${BLUE}4.${NC} استخدم Fail2ban للحماية الإضافية"
echo -e "  ${BLUE}5.${NC} راقب السجلات بانتظام: ${GREEN}sudo tail -f /var/log/ufw.log${NC}"
echo -e "  ${BLUE}6.${NC} حدّث النظام بانتظام: ${GREEN}sudo apt update && sudo apt upgrade${NC}"
echo ""

print_header "✨ ملخص الأمان"

echo ""
echo -e "${GREEN}✅ UFW مُفعّل ويعمل${NC}"
echo -e "${GREEN}✅ لم يتم تعطيل UFW أبداً خلال الإعداد${NC}"
echo -e "${GREEN}✅ تم اكتشاف منفذ SSH النشط تلقائياً: $DETECTED_SSH_PORT${NC}"
echo -e "${GREEN}✅ قاعدة SSH محمية على المنفذ: $SSH_PORT${NC}"
echo -e "${GREEN}✅ Trap handler مُفعّل للحماية من الأخطاء${NC}"
echo -e "${GREEN}✅ السكريبت idempotent - يمكن تشغيله مرات عديدة بأمان${NC}"
echo -e "${GREEN}✅ دعم non-interactive mode للـ CI/CD${NC}"
echo -e "${GREEN}✅ نظامك محمي الآن بـ UFW Firewall${NC}"
echo ""

if [ "$NON_INTERACTIVE" = true ]; then
    print_success "🤖 تم الإعداد التلقائي بنجاح (Non-Interactive Mode)"
fi

echo ""
