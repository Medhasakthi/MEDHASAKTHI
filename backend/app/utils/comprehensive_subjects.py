"""
Comprehensive educational subjects and categories for MEDHASAKTHI
Covers all major educational fields including professional and specialized areas
"""

# Comprehensive subject taxonomy covering all educational categories
COMPREHENSIVE_SUBJECTS = {
    # MEDICAL & HEALTH SCIENCES
    "PHARMACY": {
        "name": "Pharmacy",
        "code": "PHARM",
        "description": "Pharmaceutical sciences, drug development, and clinical pharmacy",
        "topics": [
            {
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
                "name": "Pharmaceutical Chemistry",
                "description": "Chemical properties and synthesis of drugs",
                "learning_objectives": [
                    "Analyze drug structure-activity relationships",
                    "Understand chemical synthesis pathways",
                    "Evaluate drug stability and formulation",
                    "Apply medicinal chemistry principles"
                ]
            },
            {
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
                "name": "Pharmacokinetics",
                "description": "Drug absorption, distribution, metabolism, and excretion",
                "learning_objectives": [
                    "Calculate pharmacokinetic parameters",
                    "Predict drug behavior in the body",
                    "Design dosing regimens",
                    "Understand bioavailability and bioequivalence"
                ]
            },
            {
                "name": "Pharmaceutical Microbiology",
                "description": "Microbiology applied to pharmaceutical sciences",
                "learning_objectives": [
                    "Understand antimicrobial mechanisms",
                    "Evaluate sterility and contamination",
                    "Apply aseptic techniques",
                    "Assess microbial resistance patterns"
                ]
            }
        ]
    },
    
    "MEDICINE": {
        "name": "Medicine",
        "code": "MED",
        "description": "Medical sciences, diagnosis, and treatment",
        "topics": [
            {"name": "Anatomy", "description": "Human body structure and organization"},
            {"name": "Physiology", "description": "Body functions and processes"},
            {"name": "Pathology", "description": "Disease mechanisms and diagnosis"},
            {"name": "Internal Medicine", "description": "Adult disease diagnosis and treatment"},
            {"name": "Surgery", "description": "Surgical procedures and techniques"}
        ]
    },
    
    "NURSING": {
        "name": "Nursing",
        "code": "NURS",
        "description": "Patient care, health promotion, and nursing practice",
        "topics": [
            {"name": "Fundamentals of Nursing", "description": "Basic nursing principles and skills"},
            {"name": "Medical-Surgical Nursing", "description": "Adult patient care in medical and surgical settings"},
            {"name": "Pediatric Nursing", "description": "Care of infants, children, and adolescents"},
            {"name": "Mental Health Nursing", "description": "Psychiatric and mental health care"},
            {"name": "Community Health Nursing", "description": "Population health and community care"}
        ]
    },
    
    # ENGINEERING & TECHNOLOGY
    "COMPUTER_SCIENCE": {
        "name": "Computer Science",
        "code": "CS",
        "description": "Computing, programming, and information technology",
        "topics": [
            {"name": "Data Structures", "description": "Organization and storage of data"},
            {"name": "Algorithms", "description": "Problem-solving procedures and efficiency"},
            {"name": "Database Systems", "description": "Data management and database design"},
            {"name": "Software Engineering", "description": "Software development methodologies"},
            {"name": "Artificial Intelligence", "description": "Machine learning and AI systems"},
            {"name": "Cybersecurity", "description": "Information security and protection"}
        ]
    },
    
    "ELECTRICAL_ENGINEERING": {
        "name": "Electrical Engineering",
        "code": "EE",
        "description": "Electrical systems, electronics, and power engineering",
        "topics": [
            {"name": "Circuit Analysis", "description": "Electrical circuit theory and analysis"},
            {"name": "Digital Electronics", "description": "Digital systems and logic design"},
            {"name": "Power Systems", "description": "Electrical power generation and distribution"},
            {"name": "Control Systems", "description": "Automatic control and feedback systems"},
            {"name": "Signal Processing", "description": "Signal analysis and processing techniques"}
        ]
    },
    
    "MECHANICAL_ENGINEERING": {
        "name": "Mechanical Engineering",
        "code": "ME",
        "description": "Mechanical systems, thermodynamics, and manufacturing",
        "topics": [
            {"name": "Thermodynamics", "description": "Heat, work, and energy transfer"},
            {"name": "Fluid Mechanics", "description": "Fluid behavior and flow analysis"},
            {"name": "Materials Science", "description": "Properties and behavior of materials"},
            {"name": "Machine Design", "description": "Mechanical component and system design"},
            {"name": "Manufacturing Processes", "description": "Production and manufacturing techniques"}
        ]
    },
    
    # BUSINESS & ECONOMICS
    "BUSINESS_ADMINISTRATION": {
        "name": "Business Administration",
        "code": "BUS",
        "description": "Business management, strategy, and operations",
        "topics": [
            {"name": "Strategic Management", "description": "Business strategy and competitive advantage"},
            {"name": "Marketing", "description": "Market analysis and promotional strategies"},
            {"name": "Finance", "description": "Financial management and investment analysis"},
            {"name": "Operations Management", "description": "Production and service operations"},
            {"name": "Human Resources", "description": "Personnel management and organizational behavior"}
        ]
    },
    
    "ECONOMICS": {
        "name": "Economics",
        "code": "ECON",
        "description": "Economic theory, markets, and policy analysis",
        "topics": [
            {"name": "Microeconomics", "description": "Individual and firm economic behavior"},
            {"name": "Macroeconomics", "description": "National and global economic systems"},
            {"name": "Econometrics", "description": "Statistical analysis of economic data"},
            {"name": "International Economics", "description": "Global trade and economic relations"},
            {"name": "Development Economics", "description": "Economic growth and development"}
        ]
    },
    
    # NATURAL SCIENCES
    "CHEMISTRY": {
        "name": "Chemistry",
        "code": "CHEM",
        "description": "Chemical properties, reactions, and molecular behavior",
        "topics": [
            {"name": "Organic Chemistry", "description": "Carbon-based compounds and reactions"},
            {"name": "Inorganic Chemistry", "description": "Non-organic compounds and materials"},
            {"name": "Physical Chemistry", "description": "Chemical thermodynamics and kinetics"},
            {"name": "Analytical Chemistry", "description": "Chemical analysis and instrumentation"},
            {"name": "Biochemistry", "description": "Chemical processes in living systems"}
        ]
    },
    
    "PHYSICS": {
        "name": "Physics",
        "code": "PHYS",
        "description": "Matter, energy, and fundamental physical laws",
        "topics": [
            {"name": "Classical Mechanics", "description": "Motion, forces, and energy"},
            {"name": "Electromagnetism", "description": "Electric and magnetic phenomena"},
            {"name": "Quantum Physics", "description": "Quantum mechanics and atomic physics"},
            {"name": "Thermodynamics", "description": "Heat, temperature, and statistical mechanics"},
            {"name": "Optics", "description": "Light behavior and optical systems"}
        ]
    },
    
    "BIOLOGY": {
        "name": "Biology",
        "code": "BIO",
        "description": "Living organisms and biological processes",
        "topics": [
            {"name": "Cell Biology", "description": "Cellular structure and function"},
            {"name": "Genetics", "description": "Heredity and genetic variation"},
            {"name": "Ecology", "description": "Organisms and environmental interactions"},
            {"name": "Evolution", "description": "Evolutionary processes and biodiversity"},
            {"name": "Molecular Biology", "description": "Biological molecules and processes"}
        ]
    },
    
    # SOCIAL SCIENCES & HUMANITIES
    "PSYCHOLOGY": {
        "name": "Psychology",
        "code": "PSYC",
        "description": "Human behavior, cognition, and mental processes",
        "topics": [
            {"name": "Cognitive Psychology", "description": "Mental processes and information processing"},
            {"name": "Social Psychology", "description": "Social influences on behavior"},
            {"name": "Developmental Psychology", "description": "Human development across lifespan"},
            {"name": "Clinical Psychology", "description": "Mental health assessment and treatment"},
            {"name": "Research Methods", "description": "Psychological research and statistics"}
        ]
    },
    
    "SOCIOLOGY": {
        "name": "Sociology",
        "code": "SOC",
        "description": "Society, social behavior, and social institutions",
        "topics": [
            {"name": "Social Theory", "description": "Sociological theories and perspectives"},
            {"name": "Social Stratification", "description": "Social class and inequality"},
            {"name": "Family and Marriage", "description": "Family structures and relationships"},
            {"name": "Deviance and Crime", "description": "Social deviance and criminal behavior"},
            {"name": "Social Change", "description": "Social movements and transformation"}
        ]
    },
    
    # LAW & LEGAL STUDIES
    "LAW": {
        "name": "Law",
        "code": "LAW",
        "description": "Legal principles, jurisprudence, and legal practice",
        "topics": [
            {"name": "Constitutional Law", "description": "Constitutional principles and rights"},
            {"name": "Criminal Law", "description": "Criminal offenses and procedures"},
            {"name": "Contract Law", "description": "Legal agreements and obligations"},
            {"name": "Tort Law", "description": "Civil wrongs and liability"},
            {"name": "International Law", "description": "Global legal frameworks and treaties"}
        ]
    },
    
    # EDUCATION
    "EDUCATION": {
        "name": "Education",
        "code": "EDU",
        "description": "Teaching, learning, and educational systems",
        "topics": [
            {"name": "Educational Psychology", "description": "Learning theories and cognitive development"},
            {"name": "Curriculum Development", "description": "Educational program design and assessment"},
            {"name": "Classroom Management", "description": "Teaching strategies and student engagement"},
            {"name": "Educational Technology", "description": "Technology integration in education"},
            {"name": "Special Education", "description": "Teaching students with diverse needs"}
        ]
    },
    
    # ARTS & LITERATURE
    "LITERATURE": {
        "name": "Literature",
        "code": "LIT",
        "description": "Literary works, analysis, and criticism",
        "topics": [
            {"name": "World Literature", "description": "Global literary traditions and works"},
            {"name": "Literary Theory", "description": "Critical approaches to literature"},
            {"name": "Poetry Analysis", "description": "Poetic forms and interpretation"},
            {"name": "Drama and Theater", "description": "Dramatic works and performance"},
            {"name": "Creative Writing", "description": "Writing techniques and composition"}
        ]
    },
    
    # MATHEMATICS
    "MATHEMATICS": {
        "name": "Mathematics",
        "code": "MATH",
        "description": "Mathematical concepts, theories, and applications",
        "topics": [
            {"name": "Calculus", "description": "Differential and integral calculus"},
            {"name": "Linear Algebra", "description": "Vector spaces and linear transformations"},
            {"name": "Statistics", "description": "Data analysis and probability theory"},
            {"name": "Discrete Mathematics", "description": "Combinatorics and graph theory"},
            {"name": "Number Theory", "description": "Properties and relationships of numbers"}
        ]
    },
    
    # AGRICULTURE & ENVIRONMENTAL SCIENCE
    "AGRICULTURE": {
        "name": "Agriculture",
        "code": "AGRI",
        "description": "Crop production, animal husbandry, and sustainable farming",
        "topics": [
            {"name": "Crop Science", "description": "Plant cultivation and crop management"},
            {"name": "Animal Science", "description": "Livestock production and animal health"},
            {"name": "Soil Science", "description": "Soil properties and fertility management"},
            {"name": "Agricultural Economics", "description": "Farm management and agricultural markets"},
            {"name": "Sustainable Agriculture", "description": "Environmental stewardship in farming"}
        ]
    },
    
    # ARCHITECTURE & DESIGN
    "ARCHITECTURE": {
        "name": "Architecture",
        "code": "ARCH",
        "description": "Building design, urban planning, and spatial design",
        "topics": [
            {"name": "Architectural Design", "description": "Design principles and spatial composition"},
            {"name": "Building Technology", "description": "Construction methods and materials"},
            {"name": "Urban Planning", "description": "City design and development planning"},
            {"name": "Sustainable Design", "description": "Environmental design and green building"},
            {"name": "Architectural History", "description": "Historical styles and movements"}
        ]
    }
}


