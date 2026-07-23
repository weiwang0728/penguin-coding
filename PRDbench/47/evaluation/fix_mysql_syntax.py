#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def fix_mysql_syntax_in_file(filepath):
 """FixedFileinMySQLLanguageMethodas SQLiteLanguageMethod"""
 try:
 with open(filepath, 'r', encoding='utf-8') as f:
 content = f.read()
 
 original_content = content
 
 # Change %s as ?
 content = re.sub(r'%s', '?', content)
 
 # Change NOW() as datetime('now')
 content = re.sub(r'NOW\(\)', "datetime('now')", content)
 
 if content != original_content:
 with open(filepath, 'w', encoding='utf-8') as f:
 f.write(content)
 print(f'+ AlreadyFixed: {filepath}')
 return True
 else:
 print(f'- NoFixed: {filepath}')
 return False
 
 except Exception as e:
 print(f'x FixedFailure: {filepath} - {e}')
 return False

def main():
 """BatchFixedservicesDirectoryunderMySQLLanguageMethod"""
 services_dir = 'src/services'
 fixed_count = 0
 
 print("StartingBatchFixedMySQLLanguageMethod...")
 
 for filename in os.listdir(services_dir):
 if filename.endswith('.py') and filename != '__init__.py':
 filepath = os.path.join(services_dir, filename)
 if fix_mysql_syntax_in_file(filepath):
 fixed_count += 1
 
 print(f"FixedSuccessfully！Fixed {fixed_count} itemsFile")

if __name__ == "__main__":
 main()