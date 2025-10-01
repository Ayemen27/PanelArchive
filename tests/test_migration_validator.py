#!/usr/bin/env python
# coding: utf-8
"""
Comprehensive Tests for Migration Validator
اختبارات شاملة لنظام التحقق من صحة Migrations

This file contains comprehensive tests for all validation functions
in migration_validator.py with 100% coverage.

يحتوي هذا الملف على اختبارات شاملة لجميع دوال التحقق
في migration_validator.py مع تغطية 100%.
"""

import os
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from migrations.migration_validator import (
    validate_migration_file,
    validate_upgrade_downgrade,
    validate_revision_format,
    check_sql_injection,
    validate_batch_mode,
    validate_all_migrations,
)


@pytest.fixture
def temp_migration_file(tmp_path):
    """
    Fixture to create a temporary migration file
    إنشاء ملف migration مؤقت للاختبار
    
    Returns:
        Function that creates a migration file with given content
    """
    def _create_file(content: str, filename: str = "test_migration.py"):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return str(file_path)
    
    return _create_file


@pytest.fixture
def temp_migrations_dir(tmp_path):
    """
    Fixture to create a temporary migrations directory
    إنشاء مجلد migrations مؤقت للاختبار
    
    Returns:
        Function that creates a migrations directory with files
    """
    def _create_dir(files: dict):
        migrations_dir = tmp_path / "versions"
        migrations_dir.mkdir(exist_ok=True)
        
        for filename, content in files.items():
            file_path = migrations_dir / filename
            file_path.write_text(content, encoding='utf-8')
        
        return str(migrations_dir)
    
    return _create_dir


@pytest.fixture
def valid_migration_content():
    """
    Valid migration file content for testing
    محتوى migration صحيح للاختبار
    """
    return '''"""Test migration

Revision ID: 002_test
Revises: 001_initial_baseline
Create Date: 2025-09-30

Test migration for validation
"""
from alembic import op
import sqlalchemy as sa

revision = '002_test'
down_revision = '001_initial_baseline'

def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(255)))

def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('email')
'''


class TestValidateMigrationFile:
    """
    Tests for validate_migration_file()
    اختبارات لدالة validate_migration_file()
    """
    
    def test_valid_migration_file(self, temp_migration_file, valid_migration_content):
        """
        Test: ✅ Valid migration file (no errors)
        اختبار: ملف migration صحيح بدون أخطاء
        """
        file_path = temp_migration_file(valid_migration_content)
        errors = validate_migration_file(file_path)
        
        assert errors == [], f"Expected no errors, got: {errors}"
    
    def test_file_not_found(self):
        """
        Test: ❌ File not found
        اختبار: الملف غير موجود
        """
        errors = validate_migration_file("/nonexistent/path/file.py")
        
        assert len(errors) > 0
        assert any("does not exist" in error or "غير موجود" in error for error in errors)
    
    def test_invalid_python_syntax(self, temp_migration_file):
        """
        Test: ❌ Invalid Python syntax
        اختبار: خطأ في بنية Python
        """
        content = '''
from alembic import op

revision = '003_bad'
down_revision = None

def upgrade() -> None:
    if True
        pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("syntax" in error.lower() for error in errors)
    
    def test_missing_alembic_import(self, temp_migration_file):
        """
        Test: ❌ Missing alembic import
        اختبار: import من alembic مفقود
        """
        content = '''"""Test migration

Revision ID: 004_test
"""
import sqlalchemy as sa

revision = '004_test'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("alembic" in error.lower() for error in errors)
    
    def test_missing_sqlalchemy_import(self, temp_migration_file):
        """
        Test: ❌ Missing sqlalchemy import
        اختبار: import من sqlalchemy مفقود
        """
        content = '''"""Test migration

Revision ID: 005_test
"""
from alembic import op

revision = '005_test'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("sqlalchemy" in error.lower() for error in errors)
    
    def test_missing_revision_variable(self, temp_migration_file):
        """
        Test: ❌ Missing revision variable
        اختبار: متغير revision مفقود
        """
        content = '''"""Test migration"""
from alembic import op
import sqlalchemy as sa

down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("revision" in error.lower() and "missing" in error.lower() for error in errors)
    
    def test_missing_down_revision_variable(self, temp_migration_file):
        """
        Test: ❌ Missing down_revision variable
        اختبار: متغير down_revision مفقود
        """
        content = '''"""Test migration"""
from alembic import op
import sqlalchemy as sa

revision = '006_test'

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("down_revision" in error.lower() for error in errors)
    
    def test_missing_docstring(self, temp_migration_file):
        """
        Test: ❌ Missing docstring
        اختبار: وثائق الملف مفقودة
        """
        content = '''from alembic import op
