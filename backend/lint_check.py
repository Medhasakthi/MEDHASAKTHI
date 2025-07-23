#!/usr/bin/env python3
"""
Simple linting check for MEDHASAKTHI codebase
Checks for common issues like unused imports, long lines, etc.
"""
import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any


class LintChecker:
    """Simple linting checker for Python files"""
    
    def __init__(self):
        self.issues = []
        self.max_line_length = 120
        
    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Check a single Python file for linting issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check line length
            for i, line in enumerate(lines, 1):
                if len(line) > self.max_line_length:
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'type': 'line_too_long',
                        'message': f'Line too long ({len(line)} > {self.max_line_length})',
                        'content': line[:50] + '...' if len(line) > 50 else line
                    })
            
            # Check for trailing whitespace
            for i, line in enumerate(lines, 1):
                if line.endswith(' ') or line.endswith('\t'):
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'type': 'trailing_whitespace',
                        'message': 'Trailing whitespace found'
                    })
            
            # Check for multiple blank lines
            blank_count = 0
            for i, line in enumerate(lines, 1):
                if line.strip() == '':
                    blank_count += 1
                    if blank_count > 2:
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'type': 'too_many_blank_lines',
                            'message': 'More than 2 consecutive blank lines'
                        })
                else:
                    blank_count = 0
            
            # Check for basic syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    'file': file_path,
                    'line': e.lineno,
                    'type': 'syntax_error',
                    'message': f'Syntax error: {e.msg}'
                })
            
            # Check imports
            self._check_imports(file_path, content, issues)
            
        except Exception as e:
            issues.append({
                'file': file_path,
                'line': 0,
                'type': 'file_error',
                'message': f'Error reading file: {str(e)}'
            })
        
        return issues
    
    def _check_imports(self, file_path: str, content: str, issues: List[Dict[str, Any]]):
        """Check import statements for issues"""
        lines = content.split('\n')
        
        # Find all import statements
        imports = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append((i, line))
        
        # Check for unused imports (basic check)
        for line_num, import_line in imports:
            if import_line.startswith('import '):
                # Extract module name
                module = import_line.replace('import ', '').split(' as ')[0].split('.')[0]
                if module not in content.replace(import_line, ''):
                    # Skip common modules that might be used indirectly
                    if module not in ['os', 'sys', 'typing', 'datetime', 'uuid', 'enum']:
                        issues.append({
                            'file': file_path,
                            'line': line_num,
                            'type': 'unused_import',
                            'message': f'Potentially unused import: {module}',
                            'content': import_line
                        })
    
    def check_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Check all Python files in a directory"""
        all_issues = []
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    issues = self.check_file(file_path)
                    all_issues.extend(issues)
        
        return all_issues
    
    def print_report(self, issues: List[Dict[str, Any]]):
        """Print a formatted report of issues"""
        if not issues:
            print("✅ No linting issues found!")
            return
        
        print(f"🔍 Found {len(issues)} linting issues:\n")
        
        # Group by file
        by_file = {}
        for issue in issues:
            file_path = issue['file']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)
        
        for file_path, file_issues in by_file.items():
            print(f"📄 {file_path}")
            for issue in file_issues:
                icon = self._get_issue_icon(issue['type'])
                print(f"  {icon} Line {issue['line']}: {issue['message']}")
                if 'content' in issue:
                    print(f"     → {issue['content']}")
            print()
    
    def _get_issue_icon(self, issue_type: str) -> str:
        """Get icon for issue type"""
        icons = {
            'line_too_long': '📏',
            'trailing_whitespace': '🔚',
            'too_many_blank_lines': '📝',
            'syntax_error': '❌',
            'unused_import': '📦',
            'file_error': '💥'
        }
        return icons.get(issue_type, '⚠️')


def main():
    """Main function to run linting checks"""
    print("🔍 MEDHASAKTHI Code Linting Check\n")
    
    checker = LintChecker()
    
    # Check specific directories
    directories_to_check = [
        'app/models',
        'app/services',
        'app/api/v1'
    ]
    
    all_issues = []
    
    for directory in directories_to_check:
        if os.path.exists(directory):
            print(f"Checking {directory}...")
            issues = checker.check_directory(directory)
            all_issues.extend(issues)
        else:
            print(f"⚠️  Directory {directory} not found")
    
    print("\n" + "="*60)
    checker.print_report(all_issues)
    
    # Summary
    if all_issues:
        issue_types = {}
        for issue in all_issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        print("📊 Issue Summary:")
        for issue_type, count in issue_types.items():
            icon = checker._get_issue_icon(issue_type)
            print(f"  {icon} {issue_type}: {count}")
        
        print(f"\n🎯 Total issues: {len(all_issues)}")
        return 1
    else:
        print("🎉 All checks passed! Code looks good.")
        return 0


if __name__ == "__main__":
    exit(main())
