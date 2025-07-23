#!/usr/bin/env python3
"""
Create Super Admin Script for MEDHASAKTHI
This script creates the initial super admin user for the system
"""
import sys
import os
import getpass
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import uuid


def create_super_admin():
    """Create super admin user"""
    
    print("🚀 MEDHASAKTHI Super Admin Creation")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if super admin already exists
        existing_admin = db.query(User).filter(
            User.role == UserRole.SUPER_ADMIN
        ).first()
        
        if existing_admin:
            print(f"⚠️  Super admin already exists: {existing_admin.email}")
            response = input("Do you want to create another super admin? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborted.")
                return
        
        # Get admin details
        print("\n📝 Enter Super Admin Details:")
        
        while True:
            email = input("Email: ").strip()
            if not email:
                print("❌ Email is required!")
                continue
            
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"❌ User with email {email} already exists!")
                continue
            
            break
        
        while True:
            full_name = input("Full Name: ").strip()
            if not full_name:
                print("❌ Full name is required!")
                continue
            break
        
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long!")
                continue
            
            confirm_password = getpass.getpass("Confirm Password: ")
            if password != confirm_password:
                print("❌ Passwords don't match!")
                continue
            
            break
        
        # Create super admin user
        super_admin = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_email_verified=True,
            email_verified_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        db.add(super_admin)
        db.commit()
        
        print("\n✅ Super Admin Created Successfully!")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {full_name}")
        print(f"🆔 ID: {super_admin.id}")
        print(f"🕒 Created: {super_admin.created_at}")
        
        print("\n🎉 You can now login to the admin panel with these credentials.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating super admin: {str(e)}")
        return False
    
    finally:
        db.close()
    
    return True