import sqlalchemy as sa

revision = '007_test'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("docstring" in error.lower() for error in errors)
    
    def test_insufficient_docstring(self, temp_migration_file):
        """
        Test: ❌ Docstring too short
        اختبار: وثائق الملف قصيرة جداً
        """
        content = '''"""Short"""
from alembic import op
import sqlalchemy as sa

revision = '008_test'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("docstring" in error.lower() for error in errors)
    
    def test_docstring_without_revision_id(self, temp_migration_file):
        """
        Test: ❌ Docstring missing 'Revision ID:'
        اختبار: وثائق الملف لا تحتوي على 'Revision ID:'
        """
        content = '''"""Test migration without proper format

This is a test migration
"""
from alembic import op
import sqlalchemy as sa

revision = '009_test'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        assert len(errors) > 0
        assert any("Revision ID" in error for error in errors)


class TestValidateUpgradeDowngrade:
    """
    Tests for validate_upgrade_downgrade()
    اختبارات لدالة validate_upgrade_downgrade()
    """
    
    def test_valid_upgrade_downgrade_functions(self, temp_migration_file, valid_migration_content):
        """
        Test: ✅ Valid upgrade/downgrade functions
        اختبار: دالتي upgrade و downgrade صحيحتان
        """
        file_path = temp_migration_file(valid_migration_content)
        errors = validate_upgrade_downgrade(file_path)
        
        assert errors == [], f"Expected no errors, got: {errors}"
    
    def test_missing_upgrade_function(self, temp_migration_file):
        """
        Test: ❌ Missing upgrade function
        اختبار: دالة upgrade مفقودة
        """
        content = '''"""Test migration

Revision ID: 010_test
"""
from alembic import op
import sqlalchemy as sa

revision = '010_test'
down_revision = None

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_upgrade_downgrade(file_path)
        
        assert len(errors) > 0
        assert any("upgrade" in error.lower() and "missing" in error.lower() for error in errors)
    
    def test_missing_downgrade_function(self, temp_migration_file):
        """
        Test: ❌ Missing downgrade function
        اختبار: دالة downgrade مفقودة
        """
        content = '''"""Test migration

Revision ID: 011_test
"""
from alembic import op
import sqlalchemy as sa

revision = '011_test'
down_revision = None

def upgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_upgrade_downgrade(file_path)
        
        assert len(errors) > 0
        assert any("downgrade" in error.lower() and "missing" in error.lower() for error in errors)
    
    def test_upgrade_with_pass_only(self, temp_migration_file):
        """
        Test: ✅ upgrade() with only pass is acceptable for baseline migrations
        اختبار: upgrade() مع pass فقط مقبول للـ baseline migrations
        """
        content = '''"""Test migration

Revision ID: 012_test
"""
from alembic import op
import sqlalchemy as sa

revision = '012_test'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_upgrade_downgrade(file_path)
        
        assert errors == []
    
    def test_file_not_found_upgrade_downgrade(self):
        """
        Test: ❌ File not found for upgrade/downgrade validation
        اختبار: الملف غير موجود عند التحقق من upgrade/downgrade
        """
        errors = validate_upgrade_downgrade("/nonexistent/path/file.py")
        
        assert len(errors) > 0
        assert any("does not exist" in error or "غير موجود" in error for error in errors)


class TestValidateRevisionFormat:
    """
    Tests for validate_revision_format()
    اختبارات لدالة validate_revision_format()
    """
    
    def test_valid_revision_format(self, temp_migration_file, valid_migration_content):
        """
        Test: ✅ Valid revision format
        اختبار: معرف revision صحيح
        """
        file_path = temp_migration_file(valid_migration_content)
        errors = validate_revision_format(file_path)
        
        assert errors == [], f"Expected no errors, got: {errors}"
    
    def test_missing_revision(self, temp_migration_file):
        """
        Test: ❌ Missing revision variable
        اختبار: متغير revision مفقود
        """
        content = '''"""Test migration

Revision ID: test
"""
from alembic import op
import sqlalchemy as sa

