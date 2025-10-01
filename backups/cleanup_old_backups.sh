#!/bin/bash

###############################################################################
# cleanup_old_backups.sh - تنظيف النسخ الاحتياطية القديمة
# Old Backups Cleanup Script
###############################################################################
# تنظيف تلقائي للنسخ القديمة حسب سياسة الاحتفاظ
# Automatic cleanup based on retention policy
###############################################################################

set -e

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# المسار الأساسي
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUPS_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/logs/backup_cleanup.log"

# عدد النسخ المحفوظة (افتراضي: 7)
KEEP_COUNT=${1:-7}

# إنشاء مجلد logs
mkdir -p "$PROJECT_DIR/logs"

# دالة الـ logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}         تنظيف النسخ الاحتياطية القديمة - Cleanup Old Backups${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

log "INFO: بدء عملية التنظيف - Starting cleanup"
log "INFO: الاحتفاظ بآخر $KEEP_COUNT نسخ - Keeping last $KEEP_COUNT backups"

# البحث عن جميع النسخ الاحتياطية
BACKUP_FILES=($(find "$BACKUPS_DIR" -name "backup_*.tar.gz" -type f | sort -r))
TOTAL_BACKUPS=${#BACKUP_FILES[@]}

log "INFO: عدد النسخ الموجودة: $TOTAL_BACKUPS"
echo -e "${BLUE}📊 عدد النسخ الموجودة:${NC} $TOTAL_BACKUPS"
echo ""

if [ $TOTAL_BACKUPS -le $KEEP_COUNT ]; then
    log "INFO: لا توجد نسخ قديمة للحذف"
    echo -e "${GREEN}✅ لا توجد نسخ قديمة للحذف${NC}"
    echo -e "${GREEN}No old backups to delete${NC}"
    echo ""
    exit 0
fi

# عدد النسخ للحذف
DELETE_COUNT=$((TOTAL_BACKUPS - KEEP_COUNT))

echo -e "${YELLOW}⚠️  سيتم حذف $DELETE_COUNT نسخة قديمة:${NC}"
echo -e "${YELLOW}Will delete $DELETE_COUNT old backup(s):${NC}"
echo ""

# قائمة النسخ المحذوفة
DELETED=0
FAILED=0

for ((i=$KEEP_COUNT; i<$TOTAL_BACKUPS; i++)); do
    BACKUP_FILE="${BACKUP_FILES[$i]}"
    BACKUP_NAME=$(basename "$BACKUP_FILE")
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    
    # حذف ملف .info المرتبط
    INFO_FILE="${BACKUP_FILE%.tar.gz}.info"
    
    echo -e "  ${RED}🗑️  حذف:${NC} $BACKUP_NAME ($BACKUP_SIZE)"
    
    if rm -f "$BACKUP_FILE" "$INFO_FILE" 2>/dev/null; then
        log "SUCCESS: تم حذف $BACKUP_NAME"
        ((DELETED++))
    else
        log "ERROR: فشل حذف $BACKUP_NAME"
        ((FAILED++))
    fi
done

echo ""
echo -e "${BLUE}======================================================================${NC}"

if [ $FAILED -eq 0 ]; then
    log "SUCCESS: تم حذف $DELETED نسخة بنجاح"
    echo -e "${GREEN}✅ تم حذف $DELETED نسخة بنجاح${NC}"
    echo -e "${GREEN}Successfully deleted $DELETED backup(s)${NC}"
else
    log "WARNING: تم حذف $DELETED نسخة، فشل حذف $FAILED"
    echo -e "${YELLOW}⚠️  تم حذف $DELETED نسخة، فشل حذف $FAILED${NC}"
    echo -e "${YELLOW}Deleted $DELETED, failed $FAILED${NC}"
fi

# عرض النسخ المتبقية
REMAINING_COUNT=$(find "$BACKUPS_DIR" -name "backup_*.tar.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUPS_DIR" 2>/dev/null | cut -f1)

echo ""
echo -e "${BLUE}📊 الإحصائيات النهائية:${NC}"
echo -e "  • النسخ المتبقية: $REMAINING_COUNT"
echo -e "  • المساحة الإجمالية: $TOTAL_SIZE"
echo -e "  • السجل: $LOG_FILE"
echo ""

log "INFO: انتهت عملية التنظيف - Cleanup completed"
echo -e "${BLUE}======================================================================${NC}"
echo ""
