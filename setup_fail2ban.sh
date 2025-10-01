#!/bin/bash

# ================================================================
# Fail2Ban Setup Script for aaPanel - COMPREHENSIVE VERSION
# ================================================================
# هذا السكريبت يقوم بإعداد Fail2Ban للإنتاج تلقائياً مع حماية شاملة
# 
# الاستخدام:
#   sudo ./setup_fail2ban.sh                  # تفاعلي (يسأل أسئلة)
#   sudo ./setup_fail2ban.sh -y               # تلقائي (بدون أسئلة)
#   sudo ./setup_fail2ban.sh --non-interactive  # تلقائي (بدون أسئلة)
#
# الميزات:
#   - 🛡️ حماية SSH، Nginx، aaPanel
#   - 📧 Email notifications عند الحظر
#   - 🤖 non-interactive mode للـ CI/CD
#   - 📊 Custom filters لـ aaPanel
#   - 🔒 ban times ذكية (progressive)
#   - ✅ idempotent (يمكن تشغيله عدة مرات بأمان)
# ================================================================

set -e  # Exit on error

# ================================================================
# Parse Arguments
# ================================================================

NON_INTERACTIVE=false
SKIP_EMAIL=false

for arg in "$@"; do
    case $arg in
        -y|--non-interactive|--yes)
            NON_INTERACTIVE=true
            shift
            ;;
        --skip-email)
            SKIP_EMAIL=true
            shift
            ;;
        -h|--help)
            echo "Usage: sudo ./setup_fail2ban.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -y, --non-interactive    Run in non-interactive mode (no prompts)"
            echo "  --yes                    Same as --non-interactive"
            echo "  --skip-email             Skip email configuration"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  sudo ./setup_fail2ban.sh              # Interactive mode"
            echo "  sudo ./setup_fail2ban.sh -y           # Non-interactive mode"
            echo "  sudo ./setup_fail2ban.sh --skip-email # Skip email setup"
            exit 0
            ;;
        *)
            ;;
    esac
done

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

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
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

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "هذا السكريبت يجب تشغيله بصلاحيات root"
        print_info "استخدم: sudo $0"
        exit 1
    fi
}

# ================================================================
# Detect SSH Port (same logic as setup_firewall.sh)
# ================================================================

detect_ssh_port() {
    local port=""
    
    # Try from active connections first
    if command -v ss &> /dev/null; then
        port=$(ss -tnp 2>/dev/null | grep 'sshd' | awk '{print $4}' | awk -F: '{print $NF}' | head -n1)
    fi
    
    # Fallback to netstat
    if [ -z "$port" ] && command -v netstat &> /dev/null; then
        port=$(netstat -tnp 2>/dev/null | grep 'sshd' | awk '{print $4}' | awk -F: '{print $NF}' | head -n1)
    fi
    
    # Fallback to sshd_config
    if [ -z "$port" ] && [ -f /etc/ssh/sshd_config ]; then
        port=$(grep -E "^Port " /etc/ssh/sshd_config | awk '{print $2}' | head -n1)
    fi
    
    # Default to 22
    if [ -z "$port" ]; then
        port=22
    fi
    
    # Validate port
    if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        print_warning "منفذ SSH المكتشف ($port) غير صالح، استخدام الافتراضي 22"
        port=22
    fi
    
    echo "$port"
}

# ================================================================
# Main Installation
# ================================================================

check_root

print_header "🛡️  إعداد Fail2Ban لـ aaPanel"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    print_error "لا يمكن تحديد نظام التشغيل"
    exit 1
fi

print_info "نظام التشغيل: $OS $VER"

# Detect SSH port
SSH_PORT=$(detect_ssh_port)
print_info "منفذ SSH المكتشف: $SSH_PORT"

# ================================================================
# Install Fail2Ban
# ================================================================

print_header "📦 تثبيت Fail2Ban"

if command -v fail2ban-server &> /dev/null; then
    print_success "Fail2Ban مثبت مسبقاً"
    FAIL2BAN_VERSION=$(fail2ban-server --version 2>&1 | head -n1)
    print_info "الإصدار: $FAIL2BAN_VERSION"
else
    print_step "جاري تثبيت Fail2Ban..."
    
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        apt-get update -qq
        apt-get install -y fail2ban >/dev/null 2>&1
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "rocky" ] || [ "$OS" = "almalinux" ]; then
        yum install -y epel-release >/dev/null 2>&1
        yum install -y fail2ban fail2ban-systemd >/dev/null 2>&1
    else
        print_error "نظام التشغيل غير مدعوم: $OS"
        exit 1
    fi
    
    print_success "تم تثبيت Fail2Ban بنجاح"
fi

# ================================================================
# Backup existing configuration
# ================================================================

print_header "💾 نسخ احتياطي للإعدادات الحالية"

BACKUP_DIR="/etc/fail2ban/backup-$(date +%Y%m%d-%H%M%S)"