down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_revision_format(file_path)
        
        assert len(errors) > 0
        assert any("revision" in error.lower() and ("not found" in error.lower() or "غير موجود" in error.lower()) for error in errors)
    
    def test_empty_revision(self, temp_migration_file):
        """
        Test: ❌ Empty revision ID
        اختبار: معرف revision فارغ
        """
        content = '''"""Test migration

Revision ID: 
"""
from alembic import op
import sqlalchemy as sa

revision = ''
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_revision_format(file_path)
        
        assert len(errors) > 0
        # Empty string is falsy, so it triggers "not found or invalid" error
        assert any("not found" in error.lower() or "invalid" in error.lower() or 
                   "غير موجود" in error.lower() or "غير صحيح" in error.lower() for error in errors)
    
    def test_short_revision(self, temp_migration_file):
        """
        Test: ❌ Revision ID too short
        اختبار: معرف revision قصير جداً
        """
        content = '''"""Test migration

Revision ID: 01
"""
from alembic import op
import sqlalchemy as sa

revision = '01'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_revision_format(file_path)
        
        assert len(errors) > 0
        assert any("short" in error.lower() or "قصير" in error.lower() for error in errors)
    
    def test_duplicate_revision_ids(self, temp_migration_file):
        """
        Test: ❌ Duplicate revision IDs
        اختبار: معرفات revision مكررة
        """
        content = '''"""Test migration

Revision ID: 013_test
"""
from alembic import op
import sqlalchemy as sa

revision = '013_test'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        existing_revisions = {'013_test', '014_test'}
        errors = validate_revision_format(file_path, existing_revisions)
        
        assert len(errors) > 0
        assert any("not unique" in error.lower() or "غير فريد" in error.lower() for error in errors)
    
    def test_file_not_found_revision(self):
        """
        Test: ❌ File not found for revision validation
        اختبار: الملف غير موجود عند التحقق من revision
        """
        errors = validate_revision_format("/nonexistent/path/file.py")
        
        assert len(errors) > 0
        assert any("does not exist" in error or "غير موجود" in error for error in errors)


class TestCheckSqlInjection:
    """
    Tests for check_sql_injection()
    اختبارات لدالة check_sql_injection()
    """
    
    def test_safe_parameterized_queries(self, temp_migration_file):
        """
        Test: ✅ Safe parameterized queries
        اختبار: استعلامات آمنة مع parameterized queries
        """
        content = '''"""Test migration

Revision ID: 015_test
"""
from alembic import op
import sqlalchemy as sa

revision = '015_test'
down_revision = None

def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(255)))

def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('email')
'''
        file_path = temp_migration_file(content)
        warnings = check_sql_injection(file_path)
        
        assert warnings == [], f"Expected no warnings, got: {warnings}"
    
    def test_string_concatenation_in_sql(self, temp_migration_file):
        """
        Test: ⚠️ String concatenation in SQL
        اختبار: دمج النصوص في SQL
        """
        content = '''"""Test migration

Revision ID: 016_test
"""
from alembic import op

revision = '016_test'
down_revision = None

def upgrade() -> None:
    table_name = 'users'
    op.execute("SELECT * FROM " + table_name)

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        warnings = check_sql_injection(file_path)
        
        assert len(warnings) > 0
        assert any("concatenation" in warning.lower() or "دمج" in warning.lower() for warning in warnings)
    
    def test_format_in_sql(self, temp_migration_file):
        """
        Test: ⚠️ .format() in SQL
        اختبار: استخدام .format() في SQL
        """
        content = '''"""Test migration

Revision ID: 017_test
"""
from alembic import op

revision = '017_test'
down_revision = None

def upgrade() -> None:
    table_name = 'users'
    op.execute("SELECT * FROM {0}".format(table_name))

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        warnings = check_sql_injection(file_path)
        
        assert len(warnings) > 0
        assert any("format" in warning.lower() for warning in warnings)
    
    def test_fstring_in_sql(self, temp_migration_file):
        """
        Test: ⚠️ f-strings in SQL
        اختبار: استخدام f-strings في SQL
        """
        content = '''"""Test migration

Revision ID: 018_test
"""
from alembic import op

revision = '018_test'
down_revision = None

def upgrade() -> None:
    table_name = 'users'
    op.execute(f"ALTER TABLE {table_name} ADD COLUMN email TEXT")

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        warnings = check_sql_injection(file_path)
        
        assert len(warnings) > 0
        assert any("f-string" in warning.lower() or "injection" in warning.lower() for warning in warnings)
    
    def test_file_not_found_sql_injection(self):
        """
        Test: ❌ File not found for SQL injection check
        اختبار: الملف غير موجود عند التحقق من SQL injection
        """
        warnings = check_sql_injection("/nonexistent/path/file.py")
        
        assert len(warnings) > 0
        assert any("does not exist" in warning or "غير موجود" in warning for warning in warnings)


