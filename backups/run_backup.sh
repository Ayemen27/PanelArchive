#!/bin/bash

###############################################################################
# run_backup.sh - تشغيل النسخ الاحتياطي ببساطة
# Simple Backup Execution Script
###############################################################################
# سكريبت wrapper بسيط لتشغيل النسخ الاحتياطي من أي مكان
# Simple wrapper to run backups from anywhere
###############################################################################

# الألوان
BLUE='\033[0;34m'
NC='\033[0m'

# المسار الأساسي للمشروع
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_SCRIPT="$PROJECT_DIR/backups/backup_manager.py"

# تغيير المجلد للمشروع
cd "$PROJECT_DIR" || exit 1

# تشغيل النسخ الاحتياطي
echo -e "${BLUE}🔄 تشغيل النسخ الاحتياطي من: $BACKUP_SCRIPT${NC}"
echo ""

python3 "$BACKUP_SCRIPT" "$@"

# حفظ كود الخروج
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${BLUE}✅ تم إنهاء النسخ الاحتياطي بنجاح${NC}"
else
    echo -e "${BLUE}⚠️  انتهى النسخ الاحتياطي مع رمز الخطأ: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
