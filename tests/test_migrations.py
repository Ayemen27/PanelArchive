# coding: utf-8
"""
اختبارات نظام Migrations
Tests for database migrations system
"""

import os
import sys
import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_migrations_directory_exists():
    """Test that migrations directory exists"""
    migrations_dir = Path('migrations')
    assert migrations_dir.exists(), "migrations directory should exist"
    assert migrations_dir.is_dir(), "migrations should be a directory"

def test_migrations_files_exist():
    """Test that essential migration files exist"""
    essential_files = [
        'migrations/env.py',
        'migrations/script.py.mako',
        'migrations/migrate.py',
        'migrations/README.md',
        'alembic.ini'
    ]
    
    for file_path in essential_files:
        assert Path(file_path).exists(), f"{file_path} should exist"

def test_alembic_config_valid():
    """Test that alembic.ini is valid"""
    alembic_ini = Path('alembic.ini')
    assert alembic_ini.exists()
    
    content = alembic_ini.read_text()
    assert '[alembic]' in content
    assert 'script_location = migrations' in content
    assert 'sqlalchemy.url' in content

def test_baseline_migration_exists():
    """Test that baseline migration exists"""
    baseline = Path('migrations/versions/001_initial_baseline.py')
    assert baseline.exists(), "Baseline migration should exist"
    
    content = baseline.read_text()
    assert 'revision = \'001_initial_baseline\'' in content
    assert 'down_revision = None' in content

def test_env_py_imports():
    """Test that env.py has correct imports"""
    env_py = Path('migrations/env.py')
    content = env_py.read_text()
    
    required_imports = [
        'from config_factory import get_config',
        'from alembic import context',
        'from sqlalchemy import engine_from_config'
    ]
    
    for import_line in required_imports:
        assert import_line in content, f"{import_line} should be in env.py"

def test_migrate_script_executable():
    """Test that migrate.py is executable"""
    migrate_script = Path('migrations/migrate.py')
    assert migrate_script.exists()
    
    import stat
    is_executable = os.access(migrate_script, os.X_OK)
    assert is_executable, "migrate.py should be executable"

def test_migrate_script_has_commands():
    """Test that migrate.py has all required commands"""
    migrate_script = Path('migrations/migrate.py')
    content = migrate_script.read_text()
    
    required_commands = [
        'def init_migrations',
        'def create_migration',
        'def upgrade',
        'def downgrade',
        'def current',
        'def history'
    ]
    
    for command in required_commands:
        assert command in content, f"{command} should be in migrate.py"

def test_readme_has_documentation():
    """Test that README.md has comprehensive documentation"""
    readme = Path('migrations/README.md')
    assert readme.exists()
    
    content = readme.read_text()
    
    required_sections = [
        'نظرة عامة',
        'الاستخدام',
        'البنية الحالية',
        'أمثلة Migrations',
        'ملاحظات مهمة',
        'استكشاف الأخطاء'
    ]
    
    for section in required_sections:
        assert section in content, f"README should have {section} section"

def test_migration_template():
    """Test that migration template is correct"""
    template = Path('migrations/script.py.mako')
    content = template.read_text()
    
    required_elements = [
        '${message}',
        'Revision ID: ${up_revision}',
        'def upgrade',
        'def downgrade'
    ]
    
    for element in required_elements:
        assert element in content, f"Template should have {element}"

def test_baseline_migration_structure():
    """Test baseline migration structure"""
    baseline = Path('migrations/versions/001_initial_baseline.py')
    content = baseline.read_text()
    
    assert 'def upgrade() -> None:' in content
    assert 'def downgrade() -> None:' in content
    assert 'pass' in content

def test_env_uses_config_factory():
    """Test that env.py uses config_factory for DATABASE_URI"""
    env_py = Path('migrations/env.py')
    content = env_py.read_text()
    
    assert 'def get_url():' in content
    assert 'app_config = get_config()' in content
    assert 'return app_config.DATABASE_URI' in content

def test_batch_alter_for_sqlite():
    """Test that env.py uses batch mode for SQLite compatibility"""
    env_py = Path('migrations/env.py')
    content = env_py.read_text()
    
    assert 'render_as_batch=True' in content

def test_readme_examples_valid():
    """Test that README examples are syntactically valid Python"""
    readme = Path('migrations/README.md')
    content = readme.read_text()
    
    assert 'op.batch_alter_table' in content
    assert 'sa.Column' in content
    assert 'op.create_table' in content
    assert 'op.drop_table' in content

if __name__ == '__main__':
    print("=" * 70)
    print("بدء اختبار نظام Migrations")
    print("Testing Migrations System")
    print("=" * 70)
    print()
    
    pytest.main([__file__, '-v', '--tb=short'])