class TestValidateBatchMode:
    """
    Tests for validate_batch_mode()
    اختبارات لدالة validate_batch_mode()
    """
    
    def test_correct_batch_alter_table_usage(self, temp_migration_file, valid_migration_content):
        """
        Test: ✅ Correct batch_alter_table usage
        اختبار: استخدام batch_alter_table بشكل صحيح
        """
        file_path = temp_migration_file(valid_migration_content)
        warnings = validate_batch_mode(file_path)
        
        assert warnings == [], f"Expected no warnings, got: {warnings}"
    
    def test_direct_alter_table_via_execute(self, temp_migration_file):
        """
        Test: ⚠️ Direct ALTER TABLE via op.execute()
        اختبار: استخدام ALTER TABLE مباشرة عبر op.execute()
        """
        content = '''"""Test migration

Revision ID: 019_test
"""
from alembic import op

revision = '019_test'
down_revision = None

def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN email TEXT")

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        warnings = validate_batch_mode(file_path)
        
        assert len(warnings) > 0
        assert any("ALTER TABLE" in warning for warning in warnings)
    
    def test_alter_column_without_batch(self, temp_migration_file):
        """
        Test: ⚠️ op.alter_column() without batch mode
        اختبار: استخدام op.alter_column() بدون batch mode
        """
        content = '''"""Test migration

Revision ID: 020_test
"""
from alembic import op

revision = '020_test'
down_revision = None

def upgrade() -> None:
    op.alter_column('users', 'name', new_column_name='full_name')

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        warnings = validate_batch_mode(file_path)
        
        assert len(warnings) > 0
        assert any("alter_column" in warning.lower() for warning in warnings)
    
    def test_drop_column_without_batch(self, temp_migration_file):
        """
        Test: ⚠️ op.drop_column() without batch mode
        اختبار: استخدام op.drop_column() بدون batch mode
        """
        content = '''"""Test migration

Revision ID: 021_test
"""
from alembic import op

revision = '021_test'
down_revision = None

def upgrade() -> None:
    op.drop_column('users', 'old_field')

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        warnings = validate_batch_mode(file_path)
        
        assert len(warnings) > 0
        assert any("drop_column" in warning.lower() for warning in warnings)
    
    def test_file_not_found_batch_mode(self):
        """
        Test: ❌ File not found for batch mode validation
        اختبار: الملف غير موجود عند التحقق من batch mode
        """
        warnings = validate_batch_mode("/nonexistent/path/file.py")
        
        assert len(warnings) > 0
        assert any("does not exist" in warning or "غير موجود" in warning for warning in warnings)


class TestValidateAllMigrations:
    """
    Tests for validate_all_migrations()
    اختبارات لدالة validate_all_migrations()
    """
    
    def test_directory_with_valid_migrations(self, temp_migrations_dir, valid_migration_content, capsys):
        """
        Test: ✅ Directory with valid migrations
        اختبار: مجلد يحتوي على migrations صحيحة
        """
        files = {
            "001_initial.py": '''"""Initial migration

Revision ID: 001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
''',
            "002_add_email.py": '''"""Add email column

Revision ID: 002_add_email
"""
from alembic import op
import sqlalchemy as sa

revision = '002_add_email'
down_revision = '001_initial'

def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(255)))

def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('email')
''',
        }
        
        migrations_dir = temp_migrations_dir(files)
        results = validate_all_migrations(migrations_dir)
        
        assert results['total_files'] == 2
        assert results['valid_files'] == 2
        assert results['files_with_errors'] == 0
    
    def test_directory_not_found(self, capsys):
        """
        Test: ❌ Directory not found
        اختبار: المجلد غير موجود
        """
        results = validate_all_migrations("/nonexistent/directory")
        
        assert 'error' in results
        assert results['error'] == 'Directory not found'
    
    def test_empty_directory(self, tmp_path, capsys):
        """
        Test: ℹ️ Empty directory
        اختبار: مجلد فارغ
        """
        empty_dir = tmp_path / "empty_versions"
        empty_dir.mkdir()
        
        results = validate_all_migrations(str(empty_dir))
        
        assert results['total'] == 0
        assert results['files'] == []
    
    def test_mixed_valid_invalid_migrations(self, temp_migrations_dir, capsys):
        """
        Test: ⚠️ Mixed valid/invalid migrations
        اختبار: خليط من migrations صحيحة وغير صحيحة
        """
        files = {
            "001_valid.py": '''"""Valid migration

