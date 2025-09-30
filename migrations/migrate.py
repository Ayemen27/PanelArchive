#!/usr/bin/env python
# coding: utf-8
"""
Migration Management Script for aaPanel
Provides commands for database migrations
"""

import os
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_command(cmd):
    """Run a shell command"""
    print(f"Running: {cmd}")
    return os.system(cmd)

def init_migrations():
    """Initialize migrations directory (already done)"""
    print("✅ Migrations directory already initialized")
    print("   Location: ./migrations/")

def create_migration(message):
    """Create a new migration"""
    if not message:
        print("❌ Error: Migration message is required")
        sys.exit(1)
    
    cmd = f'alembic revision -m "{message}"'
    result = run_command(cmd)
    
    if result == 0:
        print(f"✅ Migration created successfully: {message}")
    else:
        print("❌ Error creating migration")
        sys.exit(1)

def upgrade(revision='head'):
    """Upgrade database to a specific revision"""
    cmd = f'alembic upgrade {revision}'
    result = run_command(cmd)
    
    if result == 0:
        print(f"✅ Upgraded to {revision}")
    else:
        print("❌ Error upgrading database")
        sys.exit(1)

def downgrade(revision='-1'):
    """Downgrade database to a specific revision"""
    cmd = f'alembic downgrade {revision}'
    result = run_command(cmd)
    
    if result == 0:
        print(f"✅ Downgraded to {revision}")
    else:
        print("❌ Error downgrading database")
        sys.exit(1)

def current():
    """Show current database revision"""
    cmd = 'alembic current'
    result = run_command(cmd)
    
    if result != 0:
        print("❌ Error getting current revision")
        sys.exit(1)

def history():
    """Show migration history"""
    cmd = 'alembic history --verbose'
    result = run_command(cmd)
    
    if result != 0:
        print("❌ Error getting history")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='aaPanel Migration Management')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    subparsers.add_parser('init', help='Initialize migrations')
    
    create_parser = subparsers.add_parser('create', help='Create new migration')
    create_parser.add_argument('message', help='Migration message')
    
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('--revision', default='head', help='Target revision')
    
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('--revision', default='-1', help='Target revision')
    
    subparsers.add_parser('current', help='Show current revision')
    subparsers.add_parser('history', help='Show migration history')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    print("=" * 70)
    print("aaPanel Migration Management")
    print("=" * 70)
    print()
    
    if args.command == 'init':
        init_migrations()
    elif args.command == 'create':
        create_migration(args.message)
    elif args.command == 'upgrade':
        upgrade(args.revision)
    elif args.command == 'downgrade':
        downgrade(args.revision)
    elif args.command == 'current':
        current()
    elif args.command == 'history':
        history()

if __name__ == '__main__':
    main()
