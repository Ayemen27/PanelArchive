#!/bin/bash
#coding: utf-8
# +-------------------------------------------------------------------
# | aaPanel - Blue-Green Deployment Script
# +-------------------------------------------------------------------
# | Zero-downtime deployment with automatic rollback
# +-------------------------------------------------------------------

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# المتغيرات
REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_NAME="${IMAGE_NAME:-owner/aapanel}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
MAX_HEALTH_RETRIES=15
HEALTH_CHECK_INTERVAL=5
ACTIVE_ENV_FILE=".active_environment"

# دوال المساعدة
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

print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "$1"
    echo "═══════════════════════════════════════════════════════════"
}

# 1. اكتشاف البيئة النشطة الحالية
detect_active_environment() {
    print_header "🔍 Detecting Active Environment"
    
    # قراءة من الملف إذا كان موجوداً
    if [ -f "$ACTIVE_ENV_FILE" ]; then
        CURRENT_ACTIVE=$(cat "$ACTIVE_ENV_FILE")
        print_info "Current active environment from file: $CURRENT_ACTIVE"
    else
        # اكتشاف تلقائي من الحاويات الجارية
        if docker ps | grep -q "aapanel_app_blue"; then
            CURRENT_ACTIVE="blue"
            print_info "Detected blue environment is running"
        elif docker ps | grep -q "aapanel_app_green"; then
            CURRENT_ACTIVE="green"
            print_info "Detected green environment is running"
        else
            CURRENT_ACTIVE="none"
            print_warning "No active environment detected - this is first deployment"
        fi
    fi
    
    # تحديد البيئة المستهدفة
    if [ "$CURRENT_ACTIVE" == "blue" ]; then
        TARGET_ENV="green"
        TARGET_PORT=5002
        CURRENT_PORT=5001
    elif [ "$CURRENT_ACTIVE" == "green" ]; then
        TARGET_ENV="blue"
        TARGET_PORT=5001
        CURRENT_PORT=5002
    else
        TARGET_ENV="blue"
        TARGET_PORT=5001
        CURRENT_PORT=0
    fi
    
    print_success "Current active: ${CURRENT_ACTIVE}"
    print_success "Target deployment: ${TARGET_ENV}"
    
    echo "$CURRENT_ACTIVE" > "${ACTIVE_ENV_FILE}.backup"
}

# 2. تشغيل Shared Services
start_shared_services() {
    print_header "🔧 Starting Shared Services"
    
    # التحقق إذا كانت الخدمات المشتركة تعمل
    if docker ps | grep -q "aapanel_postgres_shared" && docker ps | grep -q "aapanel_redis_shared"; then
        print_success "Shared services already running"
        return 0
    fi
    
    print_info "Starting shared PostgreSQL and Redis services..."
    
    # بدء الخدمات المشتركة
    if docker-compose -f docker-compose.shared.yml up -d; then
        print_success "Shared services started"
        
        # انتظار جاهزية الخدمات
        print_info "Waiting for shared services to be ready..."
        sleep 5
    else
        print_error "Failed to start shared services"
        exit 1
    fi
}

# 3. Pull الصورة الجديدة
pull_new_image() {
    print_header "📦 Pulling New Docker Image"
    
    print_info "Pulling ${FULL_IMAGE}..."
    
    if docker pull "${FULL_IMAGE}"; then
        print_success "Successfully pulled ${FULL_IMAGE}"
        
        # عرض معلومات الصورة
        IMAGE_ID=$(docker images --format "{{.ID}}" "${FULL_IMAGE}" | head -1)
        IMAGE_SIZE=$(docker images --format "{{.Size}}" "${FULL_IMAGE}" | head -1)
        print_info "Image ID: ${IMAGE_ID}"
        print_info "Image Size: ${IMAGE_SIZE}"
    else
        print_error "Failed to pull image"
        exit 1
    fi
}

