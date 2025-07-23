"""
Comprehensive Indian Education System Coverage for MEDHASAKTHI
Supports ALL specializations and subdivisions across India including state-specific curricula
"""

# Complete Indian Education System Taxonomy
INDIAN_EDUCATION_SYSTEM = {

    # ==================== SCHOOL EDUCATION (CLASS 1-12) ====================
    "SCHOOL_EDUCATION": {
        "PRIMARY": {
            "name": "Primary Education",
            "classes": ["Class_1", "Class_2", "Class_3", "Class_4", "Class_5"],
            "age_range": "6-11 years",
            "boards": ["CBSE", "ICSE", "State_Boards"],
            "core_subjects": {
                "Class_1": ["English", "Hindi", "Mathematics", "Environmental_Studies", "Art_Craft"],
                "Class_2": ["English", "Hindi", "Mathematics", "Environmental_Studies", "Art_Craft"],
                "Class_3": ["English", "Hindi", "Mathematics", "Environmental_Studies", "Art_Craft", "Computer_Basics"],
                "Class_4": ["English", "Hindi", "Mathematics", "Environmental_Studies", "Social_Studies", "Computer_Basics"],
                "Class_5": ["English", "Hindi", "Mathematics", "Environmental_Studies", "Social_Studies", "Computer_Basics"]
            },
            "assessment_pattern": "Continuous_Assessment",
            "board_exams": False
        },

        "UPPER_PRIMARY": {
            "name": "Upper Primary Education",
            "classes": ["Class_6", "Class_7", "Class_8"],
            "age_range": "11-14 years",
            "boards": ["CBSE", "ICSE", "State_Boards"],
            "core_subjects": {
                "Class_6": ["English", "Hindi", "Mathematics", "Science", "Social_Science", "Computer_Science"],
                "Class_7": ["English", "Hindi", "Mathematics", "Science", "Social_Science", "Computer_Science"],
                "Class_8": ["English", "Hindi", "Mathematics", "Science", "Social_Science", "Computer_Science"]
            },
            "optional_subjects": ["Sanskrit", "French", "German", "Art", "Music", "Physical_Education"],
            "assessment_pattern": "Term_Based_Assessment",
            "board_exams": False
        },

        "SECONDARY": {
            "name": "Secondary Education",
            "classes": ["Class_9", "Class_10"],
            "age_range": "14-16 years",
            "boards": ["CBSE", "ICSE", "State_Boards"],
            "core_subjects": {
                "Class_9": ["English", "Hindi", "Mathematics", "Science", "Social_Science"],
                "Class_10": ["English", "Hindi", "Mathematics", "Science", "Social_Science"]
            },
            "optional_subjects": ["Computer_Science", "Sanskrit", "French", "German", "Art", "Music", "Physical_Education", "Home_Science"],
            "assessment_pattern": "Board_Examination",
            "board_exams": True,
            "major_exams": ["CBSE_Class_10", "ICSE_Class_10", "State_Board_Class_10"]
        },

        "HIGHER_SECONDARY": {
            "name": "Higher Secondary Education",
            "classes": ["Class_11", "Class_12"],
            "age_range": "16-18 years",
            "boards": ["CBSE", "ICSE", "State_Boards"],
            "streams": {
                "Science": {
                    "core_subjects": ["English", "Physics", "Chemistry", "Mathematics"],
                    "optional_subjects": ["Biology", "Computer_Science", "Physical_Education", "Psychology"],
                    "career_paths": ["Engineering", "Medical", "Research", "Technology"]
                },
                "Commerce": {
                    "core_subjects": ["English", "Accountancy", "Business_Studies", "Economics"],
                    "optional_subjects": ["Mathematics", "Computer_Science", "Physical_Education", "Entrepreneurship"],
                    "career_paths": ["Business", "Finance", "Management", "Economics"]
                },
                "Arts_Humanities": {
                    "core_subjects": ["English", "History", "Political_Science", "Geography"],
                    "optional_subjects": ["Psychology", "Sociology", "Philosophy", "Economics", "Fine_Arts", "Music"],
                    "career_paths": ["Civil_Services", "Law", "Journalism", "Social_Work", "Arts"]
                }
            },
            "assessment_pattern": "Board_Examination",
            "board_exams": True,
            "major_exams": ["CBSE_Class_12", "ICSE_Class_12", "State_Board_Class_12"],
            "entrance_preparation": ["JEE", "NEET", "CLAT", "NDA", "CUET"]
        }
    },

    # ==================== MEDICAL & HEALTH SCIENCES ====================
    "MEDICAL_HEALTH": {
        "MBBS": {
            "name": "Bachelor of Medicine and Bachelor of Surgery",
            "code": "MBBS",
            "duration": "5.5 years",
            "specializations": [
                "General Medicine", "Surgery", "Pediatrics", "Obstetrics & Gynecology",
                "Orthopedics", "Ophthalmology", "ENT", "Dermatology", "Psychiatry",
                "Radiology", "Pathology", "Anesthesiology", "Emergency Medicine"
            ],
            "entrance_exams": ["NEET-UG"],
            "regulatory_body": "NMC (National Medical Commission)"
        },
        
        "BDS": {
            "name": "Bachelor of Dental Surgery",
            "code": "BDS",
            "duration": "5 years",
            "specializations": [
                "Oral & Maxillofacial Surgery", "Orthodontics", "Periodontics",
                "Endodontics", "Prosthodontics", "Oral Pathology", "Pedodontics",
                "Oral Medicine & Radiology", "Public Health Dentistry"
            ],
            "entrance_exams": ["NEET-UG"],
            "regulatory_body": "DCI (Dental Council of India)"
        },
        
        "BAMS": {
            "name": "Bachelor of Ayurvedic Medicine and Surgery",
            "code": "BAMS",
            "duration": "5.5 years",
            "specializations": [
                "Kayachikitsa (Internal Medicine)", "Shalya Tantra (Surgery)",
                "Shalakya Tantra (ENT & Ophthalmology)", "Prasuti Tantra (Obstetrics)",
                "Kaumarbhritya (Pediatrics)", "Agada Tantra (Toxicology)",
                "Rasayana (Rejuvenation)", "Vajikarana (Aphrodisiac therapy)"
            ],
            "entrance_exams": ["NEET-UG"],
            "regulatory_body": "CCIM (Central Council of Indian Medicine)"
        },
        
        "BHMS": {
            "name": "Bachelor of Homeopathic Medicine and Surgery",
            "code": "BHMS",
            "duration": "5.5 years",
            "specializations": [
                "Homeopathic Materia Medica", "Organon of Medicine",
                "Homeopathic Pharmacy", "Pathology & Microbiology",
                "Forensic Medicine", "Surgery", "Obstetrics & Gynecology"
            ],
            "entrance_exams": ["NEET-UG"],
            "regulatory_body": "CCH (Central Council of Homoeopathy)"
        },
        
        "BUMS": {
            "name": "Bachelor of Unani Medicine and Surgery",
            "code": "BUMS",
            "duration": "5.5 years",
            "specializations": [
                "Moalajat (Medicine)", "Jarahat (Surgery)", "Niswan (Gynecology)",
                "Atfal (Pediatrics)", "Amraz-e-Ain, Uzn, Anf, Halaq (ENT & Ophthalmology)",
                "Ilmul Advia (Pharmacology)", "Tahaffuzi wa Samaji Tib (Preventive Medicine)"
            ],
            "entrance_exams": ["NEET-UG"],
            "regulatory_body": "CCIM (Central Council of Indian Medicine)"
        },
        
        "BSMS": {
            "name": "Bachelor of Siddha Medicine and Surgery",
            "code": "BSMS",
            "duration": "5.5 years",
            "specializations": [
                "Pothu Maruthuvam (General Medicine)", "Shalya Maruthuvam (Surgery)",
                "Kuzhandhai Maruthuvam (Pediatrics)", "Magalir Maruthuvam (Gynecology)",
                "Vaithiya Vidhi (Clinical Methods)", "Gunapadam (Pharmacology)"
            ],
            "entrance_exams": ["NEET-UG"],
            "regulatory_body": "CCIM (Central Council of Indian Medicine)"
        },
        
        "B_PHARM": {
            "name": "Bachelor of Pharmacy",
            "code": "B_PHARM",
            "duration": "4 years",
            "specializations": [
                "Pharmaceutics", "Pharmaceutical Chemistry", "Pharmacology",
                "Pharmacognosy", "Pharmaceutical Analysis", "Clinical Pharmacy",
                "Hospital Pharmacy", "Industrial Pharmacy", "Regulatory Affairs"
            ],
            "entrance_exams": ["JEE Main", "State CETs", "GPAT"],
            "regulatory_body": "PCI (Pharmacy Council of India)"
        },
        
        "NURSING": {
            "name": "Bachelor of Science in Nursing",
            "code": "B_SC_NURSING",
            "duration": "4 years",
            "specializations": [
                "Medical-Surgical Nursing", "Community Health Nursing",
                "Psychiatric Nursing", "Pediatric Nursing", "Obstetric Nursing",
                "Critical Care Nursing", "Oncology Nursing", "Geriatric Nursing"
            ],
            "entrance_exams": ["NEET-UG", "State Nursing Entrance"],
            "regulatory_body": "INC (Indian Nursing Council)"
        },
        
        "PHYSIOTHERAPY": {
            "name": "Bachelor of Physiotherapy",
            "code": "BPT",
            "duration": "4.5 years",
            "specializations": [
                "Orthopedic Physiotherapy", "Neurological Physiotherapy",
                "Cardiopulmonary Physiotherapy", "Sports Physiotherapy",
                "Pediatric Physiotherapy", "Geriatric Physiotherapy"
            ],
            "entrance_exams": ["NEET-UG", "State CETs"],
            "regulatory_body": "IAP (Indian Association of Physiotherapists)"
        },
        
        "VETERINARY": {
            "name": "Bachelor of Veterinary Science",
            "code": "B_V_SC",
            "duration": "5.5 years",
            "specializations": [
                "Veterinary Medicine", "Veterinary Surgery", "Animal Husbandry",
                "Veterinary Public Health", "Veterinary Pathology",
                "Veterinary Pharmacology", "Poultry Science", "Dairy Science"
            ],
            "entrance_exams": ["NEET-UG", "State Veterinary Entrance"],
            "regulatory_body": "VCI (Veterinary Council of India)"
        }
    },
    
    # ==================== ENGINEERING & TECHNOLOGY ====================
    "ENGINEERING": {
        "COMPUTER_SCIENCE": {
            "name": "Computer Science and Engineering",
            "code": "CSE",
            "specializations": [
                "Artificial Intelligence & Machine Learning", "Data Science",
                "Cybersecurity", "Software Engineering", "Computer Networks",
                "Database Systems", "Human-Computer Interaction", "Blockchain Technology",
                "Internet of Things (IoT)", "Cloud Computing", "Mobile App Development"
            ],
            "entrance_exams": ["JEE Main", "JEE Advanced", "State CETs"],
            "regulatory_body": "AICTE"
        },
        
        "INFORMATION_TECHNOLOGY": {
            "name": "Information Technology",
            "code": "IT",
            "specializations": [
                "Web Development", "Network Administration", "IT Security",
                "Database Administration", "System Analysis", "IT Project Management",
                "Enterprise Resource Planning", "Business Intelligence"
            ]
        },
        
        "ELECTRONICS_COMMUNICATION": {
            "name": "Electronics and Communication Engineering",
            "code": "ECE",
            "specializations": [
                "VLSI Design", "Embedded Systems", "Signal Processing",
                "Telecommunications", "Microwave Engineering", "Optical Communication",
                "Robotics", "Biomedical Electronics", "Satellite Communication"
            ]
        },
        
        "ELECTRICAL": {
            "name": "Electrical Engineering",
            "code": "EE",
            "specializations": [
                "Power Systems", "Control Systems", "Power Electronics",
                "Electrical Machines", "High Voltage Engineering",
                "Renewable Energy Systems", "Smart Grid Technology"
            ]
        },
        
        "MECHANICAL": {
            "name": "Mechanical Engineering",
            "code": "ME",
            "specializations": [
                "Thermal Engineering", "Design Engineering", "Manufacturing Engineering",
                "Automobile Engineering", "Aerospace Engineering", "Robotics",
                "CAD/CAM", "Industrial Engineering", "Materials Engineering"
            ]
        },
        
        "CIVIL": {
            "name": "Civil Engineering",
            "code": "CE",
            "specializations": [
                "Structural Engineering", "Transportation Engineering",
                "Environmental Engineering", "Geotechnical Engineering",
                "Water Resources Engineering", "Construction Management",
                "Urban Planning", "Earthquake Engineering"
            ]
        },
        
        "CHEMICAL": {
            "name": "Chemical Engineering",
            "code": "CHE",
            "specializations": [
                "Process Engineering", "Petrochemical Engineering",
                "Biochemical Engineering", "Environmental Engineering",
                "Materials Engineering", "Safety Engineering"
            ]
        },
        
        "BIOTECHNOLOGY": {
            "name": "Biotechnology Engineering",
            "code": "BT",
            "specializations": [
                "Medical Biotechnology", "Agricultural Biotechnology",
                "Industrial Biotechnology", "Environmental Biotechnology",
                "Bioinformatics", "Genetic Engineering"
            ]
        },
        
        "AEROSPACE": {
            "name": "Aerospace Engineering",
            "code": "AE",
            "specializations": [
                "Aerodynamics", "Propulsion", "Flight Mechanics",
                "Aircraft Design", "Space Technology", "Avionics"
            ]
        },
        
        "AUTOMOBILE": {
            "name": "Automobile Engineering",
            "code": "AUTO",
            "specializations": [
                "Vehicle Design", "Engine Technology", "Automotive Electronics",
                "Electric Vehicles", "Hybrid Technology", "Safety Systems"
            ]
        }
    },
    
    # ==================== MANAGEMENT & BUSINESS ====================
    "MANAGEMENT": {
        "MBA": {
            "name": "Master of Business Administration",
            "code": "MBA",
            "specializations": [
                "Finance", "Marketing", "Human Resources", "Operations",
                "Information Technology", "International Business",
                "Entrepreneurship", "Supply Chain Management", "Digital Marketing",
                "Business Analytics", "Healthcare Management", "Rural Management"
            ],
            "entrance_exams": ["CAT", "XAT", "GMAT", "MAT", "CMAT", "SNAP"],
            "regulatory_body": "AICTE"
        },
        
        "BBA": {
            "name": "Bachelor of Business Administration",
            "code": "BBA",
            "specializations": [
                "General Management", "Finance", "Marketing", "Human Resources",
                "International Business", "Digital Marketing", "Event Management"
            ]
        },
        
        "B_COM": {
            "name": "Bachelor of Commerce",
            "code": "B_COM",
            "specializations": [
                "Accounting & Finance", "Banking & Insurance", "Taxation",
                "Corporate Secretaryship", "E-Commerce", "International Business"
            ]
        }
    },
    
    # ==================== LAW ====================
    "LAW": {
        "LLB": {
            "name": "Bachelor of Laws",
            "code": "LLB",
            "duration": "3 years",
            "specializations": [
                "Constitutional Law", "Criminal Law", "Civil Law", "Corporate Law",
                "International Law", "Environmental Law", "Cyber Law",
                "Intellectual Property Law", "Human Rights Law", "Tax Law"
            ],
            "entrance_exams": ["CLAT", "AILET", "LSAT India"],
            "regulatory_body": "BCI (Bar Council of India)"
        },
        
        "BA_LLB": {
            "name": "Bachelor of Arts and Bachelor of Laws",
            "code": "BA_LLB",
            "duration": "5 years",
            "specializations": [
                "Constitutional Law", "Criminal Law", "Corporate Law",
                "International Law", "Human Rights Law", "Environmental Law"
            ]
        }
    },
    
    # ==================== PURE SCIENCES ====================
    "PURE_SCIENCES": {
        "PHYSICS": {
            "name": "Bachelor of Science in Physics",
            "code": "B_SC_PHYSICS",
            "specializations": [
                "Theoretical Physics", "Applied Physics", "Nuclear Physics",
                "Astrophysics", "Condensed Matter Physics", "Quantum Physics",
                "Medical Physics", "Geophysics"
            ]
        },
        
        "CHEMISTRY": {
            "name": "Bachelor of Science in Chemistry",
            "code": "B_SC_CHEMISTRY",
            "specializations": [
                "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry",
                "Analytical Chemistry", "Biochemistry", "Industrial Chemistry",
                "Medicinal Chemistry", "Environmental Chemistry"
            ]
        },
        
        "MATHEMATICS": {
            "name": "Bachelor of Science in Mathematics",
            "code": "B_SC_MATHEMATICS",
            "specializations": [
                "Pure Mathematics", "Applied Mathematics", "Statistics",
                "Actuarial Science", "Operations Research", "Mathematical Modeling"
            ]
        },
        
        "BIOLOGY": {
            "name": "Bachelor of Science in Biology",
            "code": "B_SC_BIOLOGY",
            "specializations": [
                "Botany", "Zoology", "Microbiology", "Biotechnology",
                "Genetics", "Ecology", "Marine Biology", "Molecular Biology"
            ]
        }
    },
    
    # ==================== AGRICULTURE ====================
    "AGRICULTURE": {
        "B_SC_AGRICULTURE": {
            "name": "Bachelor of Science in Agriculture",
            "code": "B_SC_AG",
            "duration": "4 years",
            "specializations": [
                "Agronomy", "Horticulture", "Plant Pathology", "Entomology",
                "Soil Science", "Agricultural Economics", "Animal Husbandry",
                "Dairy Science", "Fisheries", "Forestry", "Food Technology"
            ],
            "entrance_exams": ["ICAR AIEEA", "State Agriculture Entrance"],
            "regulatory_body": "ICAR (Indian Council of Agricultural Research)"
        },
        
        "FOOD_TECHNOLOGY": {
            "name": "Food Technology",
            "code": "B_TECH_FOOD",
            "specializations": [
                "Food Processing", "Food Safety", "Nutrition", "Food Packaging",
                "Dairy Technology", "Beverage Technology", "Bakery Technology"
            ]
        }
    },
    
    # ==================== ARTS & HUMANITIES ====================
    "ARTS_HUMANITIES": {
        "BA_ENGLISH": {
            "name": "Bachelor of Arts in English",
            "code": "BA_ENG",
            "specializations": [
                "English Literature", "Linguistics", "Creative Writing",
                "Journalism", "Mass Communication", "Translation Studies"
            ]
        },
        
        "BA_HINDI": {
            "name": "Bachelor of Arts in Hindi",
            "code": "BA_HINDI",
            "specializations": [
                "Hindi Literature", "Hindi Journalism", "Translation",
                "Comparative Literature", "Folk Literature"
            ]
        },
        
        "BA_HISTORY": {
            "name": "Bachelor of Arts in History",
            "code": "BA_HIST",
            "specializations": [
                "Ancient History", "Medieval History", "Modern History",
                "Art History", "Archaeological Studies"
            ]
        },
        
        "BA_POLITICAL_SCIENCE": {
            "name": "Bachelor of Arts in Political Science",
            "code": "BA_POL",
            "specializations": [
                "Indian Politics", "International Relations", "Public Administration",
                "Political Theory", "Comparative Politics"
            ]
        },
        
        "BA_ECONOMICS": {
            "name": "Bachelor of Arts in Economics",
            "code": "BA_ECON",
            "specializations": [
                "Microeconomics", "Macroeconomics", "Development Economics",
                "International Economics", "Econometrics", "Public Economics"
            ]
        },
        
        "BA_PSYCHOLOGY": {
            "name": "Bachelor of Arts in Psychology",
            "code": "BA_PSYC",
            "specializations": [
                "Clinical Psychology", "Counseling Psychology", "Educational Psychology",
                "Industrial Psychology", "Social Psychology", "Cognitive Psychology"
            ]
        },
        
        "BA_SOCIOLOGY": {
            "name": "Bachelor of Arts in Sociology",
            "code": "BA_SOC",
            "specializations": [
                "Social Work", "Rural Sociology", "Urban Sociology",
                "Industrial Sociology", "Medical Sociology"
            ]
        }
    },
    
    # ==================== EDUCATION ====================
    "EDUCATION": {
        "B_ED": {
            "name": "Bachelor of Education",
            "code": "B_ED",
            "duration": "2 years",
            "specializations": [
                "Elementary Education", "Secondary Education", "Special Education",
                "Educational Technology", "Educational Psychology",
                "Curriculum Development", "Educational Administration"
            ],
            "entrance_exams": ["State B.Ed Entrance"],
            "regulatory_body": "NCTE (National Council for Teacher Education)"
        },
        
        "D_EL_ED": {
            "name": "Diploma in Elementary Education",
            "code": "D_EL_ED",
            "duration": "2 years",
            "specializations": [
                "Primary Education", "Early Childhood Education",
                "Inclusive Education", "Language Teaching"
            ]
        }
    },
    
    # ==================== DESIGN & FINE ARTS ====================
    "DESIGN_ARTS": {
        "B_DES": {
            "name": "Bachelor of Design",
            "code": "B_DES",
            "specializations": [
                "Fashion Design", "Interior Design", "Graphic Design",
                "Product Design", "Textile Design", "Jewelry Design",
                "Animation", "Game Design", "UI/UX Design"
            ],
            "entrance_exams": ["NIFT", "NID", "UCEED", "CEED"]
        },
        
        "BFA": {
            "name": "Bachelor of Fine Arts",
            "code": "BFA",
            "specializations": [
                "Painting", "Sculpture", "Applied Arts", "Photography",
                "Printmaking", "Art History", "Visual Arts"
            ]
        },
        
        "B_ARCH": {
            "name": "Bachelor of Architecture",
            "code": "B_ARCH",
            "duration": "5 years",
            "specializations": [
                "Architectural Design", "Urban Planning", "Landscape Architecture",
                "Interior Architecture", "Sustainable Architecture"
            ],
            "entrance_exams": ["NATA", "JEE Main Paper 2"],
            "regulatory_body": "COA (Council of Architecture)"
        }
    },
    
    # ==================== HOTEL MANAGEMENT & TOURISM ====================
    "HOSPITALITY": {
        "BHM": {
            "name": "Bachelor of Hotel Management",
            "code": "BHM",
            "duration": "4 years",
            "specializations": [
                "Hotel Operations", "Food & Beverage Management",
                "Front Office Management", "Housekeeping Management",
                "Event Management", "Tourism Management"
            ],
            "entrance_exams": ["NCHMCT JEE", "State Hotel Management Entrance"]
        },
        
        "TOURISM": {
            "name": "Bachelor of Tourism Studies",
            "code": "BTS",
            "specializations": [
                "Travel Management", "Tour Operations", "Heritage Tourism",
                "Adventure Tourism", "Eco-Tourism", "Medical Tourism"
            ]
        }
    }
}


