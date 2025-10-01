#!/usr/bin/env python3
# coding: utf-8
"""
نظام النسخ الاحتياطي الشامل - Comprehensive Backup Manager
يوفر نظام نسخ احتياطي متكامل لقواعد البيانات والملفات الهامة

المميزات:
- دعم قواعد بيانات متعددة (SQLite, PostgreSQL, MySQL)
- نسخ احتياطي للمجلدات والملفات الهامة
- ضغط tar.gz مع تسمية زمنية
- الاحتفاظ بعدد محدد من النسخ
- التحقق من سلامة النسخ (MD5 checksum)
- CLI متقدم مع ألوان ANSI
- سجل شامل للعمليات

الاستخدام:
    python backups/backup_manager.py                    # نسخ احتياطي جديد
    python backups/backup_manager.py --list             # قائمة النسخ الاحتياطية
    python backups/backup_manager.py --cleanup          # تنظيف النسخ القديمة
    python backups/backup_manager.py --keep N           # تغيير عدد النسخ المحفوظة
    python backups/backup_manager.py --restore FILE     # استرجاع نسخة احتياطية
"""

import os
import sys
import argparse
import subprocess
import tarfile
import hashlib
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

# إضافة المجلد الجذر للـ PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config_factory import get_config
    from environment_detector import detect_environment
except ImportError:
    print("❌ خطأ: لا يمكن استيراد config_factory أو environment_detector")
    print("   تأكد من وجود الملفات في المجلد الجذر")
    sys.exit(1)


# ==================== ألوان ANSI للـ CLI ====================
class Colors:
    """ألوان ANSI لواجهة سطر الأوامر - ANSI Colors for CLI"""
    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def disable():
        """تعطيل الألوان"""
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


# ==================== إعداد Logging ====================
def setup_logging(log_file: str = 'backups/backup.log') -> logging.Logger:
    """
    إعداد نظام التسجيل (Logging)
    
    Args:
        log_file: مسار ملف السجل
    
    Returns:
        logging.Logger: كائن Logger
    """
    # إنشاء مجلد logs إن لم يكن موجوداً
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # إعداد Logger
    logger = logging.getLogger('BackupManager')
    logger.setLevel(logging.DEBUG)
    
    # Handler للملف
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler للـ Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # تنسيق السجلات
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # إضافة Handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


# ==================== دوال مساعدة ====================
def calculate_md5(file_path: str) -> str:
    """
    حساب MD5 checksum للملف
    
    Args:
        file_path: مسار الملف
    
    Returns:
        str: MD5 checksum بصيغة hex
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_size(size_bytes: int) -> str:
    """
    تنسيق حجم الملف بشكل قابل للقراءة
    
    Args:
        size_bytes: الحجم بالبايت
    
    Returns:
        str: الحجم المنسق (مثل: 1.5 MB)
    """
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def safe_remove_file(file_path: str, logger: logging.Logger) -> bool:
    """
    حذف ملف بشكل آمن
    
    Args:
        file_path: مسار الملف
        logger: كائن Logger
    
    Returns:
        bool: True إذا نجح الحذف، False خلاف ذلك
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"تم حذف الملف: {file_path}")
            return True
    except Exception as e:
        logger.error(f"فشل حذف الملف {file_path}: {e}")
        return False
    return False


