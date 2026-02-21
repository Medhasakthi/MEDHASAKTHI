"""
Sample data initialization for MEDHASAKTHI
"""
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.user import User, UserProfile, Institute, Student, Teacher, UserRole, SubscriptionPlan
from app.models.question import Subject, Topic, Question, QuestionType, DifficultyLevel, QuestionStatus
from app.core.security import security_manager


def create_sample_data(db: Session):
    """Create sample data for development and testing"""

    # Import comprehensive subjects including Indian education system and professional certifications
    from app.utils.comprehensive_subjects import COMPREHENSIVE_SUBJECTS
    from app.utils.indian_education_system import INDIAN_EDUCATION_SYSTEM
    from app.utils.professional_certifications import PROFESSIONAL_CERTIFICATIONS

    # Create comprehensive subjects covering ALL Indian educational fields
    subjects_data = [
        # Medical & Health Sciences (Indian System)
        {"name": "Pharmacy", "code": "PHARM", "description": "Pharmaceutical sciences, drug development, and clinical pharmacy (B.Pharm, M.Pharm, Pharm.D)"},
        {"name": "Medicine", "code": "MBBS", "description": "Bachelor of Medicine and Bachelor of Surgery - Indian medical education"},
        {"name": "Dentistry", "code": "BDS", "description": "Bachelor of Dental Surgery - Indian dental education"},
        {"name": "Ayurveda", "code": "BAMS", "description": "Bachelor of Ayurvedic Medicine and Surgery - Traditional Indian medicine"},
        {"name": "Homeopathy", "code": "BHMS", "description": "Bachelor of Homeopathic Medicine and Surgery"},
        {"name": "Unani Medicine", "code": "BUMS", "description": "Bachelor of Unani Medicine and Surgery"},
        {"name": "Nursing", "code": "NURS", "description": "Bachelor of Science in Nursing - Indian nursing education"},
        {"name": "Physiotherapy", "code": "BPT", "description": "Bachelor of Physiotherapy - Indian physiotherapy education"},
        {"name": "Veterinary Science", "code": "BVSC", "description": "Bachelor of Veterinary Science - Indian veterinary education"},

        # Engineering & Technology (Indian System)
        {"name": "Computer Science Engineering", "code": "CSE", "description": "Computer Science and Engineering - Indian engineering education"},
        {"name": "Information Technology", "code": "IT", "description": "Information Technology engineering"},
        {"name": "Electronics & Communication", "code": "ECE", "description": "Electronics and Communication Engineering"},
        {"name": "Electrical Engineering", "code": "EE", "description": "Electrical Engineering - Indian curriculum"},
        {"name": "Mechanical Engineering", "code": "ME", "description": "Mechanical Engineering - Indian curriculum"},
        {"name": "Civil Engineering", "code": "CE", "description": "Civil Engineering - Indian curriculum"},
        {"name": "Chemical Engineering", "code": "CHE", "description": "Chemical Engineering - Indian curriculum"},
        {"name": "Biotechnology", "code": "BT", "description": "Biotechnology Engineering"},
        {"name": "Aerospace Engineering", "code": "AE", "description": "Aerospace Engineering"},
        {"name": "Automobile Engineering", "code": "AUTO", "description": "Automobile Engineering"},

        # Management & Business (Indian System)
        {"name": "Business Administration", "code": "MBA", "description": "Master of Business Administration - Indian MBA programs"},
        {"name": "Bachelor of Business Administration", "code": "BBA", "description": "Bachelor of Business Administration"},
        {"name": "Commerce", "code": "BCOM", "description": "Bachelor of Commerce - Indian commerce education"},

        # Law (Indian System)
        {"name": "Law", "code": "LLB", "description": "Bachelor of Laws - Indian legal education"},
        {"name": "Integrated Law", "code": "BA_LLB", "description": "Bachelor of Arts and Bachelor of Laws - 5-year integrated program"},

        # Pure Sciences (Indian System)
        {"name": "Physics", "code": "BSC_PHYS", "description": "Bachelor of Science in Physics - Indian curriculum"},
        {"name": "Chemistry", "code": "BSC_CHEM", "description": "Bachelor of Science in Chemistry - Indian curriculum"},
        {"name": "Mathematics", "code": "BSC_MATH", "description": "Bachelor of Science in Mathematics - Indian curriculum"},
        {"name": "Biology", "code": "BSC_BIO", "description": "Bachelor of Science in Biology - Indian curriculum"},

        # Agriculture (Indian System)
        {"name": "Agriculture", "code": "BSC_AG", "description": "Bachelor of Science in Agriculture - Indian agricultural education"},
        {"name": "Food Technology", "code": "BTECH_FOOD", "description": "Food Technology - Indian food science education"},

        # Arts & Humanities (Indian System)
        {"name": "English Literature", "code": "BA_ENG", "description": "Bachelor of Arts in English - Indian curriculum"},
        {"name": "Hindi Literature", "code": "BA_HINDI", "description": "Bachelor of Arts in Hindi - Indian curriculum"},
        {"name": "History", "code": "BA_HIST", "description": "Bachelor of Arts in History - Indian curriculum"},
        {"name": "Political Science", "code": "BA_POL", "description": "Bachelor of Arts in Political Science - Indian curriculum"},
        {"name": "Economics", "code": "BA_ECON", "description": "Bachelor of Arts in Economics - Indian curriculum"},
        {"name": "Psychology", "code": "BA_PSYC", "description": "Bachelor of Arts in Psychology - Indian curriculum"},
        {"name": "Sociology", "code": "BA_SOC", "description": "Bachelor of Arts in Sociology - Indian curriculum"},

        # Education (Indian System)
        {"name": "Education", "code": "BED", "description": "Bachelor of Education - Indian teacher training"},
        {"name": "Elementary Education", "code": "DELED", "description": "Diploma in Elementary Education"},

        # Design & Fine Arts (Indian System)
        {"name": "Design", "code": "BDES", "description": "Bachelor of Design - Indian design education"},
        {"name": "Fine Arts", "code": "BFA", "description": "Bachelor of Fine Arts - Indian fine arts education"},
        {"name": "Architecture", "code": "BARCH", "description": "Bachelor of Architecture - Indian architecture education"},

        # Hotel Management & Tourism (Indian System)
        {"name": "Hotel Management", "code": "BHM", "description": "Bachelor of Hotel Management - Indian hospitality education"},
        {"name": "Tourism Studies", "code": "BTS", "description": "Bachelor of Tourism Studies"},

        # School Education (Indian Boards)
        {"name": "CBSE Class 10", "code": "CBSE_10", "description": "Central Board of Secondary Education - Class 10"},
        {"name": "CBSE Class 12", "code": "CBSE_12", "description": "Central Board of Secondary Education - Class 12"},
        {"name": "ICSE Class 10", "code": "ICSE_10", "description": "Indian Certificate of Secondary Education - Class 10"},
        {"name": "State Board Class 10", "code": "STATE_10", "description": "State Board Secondary Education - Class 10"},
        {"name": "State Board Class 12", "code": "STATE_12", "description": "State Board Higher Secondary Education - Class 12"},

        # Professional Certifications & Specialized Courses
        # Cloud Computing
        {"name": "AWS Certifications", "code": "AWS", "description": "Amazon Web Services cloud computing certifications"},
        {"name": "Microsoft Azure", "code": "AZURE", "description": "Microsoft Azure cloud platform certifications"},
        {"name": "Google Cloud Platform", "code": "GCP", "description": "Google Cloud Platform certifications"},

        # Programming Languages
        {"name": "Python Programming", "code": "PYTHON", "description": "Python programming language and frameworks"},
        {"name": "Java Programming", "code": "JAVA", "description": "Java programming language and enterprise development"},
        {"name": "JavaScript Development", "code": "JAVASCRIPT", "description": "JavaScript programming for web and mobile development"},
        {"name": "C# Programming", "code": "CSHARP", "description": "C# programming and .NET framework development"},
        {"name": "C++ Programming", "code": "CPP", "description": "C++ programming for systems and game development"},

        # DevOps & Automation
        {"name": "Docker Containerization", "code": "DOCKER", "description": "Docker container technology and orchestration"},
        {"name": "Kubernetes", "code": "KUBERNETES", "description": "Kubernetes container orchestration platform"},
        {"name": "Jenkins CI/CD", "code": "JENKINS", "description": "Jenkins continuous integration and deployment"},
        {"name": "Terraform", "code": "TERRAFORM", "description": "Infrastructure as Code with Terraform"},

        # Financial Certifications
        {"name": "Chartered Accountancy", "code": "CA", "description": "Indian Chartered Accountancy certification"},
        {"name": "Company Secretary", "code": "CS", "description": "Company Secretary certification"},
        {"name": "Cost Management Accountant", "code": "CMA", "description": "Cost and Management Accountant certification"},
        {"name": "Chartered Financial Analyst", "code": "CFA", "description": "CFA Institute Chartered Financial Analyst"},

        # Data Science & Analytics
        {"name": "Data Science", "code": "DATA_SCIENCE", "description": "Data science, machine learning, and analytics"},
        {"name": "Machine Learning", "code": "ML", "description": "Machine learning and artificial intelligence"},
        {"name": "Big Data Analytics", "code": "BIG_DATA", "description": "Big data technologies and analytics"},

        # Cybersecurity
        {"name": "Cybersecurity", "code": "CYBERSEC", "description": "Information security and cybersecurity certifications"},
        {"name": "Ethical Hacking", "code": "CEH", "description": "Certified Ethical Hacker and penetration testing"},

        # Project Management
        {"name": "Project Management", "code": "PMP", "description": "Project Management Professional and methodologies"},
        {"name": "Scrum & Agile", "code": "SCRUM", "description": "Scrum Master and Agile project management"},

        # Digital Marketing
        {"name": "Digital Marketing", "code": "DIGITAL_MKT", "description": "Digital marketing and online advertising"},
        {"name": "SEO & SEM", "code": "SEO", "description": "Search Engine Optimization and Marketing"},

        # Design & Creative
        {"name": "UI/UX Design", "code": "UIUX", "description": "User Interface and User Experience design"},
        {"name": "Adobe Creative Suite", "code": "ADOBE", "description": "Adobe Photoshop, Illustrator, and creative tools"},
    ]
    
    subjects = {}
    for subject_data in subjects_data:
        existing = db.query(Subject).filter(Subject.code == subject_data["code"]).first()
        if not existing:
            subject = Subject(**subject_data)
            db.add(subject)
            db.flush()
            subjects[subject_data["code"]] = subject
        else:
            subjects[subject_data["code"]] = existing
    
    # Create comprehensive topics including Pharmacy
    topics_data = [
        # Pharmacy Topics
        {
            "subject_code": "PHARM",
            "name": "Pharmacology",
            "description": "Study of drug action, mechanisms, and effects",
            "learning_objectives": [
                "Understand drug-receptor interactions",
                "Analyze pharmacokinetics and pharmacodynamics",
                "Evaluate drug safety and efficacy",
                "Apply dose-response relationships"
            ]
        },
        {
            "subject_code": "PHARM",
            "name": "Clinical Pharmacy",
            "description": "Patient care and therapeutic drug monitoring",
            "learning_objectives": [
                "Provide pharmaceutical care",
                "Monitor drug therapy outcomes",
                "Counsel patients on medication use",
                "Collaborate with healthcare teams"
            ]
        },
        {
            "subject_code": "PHARM",
            "name": "Pharmaceutical Chemistry",
            "description": "Chemical properties and synthesis of drugs",
            "learning_objectives": [
                "Analyze drug structure-activity relationships",
                "Understand chemical synthesis pathways",
                "Evaluate drug stability and formulation"
            ]
        },
        {
            "subject_code": "PHARM",
            "name": "Pharmacokinetics",
            "description": "Drug absorption, distribution, metabolism, and excretion",
            "learning_objectives": [
                "Calculate pharmacokinetic parameters",
                "Predict drug behavior in the body",
                "Design dosing regimens"
            ]
        },

        # Medicine Topics
        {
            "subject_code": "MED",
            "name": "Internal Medicine",
            "description": "Adult disease diagnosis and treatment",
            "learning_objectives": ["Diagnose common diseases", "Develop treatment plans", "Monitor patient outcomes"]
        },
        {
            "subject_code": "MED",
            "name": "Cardiology",
            "description": "Heart and cardiovascular system diseases",
            "learning_objectives": ["Interpret ECGs", "Diagnose heart conditions", "Manage cardiovascular risk"]
        },

        # Computer Science Topics
        {
            "subject_code": "CS",
            "name": "Data Structures",
            "description": "Organization and storage of data",
            "learning_objectives": ["Implement arrays and linked lists", "Understand trees and graphs", "Analyze algorithm complexity"]
        },
        {
            "subject_code": "CS",
            "name": "Algorithms",
            "description": "Problem-solving procedures and efficiency",
            "learning_objectives": ["Design efficient algorithms", "Analyze time complexity", "Implement sorting and searching"]
        },

        # Mathematics Topics
        {
            "subject_code": "MATH",
            "name": "Calculus",
            "description": "Differential and integral calculus",
            "learning_objectives": ["Compute derivatives", "Evaluate integrals", "Apply calculus to real problems"]
        },
        {
            "subject_code": "MATH",
            "name": "Statistics",
            "description": "Data analysis and probability theory",
            "learning_objectives": ["Analyze statistical data", "Calculate probabilities", "Perform hypothesis testing"]
        },

        # Chemistry Topics
        {
            "subject_code": "CHEM",
            "name": "Organic Chemistry",
            "description": "Carbon-based compounds and reactions",
            "learning_objectives": ["Understand organic reactions", "Predict reaction mechanisms", "Synthesize organic compounds"]
        },

        # Business Topics
        {
            "subject_code": "BUS",
            "name": "Strategic Management",
            "description": "Business strategy and competitive advantage",
            "learning_objectives": ["Develop business strategies", "Analyze competitive environments", "Implement strategic plans"]
        },

        # Professional Certification Topics
        # AWS Topics
        {
            "subject_code": "AWS",
            "name": "AWS Solutions Architecture",
            "description": "Designing scalable and resilient AWS architectures",
            "learning_objectives": [
                "Design highly available architectures",
                "Implement cost-effective solutions",
                "Ensure security best practices",
                "Optimize performance"
            ]
        },
        {
            "subject_code": "AWS",
            "name": "AWS Security",
            "description": "AWS security services and best practices",
            "learning_objectives": [
                "Implement identity and access management",
                "Secure data in transit and at rest",
                "Monitor and log security events",
                "Respond to security incidents"
            ]
        },

        # Python Topics
        {
            "subject_code": "PYTHON",
            "name": "Python Web Development",
            "description": "Building web applications with Python frameworks",
            "learning_objectives": [
                "Develop web applications using Django/Flask",
                "Implement RESTful APIs",
                "Handle database operations",
                "Deploy Python applications"
            ]
        },
        {
            "subject_code": "PYTHON",
            "name": "Python Data Science",
            "description": "Data analysis and machine learning with Python",
            "learning_objectives": [
                "Analyze data using Pandas and NumPy",
                "Create visualizations with Matplotlib",
                "Build machine learning models",
                "Process and clean data"
            ]
        },

        # Java Topics
        {
            "subject_code": "JAVA",
            "name": "Java Enterprise Development",
            "description": "Enterprise Java development with Spring framework",
            "learning_objectives": [
                "Develop enterprise applications",
                "Implement microservices architecture",
                "Use Spring Boot and Spring Security",
                "Handle database transactions"
            ]
        },

        # Docker Topics
        {
            "subject_code": "DOCKER",
            "name": "Container Fundamentals",
            "description": "Docker containerization concepts and practices",
            "learning_objectives": [
                "Create and manage Docker containers",
                "Build optimized Docker images",
                "Implement container networking",
                "Use Docker Compose for multi-container apps"
            ]
        },

        # CA Topics
        {
            "subject_code": "CA",
            "name": "Financial Accounting",
            "description": "Principles and practices of financial accounting",
            "learning_objectives": [
                "Prepare financial statements",
                "Apply accounting standards",
                "Handle complex transactions",
                "Ensure regulatory compliance"
            ]
        },
        {
            "subject_code": "CA",
            "name": "Taxation",
            "description": "Direct and indirect tax laws and compliance",
            "learning_objectives": [
                "Calculate income tax liability",
                "Handle GST compliance",
                "Plan tax strategies",
                "File tax returns"
            ]
        },

        # Data Science Topics
        {
            "subject_code": "DATA_SCIENCE",
            "name": "Machine Learning",
            "description": "Machine learning algorithms and applications",
            "learning_objectives": [
                "Implement supervised learning algorithms",
                "Apply unsupervised learning techniques",
                "Evaluate model performance",
                "Deploy ML models in production"
            ]
        },

        # Cybersecurity Topics
        {
            "subject_code": "CYBERSEC",
            "name": "Network Security",
            "description": "Securing network infrastructure and communications",
            "learning_objectives": [
                "Implement network security controls",
                "Monitor network traffic",
                "Detect and respond to threats",
                "Configure firewalls and IDS"
            ]
        },

        # Digital Marketing Topics
        {
            "subject_code": "DIGITAL_MKT",
            "name": "Google Ads",
            "description": "Google Ads campaign management and optimization",
            "learning_objectives": [
                "Create effective ad campaigns",
                "Optimize ad performance",
                "Analyze campaign metrics",
                "Manage advertising budgets"
            ]
        },

        # UI/UX Design Topics
        {
            "subject_code": "UIUX",
            "name": "User Experience Design",
            "description": "Designing user-centered digital experiences",
            "learning_objectives": [
                "Conduct user research",
                "Create user personas and journeys",
                "Design wireframes and prototypes",
                "Test and iterate designs"
            ]
        }
    ]
    
    topics = {}
    for topic_data in topics_data:
        subject = subjects[topic_data["subject_code"]]
        existing = db.query(Topic).filter(
            Topic.subject_id == subject.id,
            Topic.name == topic_data["name"]
        ).first()
        
        if not existing:
            topic = Topic(
                subject_id=subject.id,
                name=topic_data["name"],
                description=topic_data["description"],
                learning_objectives=topic_data["learning_objectives"]
            )
            db.add(topic)
            db.flush()
            topics[f"{topic_data['subject_code']}_{topic_data['name']}"] = topic
        else:
            topics[f"{topic_data['subject_code']}_{topic_data['name']}"] = existing
    
    # Create sample institute
    existing_institute = db.query(Institute).filter(Institute.code == "DEMO001").first()
    if not existing_institute:
        # Create institute admin user first
        admin_password = security_manager.hash_password("admin123!")
        admin_user = User(
            email="admin@demo-school.edu",
            password_hash=admin_password,
            role=UserRole.INSTITUTE_ADMIN.value,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        db.flush()
        
        # Create admin profile
        admin_profile = UserProfile(
            user_id=admin_user.id,
            first_name="Demo",
            last_name="Administrator",
            phone="+1234567890"
        )
        db.add(admin_profile)
        
        # Create institute
        institute = Institute(
            name="Demo High School",
            code="DEMO001",
            admin_user_id=admin_user.id,
            description="A demonstration school for MEDHASAKTHI platform",
            subscription_plan=SubscriptionPlan.PREMIUM.value,
            max_students=1000,
            max_teachers=50,
            is_active=True,
            is_verified=True
        )
        db.add(institute)
        db.flush()
    else:
        institute = existing_institute
        admin_user = db.query(User).filter(User.id == institute.admin_user_id).first()
    
    # Create sample teacher
    existing_teacher_user = db.query(User).filter(User.email == "teacher@demo-school.edu").first()
    if not existing_teacher_user:
        teacher_password = security_manager.hash_password("teacher123!")
        teacher_user = User(
            email="teacher@demo-school.edu",
            password_hash=teacher_password,
            role=UserRole.TEACHER.value,
            is_active=True,
            is_verified=True
        )
        db.add(teacher_user)
        db.flush()
        
        # Create teacher profile
        teacher_profile = UserProfile(
            user_id=teacher_user.id,
            first_name="Jane",
            last_name="Smith",
            phone="+1234567891"
        )
        db.add(teacher_profile)
        
        # Create teacher record
        teacher = Teacher(
            user_id=teacher_user.id,
            institute_id=institute.id,
            employee_id="TEACH001",
            subjects=["Mathematics", "Science"],
            experience_years=5
        )
        db.add(teacher)
    else:
        teacher_user = existing_teacher_user
    
    # Create sample student
    existing_student_user = db.query(User).filter(User.email == "student@demo-school.edu").first()
    if not existing_student_user:
        student_password = security_manager.hash_password("student123!")
        student_user = User(
            email="student@demo-school.edu",
            password_hash=student_password,
            role=UserRole.STUDENT.value,
            is_active=True,
            is_verified=True
        )
        db.add(student_user)
        db.flush()
        
        # Create student profile
        student_profile = UserProfile(
            user_id=student_user.id,
            first_name="John",
            last_name="Doe",
            phone="+1234567892"
        )
        db.add(student_profile)
        
        # Create student record
        student = Student(
            user_id=student_user.id,
            institute_id=institute.id,
            student_id="STU001",
            grade_level="10",
            class_section="A",
            academic_year="2024"
        )
        db.add(student)
    
    # Create comprehensive sample questions including Pharmacy
    sample_questions = [
        # Pharmacy Questions
        {
            "question_text": "A 65-year-old patient with heart failure is prescribed digoxin 0.25mg daily. Which of the following parameters should be monitored most closely?",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "subject_code": "PHARM",
            "topic_name": "Clinical Pharmacy",
            "grade_level": "PharmD",
            "options": [
                {"id": "A", "text": "Blood pressure", "is_correct": False},
                {"id": "B", "text": "Serum potassium and digoxin levels", "is_correct": True},
                {"id": "C", "text": "Liver function tests", "is_correct": False},
                {"id": "D", "text": "Complete blood count", "is_correct": False}
            ],
            "explanation": "Digoxin has a narrow therapeutic index. Hypokalemia increases digoxin toxicity risk, and serum digoxin levels must be monitored to ensure therapeutic range (1-2 ng/mL).",
            "keywords": ["digoxin", "therapeutic drug monitoring", "heart failure", "clinical pharmacy"]
        },
        {
            "question_text": "Calculate the bioavailability of a drug if the AUC after oral administration is 80 mg·h/L and the AUC after IV administration is 100 mg·h/L (same dose).",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.ADVANCED.value,
            "subject_code": "PHARM",
            "topic_name": "Pharmacokinetics",
            "grade_level": "PharmD",
            "options": [
                {"id": "A", "text": "60%", "is_correct": False},
                {"id": "B", "text": "70%", "is_correct": False},
                {"id": "C", "text": "80%", "is_correct": True},
                {"id": "D", "text": "90%", "is_correct": False}
            ],
            "explanation": "Bioavailability (F) = (AUC_oral / AUC_IV) × 100% = (80/100) × 100% = 80%",
            "keywords": ["bioavailability", "pharmacokinetics", "AUC", "calculation"]
        },
        {
            "question_text": "Which mechanism of action is responsible for the therapeutic effect of ACE inhibitors in treating hypertension?",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "subject_code": "PHARM",
            "topic_name": "Pharmacology",
            "grade_level": "PharmD",
            "options": [
                {"id": "A", "text": "Blocking calcium channels", "is_correct": False},
                {"id": "B", "text": "Inhibiting angiotensin-converting enzyme", "is_correct": True},
                {"id": "C", "text": "Blocking beta-adrenergic receptors", "is_correct": False},
                {"id": "D", "text": "Inhibiting sodium-potassium pump", "is_correct": False}
            ],
            "explanation": "ACE inhibitors block the conversion of angiotensin I to angiotensin II, reducing vasoconstriction and aldosterone secretion, thereby lowering blood pressure.",
            "keywords": ["ACE inhibitors", "hypertension", "mechanism of action", "pharmacology"]
        },

        # Medicine Questions
        {
            "question_text": "A 45-year-old male presents with chest pain, diaphoresis, and shortness of breath. ECG shows ST-elevation in leads II, III, and aVF. What is the most likely diagnosis?",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.ADVANCED.value,
            "subject_code": "MED",
            "topic_name": "Cardiology",
            "grade_level": "MD",
            "options": [
                {"id": "A", "text": "Anterior STEMI", "is_correct": False},
                {"id": "B", "text": "Inferior STEMI", "is_correct": True},
                {"id": "C", "text": "Lateral STEMI", "is_correct": False},
                {"id": "D", "text": "Unstable angina", "is_correct": False}
            ],
            "explanation": "ST-elevation in leads II, III, and aVF indicates inferior wall myocardial infarction, typically due to right coronary artery occlusion.",
            "keywords": ["STEMI", "myocardial infarction", "ECG", "cardiology"]
        },

        # Computer Science Questions
        {
            "question_text": "What is the time complexity of searching for an element in a balanced binary search tree?",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "subject_code": "CS",
            "topic_name": "Data Structures",
            "grade_level": "Undergraduate",
            "options": [
                {"id": "A", "text": "O(1)", "is_correct": False},
                {"id": "B", "text": "O(log n)", "is_correct": True},
                {"id": "C", "text": "O(n)", "is_correct": False},
                {"id": "D", "text": "O(n²)", "is_correct": False}
            ],
            "explanation": "In a balanced BST, the height is log n, so search operations take O(log n) time in the average and best case.",
            "keywords": ["binary search tree", "time complexity", "algorithms", "data structures"]
        },

        # Mathematics Questions
        {
            "question_text": "What is the derivative of f(x) = 3x² + 2x - 5?",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "subject_code": "MATH",
            "topic_name": "Calculus",
            "grade_level": "Undergraduate",
            "options": [
                {"id": "A", "text": "6x + 2", "is_correct": True},
                {"id": "B", "text": "6x - 5", "is_correct": False},
                {"id": "C", "text": "3x + 2", "is_correct": False},
                {"id": "D", "text": "6x² + 2x", "is_correct": False}
            ],
            "explanation": "Using the power rule: d/dx(3x²) = 6x, d/dx(2x) = 2, d/dx(-5) = 0. Therefore, f'(x) = 6x + 2.",
            "keywords": ["derivative", "calculus", "power rule", "differentiation"]
        },

        # Chemistry Questions
        {
            "question_text": "What type of reaction occurs when an alkene reacts with hydrogen gas in the presence of a catalyst?",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "subject_code": "CHEM",
            "topic_name": "Organic Chemistry",
            "grade_level": "Undergraduate",
            "options": [
                {"id": "A", "text": "Substitution", "is_correct": False},
                {"id": "B", "text": "Elimination", "is_correct": False},
                {"id": "C", "text": "Addition (Hydrogenation)", "is_correct": True},
                {"id": "D", "text": "Oxidation", "is_correct": False}
            ],
            "explanation": "Hydrogenation is an addition reaction where hydrogen atoms are added across the double bond of an alkene, typically using Pd, Pt, or Ni catalysts.",
            "keywords": ["hydrogenation", "alkene", "addition reaction", "organic chemistry"]
        },

        # Business Questions
        {
            "question_text": "Which of the following is NOT one of Porter's Five Forces?",
            "question_type": QuestionType.MULTIPLE_CHOICE.value,
            "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
            "subject_code": "BUS",
            "topic_name": "Strategic Management",
            "grade_level": "MBA",
            "options": [
                {"id": "A", "text": "Threat of new entrants", "is_correct": False},
                {"id": "B", "text": "Bargaining power of suppliers", "is_correct": False},
                {"id": "C", "text": "Threat of substitute products", "is_correct": False},
                {"id": "D", "text": "Market share concentration", "is_correct": True}
            ],
            "explanation": "Porter's Five Forces include: threat of new entrants, bargaining power of suppliers, bargaining power of buyers, threat of substitutes, and competitive rivalry. Market share concentration is not one of the five forces.",
            "keywords": ["Porter's Five Forces", "strategic management", "competitive analysis", "business strategy"]
        }
    ]
    
    for q_data in sample_questions:
        subject = subjects[q_data["subject_code"]]
        topic = topics[f"{q_data['subject_code']}_{q_data['topic_name']}"]
        
        existing = db.query(Question).filter(
            Question.question_text == q_data["question_text"]
        ).first()
        
        if not existing:
            question = Question(
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                difficulty_level=q_data["difficulty_level"],
                subject_id=subject.id,
                topic_id=topic.id,
                grade_level=q_data["grade_level"],
                options=q_data.get("options"),
                correct_answer=q_data.get("correct_answer"),
                explanation=q_data["explanation"],
                keywords=q_data["keywords"],
                status=QuestionStatus.APPROVED.value,
                created_by=teacher_user.id,
                approved_by=admin_user.id,
                approved_at=datetime.utcnow()
            )
            db.add(question)
    
    # Commit all changes
    db.commit()
    
    print("✅ Sample data created successfully!")
    print("\n📚 Sample Accounts Created:")
    print("🔑 Institute Admin: admin@demo-school.edu / admin123!")
    print("👨‍🏫 Teacher: teacher@demo-school.edu / teacher123!")
    print("👨‍🎓 Student: student@demo-school.edu / student123!")
    print("\n🏫 Institute: Demo High School (Code: DEMO001)")
    print(f"📖 Subjects: {len(subjects_data)} created")
    print(f"📝 Topics: {len(topics_data)} created")
    print(f"❓ Sample Questions: {len(sample_questions)} created")


def reset_sample_data(db: Session):
    """Reset sample data (for development only)"""
    print("⚠️ Resetting sample data...")
    
    # Delete in reverse order of dependencies
    db.query(Question).delete()
    db.query(Topic).delete()
    db.query(Subject).delete()
    db.query(Student).delete()
    db.query(Teacher).delete()
    db.query(Institute).delete()
    db.query(UserProfile).delete()
    db.query(User).delete()
    
    db.commit()
    print("🗑️ Sample data reset complete!")


if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        create_sample_data(db)
    finally:
        db.close()