# Comprehensive Indian Education Boards and Curricula
INDIAN_EDUCATION_BOARDS = {
    "NATIONAL_BOARDS": {
        "CBSE": {
            "name": "Central Board of Secondary Education",
            "full_name": "Central Board of Secondary Education",
            "coverage": "National and International",
            "headquarters": "New Delhi",
            "established": "1962",
            "curriculum_focus": "NCERT_Based",
            "assessment_pattern": {
                "primary": "Continuous_Comprehensive_Evaluation",
                "secondary": "Term_Based_Assessment",
                "higher_secondary": "Board_Examination"
            },
            "class_wise_subjects": {
                "Class_1_5": {
                    "core": ["English", "Hindi", "Mathematics", "Environmental_Studies"],
                    "co_curricular": ["Art_Education", "Health_Physical_Education", "Work_Education"]
                },
                "Class_6_8": {
                    "core": ["English", "Hindi", "Mathematics", "Science", "Social_Science"],
                    "optional": ["Sanskrit", "Computer_Science", "Art_Education", "Music"]
                },
                "Class_9_10": {
                    "core": ["English", "Hindi", "Mathematics", "Science", "Social_Science"],
                    "optional": ["Computer_Science", "Sanskrit", "French", "German", "Art", "Music", "Home_Science"]
                },
                "Class_11_12": {
                    "Science": ["English", "Physics", "Chemistry", "Mathematics", "Biology/Computer_Science"],
                    "Commerce": ["English", "Accountancy", "Business_Studies", "Economics", "Mathematics/Computer_Science"],
                    "Humanities": ["English", "History", "Political_Science", "Geography", "Psychology/Economics"]
                }
            },
            "examination_pattern": {
                "Class_10": "Board_Exam_100_Marks_Per_Subject",
                "Class_12": "Board_Exam_100_Marks_Per_Subject"
            },
            "grading_system": "9_Point_Grading_Scale",
            "languages_supported": ["Hindi", "English", "Sanskrit", "French", "German", "Spanish"]
        },

        "ICSE": {
            "name": "Indian Certificate of Secondary Education",
            "full_name": "Council for the Indian School Certificate Examinations",
            "coverage": "National",
            "headquarters": "New Delhi",
            "established": "1958",
            "curriculum_focus": "Comprehensive_English_Medium",
            "assessment_pattern": {
                "primary": "Internal_Assessment",
                "secondary": "Board_Examination",
                "higher_secondary": "ISC_Board_Examination"
            },
            "class_wise_subjects": {
                "Class_1_5": {
                    "core": ["English", "Second_Language", "Mathematics", "Environmental_Science"],
                    "co_curricular": ["Art", "Craft", "Music", "Physical_Education"]
                },
                "Class_6_8": {
                    "core": ["English", "Second_Language", "Mathematics", "Physics", "Chemistry", "Biology", "History", "Geography"],
                    "optional": ["Computer_Applications", "Art", "Music", "Physical_Education"]
                },
                "Class_9_10": {
                    "core": ["English", "Second_Language", "Mathematics", "Physics", "Chemistry", "Biology", "History_Civics", "Geography"],
                    "optional": ["Computer_Applications", "Commercial_Studies", "Economics", "Art", "Music"]
                },
                "Class_11_12_ISC": {
                    "Science": ["English", "Second_Language", "Physics", "Chemistry", "Mathematics", "Biology/Computer_Science"],
                    "Commerce": ["English", "Second_Language", "Mathematics", "Accounts", "Commerce", "Economics"],
                    "Arts": ["English", "Second_Language", "History", "Political_Science", "Geography", "Psychology"]
                }
            },
            "examination_pattern": {
                "Class_10_ICSE": "Board_Exam_100_Marks_Per_Subject",
                "Class_12_ISC": "Board_Exam_100_Marks_Per_Subject"
            },
            "grading_system": "Percentage_Based",
            "languages_supported": ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", "French", "German"]
        }
    },

    "STATE_BOARDS": {
        "Maharashtra": {
            "name": "Maharashtra State Board",
            "full_name": "Maharashtra State Board of Secondary and Higher Secondary Education",
            "coverage": "Maharashtra State",
            "headquarters": "Pune",
            "medium_of_instruction": ["Marathi", "Hindi", "English", "Urdu"],
            "curriculum_focus": "State_Specific_Regional_Context"
        },
        "Tamil_Nadu": {
            "name": "Tamil Nadu State Board",
            "full_name": "Tamil Nadu State Board of School Education",
            "coverage": "Tamil Nadu State",
            "headquarters": "Chennai",
            "medium_of_instruction": ["Tamil", "English"],
            "curriculum_focus": "Tamil_Culture_Regional_Context"
        },
        "Karnataka": {
            "name": "Karnataka State Board",
            "full_name": "Karnataka Secondary Education Examination Board",
            "coverage": "Karnataka State",
            "headquarters": "Bangalore",
            "medium_of_instruction": ["Kannada", "English", "Hindi"],
            "curriculum_focus": "Kannada_Culture_Regional_Context"
        },
        "Uttar_Pradesh": {
            "name": "UP Board",
            "full_name": "Uttar Pradesh Madhyamik Shiksha Parishad",
            "coverage": "Uttar Pradesh State",
            "headquarters": "Allahabad",
            "medium_of_instruction": ["Hindi", "English", "Urdu"],
            "curriculum_focus": "Hindi_Regional_Context"
        },
        "West_Bengal": {
            "name": "West Bengal Board",
            "full_name": "West Bengal Board of Secondary Education",
            "coverage": "West Bengal State",
            "headquarters": "Kolkata",
            "medium_of_instruction": ["Bengali", "English", "Hindi"],
            "curriculum_focus": "Bengali_Culture_Regional_Context"
        },
        "Rajasthan": {
            "name": "Rajasthan Board",
            "full_name": "Board of Secondary Education Rajasthan",
            "coverage": "Rajasthan State",
            "headquarters": "Ajmer",
            "medium_of_instruction": ["Hindi", "English"],
            "curriculum_focus": "Rajasthani_Culture_Regional_Context"
        },
        "Gujarat": {
            "name": "Gujarat Board",
            "full_name": "Gujarat Secondary and Higher Secondary Education Board",
            "coverage": "Gujarat State",
            "headquarters": "Gandhinagar",
            "medium_of_instruction": ["Gujarati", "English", "Hindi"],
            "curriculum_focus": "Gujarati_Culture_Regional_Context"
        },
        "Andhra_Pradesh": {
            "name": "AP Board",
            "full_name": "Board of Intermediate Education Andhra Pradesh",
            "coverage": "Andhra Pradesh State",
            "headquarters": "Hyderabad",
            "medium_of_instruction": ["Telugu", "English"],
            "curriculum_focus": "Telugu_Culture_Regional_Context"
        },
        "Kerala": {
            "name": "Kerala Board",
            "full_name": "Kerala Board of Public Examinations",
            "coverage": "Kerala State",
            "headquarters": "Thiruvananthapuram",
            "medium_of_instruction": ["Malayalam", "English"],
            "curriculum_focus": "Malayalam_Culture_Regional_Context"
        },
        "Punjab": {
            "name": "Punjab Board",
            "full_name": "Punjab School Education Board",
            "coverage": "Punjab State",
            "headquarters": "Mohali",
            "medium_of_instruction": ["Punjabi", "English", "Hindi"],
            "curriculum_focus": "Punjabi_Culture_Regional_Context"
        }
    }
},