# 4. نشر على البيئة المستهدفة
deploy_target_environment() {
    print_header "🚀 Deploying to ${TARGET_ENV^^} Environment"
    
    print_info "Starting ${TARGET_ENV} environment on port ${TARGET_PORT}..."
    
    # إيقاف البيئة المستهدفة إذا كانت موجودة
    if docker ps -a | grep -q "aapanel_app_${TARGET_ENV}"; then
        print_info "Stopping existing ${TARGET_ENV} containers..."
        docker-compose -f "docker-compose.${TARGET_ENV}.yml" down
    fi
    
    # تصدير المتغيرات
    export REGISTRY
    export IMAGE_NAME
    export IMAGE_TAG
    
    # بدء البيئة المستهدفة
    if docker-compose -f "docker-compose.${TARGET_ENV}.yml" up -d --remove-orphans; then
        print_success "${TARGET_ENV^^} environment started"
    else
        print_error "Failed to start ${TARGET_ENV} environment"
        return 1
    fi
    
    # عرض حالة الحاويات
    print_info "Container status:"
    docker-compose -f "docker-compose.${TARGET_ENV}.yml" ps
}

# 5. Health Check للبيئة المستهدفة
health_check_target() {
    print_header "🏥 Health Check - ${TARGET_ENV^^} Environment"
    
    RETRY_COUNT=0
    TARGET_URL="http://localhost:${TARGET_PORT}"
    
    print_info "Waiting for ${TARGET_ENV} application to be ready..."
    sleep 10
    
    while [ $RETRY_COUNT -lt $MAX_HEALTH_RETRIES ]; do
        # محاولة health endpoint
        if curl -f -s "${TARGET_URL}/health" > /dev/null 2>&1; then
            print_success "Health check passed! (${TARGET_URL}/health)"
            return 0
        fi
        
        # محاولة الصفحة الرئيسية
        if curl -f -s "${TARGET_URL}/" > /dev/null 2>&1; then
            print_success "Health check passed! (${TARGET_URL}/)"
            return 0
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        print_warning "Health check attempt ${RETRY_COUNT}/${MAX_HEALTH_RETRIES} failed, retrying in ${HEALTH_CHECK_INTERVAL}s..."
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    print_error "Health check failed after ${MAX_HEALTH_RETRIES} attempts"
    
    # عرض logs للمساعدة في التشخيص
    print_info "${TARGET_ENV^^} application logs:"
    docker-compose -f "docker-compose.${TARGET_ENV}.yml" logs --tail=50 app-${TARGET_ENV}
    
    return 1
}

# 6. التبديل للبيئة الجديدة
switch_traffic() {
    print_header "🔄 Switching Traffic to ${TARGET_ENV^^}"
    
    # تحديث الملف النشط
    echo "$TARGET_ENV" > "$ACTIVE_ENV_FILE"
    print_success "Updated active environment to: $TARGET_ENV"
    
    # تشغيل سكريبت التبديل إن وُجد
    if [ -f "switch.sh" ]; then
        print_info "Executing switch script..."
        bash switch.sh "$TARGET_ENV" "$TARGET_PORT"
    else
        print_warning "No switch.sh found - manual traffic switch required"
        print_info "Please update your load balancer/nginx to point to port ${TARGET_PORT}"
    fi
    
    print_success "Traffic switched to ${TARGET_ENV} on port ${TARGET_PORT}"
}

# 7. إيقاف البيئة القديمة
stop_old_environment() {
    print_header "⏹️  Stopping Old Environment"
    
    if [ "$CURRENT_ACTIVE" == "none" ]; then
        print_info "No old environment to stop (first deployment)"
        return 0
    fi
    
    print_info "Waiting 30 seconds before stopping old environment..."
    sleep 30
    
    print_info "Stopping ${CURRENT_ACTIVE} environment..."
    if docker-compose -f "docker-compose.${CURRENT_ACTIVE}.yml" stop app-${CURRENT_ACTIVE}; then
        print_success "${CURRENT_ACTIVE^^} environment stopped"
    else
        print_warning "Failed to stop ${CURRENT_ACTIVE} environment (non-critical)"
    fi
    
    print_info "Keeping ${CURRENT_ACTIVE} containers for quick rollback if needed"
}