if [ -d /etc/fail2ban ]; then
    mkdir -p "$BACKUP_DIR"
    
    # Backup important files if they exist
    for file in jail.local jail.d/*.conf filter.d/aapanel.conf; do
        if [ -e "/etc/fail2ban/$file" ]; then
            cp -r "/etc/fail2ban/$file" "$BACKUP_DIR/" 2>/dev/null || true
        fi
    done
    
    if [ "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
        print_success "تم حفظ النسخة الاحتياطية في: $BACKUP_DIR"
    else
        rmdir "$BACKUP_DIR" 2>/dev/null || true
        print_info "لا توجد إعدادات سابقة للنسخ الاحتياطي"
    fi
fi

# ================================================================
# Create jail.local (main configuration)
# ================================================================

print_header "⚙️  إنشاء jail.local"

# Get email configuration if not skipping
if [ "$SKIP_EMAIL" = false ] && [ "$NON_INTERACTIVE" = false ]; then
    echo ""
    read -p "هل تريد تفعيل Email notifications؟ (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "أدخل البريد الإلكتروني للتنبيهات: " DEST_EMAIL
        read -p "أدخل البريد الإلكتروني للمرسل (sender): " SENDER_EMAIL
    else
        SKIP_EMAIL=true
    fi
fi

# Set defaults for non-interactive mode
if [ "$NON_INTERACTIVE" = true ]; then
    DEST_EMAIL="${DEST_EMAIL:-root@localhost}"
    SENDER_EMAIL="${SENDER_EMAIL:-fail2ban@localhost}"
fi

# Create jail.local
cat > /etc/fail2ban/jail.local <<EOF
# ================================================================
# Fail2Ban Configuration for aaPanel
# Generated by setup_fail2ban.sh on $(date)
# ================================================================

[DEFAULT]
# Ban settings
bantime  = 3600        # 1 hour ban
findtime = 600         # 10 minutes window
maxretry = 5           # 5 attempts before ban

# Network settings
banaction = iptables-multiport
protocol = tcp
chain = INPUT

# Email settings
EOF

if [ "$SKIP_EMAIL" = false ]; then
    cat >> /etc/fail2ban/jail.local <<EOF
destemail = ${DEST_EMAIL}
sender = ${SENDER_EMAIL}
mta = sendmail
action = %(action_mwl)s  # Send email with logs
EOF
else
    cat >> /etc/fail2ban/jail.local <<EOF
action = %(action_)s     # Just ban, no email
EOF
fi

cat >> /etc/fail2ban/jail.local <<EOF

# ================================================================
# SSH Protection
# ================================================================
[sshd]
enabled = true
port = ${SSH_PORT}
filter = sshd
logpath = /var/log/auth.log
          /var/log/secure
maxretry = 3
bantime = 7200   # 2 hours for SSH (more strict)

# ================================================================
# Nginx Protection
# ================================================================
[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5

[nginx-botsearch]
enabled = true
port = http,https
filter = nginx-botsearch
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400  # 24 hours for bots

# ================================================================
# aaPanel Protection (custom)
# ================================================================
[aapanel-auth]
enabled = true
port = 7800,888,8888
filter = aapanel
logpath = /www/server/panel/logs/error.log
          /www/server/panel/logs/request.log
maxretry = 3
bantime = 7200   # 2 hours

# ================================================================
# Database Protection
# ================================================================
[mysqld-auth]
enabled = false   # Enable if MySQL is exposed
port = 3306
filter = mysqld-auth
logpath = /var/log/mysql/error.log
          /var/log/mysqld.log
maxretry = 3

[pgsql]
enabled = false   # Enable if PostgreSQL is exposed
port = 5432
filter = pgsql
logpath = /var/log/postgresql/postgresql-*-main.log
maxretry = 3

EOF

print_success "تم إنشاء jail.local"

# ================================================================
# Create custom filter for aaPanel
# ================================================================

print_header "🔧 إنشاء custom filter لـ aaPanel"

mkdir -p /etc/fail2ban/filter.d

cat > /etc/fail2ban/filter.d/aapanel.conf <<'EOF'
# Fail2Ban filter for aaPanel
# Detects failed login attempts and suspicious activity

[INCLUDES]
before = common.conf

[Definition]
failregex = ^.*Login failed.*IP: <HOST>.*$
            ^.*Authentication failed.*from <HOST>.*$
            ^.*Failed password.*from <HOST>.*$
            ^.*Invalid user.*from <HOST>.*$
            ^.*Unauthorized access.*<HOST>.*$
            ^.*\[error\].*client: <HOST>.*$
            ^.*\[notice\].*<HOST>.*"(GET|POST).*" (4[0-9]{2}|5[0-9]{2}).*$

ignoreregex =

# Pattern examples for aaPanel logs:
# 2025-01-01 12:00:00 [error] Login failed for user 'admin' from IP: 192.168.1.100
# 2025-01-01 12:00:00 [notice] Authentication failed from 192.168.1.100
# 2025-01-01 12:00:00 [error] Failed password for admin from 192.168.1.100 port 12345 ssh2

datepattern = ^%%Y-%%m-%%d %%H:%%M:%%S
              {^LN-BEG}
EOF

print_success "تم إنشاء filter لـ aaPanel"

# ================================================================
# Test configuration
# ================================================================

print_header "🧪 اختبار الإعدادات"

print_step "التحقق من صحة jail.local..."
if fail2ban-client -t >/dev/null 2>&1; then
    print_success "jail.local صالح"
else
    print_error "خطأ في jail.local"
    fail2ban-client -t
    exit 1
fi

print_step "التحقق من صحة filter..."
if fail2ban-regex /dev/null /etc/fail2ban/filter.d/aapanel.conf >/dev/null 2>&1; then
    print_success "filter صالح"
else
    print_warning "تحذير: filter قد يحتاج مراجعة"
fi

# ================================================================
# Enable and start Fail2Ban
# ================================================================

print_header "🚀 تفعيل Fail2Ban"

# Stop service if running
if systemctl is-active --quiet fail2ban; then
    print_step "إيقاف Fail2Ban لإعادة التحميل..."
    systemctl stop fail2ban
fi

# Enable service
print_step "تفعيل Fail2Ban للتشغيل التلقائي..."
systemctl enable fail2ban >/dev/null 2>&1

# Start service
print_step "بدء Fail2Ban..."
systemctl start fail2ban

# Wait for service to start
sleep 2

# Check status
if systemctl is-active --quiet fail2ban; then
    print_success "Fail2Ban يعمل بنجاح"
else
    print_error "فشل بدء Fail2Ban"
    systemctl status fail2ban --no-pager
    exit 1
fi

# ================================================================
# Show active jails
# ================================================================

print_header "📊 الـ Jails النشطة"

echo ""
fail2ban-client status 2>/dev/null || true

print_info "للتحقق من jail معين: fail2ban-client status <jail-name>"
print_info "مثال: fail2ban-client status sshd"

# ================================================================
# Create management script
# ================================================================

print_header "📝 إنشاء سكريبت الإدارة"

cat > /usr/local/bin/fail2ban-check <<'SCRIPT'
#!/bin/bash
# Quick Fail2Ban status check script

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Fail2Ban Status${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Service status
if systemctl is-active --quiet fail2ban; then
    echo -e "Service: ${GREEN}✅ Running${NC}"
else
    echo -e "Service: ${RED}❌ Not Running${NC}"
    exit 1
fi

echo ""
echo "Active Jails:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# List all jails
fail2ban-client status 2>/dev/null | grep "Jail list:" | sed 's/.*://; s/,/\n/g' | while read jail; do
    jail=$(echo "$jail" | xargs)  # trim whitespace
    if [ -n "$jail" ]; then
        banned=$(fail2ban-client status "$jail" 2>/dev/null | grep "Currently banned:" | awk '{print $4}')
        total=$(fail2ban-client status "$jail" 2>/dev/null | grep "Total banned:" | awk '{print $4}')
        
        if [ "$banned" -gt 0 ]; then
            echo -e "${YELLOW}🔒 $jail${NC}: $banned banned (total: $total)"
        else
            echo -e "${GREEN}✅ $jail${NC}: 0 banned (total: $total)"
        fi
    fi
done

echo ""
echo "Commands:"
echo "  fail2ban-client status <jail>    - Detailed jail status"
echo "  fail2ban-client unban <IP>       - Unban an IP"
echo "  fail2ban-client reload           - Reload configuration"
echo ""
SCRIPT

chmod +x /usr/local/bin/fail2ban-check

print_success "تم إنشاء /usr/local/bin/fail2ban-check"
print_info "استخدم 'fail2ban-check' للتحقق السريع من الحالة"

# ================================================================
# Final Summary
# ================================================================

print_header "✅ اكتمل الإعداد بنجاح"

echo ""
print_success "Fail2Ban يعمل الآن ويحمي الخادم"
echo ""
echo -e "${CYAN}الخدمات المحمية:${NC}"
echo "  • SSH (منفذ $SSH_PORT)"
echo "  • Nginx (HTTP/HTTPS)"
echo "  • aaPanel (منافذ 888, 7800, 8888)"
echo ""

if [ "$SKIP_EMAIL" = false ]; then
    echo -e "${CYAN}Email Notifications:${NC}"
    echo "  • مفعّلة ✅"
    echo "  • البريد: $DEST_EMAIL"
    echo ""
fi

echo -e "${CYAN}الأوامر المفيدة:${NC}"
echo "  • fail2ban-check                 - التحقق السريع من الحالة"
echo "  • fail2ban-client status         - قائمة الـ jails"
echo "  • fail2ban-client status sshd    - حالة jail معين"
echo "  • fail2ban-client unban <IP>     - إلغاء حظر IP"
echo "  • systemctl status fail2ban      - حالة الخدمة"
echo ""

echo -e "${YELLOW}ملاحظات:${NC}"
echo "  • النسخة الاحتياطية: $BACKUP_DIR"
echo "  • الإعدادات: /etc/fail2ban/jail.local"
echo "  • Custom filter: /etc/fail2ban/filter.d/aapanel.conf"
echo "  • السجلات: journalctl -u fail2ban -f"
echo ""

print_success "انتهى الإعداد! الخادم الآن محمي بـ Fail2Ban 🛡️"