# State-specific educational boards and curricula (Legacy - keeping for compatibility)
INDIAN_STATE_BOARDS = {
    "CBSE": {
        "name": "Central Board of Secondary Education",
        "coverage": "National",
        "subjects": ["Mathematics", "Science", "Social Science", "English", "Hindi", "Sanskrit"]
    },
    "ICSE": {
        "name": "Indian Certificate of Secondary Education",
        "coverage": "National",
        "subjects": ["Mathematics", "Science", "History", "Geography", "English", "Second Language"]
    },
    "STATE_BOARDS": {
        "Maharashtra": ["SSC", "HSC"],
        "Tamil Nadu": ["SSLC", "HSC"],
        "Karnataka": ["SSLC", "PUC"],
        "Kerala": ["SSLC", "HSE"],
        "West Bengal": ["Madhyamik", "Higher Secondary"],
        "Gujarat": ["SSC", "HSC"],
        "Rajasthan": ["RBSE"],
        "Uttar Pradesh": ["UP Board"],
        "Bihar": ["BSEB"],
        "Odisha": ["BSE", "CHSE"],
        "Andhra Pradesh": ["SSC", "Intermediate"],
        "Telangana": ["SSC", "Intermediate"],
        "Madhya Pradesh": ["MPBSE"],
        "Haryana": ["HBSE"],
        "Punjab": ["PSEB"],
        "Himachal Pradesh": ["HPBOSE"],
        "Uttarakhand": ["UBSE"],
        "Jharkhand": ["JAC"],
        "Chhattisgarh": ["CGBSE"],
        "Assam": ["SEBA", "AHSEC"],
        "Tripura": ["TBSE"],
        "Manipur": ["BSEM"],
        "Meghalaya": ["MBOSE"],
        "Mizoram": ["MBSE"],
        "Nagaland": ["NBSE"],
        "Arunachal Pradesh": ["APBSE"],
        "Sikkim": ["SBSE"],
        "Goa": ["GBSHSE"],
        "Jammu & Kashmir": ["JKBOSE"]
    }
}


