#!/usr/bin/env python3
"""
MEDHASAKTHI - Pharmacy Question Generation Demo
Demonstrates AI-powered question generation for Pharmacy and other professional fields
"""
import asyncio
import json
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, create_tables
from app.services.ai_question_service import ai_question_generator
from app.models.question import QuestionType, DifficultyLevel
from app.utils.sample_data import create_sample_data
from app.utils.comprehensive_subjects import COMPREHENSIVE_SUBJECTS


async def demo_pharmacy_question_generation():
    """Demonstrate AI question generation for Pharmacy"""
    
    print("🎓 MEDHASAKTHI - AI Question Generation Demo")
    print("=" * 60)
    print("🧬 Specializing in PHARMACY and Professional Education")
    print("=" * 60)
    
    # Initialize database
    create_tables()
    db = SessionLocal()
    
    try:
        # Create sample data
        print("\n📚 Setting up comprehensive educational database...")
        create_sample_data(db)
        
        # Get pharmacy subject and topics
        from app.models.question import Subject, Topic
        pharmacy_subject = db.query(Subject).filter(Subject.code == "PHARM").first()
        
        if not pharmacy_subject:
            print("❌ Pharmacy subject not found. Please run sample data creation first.")
            return
        
        pharmacy_topics = db.query(Topic).filter(Topic.subject_id == pharmacy_subject.id).all()
        
        print(f"\n✅ Found Pharmacy subject with {len(pharmacy_topics)} topics:")
        for topic in pharmacy_topics:
            print(f"   📖 {topic.name}: {topic.description}")
        
        # Demo 1: Pharmacology MCQ
        print("\n" + "="*60)
        print("🧪 DEMO 1: Pharmacology Multiple Choice Question")
        print("="*60)
        
        pharmacology_topic = next((t for t in pharmacy_topics if "Pharmacology" in t.name), None)
        if pharmacology_topic:
            success, message, questions = await ai_question_generator.generate_questions(
                subject_id=str(pharmacy_subject.id),
                topic_id=str(pharmacology_topic.id),
                question_type=QuestionType.MULTIPLE_CHOICE,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                count=1,
                grade_level="PharmD",
                learning_objective="Understand drug mechanisms of action",
                context="Cardiovascular pharmacology for heart failure treatment",
                db=db
            )
            
            if success and questions:
                print("✅ Generated Pharmacology Question:")
                print_question_details(questions[0])
            else:
                print(f"❌ Generation failed: {message}")
        
        # Demo 2: Clinical Pharmacy Case
        print("\n" + "="*60)
        print("🏥 DEMO 2: Clinical Pharmacy Case Question")
        print("="*60)
        
        clinical_topic = next((t for t in pharmacy_topics if "Clinical" in t.name), None)
        if clinical_topic:
            success, message, questions = await ai_question_generator.generate_questions(
                subject_id=str(pharmacy_subject.id),
                topic_id=str(clinical_topic.id),
                question_type=QuestionType.SHORT_ANSWER,
                difficulty_level=DifficultyLevel.ADVANCED,
                count=1,
                grade_level="PharmD",
                learning_objective="Apply pharmaceutical care principles",
                context="Patient with diabetes and hypertension requiring medication therapy management",
                db=db
            )
            
            if success and questions:
                print("✅ Generated Clinical Pharmacy Question:")
                print_question_details(questions[0])
            else:
                print(f"❌ Generation failed: {message}")
        
        # Demo 3: Pharmacokinetics Calculation
        print("\n" + "="*60)
        print("📊 DEMO 3: Pharmacokinetics Calculation")
        print("="*60)
        
        pk_topic = next((t for t in pharmacy_topics if "Pharmacokinetics" in t.name), None)
        if pk_topic:
            success, message, questions = await ai_question_generator.generate_questions(
                subject_id=str(pharmacy_subject.id),
                topic_id=str(pk_topic.id),
                question_type=QuestionType.MULTIPLE_CHOICE,
                difficulty_level=DifficultyLevel.ADVANCED,
                count=1,
                grade_level="PharmD",
                learning_objective="Calculate pharmacokinetic parameters",
                context="Bioavailability and bioequivalence calculations for generic drug approval",
                db=db
            )
            
            if success and questions:
                print("✅ Generated Pharmacokinetics Question:")
                print_question_details(questions[0])
            else:
                print(f"❌ Generation failed: {message}")
        
        # Demo 4: Other Professional Fields
        print("\n" + "="*60)
        print("🌟 DEMO 4: Other Professional Fields")
        print("="*60)
        
        # Medicine
        med_subject = db.query(Subject).filter(Subject.code == "MED").first()
        if med_subject:
            med_topics = db.query(Topic).filter(Topic.subject_id == med_subject.id).all()
            if med_topics:
                success, message, questions = await ai_question_generator.generate_questions(
                    subject_id=str(med_subject.id),
                    topic_id=str(med_topics[0].id),
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    difficulty_level=DifficultyLevel.ADVANCED,
                    count=1,
                    grade_level="MD",
                    learning_objective="Diagnose cardiovascular conditions",
                    context="Emergency department patient with chest pain",
                    db=db
                )
                
                if success and questions:
                    print("✅ Generated Medicine Question:")
                    print_question_details(questions[0])
        
        # Computer Science
        cs_subject = db.query(Subject).filter(Subject.code == "CS").first()
        if cs_subject:
            cs_topics = db.query(Topic).filter(Topic.subject_id == cs_subject.id).all()
            if cs_topics:
                success, message, questions = await ai_question_generator.generate_questions(
                    subject_id=str(cs_subject.id),
                    topic_id=str(cs_topics[0].id),
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    count=1,
                    grade_level="Undergraduate",
                    learning_objective="Analyze algorithm complexity",
                    context="Software engineering interview preparation",
                    db=db
                )
                
                if success and questions:
                    print("✅ Generated Computer Science Question:")
                    print_question_details(questions[0])
        
        # Summary
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE COVERAGE SUMMARY")
        print("="*60)
        
        all_subjects = db.query(Subject).all()
        print(f"📚 Total Subjects Available: {len(all_subjects)}")
        
        for subject in all_subjects:
            topic_count = db.query(Topic).filter(Topic.subject_id == subject.id).count()
            print(f"   🎯 {subject.name} ({subject.code}): {topic_count} topics")
        
        print("\n🎉 MEDHASAKTHI supports ALL educational categories:")
        print("   🏥 Medical & Health Sciences (Pharmacy, Medicine, Nursing)")
        print("   🔧 Engineering & Technology (CS, EE, ME)")
        print("   💼 Business & Economics")
        print("   🧪 Natural Sciences (Chemistry, Physics, Biology)")
        print("   📚 Social Sciences & Humanities")
        print("   ⚖️ Law & Legal Studies")
        print("   🎓 Education")
        print("   📐 Mathematics")
        print("   🌾 Agriculture & Environmental Science")
        print("   🏗️ Architecture & Design")
        
        print("\n✨ SPECIAL FEATURES FOR PROFESSIONAL FIELDS:")
        print("   💊 Pharmacy: Clinical cases, drug calculations, therapeutic monitoring")
        print("   🩺 Medicine: Diagnostic scenarios, treatment planning, case analysis")
        print("   💻 Engineering: Design problems, technical analysis, calculations")
        print("   ⚖️ Law: Case analysis, statutory interpretation, legal reasoning")
        print("   💼 Business: Strategic planning, financial analysis, case studies")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def print_question_details(question_data):
    """Print formatted question details"""
    print(f"\n📝 Question: {question_data.get('question_text', 'N/A')}")
    
    if question_data.get('options'):
        print("\n📋 Options:")
        for option in question_data['options']:
            marker = "✅" if option.get('is_correct') else "❌"
            print(f"   {option['id']}) {option['text']} {marker}")
    
    if question_data.get('correct_answer'):
        print(f"\n✅ Correct Answer: {question_data['correct_answer']}")
    
    if question_data.get('explanation'):
        print(f"\n💡 Explanation: {question_data['explanation']}")
    
    if question_data.get('keywords'):
        print(f"\n🏷️ Keywords: {', '.join(question_data['keywords'])}")
    
    print(f"\n📊 Difficulty: {question_data.get('difficulty_level', 'N/A')}")
    print(f"🎯 Type: {question_data.get('question_type', 'N/A')}")
    print(f"⏱️ Estimated Time: {question_data.get('estimated_time', 'N/A')} seconds")


