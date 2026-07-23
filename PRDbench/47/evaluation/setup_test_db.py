#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CreateTestUseSQLiteDatabaseGenerationMySQLImportLineAssessment
"""

import sqlite3
import os
import sys

def create_test_database():
 """CreateTest DatabaseandTableResultStructure"""
 db_path = 'evaluation/test_library.db'
 
 # DeleteAlreadySaveinDatabase
 if os.path.exists(db_path):
 os.remove(db_path)
 
 conn = sqlite3.connect(db_path)
 cursor = conn.cursor()
 
 try:
 # CreateUserTable
 cursor.execute('''
 CREATE TABLE user (
 StudentId VARCHAR(20) PRIMARY KEY,
 Name VARCHAR(20) NOT NULL,
 Password VARCHAR(32) NOT NULL,
 IsAdmin TINYINT DEFAULT 0,
 tel VARCHAR(30),
 CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 )
 ''')
 
 # CreateBookTable
 cursor.execute('''
 CREATE TABLE book (
 BookId VARCHAR(30) PRIMARY KEY,
 BookName VARCHAR(30) NOT NULL,
 Auth VARCHAR(20) NOT NULL,
 Category VARCHAR(10),
 Publisher VARCHAR(30),
 PublishTime DATE,
 NumStorage INT DEFAULT 0,
 NumCanBorrow INT DEFAULT 0,
 NumBookinged INT DEFAULT 0
 )
 ''')
 
 # CreateBorrowingTable
 cursor.execute('''
 CREATE TABLE user_book (
 StudentId VARCHAR(20),
 BookId VARCHAR(30),
 BorrowTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 ReturnTime TIMESTAMP NULL,
 BorrowState TINYINT DEFAULT 1,
 BookingState TINYINT DEFAULT 0,
 FOREIGN KEY (StudentId) REFERENCES user(StudentId),
 FOREIGN KEY (BookId) REFERENCES book(BookId)
 )
 ''')
 
 # InputTest Data
 # DefaultCertifiedManagementcursor.execute('''
 INSERT INTO user (StudentId, Name, Password, IsAdmin, tel) 
 VALUES (?, ?, ?, ?, ?)
 ''', ('admin', 'SystemManagement', 'e10adc3949ba59abbe56e057f20f883e', 1, 'admin@library.com'))
 
 # Test User
 cursor.execute('''
 INSERT INTO user (StudentId, Name, Password, IsAdmin, tel) 
 VALUES (?, ?, ?, ?, ?)
 ''', ('TEST001', 'Test User', 'e10adc3949ba59abbe56e057f20f883e', 0, 'test@email.com'))
 
 # TestBook
 cursor.execute('''
 INSERT INTO book (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged) 
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
 ''', ('ISBN001', 'PythonCodeProcessInput', 'Sam', 'DesignCalculateMachine', 'PersonOutputEdition', '2023-01-01', 10, 8, 0))
 
 cursor.execute('''
 INSERT INTO book (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged) 
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
 ''', ('ISBN002', 'JavaProgramDesignDesign', '', 'DesignCalculateMachine', 'CleanASUSOutputEdition', '2023-02-01', 5, 0, 2))
 
 conn.commit()
 print("Test DatabaseCreateSuccess!")
 print(f"DatabasePositionSet: {os.path.abspath(db_path)}")
 return True
 
 except Exception as e:
 print(f"CreateTest DatabaseFailure: {e}")
 return False
 finally:
 conn.close()

if __name__ == '__main__':
 success = create_test_database()
 sys.exit(0 if success else 1)