# Professional entrance examinations in India
INDIAN_ENTRANCE_EXAMS = {
    "MEDICAL": ["NEET-UG", "NEET-PG", "AIIMS", "JIPMER"],
    "ENGINEERING": ["JEE Main", "JEE Advanced", "BITSAT", "VITEEE", "SRMJEEE", "COMEDK"],
    "MANAGEMENT": ["CAT", "XAT", "GMAT", "MAT", "CMAT", "SNAP", "IIFT", "NMAT"],
    "LAW": ["CLAT", "AILET", "LSAT India", "SLAT"],
    "DESIGN": ["NIFT", "NID", "UCEED", "CEED"],
    "AGRICULTURE": ["ICAR AIEEA"],
    "ARCHITECTURE": ["NATA", "JEE Main Paper 2"],
    "HOTEL_MANAGEMENT": ["NCHMCT JEE"],
    "TEACHING": ["CTET", "State TETs"],
    "CIVIL_SERVICES": ["UPSC CSE", "State PSCs"],
    "BANKING": ["IBPS", "SBI", "RBI"],
    "DEFENCE": ["NDA", "CDS", "AFCAT"]
}


# Regional languages and literature
INDIAN_LANGUAGES = {
    "CLASSICAL": ["Sanskrit", "Tamil", "Telugu", "Kannada", "Malayalam", "Odia"],
    "SCHEDULED": [
        "Hindi", "Bengali", "Marathi", "Telugu", "Tamil", "Gujarati", "Urdu",
        "Kannada", "Odia", "Malayalam", "Punjabi", "Assamese", "Maithili",
        "Santali", "Kashmiri", "Nepali", "Konkani", "Sindhi", "Dogri", "Manipuri",
        "Bodo", "Sanskrit"
    ],
    "REGIONAL": [
        "Bhojpuri", "Magahi", "Awadhi", "Chhattisgarhi", "Rajasthani",
        "Haryanvi", "Kumaoni", "Garhwali", "Tulu", "Kodava"
    ]
}


def get_indian_specialization_coverage():
    """Get comprehensive coverage of Indian educational specializations"""
    total_specializations = 0
    coverage_summary = {}
    
    for category, fields in INDIAN_EDUCATION_SYSTEM.items():
        category_count = 0
        for field, details in fields.items():
            if isinstance(details, dict) and "specializations" in details:
                category_count += len(details["specializations"])
        
        coverage_summary[category] = category_count
        total_specializations += category_count
    
    return {
        "total_specializations": total_specializations,
        "category_breakdown": coverage_summary,
        "state_boards": len(INDIAN_STATE_BOARDS["STATE_BOARDS"]),
        "entrance_exams": sum(len(exams) for exams in INDIAN_ENTRANCE_EXAMS.values()),
        "languages_supported": len(INDIAN_LANGUAGES["SCHEDULED"])
    }