# ==================== BackupManager Class ====================
class BackupManager:
    """
    مدير النسخ الاحتياطي - Backup Manager
    
    يوفر جميع وظائف النسخ الاحتياطي والاسترجاع
    """
    
    def __init__(self, backup_dir: str = 'backups', retention: int = 7):
        """
        تهيئة مدير النسخ الاحتياطي
        
        Args:
            backup_dir: مجلد حفظ النسخ الاحتياطية
            retention: عدد النسخ المحفوظة (الافتراضي: 7)
        """
        self.backup_dir = Path(backup_dir)
        self.retention = int(os.environ.get('BACKUP_RETENTION', retention))
        self.logger = setup_logging()
        self.config = get_config()
        
        # إنشاء مجلد النسخ الاحتياطية
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # المجلدات والملفات المراد نسخها
        self.backup_items = [
            'data/',
            'logs/',
            '.env',
            'alembic.ini'
        ]
        
        self.logger.info(f"تم تهيئة BackupManager - البيئة: {self.config.ENVIRONMENT}")
    
    def create_backup(self) -> Optional[str]:
        """
        إنشاء نسخة احتياطية جديدة
        
        Returns:
            str: مسار ملف النسخة الاحتياطية، أو None في حالة الفشل
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        temp_dir = self.backup_dir / f"temp_{timestamp}"
        
        try:
            print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
            print(f"{Colors.BOLD}🔄 بدء عملية النسخ الاحتياطي - Starting Backup{Colors.ENDC}")
            print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
            
            # إنشاء مجلد مؤقت
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"تم إنشاء المجلد المؤقت: {temp_dir}")
            
            # نسخ قاعدة البيانات
            db_backup_success = self._backup_database(temp_dir)
            if not db_backup_success:
                print(f"{Colors.WARNING}⚠️  تحذير: فشل نسخ قاعدة البيانات{Colors.ENDC}")
            
            # نسخ الملفات والمجلدات
            files_copied = self._backup_files(temp_dir)
            
            if files_copied == 0 and not db_backup_success:
                print(f"{Colors.FAIL}❌ لا توجد بيانات للنسخ الاحتياطي{Colors.ENDC}")
                shutil.rmtree(temp_dir)
                return None
            
            # ضغط الملفات
            print(f"\n{Colors.OKCYAN}📦 جاري ضغط الملفات...{Colors.ENDC}")
            self._create_tarball(temp_dir, backup_path)
            
            # حساب MD5 checksum
            print(f"{Colors.OKCYAN}🔐 جاري حساب checksum...{Colors.ENDC}")
            md5_hash = calculate_md5(str(backup_path))
            
            # حفظ معلومات النسخة
            info_file = backup_path.with_suffix('.tar.gz.info')
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Backup Name: {backup_name}\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Environment: {self.config.ENVIRONMENT}\n")
                f.write(f"Database Type: {self.config.DATABASE_TYPE}\n")
                f.write(f"MD5: {md5_hash}\n")
                f.write(f"Size: {format_size(backup_path.stat().st_size)}\n")
            
            # حذف المجلد المؤقت
            shutil.rmtree(temp_dir)
            
            # تنظيف النسخ القديمة
            self._cleanup_old_backups()
            
            # عرض النتائج
            size = format_size(backup_path.stat().st_size)
            print(f"\n{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}✅ تم إنشاء النسخة الاحتياطية بنجاح!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}")
            print(f"📁 الملف: {Colors.BOLD}{backup_path}{Colors.ENDC}")
            print(f"📊 الحجم: {Colors.BOLD}{size}{Colors.ENDC}")
            print(f"🔐 MD5: {Colors.BOLD}{md5_hash}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}\n")
            
            self.logger.info(f"نسخة احتياطية ناجحة: {backup_path} ({size})")
            
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"فشل إنشاء النسخة الاحتياطية: {e}")
            print(f"\n{Colors.FAIL}❌ خطأ: {e}{Colors.ENDC}\n")
            
            # تنظيف في حالة الفشل
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            if backup_path.exists():
                backup_path.unlink()
            
            return None
    
    def _backup_database(self, temp_dir: Path) -> bool:
        """
        نسخ قاعدة البيانات
        
        Args:
            temp_dir: المجلد المؤقت
        
        Returns:
            bool: True إذا نجح النسخ، False خلاف ذلك
        """
        db_type = self.config.DATABASE_TYPE
        db_uri = self.config.DATABASE_URI
        
        print(f"{Colors.OKCYAN}💾 نسخ احتياطي لقاعدة البيانات ({db_type})...{Colors.ENDC}")
        
        try:
            if db_type == 'sqlite':
                return self._backup_sqlite(temp_dir)
            elif db_type == 'postgresql':
                return self._backup_postgresql(temp_dir)
            elif db_type == 'mysql':
                return self._backup_mysql(temp_dir)
            else:
                self.logger.warning(f"نوع قاعدة بيانات غير مدعوم: {db_type}")
                return False
        except Exception as e:
            self.logger.error(f"فشل نسخ قاعدة البيانات: {e}")
            return False
    
    def _backup_sqlite(self, temp_dir: Path) -> bool:
        """
        نسخ قاعدة بيانات SQLite
        
        Args:
            temp_dir: المجلد المؤقت
        
        Returns:
            bool: True إذا نجح النسخ
        """
        import sqlite3
        
        # استخراج مسار قاعدة البيانات من URI
        db_uri = self.config.DATABASE_URI
        db_path_match = re.search(r'sqlite:///(.+)', db_uri)
        
        if not db_path_match:
            self.logger.error(f"لا يمكن استخراج مسار قاعدة البيانات من: {db_uri}")
            return False
        
        db_path = db_path_match.group(1)
        
        if not os.path.exists(db_path):
            self.logger.warning(f"قاعدة البيانات غير موجودة: {db_path}")
            return False
        
        # إنشاء dump
        dump_file = temp_dir / 'database_sqlite.sql'
        
        try:
            conn = sqlite3.connect(db_path)
            with open(dump_file, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            conn.close()
            
            # نسخ ملف قاعدة البيانات الأصلي أيضاً
            db_file_copy = temp_dir / os.path.basename(db_path)
            shutil.copy2(db_path, db_file_copy)
            
            self.logger.info(f"تم نسخ SQLite: {db_path}")
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} تم نسخ قاعدة بيانات SQLite")
            return True
            
        except Exception as e:
            self.logger.error(f"فشل نسخ SQLite: {e}")
            return False
    
    def _backup_postgresql(self, temp_dir: Path) -> bool:
        """
        نسخ قاعدة بيانات PostgreSQL باستخدام pg_dump
        
        Args:
            temp_dir: المجلد المؤقت
        
        Returns:
            bool: True إذا نجح النسخ
        """
        # التحقق من وجود pg_dump
        if shutil.which('pg_dump') is None:
            self.logger.warning("pg_dump غير موجود - تخطي نسخ PostgreSQL")
            print(f"  {Colors.WARNING}⚠{Colors.ENDC}  pg_dump غير متوفر")
            return False
        
        # استخراج معلومات الاتصال من DATABASE_URI
        db_uri = self.config.DATABASE_URI
        dump_file = temp_dir / 'database_postgresql.sql'
        
        try:
            # استخدام DATABASE_URI كاملاً
            env = os.environ.copy()
            
            # pg_dump يدعم DATABASE_URL مباشرة
            result = subprocess.run(
                ['pg_dump', db_uri],
                stdout=open(dump_file, 'w'),
                stderr=subprocess.PIPE,
                env=env,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info(f"تم نسخ PostgreSQL بنجاح")
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} تم نسخ قاعدة بيانات PostgreSQL")
                return True
            else:
                self.logger.error(f"فشل pg_dump: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("انتهت مهلة pg_dump (5 دقائق)")
            return False
        except Exception as e:
            self.logger.error(f"فشل نسخ PostgreSQL: {e}")
            return False
    
    def _backup_mysql(self, temp_dir: Path) -> bool:
        """
        نسخ قاعدة بيانات MySQL باستخدام mysqldump
        
        Args:
            temp_dir: المجلد المؤقت
        
        Returns:
            bool: True إذا نجح النسخ
        """
        # التحقق من وجود mysqldump
        if shutil.which('mysqldump') is None:
            self.logger.warning("mysqldump غير موجود - تخطي نسخ MySQL")
            print(f"  {Colors.WARNING}⚠{Colors.ENDC}  mysqldump غير متوفر")
            return False
        
        # استخراج معلومات الاتصال
        db_uri = self.config.DATABASE_URI
        dump_file = temp_dir / 'database_mysql.sql'
        
        # تحليل URI (مثال: mysql+pymysql://user:pass@host:port/dbname)
        match = re.search(r'mysql\+?[^:]*://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_uri)
        
        if not match:
            self.logger.error(f"لا يمكن تحليل MySQL URI: {db_uri}")
            return False
        
        user, password, host, port, database = match.groups()
        
        try:
            cmd = [
                'mysqldump',
                f'--host={host}',
                f'--port={port}',
                f'--user={user}',
                f'--password={password}',
                database
            ]
            
            result = subprocess.run(
                cmd,
                stdout=open(dump_file, 'w'),
                stderr=subprocess.PIPE,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info(f"تم نسخ MySQL بنجاح")
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} تم نسخ قاعدة بيانات MySQL")
                return True
            else:
                self.logger.error(f"فشل mysqldump: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("انتهت مهلة mysqldump (5 دقائق)")
            return False
        except Exception as e:
            self.logger.error(f"فشل نسخ MySQL: {e}")
            return False
    
    def _backup_files(self, temp_dir: Path) -> int:
        """
        نسخ الملفات والمجلدات الهامة
        
        Args:
            temp_dir: المجلد المؤقت
        
        Returns:
            int: عدد الملفات/المجلدات المنسوخة
        """
        print(f"\n{Colors.OKCYAN}📂 نسخ الملفات والمجلدات...{Colors.ENDC}")
        
        copied_count = 0
        
        for item in self.backup_items:
            source_path = Path(item)
            
            if not source_path.exists():
                self.logger.debug(f"العنصر غير موجود: {item}")
                continue
            
            # تحديد المسار الوجهة
            dest_path = temp_dir / item
            
            try:
                if source_path.is_dir():
                    # نسخ مجلد
                    shutil.copytree(source_path, dest_path, 
                                   ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '*.tmp'))
                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {item} (مجلد)")
                    self.logger.info(f"تم نسخ المجلد: {item}")
                else:
                    # نسخ ملف
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # للـ .env نسخ نسخة آمنة (إخفاء كلمات المرور)
                    if item == '.env':
                        self._copy_safe_env(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                    
                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {item}")
                    self.logger.info(f"تم نسخ الملف: {item}")
                
                copied_count += 1
                
            except Exception as e:
                self.logger.error(f"فشل نسخ {item}: {e}")
                print(f"  {Colors.FAIL}✗{Colors.ENDC} {item} - خطأ: {e}")
        
        return copied_count
    
    def _copy_safe_env(self, source: Path, dest: Path):
        """
        نسخ ملف .env بشكل آمن (إخفاء كلمات المرور)
        
        Args:
            source: الملف المصدر
            dest: الملف الوجهة
        """
        sensitive_keys = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API_KEY']
        
        with open(source, 'r', encoding='utf-8') as f_in:
            with open(dest, 'w', encoding='utf-8') as f_out:
                for line in f_in:
                    # إذا كانت السطر يحتوي على مفتاح حساس، استبدل القيمة
                    if any(key in line.upper() for key in sensitive_keys):
                        if '=' in line:
                            key_part = line.split('=')[0]
                            f_out.write(f"{key_part}=***HIDDEN***\n")
                            continue
                    
                    f_out.write(line)
        
        self.logger.info("تم نسخ .env بشكل آمن (تم إخفاء القيم الحساسة)")
    
    def _create_tarball(self, source_dir: Path, output_file: Path):
        """
        إنشاء ملف tar.gz مضغوط
        
        Args:
            source_dir: المجلد المصدر
            output_file: ملف الإخراج
        """
        with tarfile.open(output_file, 'w:gz') as tar:
            tar.add(source_dir, arcname='backup')
        
        self.logger.info(f"تم إنشاء tarball: {output_file}")
    
    def _cleanup_old_backups(self):
        """تنظيف النسخ الاحتياطية القديمة"""
        backups = self.list_backups()
        
        if len(backups) > self.retention:
            to_delete = backups[self.retention:]
            
            print(f"\n{Colors.WARNING}🗑️  تنظيف النسخ القديمة (الاحتفاظ بـ {self.retention} نسخ)...{Colors.ENDC}")
            
            for backup in to_delete:
                try:
                    backup_path = Path(backup['path'])
                    info_path = backup_path.with_suffix('.tar.gz.info')
                    
                    backup_path.unlink()
                    if info_path.exists():
                        info_path.unlink()
                    
                    print(f"  {Colors.WARNING}✓{Colors.ENDC} حذف: {backup['name']}")
                    self.logger.info(f"تم حذف نسخة قديمة: {backup['name']}")
                    
                except Exception as e:
                    self.logger.error(f"فشل حذف {backup['name']}: {e}")
    
    def list_backups(self) -> List[Dict]:
        """
        قائمة بجميع النسخ الاحتياطية
        
        Returns:
            List[Dict]: قائمة النسخ الاحتياطية (مرتبة من الأحدث للأقدم)
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob('backup_*.tar.gz'), reverse=True):
            info_file = backup_file.with_suffix('.tar.gz.info')
            
            backup_info = {
                'name': backup_file.name,
                'path': str(backup_file),
                'size': format_size(backup_file.stat().st_size),
                'size_bytes': backup_file.stat().st_size,
                'created': datetime.fromtimestamp(backup_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'md5': None,
                'environment': None,
                'database': None
            }
            
            # قراءة معلومات إضافية من ملف .info
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('MD5:'):
                            backup_info['md5'] = line.split(':', 1)[1].strip()
                        elif line.startswith('Environment:'):
                            backup_info['environment'] = line.split(':', 1)[1].strip()
                        elif line.startswith('Database Type:'):
                            backup_info['database'] = line.split(':', 1)[1].strip()
            
            backups.append(backup_info)
        
        return backups
    
    def display_backups(self):
        """عرض قائمة النسخ الاحتياطية"""
        backups = self.list_backups()
        
        if not backups:
            print(f"\n{Colors.WARNING}⚠️  لا توجد نسخ احتياطية{Colors.ENDC}\n")
            return
        
        print(f"\n{Colors.HEADER}{'=' * 100}{Colors.ENDC}")
        print(f"{Colors.BOLD}📋 قائمة النسخ الاحتياطية - Backup List{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 100}{Colors.ENDC}\n")
        
        for i, backup in enumerate(backups, 1):
            print(f"{Colors.BOLD}{i}. {backup['name']}{Colors.ENDC}")
            print(f"   📅 التاريخ: {backup['created']}")
            print(f"   📊 الحجم: {backup['size']}")
            if backup['environment']:
                print(f"   🌍 البيئة: {backup['environment']}")
            if backup['database']:
                print(f"   💾 قاعدة البيانات: {backup['database']}")
            if backup['md5']:
                print(f"   🔐 MD5: {backup['md5']}")
            print()
        
        total_size = sum(b['size_bytes'] for b in backups)
        print(f"{Colors.HEADER}{'=' * 100}{Colors.ENDC}")
        print(f"📊 إجمالي: {len(backups)} نسخة احتياطية | الحجم الكلي: {format_size(total_size)}")
        print(f"{Colors.HEADER}{'=' * 100}{Colors.ENDC}\n")
    
    def cleanup_all(self):
        """تنظيف النسخ القديمة يدوياً"""
        backups = self.list_backups()
        
        if len(backups) <= self.retention:
            print(f"\n{Colors.OKGREEN}✅ لا توجد نسخ قديمة للحذف{Colors.ENDC}")
            print(f"   النسخ الحالية: {len(backups)} | الحد الأقصى: {self.retention}\n")
            return
        
        to_delete = backups[self.retention:]
        
        print(f"\n{Colors.WARNING}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.WARNING}🗑️  سيتم حذف {len(to_delete)} نسخة قديمة{Colors.ENDC}")
        print(f"{Colors.WARNING}{'=' * 70}{Colors.ENDC}\n")
        
        for backup in to_delete:
            print(f"  - {backup['name']} ({backup['size']}) - {backup['created']}")
        
        confirm = input(f"\n{Colors.BOLD}هل تريد المتابعة؟ (yes/no): {Colors.ENDC}").lower()
        
        if confirm in ['yes', 'y', 'نعم']:
            self._cleanup_old_backups()
            print(f"\n{Colors.OKGREEN}✅ تم التنظيف بنجاح{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.WARNING}❌ تم الإلغاء{Colors.ENDC}\n")
    
    def restore_backup(self, backup_file: str):
        """
        استرجاع نسخة احتياطية
        
        Args:
            backup_file: مسار ملف النسخة الاحتياطية
        """
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            print(f"{Colors.FAIL}❌ الملف غير موجود: {backup_file}{Colors.ENDC}")
            return
        
        print(f"\n{Colors.WARNING}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.WARNING}⚠️  تحذير: استرجاع النسخة الاحتياطية{Colors.ENDC}")
        print(f"{Colors.WARNING}{'=' * 70}{Colors.ENDC}")
        print(f"\nهذه العملية ستستبدل البيانات الحالية!")
        print(f"الملف: {backup_path.name}\n")
        
        confirm = input(f"{Colors.BOLD}هل تريد المتابعة؟ (yes/no): {Colors.ENDC}").lower()
        
        if confirm not in ['yes', 'y', 'نعم']:
            print(f"\n{Colors.WARNING}❌ تم الإلغاء{Colors.ENDC}\n")
            return
        
        try:
            # التحقق من MD5
            info_file = backup_path.with_suffix('.tar.gz.info')
            if info_file.exists():
                with open(info_file, 'r') as f:
                    for line in f:
                        if line.startswith('MD5:'):
                            expected_md5 = line.split(':', 1)[1].strip()
                            actual_md5 = calculate_md5(str(backup_path))
                            
                            if expected_md5 != actual_md5:
                                print(f"{Colors.FAIL}❌ فشل التحقق من MD5!{Colors.ENDC}")
                                print(f"   المتوقع: {expected_md5}")
                                print(f"   الفعلي: {actual_md5}")
                                return
                            
                            print(f"{Colors.OKGREEN}✓ تم التحقق من MD5 بنجاح{Colors.ENDC}")
            
            # استخراج الملفات
            restore_dir = Path('restore_temp')
            restore_dir.mkdir(exist_ok=True)
            
            print(f"\n{Colors.OKCYAN}📦 جاري استخراج الملفات...{Colors.ENDC}")
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(restore_dir)
            
            print(f"{Colors.OKGREEN}✅ تم الاسترجاع بنجاح!{Colors.ENDC}")
            print(f"📁 الملفات المستخرجة في: {restore_dir}\n")
            print(f"{Colors.WARNING}⚠️  يجب نقل الملفات يدوياً إلى المواقع المناسبة{Colors.ENDC}\n")
            
            self.logger.info(f"تم استرجاع النسخة: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"فشل الاسترجاع: {e}")
            print(f"\n{Colors.FAIL}❌ خطأ في الاسترجاع: {e}{Colors.ENDC}\n")


# ==================== CLI Interface ====================
def main():
    """الواجهة الرئيسية لسطر الأوامر - Main CLI Interface"""
    
    parser = argparse.ArgumentParser(
        description='نظام النسخ الاحتياطي الشامل - Comprehensive Backup Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  python backups/backup_manager.py                # إنشاء نسخة احتياطية جديدة
  python backups/backup_manager.py --list         # عرض قائمة النسخ
  python backups/backup_manager.py --cleanup      # تنظيف النسخ القديمة
  python backups/backup_manager.py --keep 10      # تغيير عدد النسخ المحفوظة
  python backups/backup_manager.py --restore FILE # استرجاع نسخة احتياطية
        """
    )
    
    parser.add_argument('--list', action='store_true',
                       help='عرض قائمة النسخ الاحتياطية')
    parser.add_argument('--cleanup', action='store_true',
                       help='تنظيف النسخ القديمة')
    parser.add_argument('--keep', type=int, metavar='N',
                       help='تغيير عدد النسخ المحفوظة (الافتراضي: 7)')
    parser.add_argument('--restore', type=str, metavar='FILE',
                       help='استرجاع نسخة احتياطية من ملف')
    parser.add_argument('--no-color', action='store_true',
                       help='تعطيل الألوان في الإخراج')
    
    args = parser.parse_args()
    
    # تعطيل الألوان إذا طُلب ذلك
    if args.no_color:
        Colors.disable()
    
    # إنشاء BackupManager
    retention = args.keep if args.keep else 7
    manager = BackupManager(retention=retention)
    
    # تنفيذ الأمر المطلوب
    if args.list:
        manager.display_backups()
    elif args.cleanup:
        manager.cleanup_all()
    elif args.restore:
        manager.restore_backup(args.restore)
    elif args.keep:
        print(f"\n{Colors.OKGREEN}✅ تم تعيين عدد النسخ المحفوظة إلى: {args.keep}{Colors.ENDC}\n")
        manager.display_backups()
    else:
        # الافتراضي: إنشاء نسخة احتياطية جديدة
        manager.create_backup()


if __name__ == '__main__':
    main()
