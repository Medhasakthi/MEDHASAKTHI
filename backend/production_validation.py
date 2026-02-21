#!/usr/bin/env python3
"""
Production Validation Script for MEDHASAKTHI
Comprehensive validation of all components before deployment
"""

import os
import sys
import asyncio
import subprocess
import importlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionValidator:
    """Comprehensive production validation"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        
    async def run_all_validations(self) -> Dict[str, Any]:
        """Run all production validations"""
        print("🔍 MEDHASAKTHI Production Validation")
        print("=" * 60)
        
        # 1. Import Validation
        await self._validate_imports()
        
        # 2. Database Model Validation
        await self._validate_database_models()
        
        # 3. API Endpoint Validation
        await self._validate_api_endpoints()
        
        # 4. Service Layer Validation
        await self._validate_services()
        
        # 5. Configuration Validation
        await self._validate_configuration()
        
        # 6. Security Validation
        await self._validate_security()
        
        # 7. Load Balancer Validation
        await self._validate_load_balancer()
        
        # 8. Frontend Component Validation
        await self._validate_frontend()
        
        # Generate report
        return self._generate_report()
    
    async def _validate_imports(self):
        """Validate all Python imports"""
        print("\n📦 Validating Python Imports...")
        
        critical_modules = [
            'app.core.auth',
            'app.core.config',
            'app.core.database',
            'app.models.server',
            'app.models.user',
            'app.services.load_balancer_service',
            'app.services.auto_scaling_service',
            'app.services.scaling_scheduler',
            'app.api.v1.endpoints.load_balancer'
        ]
        
        for module_name in critical_modules:
            try:
                importlib.import_module(module_name)
                self.passed_checks.append(f"✅ Import: {module_name}")
            except ImportError as e:
                self.errors.append(f"❌ Import Error: {module_name} - {e}")
            except Exception as e:
                self.warnings.append(f"⚠️ Import Warning: {module_name} - {e}")
    
    async def _validate_database_models(self):
        """Validate database models and relationships"""
        print("\n🗄️ Validating Database Models...")
        
        try:
            from app.models.server import Server, ServerMetrics, LoadBalancerConfig
            from app.models.user import User
            
            # Check model attributes
            required_server_attrs = ['hostname', 'ip_address', 'port', 'server_type']
            for attr in required_server_attrs:
                if hasattr(Server, attr):
                    self.passed_checks.append(f"✅ Server.{attr} exists")
                else:
                    self.errors.append(f"❌ Missing Server.{attr}")
            
            # Check relationships
            if hasattr(Server, 'metrics'):
                self.passed_checks.append("✅ Server.metrics relationship exists")
            else:
                self.errors.append("❌ Missing Server.metrics relationship")
            
            if hasattr(User, 'added_servers'):
                self.passed_checks.append("✅ User.added_servers relationship exists")
            else:
                self.errors.append("❌ Missing User.added_servers relationship")
                
        except Exception as e:
            self.errors.append(f"❌ Database Model Error: {e}")
    
    async def _validate_api_endpoints(self):
        """Validate API endpoints"""
        print("\n🌐 Validating API Endpoints...")
        
        try:
            from app.api.v1.endpoints.load_balancer import router
            
            # Check if router has routes
            if router.routes:
                self.passed_checks.append(f"✅ Load Balancer API has {len(router.routes)} routes")
            else:
                self.errors.append("❌ Load Balancer API has no routes")
            
            # Check specific endpoints
            route_paths = [route.path for route in router.routes]
            required_paths = ['/servers', '/status', '/config']
            
            for path in required_paths:
                if any(path in route_path for route_path in route_paths):
                    self.passed_checks.append(f"✅ API endpoint exists: {path}")
                else:
                    self.errors.append(f"❌ Missing API endpoint: {path}")
                    
        except Exception as e:
            self.errors.append(f"❌ API Endpoint Error: {e}")
    
    async def _validate_services(self):
        """Validate service layer"""
        print("\n⚙️ Validating Services...")
        
        try:
            from app.services.load_balancer_service import LoadBalancerService
            from app.services.auto_scaling_service import AutoScalingService
            from app.services.scaling_scheduler import ScalingScheduler
            
            # Check service methods
            lb_service = LoadBalancerService()
            required_methods = ['add_server', 'remove_server', 'get_server_status']
            
            for method in required_methods:
                if hasattr(lb_service, method):
                    self.passed_checks.append(f"✅ LoadBalancerService.{method} exists")
                else:
                    self.errors.append(f"❌ Missing LoadBalancerService.{method}")
            
            # Check auto-scaling service
            auto_service = AutoScalingService()
            if hasattr(auto_service, 'monitor_and_scale'):
                self.passed_checks.append("✅ AutoScalingService.monitor_and_scale exists")
            else:
                self.errors.append("❌ Missing AutoScalingService.monitor_and_scale")
                
        except Exception as e:
            self.errors.append(f"❌ Service Validation Error: {e}")
    
    async def _validate_configuration(self):
        """Validate configuration settings"""
        print("\n⚙️ Validating Configuration...")
        
        try:
            from app.core.config import settings
            
            # Check critical settings
            critical_settings = [
                'SECRET_KEY', 'DATABASE_URL', 'REDIS_URL',
                'AUTO_SCALING_ENABLED', 'MIN_SERVERS', 'MAX_SERVERS'
            ]
            
            for setting in critical_settings:
                if hasattr(settings, setting):
                    value = getattr(settings, setting)
                    if value is not None:
                        self.passed_checks.append(f"✅ Config: {setting} = {str(value)[:50]}")
                    else:
                        self.warnings.append(f"⚠️ Config: {setting} is None")
                else:
                    self.errors.append(f"❌ Missing config: {setting}")
            
            # Check security settings
            if settings.SECRET_KEY == "your-super-secret-key-change-this-in-production":
                self.errors.append("❌ SECRET_KEY is using default value - SECURITY RISK!")
            else:
                self.passed_checks.append("✅ SECRET_KEY is customized")
                
        except Exception as e:
            self.errors.append(f"❌ Configuration Error: {e}")
    
    async def _validate_security(self):
        """Validate security implementation"""
        print("\n🔒 Validating Security...")
        
        try:
            from app.core.auth import get_current_super_admin, verify_password, create_access_token
            
            # Check auth functions exist
            auth_functions = [
                ('get_current_super_admin', get_current_super_admin),
                ('verify_password', verify_password),
                ('create_access_token', create_access_token)
            ]
            
            for name, func in auth_functions:
                if callable(func):
                    self.passed_checks.append(f"✅ Auth function: {name}")
                else:
                    self.errors.append(f"❌ Auth function not callable: {name}")
                    
        except Exception as e:
            self.errors.append(f"❌ Security Validation Error: {e}")
    
    async def _validate_load_balancer(self):
        """Validate load balancer implementation"""
        print("\n⚖️ Validating Load Balancer...")
        
        try:
            from app.services.load_balancer_service import load_balancer_service
            
            # Check service instance
            if load_balancer_service:
                self.passed_checks.append("✅ Load balancer service instance exists")
            else:
                self.errors.append("❌ Load balancer service instance not found")
            
            # Check nginx config path
            if hasattr(load_balancer_service, 'nginx_config_path'):
                self.passed_checks.append("✅ Nginx config path configured")
            else:
                self.warnings.append("⚠️ Nginx config path not configured")
                
        except Exception as e:
            self.errors.append(f"❌ Load Balancer Validation Error: {e}")
    
    async def _validate_frontend(self):
        """Validate frontend components"""
        print("\n🎨 Validating Frontend...")
        
        frontend_path = Path("../frontend")
        if frontend_path.exists():
            # Check package.json
            package_json = frontend_path / "package.json"
            if package_json.exists():
                self.passed_checks.append("✅ Frontend package.json exists")
            else:
                self.errors.append("❌ Frontend package.json missing")
            
            # Check key components
            components_path = frontend_path / "src" / "components"
            if components_path.exists():
                required_components = [
                    "LoadBalancerManagement.tsx",
                    "LoadBalancerDashboard.tsx",
                    "AdminDashboard.tsx"
                ]
                
                for component in required_components:
                    component_file = components_path / component
                    if component_file.exists():
                        self.passed_checks.append(f"✅ Frontend component: {component}")
                    else:
                        self.errors.append(f"❌ Missing frontend component: {component}")
            else:
                self.warnings.append("⚠️ Frontend components directory not found")
        else:
            self.warnings.append("⚠️ Frontend directory not found")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.errors)
        success_rate = (len(self.passed_checks) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n📈 Summary:")
        print(f"   ✅ Passed: {len(self.passed_checks)}")
        print(f"   ⚠️ Warnings: {len(self.warnings)}")
        print(f"   ❌ Errors: {len(self.errors)}")
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        if self.passed_checks:
            print(f"\n✅ PASSED CHECKS ({len(self.passed_checks)}):")
            for check in self.passed_checks:
                print(f"   {check}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        
        # Production readiness assessment
        print(f"\n🎯 PRODUCTION READINESS:")
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                print("   🟢 FULLY READY - No issues found!")
            elif len(self.warnings) <= 3:
                print("   🟡 MOSTLY READY - Minor warnings only")
            else:
                print("   🟠 READY WITH CAUTION - Multiple warnings")
        else:
            print("   🔴 NOT READY - Critical errors must be fixed")
        
        return {
            'passed': len(self.passed_checks),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'success_rate': success_rate,
            'production_ready': len(self.errors) == 0,
            'details': {
                'passed_checks': self.passed_checks,
                'warnings': self.warnings,
                'errors': self.errors
            }
        }

async def main():
    """Main validation function"""
    validator = ProductionValidator()
    
    try:
        report = await validator.run_all_validations()
        
        # Exit with appropriate code
        if report['errors'] > 0:
            print(f"\n❌ Validation failed with {report['errors']} errors")
            sys.exit(1)
        elif report['warnings'] > 5:
            print(f"\n⚠️ Validation passed with {report['warnings']} warnings")
            sys.exit(2)
        else:
            print(f"\n✅ Validation passed successfully!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Validation script error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
