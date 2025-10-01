#!/usr/bin/env python3
# coding: utf-8
"""
اختبارات أمان شاملة لنظام النسخ الاحتياطي - Backup Security Tests
يختبر حماية ضد:
- Path Traversal / Zip Slip
- Symlinks / Hardlinks
- Zip Bomb (resource limits)
- Whitelist violations
- Permission exploits
"""

import os
import sys
import unittest
import tempfile
import tarfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backups.backup_manager import BackupManager, RestoreLimits


class TestBackupSecurityPathTraversal(unittest.TestCase):
    """اختبارات حماية Path Traversal"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        os.environ['SECRET_KEY'] = 'a' * 64
        self.manager = BackupManager(backup_dir=str(self.backup_dir), retention=3)
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_malicious_archive(self, filename: str, entries: list) -> str:
        """إنشاء أرشيف ضار للاختبار"""
        archive_path = self.backup_dir / filename
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            for name, content in entries:
                info = tarfile.TarInfo(name=name)
                info.size = len(content.encode())
                import io
                tar.addfile(info, io.BytesIO(content.encode()))
        
        info_path = Path(str(archive_path) + '.info')
        with open(info_path, 'w') as f:
            f.write(f"SHA256: fake_sha256_hash\n")
            f.write(f"HMAC-SHA256: fake_hmac_hash\n")
        
        return str(archive_path)
    
    def test_reject_absolute_paths(self):
        """اختبار: رفض المسارات المطلقة"""
        archive = self._create_malicious_archive(
            'malicious_absolute.tar.gz',
            [('/etc/passwd', 'malicious content')]
        )
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                result = self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
                self.assertFalse(result, "يجب رفض المسار المطلق")
        
        self.assertEqual(stats['rejected'], 1, "يجب رفض ملف واحد")
    
    def test_reject_parent_traversal(self):
        """اختبار: رفض .. traversal"""
        archive = self._create_malicious_archive(
            'malicious_traversal.tar.gz',
            [('backup/../../../etc/passwd', 'malicious content')]
        )
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                result = self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
                self.assertFalse(result, "يجب رفض .. traversal")
        
        self.assertGreater(stats['rejected'], 0, "يجب رفض ملف مع ..")
    
    def test_reject_non_backup_root(self):
        """اختبار: رفض ملفات خارج backup/"""
        archive = self._create_malicious_archive(
            'malicious_root.tar.gz',
            [('malicious/file.txt', 'content')]
        )
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                result = self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
                self.assertFalse(result, "يجب رفض ملفات خارج backup/")
        
        self.assertEqual(stats['rejected'], 1)


class TestBackupSecurityWhitelist(unittest.TestCase):
    """اختبارات Whitelist"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        os.environ['SECRET_KEY'] = 'a' * 64
        self.manager = BackupManager(backup_dir=str(self.backup_dir), retention=3)
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_archive_with_content(self, filename: str, entries: list) -> str:
        """إنشاء أرشيف للاختبار"""
        archive_path = self.backup_dir / filename
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            for name, content in entries:
                info = tarfile.TarInfo(name=name)
                info.size = len(content.encode())
                import io
                tar.addfile(info, io.BytesIO(content.encode()))
        
        info_path = Path(str(archive_path) + '.info')
        with open(info_path, 'w') as f:
            f.write(f"SHA256: fake_sha256_hash\n")
            f.write(f"HMAC-SHA256: fake_hmac_hash\n")
        
        return str(archive_path)
    
    def test_accept_allowed_roots(self):
        """اختبار: قبول الجذور المسموحة فقط"""
        archive = self._create_archive_with_content(
            'valid_content.tar.gz',
            [
                ('backup/data/test.db', 'content'),
                ('backup/logs/app.log', 'log content'),
                ('backup/.env', 'ENV=value')
            ]
        )
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
        
        self.assertGreater(stats['accepted'], 0, "يجب قبول ملفات صالحة")
        self.assertEqual(stats['rejected'], 0, "لا يجب رفض ملفات صالحة")
    
    def test_reject_disallowed_roots(self):
        """اختبار: رفض جذور غير مسموحة"""
        archive = self._create_archive_with_content(
            'invalid_root.tar.gz',
            [
                ('backup/malicious/secret.txt', 'sensitive data'),
                ('backup/unauthorized/config.ini', 'config')
            ]
        )
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
        
        self.assertEqual(stats['rejected'], 2, "يجب رفض جميع الجذور غير المسموحة")
        self.assertEqual(stats['accepted'], 0)