def get_pharmacy_specific_prompts():
    """Get specialized prompts for pharmacy questions"""
    return {
        "pharmacology_mcq": """
        Generate a high-quality pharmacology multiple choice question.
        
        Requirements:
        - Focus on {specific_topic} (e.g., drug mechanisms, side effects, interactions)
        - Difficulty level: {difficulty}
        - Include drug names, mechanisms, or clinical scenarios
        - Options should test understanding of pharmacological principles
        - Explanation should include mechanism of action or clinical relevance
        
        Context: {context}
        
        Return in JSON format with question_text, options, explanation, and clinical_relevance.
        """,
        
        "clinical_pharmacy_scenario": """
        Generate a clinical pharmacy case-based question.
        
        Scenario: A patient presents with {clinical_scenario}
        
        Requirements:
        - Difficulty level: {difficulty}
        - Include patient demographics, medical history, current medications
        - Test pharmaceutical care decision-making
        - Include drug interactions, dosing, or monitoring considerations
        - Provide evidence-based rationale
        
        Return comprehensive case with question, options, and clinical reasoning.
        """,
        
        "pharmaceutical_calculations": """
        Generate a pharmaceutical calculation problem.
        
        Requirements:
        - Topic: {calculation_type} (e.g., dosing, concentration, bioavailability)
        - Difficulty level: {difficulty}
        - Include realistic clinical values
        - Show step-by-step solution
        - Include units and proper significant figures
        
        Return with problem statement, solution steps, and final answer.
        """
    }