Revision ID: 001_valid
"""
from alembic import op
import sqlalchemy as sa

revision = '001_valid'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
''',
            "002_invalid.py": '''"""Invalid migration - missing imports

Revision ID: 002_invalid
"""

revision = '002_invalid'
down_revision = '001_valid'

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
''',
            "003_sql_injection.py": '''"""Migration with SQL injection risk

Revision ID: 003_sql_injection
"""
from alembic import op
import sqlalchemy as sa

revision = '003_sql_injection'
down_revision = '002_invalid'

def upgrade() -> None:
    table_name = 'users'
    op.execute(f"ALTER TABLE {table_name} ADD COLUMN email TEXT")

def downgrade() -> None:
    pass
''',
        }
        
        migrations_dir = temp_migrations_dir(files)
        results = validate_all_migrations(migrations_dir)
        
        assert results['total_files'] == 3
        assert results['files_with_errors'] > 0
        assert results['files_with_warnings'] > 0
    
    def test_migration_with_only_warnings(self, temp_migrations_dir, capsys):
        """
        Test: ⚠️ Migration with only warnings (no errors)
        اختبار: migration مع تحذيرات فقط (بدون أخطاء)
        """
        files = {
            "001_warnings.py": '''"""Migration with warnings

Revision ID: 001_warnings
"""
from alembic import op
import sqlalchemy as sa

revision = '001_warnings'
down_revision = None

def upgrade() -> None:
    op.alter_column('users', 'name', new_column_name='full_name')

def downgrade() -> None:
    pass
''',
        }
        
        migrations_dir = temp_migrations_dir(files)
        results = validate_all_migrations(migrations_dir)
        
        assert results['total_files'] == 1
        assert results['files_with_errors'] == 0
        assert results['files_with_warnings'] == 1


class TestEdgeCases:
    """
    Additional edge case tests
    اختبارات إضافية للحالات الحدية
    """
    
    def test_migration_with_multiple_sql_injection_patterns(self, temp_migration_file):
        """
        Test: Multiple SQL injection patterns in one file
        اختبار: أنماط SQL injection متعددة في ملف واحد
        """
        content = '''"""Test migration with multiple risks

Revision ID: 022_multi_risk
"""
from alembic import op

revision = '022_multi_risk'
down_revision = None

def upgrade() -> None:
    table = 'users'
    column = 'email'
    op.execute("SELECT * FROM " + table)
    op.execute("ALTER TABLE {0} ADD COLUMN {1} TEXT".format(table, column))
    op.execute(f"UPDATE {table} SET {column} = 'default'")

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        warnings = check_sql_injection(file_path)
        
        assert len(warnings) >= 3
    
    def test_migration_with_sqlalchemy_dialect_imports(self, temp_migration_file):
        """
        Test: Migration with various SQLAlchemy imports (valid)
        اختبار: migration مع أنواع مختلفة من imports SQLAlchemy (صحيح)
        """
        content = '''"""Test migration with dialect imports

Revision ID: 023_dialects
"""
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects import mysql
import sqlalchemy as sa

revision = '023_dialects'
down_revision = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        # This is a valid migration, SQLAlchemy dialect imports are recognized
        assert errors == [], f"Expected no errors for valid dialect imports, got: {errors}"
    
    def test_non_python_file(self, tmp_path):
        """
        Test: Non-Python file validation
        اختبار: التحقق من ملف غير Python
        """
        file_path = tmp_path / "not_python.txt"
        file_path.write_text("This is not a Python file")
        
        errors = validate_migration_file(str(file_path))
        
        assert len(errors) > 0
        assert any("not a Python file" in error for error in errors)
    
    def test_migration_with_complex_down_revision(self, temp_migration_file):
        """
        Test: Migration with tuple down_revision (multiple parents) - valid
        اختبار: migration مع down_revision معقد (آباء متعددة) - صحيح
        """
        content = '''"""Test migration with multiple parents

Revision ID: 024_merge
"""
from alembic import op
import sqlalchemy as sa

revision = '024_merge'
down_revision = ('023_dialects', '022_multi_risk')

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''
        file_path = temp_migration_file(content)
        errors = validate_migration_file(file_path)
        
        # This is a valid migration structure for merge migrations
        assert errors == [], f"Expected no errors for merge migration, got: {errors}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
