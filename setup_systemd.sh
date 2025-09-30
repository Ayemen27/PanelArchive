#!/bin/bash
#coding: utf-8
# +-------------------------------------------------------------------
# | aaPanel - systemd Service Setup Script
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 aaPanel(www.aapanel.com) All rights reserved.
# +-------------------------------------------------------------------

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تعريف المتغيرات
PANEL_PATH="/www/server/panel"
SERVICE_FILE="aapanel.service"
SYSTEMD_PATH="/etc/systemd/system"
USER="www"
GROUP="www"

# دالة طباعة الرسائل
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# التحقق من صلاحيات root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "يجب تشغيل هذا السكريبت كـ root"
        exit 1
    fi
}

# التحقق من وجود المستخدم www
check_user() {
    print_info "التحقق من وجود المستخدم $USER..."
    
    if ! id "$USER" &>/dev/null; then
        print_warning "المستخدم $USER غير موجود، سيتم إنشاؤه..."
        groupadd -r $GROUP 2>/dev/null || true
        useradd -r -g $GROUP -s /sbin/nologin -d /www -M $USER
        print_success "تم إنشاء المستخدم $USER"
    else
        print_success "المستخدم $USER موجود"
    fi
}

# التحقق من وجود مسار التطبيق
check_panel_path() {
    print_info "التحقق من مسار التطبيق..."
    
    if [ ! -d "$PANEL_PATH" ]; then
        print_error "مسار التطبيق $PANEL_PATH غير موجود"
        exit 1
    fi
    
    print_success "مسار التطبيق موجود"
}

# التحقق من الاعتماديات
check_dependencies() {
    print_info "التحقق من الاعتماديات..."
    
    # التحقق من Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 غير مثبت"
        exit 1
    fi
    print_success "Python 3 متوفر: $(python3 --version)"
    
    # التحقق من python3-venv
    if ! python3 -m venv --help &> /dev/null; then
        print_warning "python3-venv غير مثبت، سيتم التثبيت..."
        apt-get update && apt-get install -y python3-venv
    fi
    
    # إنشاء virtualenv إن لم يكن موجوداً
    VENV_PATH="$PANEL_PATH/venv"
    if [ ! -d "$VENV_PATH" ]; then
        print_info "إنشاء virtualenv في $VENV_PATH..."
        python3 -m venv "$VENV_PATH"
        print_success "تم إنشاء virtualenv"
    else
        print_success "virtualenv موجود"
    fi
    
    # تفعيل virtualenv وتثبيت الاعتماديات
    print_info "تثبيت الاعتماديات في virtualenv..."
    source "$VENV_PATH/bin/activate"
    pip install --upgrade pip
    pip install gunicorn gevent-websocket
    
    # تثبيت requirements.txt إن وجد
    if [ -f "$PANEL_PATH/requirements.txt" ]; then
        pip install -r "$PANEL_PATH/requirements.txt"
    fi
    
    deactivate
    print_success "تم تثبيت جميع الاعتماديات في virtualenv"
    
    # التحقق من ملف .env
    if [ ! -f "$PANEL_PATH/.env" ]; then
        print_warning "ملف .env غير موجود"
        if [ -f "$PANEL_PATH/.env.example" ]; then
            print_info "نسخ .env من .env.example..."
            cp "$PANEL_PATH/.env.example" "$PANEL_PATH/.env"
            print_warning "تحذير: يجب تعديل ملف .env بالإعدادات الصحيحة!"
        else
            print_error "ملف .env.example غير موجود أيضاً"
            exit 1
        fi
    else
        print_success "ملف .env موجود"
    fi
}

# إنشاء المجلدات المطلوبة
create_directories() {
    print_info "إنشاء المجلدات المطلوبة..."
    
    mkdir -p "$PANEL_PATH/logs"
    mkdir -p "$PANEL_PATH/data"
    mkdir -p "$PANEL_PATH/BTPanel/static/upload"
    
    print_success "تم إنشاء المجلدات"
}

# ضبط الصلاحيات
set_permissions() {
    print_info "ضبط الصلاحيات..."
    
    chown -R $USER:$GROUP "$PANEL_PATH"
    chmod -R 755 "$PANEL_PATH"
    chmod -R 775 "$PANEL_PATH/logs"
    chmod -R 775 "$PANEL_PATH/data"
    chmod 600 "$PANEL_PATH/.env"
    
    print_success "تم ضبط الصلاحيات"
}

# تثبيت systemd service
install_service() {
    print_info "تثبيت systemd service..."
    
    # نسخ ملف الخدمة
    if [ -f "$SERVICE_FILE" ]; then
        cp "$SERVICE_FILE" "$SYSTEMD_PATH/"
        print_success "تم نسخ ملف الخدمة"
    else
        print_error "ملف $SERVICE_FILE غير موجود"
        exit 1
    fi
    
    # إعادة تحميل systemd
    systemctl daemon-reload
    print_success "تم إعادة تحميل systemd"
    
    # تفعيل الخدمة للبدء التلقائي
    systemctl enable aapanel.service
    print_success "تم تفعيل الخدمة للبدء التلقائي"
}

# اختبار الخدمة
test_service() {
    print_info "اختبار الخدمة..."
    
    # التحقق من صحة ملف الخدمة
    systemctl cat aapanel.service &>/dev/null
    if [ $? -eq 0 ]; then
        print_success "ملف الخدمة صحيح"
    else
        print_error "ملف الخدمة يحتوي على أخطاء"
        exit 1
    fi
}

# بدء الخدمة
start_service() {
    print_info "بدء الخدمة..."
    
    systemctl start aapanel.service
    
    # الانتظار قليلاً
    sleep 3
    
    # التحقق من الحالة
    if systemctl is-active --quiet aapanel.service; then
        print_success "الخدمة تعمل بنجاح!"
        systemctl status aapanel.service --no-pager
    else
        print_error "فشل بدء الخدمة"
        print_info "عرض السجلات:"
        journalctl -u aapanel.service -n 50 --no-pager
        exit 1
    fi
}

# عرض معلومات ما بعد التثبيت
post_install_info() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ تم تثبيت aaPanel systemd service بنجاح   ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    print_info "الأوامر المفيدة:"
    echo -e "  ${YELLOW}# عرض حالة الخدمة${NC}"
    echo "    sudo systemctl status aapanel"
    echo ""
    echo -e "  ${YELLOW}# بدء الخدمة${NC}"
    echo "    sudo systemctl start aapanel"
    echo ""
    echo -e "  ${YELLOW}# إيقاف الخدمة${NC}"
    echo "    sudo systemctl stop aapanel"
    echo ""
    echo -e "  ${YELLOW}# إعادة تشغيل الخدمة${NC}"
    echo "    sudo systemctl restart aapanel"
    echo ""
    echo -e "  ${YELLOW}# عرض السجلات${NC}"
    echo "    sudo journalctl -u aapanel -f"
    echo ""
    echo -e "  ${YELLOW}# تعطيل البدء التلقائي${NC}"
    echo "    sudo systemctl disable aapanel"
    echo ""
    print_info "ملاحظات مهمة:"
    echo "  - تأكد من تعديل ملف .env بالإعدادات الصحيحة"
    echo "  - السجلات في: $PANEL_PATH/logs/"
    echo "  - الخدمة ستبدأ تلقائياً عند إعادة تشغيل النظام"
    echo ""
}

# Main function
main() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     aaPanel systemd Service Setup Script     ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_root
    check_user
    check_panel_path
    check_dependencies
    create_directories
    set_permissions
    install_service
    test_service
    start_service
    post_install_info
}

# تشغيل السكريبت
main