# 8. Rollback عند الفشل
rollback() {
    print_header "⚠️  Rolling Back Deployment"
    
    print_error "Deployment failed, initiating rollback..."
    
    # إيقاف البيئة الفاشلة
    print_info "Stopping failed ${TARGET_ENV} environment..."
    docker-compose -f "docker-compose.${TARGET_ENV}.yml" down
    
    # استعادة البيئة السابقة إن وُجدت
    if [ -f "${ACTIVE_ENV_FILE}.backup" ]; then
        PREVIOUS_ACTIVE=$(cat "${ACTIVE_ENV_FILE}.backup")
        
        if [ "$PREVIOUS_ACTIVE" != "none" ]; then
            print_info "Restoring ${PREVIOUS_ACTIVE} environment..."
            
            # التأكد من أن البيئة السابقة تعمل
            if ! docker ps | grep -q "aapanel_app_${PREVIOUS_ACTIVE}"; then
                print_info "Starting ${PREVIOUS_ACTIVE} environment..."
                docker-compose -f "docker-compose.${PREVIOUS_ACTIVE}.yml" up -d
            fi
            
            # استعادة ملف البيئة النشطة
            cp "${ACTIVE_ENV_FILE}.backup" "$ACTIVE_ENV_FILE"
            
            print_success "Rollback completed - ${PREVIOUS_ACTIVE} environment is active"
        else
            print_error "No previous environment to rollback to"
        fi
    else
        print_error "No backup found for rollback"
    fi
}

# 9. تنظيف الموارد
cleanup() {
    print_header "🧹 Cleanup"
    
    # حذف الصور القديمة (احتفظ بآخر 3 إصدارات)
    print_info "Removing old images..."
    docker images "${REGISTRY}/${IMAGE_NAME}" --format "{{.ID}}" | tail -n +4 | xargs -r docker rmi -f 2>/dev/null || true
    
    # حذف volumes اليتيمة
    print_info "Removing orphan volumes..."
    docker volume prune -f || true
    
    print_success "Cleanup completed"
}

# 10. عرض ملخص النشر
deployment_summary() {
    print_header "📊 Deployment Summary"
    
    echo ""
    echo "✅ Blue-Green Deployment completed successfully!"
    echo ""
    echo "Image: ${FULL_IMAGE}"
    echo "Active Environment: ${TARGET_ENV^^}"
    echo "Active Port: ${TARGET_PORT}"
    echo ""
    echo "Container Status:"
    docker-compose -f "docker-compose.${TARGET_ENV}.yml" ps
    echo ""
    echo "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose -f "docker-compose.${TARGET_ENV}.yml" ps -q) 2>/dev/null || true
    echo ""
    print_success "Application is now live on ${TARGET_ENV^^}! 🎉"
}

# ==================== التنفيذ الرئيسي ====================
main() {
    print_header "🚀 aaPanel Blue-Green Deployment"
    echo "Image: ${FULL_IMAGE}"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 1. اكتشاف البيئة النشطة
    detect_active_environment
    
    # 2. تشغيل Shared Services
    start_shared_services
    
    # 3. Pull الصورة الجديدة
    pull_new_image
    
    # 4. نشر على البيئة المستهدفة
    if ! deploy_target_environment; then
        rollback
        exit 1
    fi
    
    # 5. Health Check
    if ! health_check_target; then
        rollback
        exit 1
    fi
    
    # 6. التبديل للبيئة الجديدة
    switch_traffic
    
    # 7. إيقاف البيئة القديمة
    stop_old_environment
    
    # 8. التنظيف
    cleanup
    
    # 9. ملخص النشر
    deployment_summary
    
    print_success "Blue-Green Deployment completed successfully! ✅"
    exit 0
}

# معالجة الإشارات للـ rollback عند المقاطعة
trap rollback INT TERM

# تشغيل السكريبت
main "$@"
