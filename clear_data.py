#!/usr/bin/env python3
"""
Session & User Data Management Utility

Provides commands to clear, inspect, and manage session/user persistence files.

Usage:
    python clear_data.py --help                    # Show all options
    python clear_data.py --clear-all               # Delete everything
    python clear_data.py --clear-sessions          # Delete all sessions only
    python clear_data.py --clear-user <uid>        # Delete specific user
    python clear_data.py --list                    # List all files
    python clear_data.py --stats                   # Show storage stats
    python clear_data.py --cleanup                 # Remove old sessions (7+ days)
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# Import from core module
try:
    from core.session_store import (
        CACHE_DIR,
        DATA_DIR,
        delete_user,
        cleanup_old_sessions,
        user_exists,
    )
except ImportError:
    # Fallback if running outside app context
    CACHE_DIR = Path(".cache")
    DATA_DIR = Path("data/users")


def clear_all() -> None:
    """Delete all session and user data."""
    deleted_sessions = 0
    deleted_users = 0
    
    # Clear sessions
    if CACHE_DIR.exists():
        for file in CACHE_DIR.glob("session_*.json"):
            try:
                file.unlink()
                deleted_sessions += 1
            except OSError as e:
                print(f"[ERROR] Failed to delete {file}: {e}")
        
        # Also clear lock files
        for file in CACHE_DIR.glob("*.lock"):
            try:
                file.unlink()
            except OSError:
                pass
    
    # Clear users
    if DATA_DIR.exists():
        for file in DATA_DIR.glob("*.json"):
            try:
                file.unlink()
                deleted_users += 1
            except OSError as e:
                print(f"[ERROR] Failed to delete {file}: {e}")
        
        # Also clear lock files
        for file in DATA_DIR.glob("*.lock"):
            try:
                file.unlink()
            except OSError:
                pass
    
    print(f"✅ Deleted {deleted_sessions} session(s) and {deleted_users} user(s)")


def clear_sessions() -> None:
    """Delete all session files."""
    deleted = 0
    
    if CACHE_DIR.exists():
        for file in CACHE_DIR.glob("session_*.json"):
            try:
                file.unlink()
                deleted += 1
            except OSError as e:
                print(f"[ERROR] Failed to delete {file}: {e}")
        
        # Also clear lock files
        for file in CACHE_DIR.glob("*.lock"):
            try:
                file.unlink()
            except OSError:
                pass
    
    print(f"✅ Deleted {deleted} session(s)")


def clear_user(uid: str) -> None:
    """Delete a specific user file."""
    user_file = DATA_DIR / f"{uid}.json"
    
    if not user_file.exists():
        print(f"❌ User {uid} not found")
        return
    
    try:
        user_file.unlink()
        print(f"✅ Deleted user: {uid}")
    except OSError as e:
        print(f"[ERROR] Failed to delete user {uid}: {e}")


def list_files() -> None:
    """List all session and user files with details."""
    print("\n=== SESSION FILES ===")
    
    if CACHE_DIR.exists() and list(CACHE_DIR.glob("session_*.json")):
        for file in sorted(CACHE_DIR.glob("session_*.json")):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                session_id = data.get('session_id', 'unknown')
                created = datetime.fromtimestamp(data.get('created_at', 0))
                accessed = datetime.fromtimestamp(data.get('last_accessed', 0))
                route = data.get('current_route', 'none')
                
                print(f"\n📄 {file.name}")
                print(f"   ID: {session_id}")
                print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Last Accessed: {accessed.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Route: {route}")
                print(f"   Size: {file.stat().st_size:,} bytes")
            except Exception as e:
                print(f"\n❌ {file.name}: {e}")
    else:
        print("   (no sessions)")
    
    print("\n=== USER FILES ===")
    
    if DATA_DIR.exists() and list(DATA_DIR.glob("*.json")):
        for file in sorted(DATA_DIR.glob("*.json")):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                uid = data.get('uid', 'unknown')
                created = datetime.fromtimestamp(data.get('created_at', 0))
                updated = datetime.fromtimestamp(data.get('last_updated', 0))
                
                # Get profile info
                profile = data.get('profile', {})
                name = profile.get('name', 'No name')
                
                # Count progress
                progress = data.get('progress', {})
                completed = sum(1 for p in progress.values() if isinstance(p, dict) and p.get('completed'))
                
                print(f"\n👤 {file.name}")
                print(f"   UID: {uid}")
                print(f"   Name: {name}")
                print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Last Updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Completed Products: {completed}")
                print(f"   Size: {file.stat().st_size:,} bytes")
            except Exception as e:
                print(f"\n❌ {file.name}: {e}")
    else:
        print("   (no users)")
    
    print()


def show_stats() -> None:
    """Show storage statistics."""
    session_count = 0
    session_size = 0
    user_count = 0
    user_size = 0
    
    # Count sessions
    if CACHE_DIR.exists():
        for file in CACHE_DIR.glob("session_*.json"):
            session_count += 1
            session_size += file.stat().st_size
    
    # Count users
    if DATA_DIR.exists():
        for file in DATA_DIR.glob("*.json"):
            user_count += 1
            user_size += file.stat().st_size
    
    total_size = session_size + user_size
    
    print("\n=== STORAGE STATISTICS ===")
    print(f"\n📊 Sessions:")
    print(f"   Count: {session_count}")
    print(f"   Total Size: {session_size:,} bytes ({session_size / 1024:.1f} KB)")
    print(f"   Avg Size: {session_size // session_count if session_count > 0 else 0:,} bytes")
    
    print(f"\n👥 Users:")
    print(f"   Count: {user_count}")
    print(f"   Total Size: {user_size:,} bytes ({user_size / 1024:.1f} KB)")
    print(f"   Avg Size: {user_size // user_count if user_count > 0 else 0:,} bytes")
    
    print(f"\n💾 Total:")
    print(f"   Combined Size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
    print()


def cleanup_old(days: int = 7) -> None:
    """Remove old session files."""
    try:
        deleted = cleanup_old_sessions(max_age_days=days)
        print(f"✅ Cleaned up {deleted} old session(s) (>{days} days)")
    except Exception as e:
        print(f"[ERROR] Cleanup failed: {e}")


def inspect_file(path: str) -> None:
    """Inspect a specific file."""
    file_path = Path(path)
    
    if not file_path.exists():
        print(f"❌ File not found: {path}")
        return
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"\n=== {file_path.name} ===")
        print(json.dumps(data, indent=2))
        print()
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage session and user data persistence files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_data.py --clear-all                 # Nuclear option
  python clear_data.py --clear-sessions             # Clear sessions only
  python clear_data.py --clear-user anon_abc123     # Clear specific user
  python clear_data.py --list                       # See what's stored
  python clear_data.py --stats                      # Storage statistics
  python clear_data.py --cleanup                    # Remove old sessions
  python clear_data.py --inspect .cache/session_*.json  # View file contents
        """
    )
    
    parser.add_argument(
        '--clear-all',
        action='store_true',
        help='Delete all session and user data (DESTRUCTIVE)'
    )
    
    parser.add_argument(
        '--clear-sessions',
        action='store_true',
        help='Delete all session files'
    )
    
    parser.add_argument(
        '--clear-user',
        metavar='UID',
        help='Delete a specific user by UID'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all files with details'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show storage statistics'
    )
    
    parser.add_argument(
        '--cleanup',
        nargs='?',
        const=7,
        type=int,
        metavar='DAYS',
        help='Remove sessions older than DAYS (default: 7)'
    )
    
    parser.add_argument(
        '--inspect',
        metavar='PATH',
        help='Inspect a specific file (show JSON contents)'
    )
    
    args = parser.parse_args()
    
    # Execute commands
    executed = False
    
    if args.clear_all:
        confirm = input("⚠️  Delete ALL session and user data? [y/N]: ")
        if confirm.lower() == 'y':
            clear_all()
            executed = True
        else:
            print("❌ Cancelled")
            executed = True
    
    if args.clear_sessions:
        confirm = input("⚠️  Delete ALL session files? [y/N]: ")
        if confirm.lower() == 'y':
            clear_sessions()
            executed = True
        else:
            print("❌ Cancelled")
            executed = True
    
    if args.clear_user:
        confirm = input(f"⚠️  Delete user {args.clear_user}? [y/N]: ")
        if confirm.lower() == 'y':
            clear_user(args.clear_user)
            executed = True
        else:
            print("❌ Cancelled")
            executed = True
    
    if args.list:
        list_files()
        executed = True
    
    if args.stats:
        show_stats()
        executed = True
    
    if args.cleanup is not None:
        cleanup_old(days=args.cleanup)
        executed = True
    
    if args.inspect:
        inspect_file(args.inspect)
        executed = True
    
    if not executed:
        parser.print_help()


if __name__ == '__main__':
    main()