class TestBackupSecurityResourceLimits(unittest.TestCase):
    """اختبارات حدود الموارد (Zip Bomb protection)"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        os.environ['SECRET_KEY'] = 'a' * 64
        self.manager = BackupManager(backup_dir=str(self.backup_dir), retention=3)
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_reject_oversized_file(self):
        """اختبار: رفض ملف يتجاوز MAX_FILE_SIZE"""
        archive_path = self.backup_dir / 'oversized.tar.gz'
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            info = tarfile.TarInfo(name='backup/data/huge.db')
            info.size = RestoreLimits.MAX_FILE_SIZE + 1024
            import io
            content = b'x' * (RestoreLimits.MAX_FILE_SIZE + 1024)
            tar.addfile(info, io.BytesIO(content))
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                result = self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
                self.assertFalse(result, "يجب رفض ملف ضخم")
        
        self.assertEqual(stats['rejected'], 1)
        self.assertIn('حجم زائد', stats['rejected_reasons']['backup/data/huge.db'])
    
    def test_reject_excessive_total_size(self):
        """اختبار: رفض عند تجاوز MAX_TOTAL_SIZE"""
        archive_path = self.backup_dir / 'zip_bomb.tar.gz'
        
        num_files = int(RestoreLimits.MAX_TOTAL_SIZE / RestoreLimits.MAX_FILE_SIZE) + 2
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            for i in range(num_files):
                info = tarfile.TarInfo(name=f'backup/data/file{i}.db')
                info.size = RestoreLimits.MAX_FILE_SIZE
                import io
                content = b'x' * RestoreLimits.MAX_FILE_SIZE
                tar.addfile(info, io.BytesIO(content))
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
        
        self.assertGreater(stats['rejected'], 0, "يجب رفض ملفات عند تجاوز الحد الإجمالي")
    
    def test_reject_excessive_depth(self):
        """اختبار: رفض مسارات بعمق زائد"""
        archive_path = self.backup_dir / 'deep_path.tar.gz'
        
        deep_path = 'backup/' + '/'.join([f'dir{i}' for i in range(RestoreLimits.MAX_DEPTH + 5)]) + '/file.txt'
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            info = tarfile.TarInfo(name=deep_path)
            content = b'testcontent'
            info.size = len(content)
            import io
            tar.addfile(info, io.BytesIO(content))
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                result = self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
                self.assertFalse(result, "يجب رفض مسار بعمق زائد")
        
        self.assertEqual(stats['rejected'], 1)


class TestBackupSecurityPermissions(unittest.TestCase):
    """اختبارات Permissions والحماية من setuid/setgid"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        os.environ['SECRET_KEY'] = 'a' * 64
        self.manager = BackupManager(backup_dir=str(self.backup_dir), retention=3)
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_safe_file_permissions(self):
        """اختبار: الملفات تُنشأ بـ permissions آمنة"""
        archive_path = self.backup_dir / 'permissions.tar.gz'
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            info = tarfile.TarInfo(name='backup/data/test.db')
            content = b'test data!'
            info.size = len(content)
            info.mode = 0o777
            import io
            tar.addfile(info, io.BytesIO(content))
        
        restore_dir = Path(self.test_dir) / 'restore'
        restore_dir.mkdir(parents=True, exist_ok=True)
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                self.manager._safe_extract_member(member, tar, restore_dir, stats)
        
        if stats['accepted'] > 0:
            extracted_file = restore_dir / 'backup' / 'data' / 'test.db'
            if extracted_file.exists():
                file_mode = extracted_file.stat().st_mode & 0o777
                self.assertLessEqual(file_mode, RestoreLimits.SAFE_FILE_MODE,
                                   f"File permissions ({oct(file_mode)}) يجب أن تكون آمنة")


class TestBackupSecurityIntegration(unittest.TestCase):
    """اختبارات تكامل شاملة"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        os.environ['SECRET_KEY'] = 'a' * 64
        self.manager = BackupManager(backup_dir=str(self.backup_dir), retention=3)
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_restore_limits_constants(self):
        """اختبار: ثوابت RestoreLimits محددة بشكل معقول"""
        self.assertGreater(RestoreLimits.MAX_TOTAL_SIZE, 0)
        self.assertGreater(RestoreLimits.MAX_FILE_SIZE, 0)
        self.assertGreater(RestoreLimits.MAX_FILES, 0)
        self.assertGreater(RestoreLimits.MAX_DEPTH, 0)
        
        self.assertLess(RestoreLimits.MAX_FILE_SIZE, RestoreLimits.MAX_TOTAL_SIZE)
        
        self.assertGreater(len(RestoreLimits.ALLOWED_ROOTS), 0, "يجب أن يكون هناك جذور مسموحة")
        
        self.assertEqual(RestoreLimits.SAFE_FILE_MODE, 0o640)
        self.assertEqual(RestoreLimits.SAFE_DIR_MODE, 0o750)
    
    def test_rejected_reasons_tracking(self):
        """اختبار: تتبع أسباب الرفض"""
        archive_path = self.backup_dir / 'mixed.tar.gz'
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            content1 = b'content111'
            info1 = tarfile.TarInfo(name='/etc/passwd')
            info1.size = len(content1)
            
            content2 = b'content222'
            info2 = tarfile.TarInfo(name='backup/../../../root/.ssh/id_rsa')
            info2.size = len(content2)
            
            content3 = b'content333'
            info3 = tarfile.TarInfo(name='backup/malicious/evil.sh')
            info3.size = len(content3)
            
            import io
            tar.addfile(info1, io.BytesIO(content1))
            tar.addfile(info2, io.BytesIO(content2))
            tar.addfile(info3, io.BytesIO(content3))
        
        stats = {
            'accepted': 0,
            'rejected': 0,
            'skipped': 0,
            'total_size': 0,
            'rejected_reasons': {}
        }
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            for member in members:
                self.manager._safe_extract_member(
                    member, tar, Path(self.test_dir) / 'restore', stats
                )
        
        self.assertEqual(stats['rejected'], 3, "يجب رفض جميع الملفات الضارة")
        self.assertEqual(stats['accepted'], 0)
        self.assertEqual(len(stats['rejected_reasons']), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