def get_subject_specific_question_types():
    """Get question types specific to different subjects"""
    return {
        "PHARMACY": [
            "multiple_choice",
            "clinical_case",
            "calculation",
            "drug_interaction",
            "dosing_problem"
        ],
        "MEDICINE": [
            "multiple_choice", 
            "clinical_case",
            "diagnosis_scenario",
            "treatment_plan",
            "differential_diagnosis"
        ],
        "ENGINEERING": [
            "multiple_choice",
            "calculation",
            "design_problem",
            "analysis_question",
            "troubleshooting"
        ],
        "LAW": [
            "multiple_choice",
            "case_analysis",
            "legal_reasoning",
            "statute_interpretation",
            "ethical_scenario"
        ],
        "BUSINESS": [
            "multiple_choice",
            "case_study",
            "financial_analysis",
            "strategic_planning",
            "market_analysis"
        ]
    }


def get_professional_exam_standards():
    """Get professional examination standards for different fields"""
    return {
        "PHARMACY": {
            "licensing_exams": ["NAPLEX", "MPJE", "FPGEE"],
            "certification_bodies": ["BPS", "BCPS", "BCCCP"],
            "competency_areas": [
                "Patient Safety and Quality Assurance",
                "Order Entry and Processing", 
                "Dispensing Process",
                "Patient Care and Consultation",
                "Health and Wellness Promotion"
            ]
        },
        "MEDICINE": {
            "licensing_exams": ["USMLE", "COMLEX", "MCCEE"],
            "specialty_boards": ["ABIM", "ABFM", "ABS"],
            "competency_areas": [
                "Patient Care",
                "Medical Knowledge",
                "Practice-based Learning",
                "Interpersonal Communication",
                "Professionalism"
            ]
        },
        "ENGINEERING": {
            "licensing_exams": ["FE", "PE", "SE"],
            "certification_bodies": ["IEEE", "ASME", "ASCE"],
            "competency_areas": [
                "Technical Knowledge",
                "Problem Solving",
                "Design and Analysis",
                "Professional Practice",
                "Ethics and Safety"
            ]
        }
    }
