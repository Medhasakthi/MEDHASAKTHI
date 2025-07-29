#!/usr/bin/env python3
"""
MEDHASAKTHI Backend Dependency Checker
Validates all dependencies and identifies potential conflicts
"""
import subprocess
import sys
import pkg_resources
from typing import List, Dict, Tuple

def check_package_availability(package_name: str) -> Tuple[bool, str]:
    """Check if a package is available on PyPI"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, "Available"
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Timeout checking package"
    except Exception as e:
        return False, str(e)

def parse_requirements(file_path: str) -> List[str]:
    """Parse requirements.txt file"""
    requirements = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, etc.)
                    package = line.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0]
                    requirements.append(line)
    except FileNotFoundError:
        print(f"❌ Requirements file not found: {file_path}")
        return []
    return requirements

def main():
    print("🔍 MEDHASAKTHI Backend Dependency Checker")
    print("=" * 50)
    
    # Check requirements.txt
    requirements = parse_requirements("requirements.txt")
    if not requirements:
        return
    
    print(f"📦 Found {len(requirements)} packages to check")
    print()
    
    available_packages = []
    unavailable_packages = []
    
    for i, req in enumerate(requirements, 1):
        package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0]
        print(f"[{i:2d}/{len(requirements)}] Checking {package_name}...", end=" ")
        
        is_available, message = check_package_availability(package_name)
        if is_available:
            print("✅")
            available_packages.append(req)
        else:
            print(f"❌ {message}")
            unavailable_packages.append((req, message))
    
    print()
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Available packages: {len(available_packages)}")
    print(f"❌ Unavailable packages: {len(unavailable_packages)}")
    
    if unavailable_packages:
        print()
        print("❌ UNAVAILABLE PACKAGES:")
        for package, error in unavailable_packages:
            print(f"   - {package}: {error}")
        
        print()
        print("🔧 RECOMMENDATIONS:")
        print("1. Remove unavailable packages from requirements.txt")
        print("2. Find alternative packages")
        print("3. Use requirements-minimal.txt for basic functionality")
    
    # Generate a clean requirements file
    if available_packages:
        with open("requirements-clean.txt", "w") as f:
            f.write("# Auto-generated clean requirements\n")
            f.write("# Only includes packages available on PyPI\n\n")
            for package in available_packages:
                f.write(f"{package}\n")
        print(f"📝 Generated requirements-clean.txt with {len(available_packages)} packages")
    
    print()
    print("✅ Dependency check completed!")

if __name__ == "__main__":
    main()