def create_sample_data():
    """Create sample data for testing"""
    
    print("\n🎯 Creating Sample Data...")
    
    db = next(get_db())
    
    try:
        # Create sample institute
        from app.models.institute import Institute
        
        sample_institute = Institute(
            id=uuid.uuid4(),
            name="Demo High School",
            code="DEMO001",
            type="High School",
            address="123 Education Street",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400001",
            phone="+91-22-12345678",
            email="admin@demohighschool.edu",
            established_year=2000,
            principal_name="Dr. Jane Smith",
            is_active=True,
            subscription_type="premium",
            created_at=datetime.utcnow()
        )
        
        db.add(sample_institute)
        
        # Create sample UPI configuration
        from app.models.upi_payment import UPIConfiguration, UPIProvider
        from decimal import Decimal
        
        sample_upi_config = UPIConfiguration(
            id=uuid.uuid4(),
            upi_id="medhasakthi@paytm",
            upi_name="MEDHASAKTHI Education",
            provider=UPIProvider.PAYTM,
            is_active=True,
            is_primary=True,
            display_name="MEDHASAKTHI",
            description="Primary UPI account for payments",
            min_amount=Decimal("1.00"),
            max_amount=Decimal("100000.00"),
            auto_generate_qr=True,
            include_amount_in_qr=True,
            include_note_in_qr=True,
            require_screenshot=True,
            auto_verify_payments=False,
            verification_timeout_minutes=30,
            notify_on_payment=True,
            total_transactions=0,
            total_amount=Decimal("0.00"),
            success_rate=Decimal("0.00"),
            created_by="system",
            created_at=datetime.utcnow()
        )
        
        db.add(sample_upi_config)
        
        # Create sample global pricing configuration
        from app.models.pricing_config import GlobalPricingConfig
        
        sample_pricing_config = GlobalPricingConfig(
            id=uuid.uuid4(),
            config_name="Default Pricing Configuration",
            config_version="1.0",
            description="Initial pricing configuration for MEDHASAKTHI",
            base_exam_fee=Decimal("500.00"),
            base_certification_fee=Decimal("1000.00"),
            base_retake_fee=Decimal("300.00"),
            primary_currency="INR",
            supported_currencies=["INR", "USD"],
            currency_conversion_rates={"USD": 83.0},
            student_multiplier=Decimal("0.7"),  # 30% discount for students
            professional_multiplier=Decimal("1.0"),  # No discount
            enterprise_multiplier=Decimal("1.2"),  # 20% premium
            premium_multiplier=Decimal("1.5"),  # 50% premium
            country_pricing_multipliers={
                "India": 1.0,
                "USA": 2.5,
                "UK": 2.2,
                "Canada": 2.3
            },
            state_pricing_multipliers={
                "Maharashtra": 1.1,
                "Karnataka": 1.0,
                "Delhi": 1.2,
                "Tamil Nadu": 1.0,
                "West Bengal": 0.9
            },
            city_tier_multipliers={
                "tier_1": 1.2,
                "tier_2": 1.0,
                "tier_3": 0.8
            },
            bulk_discount_config={
                "5_programs": 0.05,   # 5% discount for 5+ programs
                "10_programs": 0.10,  # 10% discount for 10+ programs
                "20_programs": 0.15   # 15% discount for 20+ programs
            },
            referral_discount_percent=10,
            loyalty_discount_config={
                "bronze": 0.05,   # 5% for bronze members
                "silver": 0.10,   # 10% for silver members
                "gold": 0.15,     # 15% for gold members
                "platinum": 0.20  # 20% for platinum members
            },
            gateway_charges_config={
                "upi": 0.0,       # No charges for UPI
                "card": 0.025,    # 2.5% for cards
                "netbanking": 0.015  # 1.5% for net banking
            },
            convenience_fee_percent=Decimal("0.00"),
            tax_config={
                "gst_rate": 0.18,  # 18% GST
                "applicable_states": ["all"]
            },
            tax_inclusive_pricing=True,
            is_active=True,
            effective_from=datetime.utcnow(),
            created_by="system",
            approval_status="active",
            approval_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        db.add(sample_pricing_config)
        
        # Create sample certification programs
        from app.models.independent_learner import CertificationProgram, EducationLevel
        
        sample_programs = [
            {
                "program_code": "WD101",
                "title": "Web Development Fundamentals",
                "description": "Learn the basics of web development with HTML, CSS, and JavaScript",
                "category": "Technology",
                "subcategory": "Web Development",
                "level": "Beginner",
                "duration_hours": 40,
                "validity_months": 24,
                "min_education_level": EducationLevel.CLASS_12TH,
                "min_age": 16,
                "base_price": Decimal("2000.00"),
                "currency": "INR",
                "total_questions": 100,
                "exam_duration_minutes": 120,
                "passing_percentage": 70,
                "max_attempts": 3,
                "retake_fee": Decimal("500.00"),
                "practice_tests_count": 5,
                "is_active": True,
                "is_featured": True
            },
            {
                "program_code": "DS201",
                "title": "Data Science with Python",
                "description": "Master data science concepts using Python and popular libraries",
                "category": "Technology",
                "subcategory": "Data Science",
                "level": "Intermediate",
                "duration_hours": 60,
                "validity_months": 36,
                "min_education_level": EducationLevel.UNDERGRADUATE,
                "min_age": 18,
                "base_price": Decimal("3500.00"),
                "currency": "INR",
                "total_questions": 120,
                "exam_duration_minutes": 150,
                "passing_percentage": 75,
                "max_attempts": 3,
                "retake_fee": Decimal("800.00"),
                "practice_tests_count": 8,
                "is_active": True,
                "is_featured": True
            },
            {
                "program_code": "DM301",
                "title": "Digital Marketing Mastery",
                "description": "Comprehensive digital marketing course covering SEO, SEM, and social media",
                "category": "Business",
                "subcategory": "Marketing",
                "level": "Intermediate",
                "duration_hours": 50,
                "validity_months": 24,
                "min_education_level": EducationLevel.CLASS_12TH,
                "min_age": 18,
                "base_price": Decimal("2500.00"),
                "currency": "INR",
                "total_questions": 100,
                "exam_duration_minutes": 120,
                "passing_percentage": 70,
                "max_attempts": 3,
                "retake_fee": Decimal("600.00"),
                "practice_tests_count": 6,
                "is_active": True,
                "is_featured": False
            }
        ]
        
        for program_data in sample_programs:
            program = CertificationProgram(
                id=uuid.uuid4(),
                **program_data,
                created_at=datetime.utcnow()
            )
            db.add(program)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print("📚 Created 3 sample certification programs")
        print("🏫 Created 1 sample institute")
        print("💳 Created UPI payment configuration")
        print("💰 Created global pricing configuration")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {str(e)}")
        return False
    
    finally:
        db.close()
    
    return True


def main():
    """Main function"""
    
    print("🎓 MEDHASAKTHI System Setup")
    print("=" * 50)
    
    # Create super admin
    if not create_super_admin():
        return
    
    # Ask if user wants to create sample data
    print("\n" + "=" * 50)
    response = input("Do you want to create sample data for testing? (Y/n): ")
    
    if response.lower() != 'n':
        create_sample_data()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Start the application server")
    print("2. Login to the admin panel with your super admin credentials")
    print("3. Configure additional settings as needed")
    print("4. Start onboarding institutes and learners")
    
    print("\n🌐 Access URLs:")
    print("- Admin Panel: http://localhost:8000/admin")
    print("- API Documentation: http://localhost:8000/docs")
    print("- Health Check: http://localhost:8000/health")


if __name__ == "__main__":
    main()