def show_comprehensive_subjects():
    """Show all available subjects and their coverage"""
    print("\n📚 COMPREHENSIVE EDUCATIONAL COVERAGE")
    print("="*60)
    
    for category, subjects in {
        "🏥 MEDICAL & HEALTH SCIENCES": ["PHARM", "MED", "NURS"],
        "🔧 ENGINEERING & TECHNOLOGY": ["CS", "EE", "ME"],
        "💼 BUSINESS & ECONOMICS": ["BUS", "ECON"],
        "🧪 NATURAL SCIENCES": ["CHEM", "PHYS", "BIO"],
        "📚 SOCIAL SCIENCES": ["PSYC", "SOC"],
        "⚖️ LAW & LEGAL": ["LAW"],
        "🎓 EDUCATION": ["EDU"],
        "📐 MATHEMATICS": ["MATH"],
        "🌾 AGRICULTURE": ["AGRI"],
        "🏗️ ARCHITECTURE": ["ARCH"]
    }.items():
        print(f"\n{category}:")
        for subject_code in subjects:
            if subject_code in COMPREHENSIVE_SUBJECTS:
                subject_info = COMPREHENSIVE_SUBJECTS[subject_code]
                topic_count = len(subject_info.get("topics", []))
                print(f"   📖 {subject_info['name']} ({subject_code}): {topic_count} topics")


if __name__ == "__main__":
    print("🚀 Starting MEDHASAKTHI Pharmacy & Professional Education Demo...")
    
    # Show comprehensive coverage
    show_comprehensive_subjects()
    
    # Run the demo
    asyncio.run(demo_pharmacy_question_generation())
    
    print("\n🎉 Demo completed! MEDHASAKTHI is ready for ALL educational categories!")
    print("💊 Pharmacy questions: ✅ Fully supported with specialized prompts")
    print("🏥 Medical questions: ✅ Clinical cases and diagnostic scenarios") 
    print("🔧 Engineering questions: ✅ Technical analysis and design problems")
    print("💼 Business questions: ✅ Strategic planning and case studies")
    print("📚 All other fields: ✅ Comprehensive coverage with specialized features")
