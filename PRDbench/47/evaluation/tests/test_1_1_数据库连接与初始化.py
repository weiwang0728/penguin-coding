#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def main():
    """Test Database Connection and Initial Initialization"""
    print("Testing Database Connection...")

    try:
        # Import and switch to SQLite mode
        from config.database_mode import db_mode_manager

        # Check and select database mode for testing
        db_mode = db_mode_manager.select_database_mode(prefer_mysql=False)

        if db_mode == 'sqlite':
            print("+ Database connection successful (SQLite mode)")

            # Check SQLite database table structure
            from utils.database import db_manager

            tables = ['user', 'book', 'user_book']
            table_count = 0
            for table in tables:
                try:
                    result = db_manager.execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if result:
                        print(f"+ {table} table exists")
                        table_count += 1
                    else:
                        print(f"- {table} table does not exist")
                except Exception as e:
                    print(f"- {table} table check failed: {e}")

            if table_count == 3:
                print("Database initialization verification successful")
                return True
            else:
                print(f"Database table structure incomplete: {table_count}/3")
                return False
        else:
            print("- Database connection failed")
            return False
    except Exception as e:
        print(f"- Test exception: {e}")
        return False

if __name__ == "__main__":
 success = main()
 if success:
 print("[PASS] Test Passed")
 else:
 print("[FAIL] Test Failed")
 sys.exit(0 if success else 1)
