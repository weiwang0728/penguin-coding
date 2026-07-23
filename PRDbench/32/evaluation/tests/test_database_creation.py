import pytest
import sqlite3
import os
import sys
import tempfile

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from database.db import DataBase


class TestDatabaseCreation:
    """Test database and table structure creation"""

    def test_database_table_creation(self):
        """Test database file creation and table structure creation"""
        # Create temporary database file path
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_db_path = temp_file.name

        try:
            # Ensure temporary file doesn't exist (test creation from scratch)
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)

            # Create database instance
            db = DataBase(temp_db_path)

            # Verify if database file was created
            assert os.path.exists(temp_db_path), "Database file should be created"

            # Create table structure
            db.create_tables()

            # Verify tables exist
            cursor = db.cursor

            # Check if doc table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='doc'")
            doc_table = cursor.fetchone()
            assert doc_table is not None, "doc table should exist"

            # Check if word table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='word'")
            word_table = cursor.fetchone()
            assert word_table is not None, "word table should exist"

            # Verify doc table structure
            cursor.execute("PRAGMA table_info(doc)")
            doc_columns = cursor.fetchall()
            doc_column_names = [col[1] for col in doc_columns]
            expected_doc_columns = ['id', 'title', 'link']
            for col in expected_doc_columns:
                assert col in doc_column_names, f"doc table should contain {col} column"

            # Verify word table structure
            cursor.execute("PRAGMA table_info(word)")
            word_columns = cursor.fetchall()
            word_column_names = [col[1] for col in word_columns]
            expected_word_columns = ['term', 'list']
            for col in expected_word_columns:
                assert col in word_column_names, f"word table should contain {col} column"

            # Verify primary key constraints
            doc_pk = [col for col in doc_columns if col[5] == 1]  # pk field of 1 indicates primary key
            assert len(doc_pk) == 1 and doc_pk[0][1] == 'id', "doc table's id should be primary key"

            word_pk = [col for col in word_columns if col[5] == 1]
            assert len(word_pk) == 1 and word_pk[0][1] == 'term', "word table's term should be primary key"

            # Close database connection
            db.close()

        finally:
            # Clean up temporary file
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)


if __name__ == "__main__":
    pytest.main([__file__])