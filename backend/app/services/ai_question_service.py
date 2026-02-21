"""
AI-powered question generation service
"""
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import requests

from app.core.config import settings
from app.models.question import (
    Question, Subject, Topic, AIQuestionGeneration,
    QuestionType, DifficultyLevel, QuestionStatus
)
from app.models.user import User
from app.utils.comprehensive_subjects import get_pharmacy_specific_prompts, get_subject_specific_question_types
from app.utils.indian_education_system import INDIAN_EDUCATION_SYSTEM, INDIAN_STATE_BOARDS, INDIAN_ENTRANCE_EXAMS
from app.utils.professional_certifications import PROFESSIONAL_CERTIFICATIONS, INDUSTRY_SKILLS


class AIQuestionGenerator:
    """AI-powered question generation service"""
    
    def __init__(self):
        self.openai_client = None
        self.huggingface_models = {}
        self.local_models = {}
        
        # Initialize OpenAI if API key is available
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
        
        # Question generation prompts
        self.prompts = {
            QuestionType.MULTIPLE_CHOICE: self._get_mcq_prompt(),
            QuestionType.TRUE_FALSE: self._get_true_false_prompt(),
            QuestionType.FILL_IN_BLANK: self._get_fill_blank_prompt(),
            QuestionType.SHORT_ANSWER: self._get_short_answer_prompt(),
            QuestionType.ESSAY: self._get_essay_prompt(),
        }

        # Specialized prompts for professional fields
        self.specialized_prompts = {
            "PHARMACY": get_pharmacy_specific_prompts(),
            "MEDICINE": self._get_medical_prompts(),
            "ENGINEERING": self._get_engineering_prompts(),
            "LAW": self._get_law_prompts(),
            "BUSINESS": self._get_business_prompts()
        }

        # Indian education system specific prompts
        self.indian_prompts = {
            "NEET": self._get_neet_prompts(),
            "JEE": self._get_jee_prompts(),
            "CBSE": self._get_cbse_prompts(),
            "ICSE": self._get_icse_prompts(),
            "STATE_BOARDS": self._get_state_board_prompts(),
            "ENTRANCE_EXAMS": self._get_entrance_exam_prompts()
        }

        # Professional certification and specialized course prompts
        self.professional_prompts = {
            "CLOUD": self._get_cloud_prompts(),
            "PROGRAMMING": self._get_programming_prompts(),
            "DEVOPS": self._get_devops_prompts(),
            "FINANCE": self._get_finance_prompts(),
            "DATA_SCIENCE": self._get_data_science_prompts(),
            "CYBERSECURITY": self._get_cybersecurity_prompts(),
            "PROJECT_MANAGEMENT": self._get_project_management_prompts(),
            "DIGITAL_MARKETING": self._get_digital_marketing_prompts()
        }
    
    def _get_mcq_prompt(self) -> str:
        """Get prompt template for multiple choice questions"""
        return """
        Generate a high-quality multiple choice question for {subject} on the topic of {topic}.
        
        Requirements:
        - Difficulty level: {difficulty}
        - Grade level: {grade_level}
        - Question should test {learning_objective}
        - Include 4 options (A, B, C, D)
        - Only one correct answer
        - Distractors should be plausible but clearly incorrect
        - Include a detailed explanation
        - Provide hints if needed
        
        Context: {context}
        
        Return the response in this exact JSON format:
        {{
            "question_text": "The question text here",
            "options": [
                {{"id": "A", "text": "Option A text", "is_correct": false}},
                {{"id": "B", "text": "Option B text", "is_correct": true}},
                {{"id": "C", "text": "Option C text", "is_correct": false}},
                {{"id": "D", "text": "Option D text", "is_correct": false}}
            ],
            "explanation": "Detailed explanation of why B is correct and others are wrong",
            "hints": ["Hint 1", "Hint 2"],
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "estimated_time": 60,
            "bloom_taxonomy_level": "application"
        }}
        """
    
    def _get_true_false_prompt(self) -> str:
        """Get prompt template for true/false questions"""
        return """
        Generate a high-quality true/false question for {subject} on the topic of {topic}.
        
        Requirements:
        - Difficulty level: {difficulty}
        - Grade level: {grade_level}
        - Question should test {learning_objective}
        - Statement should be clearly true or false
        - Avoid ambiguous statements
        - Include detailed explanation
        - Provide reasoning for the answer
        
        Context: {context}
        
        Return the response in this exact JSON format:
        {{
            "question_text": "The statement to evaluate",
            "correct_answer": "true",
            "explanation": "Detailed explanation of why this is true/false",
            "hints": ["Hint 1", "Hint 2"],
            "keywords": ["keyword1", "keyword2"],
            "estimated_time": 30,
            "bloom_taxonomy_level": "knowledge"
        }}
        """
    
    def _get_fill_blank_prompt(self) -> str:
        """Get prompt template for fill-in-the-blank questions"""
        return """
        Generate a high-quality fill-in-the-blank question for {subject} on the topic of {topic}.
        
        Requirements:
        - Difficulty level: {difficulty}
        - Grade level: {grade_level}
        - Question should test {learning_objective}
        - Use _____ for blanks
        - Provide clear context
        - Include possible alternative answers
        - Include detailed explanation
        
        Context: {context}
        
        Return the response in this exact JSON format:
        {{
            "question_text": "The sentence with _____ blanks to fill",
            "correct_answer": "primary answer",
            "alternative_answers": ["alternative1", "alternative2"],
            "explanation": "Detailed explanation of the answer",
            "hints": ["Hint 1", "Hint 2"],
            "keywords": ["keyword1", "keyword2"],
            "estimated_time": 45,
            "bloom_taxonomy_level": "comprehension"
        }}
        """
    
    def _get_short_answer_prompt(self) -> str:
        """Get prompt template for short answer questions"""
        return """
        Generate a high-quality short answer question for {subject} on the topic of {topic}.
        
        Requirements:
        - Difficulty level: {difficulty}
        - Grade level: {grade_level}
        - Question should test {learning_objective}
        - Answer should be 1-3 sentences
        - Include key points for grading
        - Include detailed explanation
        
        Context: {context}
        
        Return the response in this exact JSON format:
        {{
            "question_text": "The question requiring a short answer",
            "correct_answer": "Sample correct answer",
            "key_points": ["Key point 1", "Key point 2", "Key point 3"],
            "explanation": "Detailed explanation and grading rubric",
            "hints": ["Hint 1", "Hint 2"],
            "keywords": ["keyword1", "keyword2"],
            "estimated_time": 120,
            "bloom_taxonomy_level": "analysis"
        }}
        """
    
    def _get_essay_prompt(self) -> str:
        """Get prompt template for essay questions"""
        return """
        Generate a high-quality essay question for {subject} on the topic of {topic}.
        
        Requirements:
        - Difficulty level: {difficulty}
        - Grade level: {grade_level}
        - Question should test {learning_objective}
        - Should require critical thinking
        - Include grading rubric
        - Include sample answer outline
        
        Context: {context}
        
        Return the response in this exact JSON format:
        {{
            "question_text": "The essay question",
            "grading_rubric": {{
                "excellent": "Criteria for excellent (90-100%)",
                "good": "Criteria for good (80-89%)",
                "satisfactory": "Criteria for satisfactory (70-79%)",
                "needs_improvement": "Criteria for needs improvement (60-69%)"
            }},
            "sample_outline": ["Point 1", "Point 2", "Point 3"],
            "explanation": "What the question is testing and how to approach it",
            "keywords": ["keyword1", "keyword2"],
            "estimated_time": 1800,
            "bloom_taxonomy_level": "synthesis"
        }}
        """

    def _get_pharmacy_clinical_prompt(self) -> str:
        """Get specialized prompt for pharmacy clinical cases"""
        return """
        Generate a clinical pharmacy case question for {subject} - {topic}.

        Patient Case:
        - Age: {age}, Gender: {gender}
        - Medical conditions: {conditions}
        - Current medications: {medications}
        - Allergies: {allergies}
        - Lab values: {lab_values}

        Requirements:
        - Difficulty level: {difficulty}
        - Test pharmaceutical care decision-making
        - Include drug interactions, dosing, or monitoring
        - Consider patient-specific factors
        - Provide evidence-based recommendations

        Clinical scenario: {context}

        Return in JSON format:
        {{
            "case_presentation": "Detailed patient case",
            "question_text": "What is the most appropriate pharmaceutical intervention?",
            "options": [
                {{"id": "A", "text": "Option A", "is_correct": false}},
                {{"id": "B", "text": "Option B", "is_correct": true}},
                {{"id": "C", "text": "Option C", "is_correct": false}},
                {{"id": "D", "text": "Option D", "is_correct": false}}
            ],
            "clinical_reasoning": "Evidence-based rationale for the correct answer",
            "monitoring_parameters": ["Parameter 1", "Parameter 2"],
            "patient_counseling_points": ["Point 1", "Point 2"],
            "drug_information": "Relevant pharmacological information",
            "keywords": ["pharmacy", "clinical", "patient care"],
            "estimated_time": 300,
            "competency_area": "Patient Care and Consultation"
        }}
        """

    def _get_pharmacy_calculation_prompt(self) -> str:
        """Get specialized prompt for pharmacy calculations"""
        return """
        Generate a pharmaceutical calculation problem for {subject} - {topic}.

        Calculation type: {calculation_type}
        Clinical context: {context}

        Requirements:
        - Difficulty level: {difficulty}
        - Include realistic clinical values
        - Test pharmaceutical mathematics
        - Show units and proper significant figures
        - Provide step-by-step solution

        Return in JSON format:
        {{
            "problem_statement": "Clear calculation problem with given values",
            "question_text": "Calculate the required dose/concentration/etc.",
            "given_values": {{
                "parameter1": "value with units",
                "parameter2": "value with units"
            }},
            "solution_steps": [
                "Step 1: Identify the formula",
                "Step 2: Substitute values",
                "Step 3: Calculate result"
            ],
            "final_answer": "Answer with correct units and significant figures",
            "formula_used": "Relevant pharmaceutical formula",
            "clinical_significance": "Why this calculation matters in practice",
            "keywords": ["calculation", "dosing", "pharmaceutical math"],
            "estimated_time": 180
        }}
        """

    async def generate_questions(
        self,
        subject_id: str,
        topic_id: Optional[str],
        question_type: QuestionType,
        difficulty_level: DifficultyLevel,
        count: int,
        grade_level: Optional[str] = None,
        learning_objective: Optional[str] = None,
        context: Optional[str] = None,
        user_id: Optional[str] = None,
        institute_id: Optional[str] = None,
        db: Session = None
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Generate questions using AI
        
        Returns:
            (success, message, questions_data)
        """
        try:
            start_time = time.time()
            
            # Create generation record
            generation_record = None
            if db and user_id:
                generation_record = AIQuestionGeneration(
                    requested_by=user_id,
                    institute_id=institute_id,
                    subject_id=subject_id,
                    topic_id=topic_id,
                    question_type=question_type.value,
                    difficulty_level=difficulty_level.value,
                    count_requested=count,
                    ai_model="gpt-4" if self.openai_client else "huggingface",
                    status="processing"
                )
                db.add(generation_record)
                db.commit()
            
            # Get subject and topic information
            subject_info = await self._get_subject_info(subject_id, db)
            topic_info = await self._get_topic_info(topic_id, db) if topic_id else None
            
            # Generate questions
            questions = []
            for i in range(count):
                try:
                    question_data = await self._generate_single_question(
                        subject_info=subject_info,
                        topic_info=topic_info,
                        question_type=question_type,
                        difficulty_level=difficulty_level,
                        grade_level=grade_level,
                        learning_objective=learning_objective,
                        context=context
                    )
                    
                    if question_data:
                        questions.append(question_data)
                    
                except Exception as e:
                        print(f"Error generating question {i+1}: {str(e)}")
                        continue
            
            generation_time = time.time() - start_time
            
            # Update generation record
            if generation_record:
                generation_record.count_generated = len(questions)
                generation_record.generation_time = generation_time
                generation_record.status = "completed" if questions else "failed"
                generation_record.completed_at = datetime.utcnow()
                if not questions:
                    generation_record.error_message = "No questions generated successfully"
                db.commit()
            
            if not questions:
                return False, "Failed to generate any questions", []
            
            return True, f"Successfully generated {len(questions)} questions", questions
            
        except Exception as e:
            if generation_record:
                generation_record.status = "failed"
                generation_record.error_message = str(e)
                generation_record.completed_at = datetime.utcnow()
                db.commit()
            
            return False, f"Question generation failed: {str(e)}", []
    
    async def _generate_single_question(
        self,
        subject_info: Dict[str, Any],
        topic_info: Optional[Dict[str, Any]],
        question_type: QuestionType,
        difficulty_level: DifficultyLevel,
        grade_level: Optional[str],
        learning_objective: Optional[str],
        context: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Generate a single question using AI"""
        try:
            # Determine if we need specialized prompts
            subject_code = subject_info.get("code", "").upper()

            # Check for specialized prompts first
            if subject_code in self.specialized_prompts:
                prompt_template = self._get_specialized_prompt(
                    subject_code, question_type, topic_info
                )
            else:
                prompt_template = self.prompts.get(question_type)

            if not prompt_template:
                raise ValueError(f"No prompt template for question type: {question_type}")

            # Prepare context for specialized subjects
            specialized_context = self._prepare_specialized_context(
                subject_code, topic_info, context
            )

            prompt = prompt_template.format(
                subject=subject_info.get("name", ""),
                topic=topic_info.get("name", "") if topic_info else "general",
                difficulty=difficulty_level.value,
                grade_level=grade_level or "general",
                learning_objective=learning_objective or "understanding",
                context=specialized_context,
                **specialized_context  # Unpack additional context variables
            )
            
            # Generate using available AI service
            if self.openai_client:
                response = await self._generate_with_openai(prompt)
            else:
                response = await self._generate_with_huggingface(prompt)
            
            if not response:
                return None
            
            # Parse and validate response
            question_data = self._parse_ai_response(response, question_type)
            if not question_data:
                return None
            
            # Add metadata
            question_data.update({
                "subject_id": subject_info.get("id"),
                "topic_id": topic_info.get("id") if topic_info else None,
                "question_type": question_type.value,
                "difficulty_level": difficulty_level.value,
                "grade_level": grade_level,
                "ai_generated": True,
                "ai_model_used": "gpt-4" if self.openai_client else "huggingface",
                "generation_prompt": prompt[:500],  # Store first 500 chars
                "status": QuestionStatus.PENDING_REVIEW.value
            })
            
            return question_data
            
        except Exception as e:
            print(f"Error generating single question: {str(e)}")
            return None
    
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Generate question using OpenAI GPT"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator specializing in generating high-quality exam questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI generation error: {str(e)}")
            return None
    
    async def _generate_with_huggingface(self, prompt: str) -> Optional[str]:
        """Generate question using Hugging Face models"""
        try:
            # Use a free text generation model
            if "text_generator" not in self.huggingface_models:
                self.huggingface_models["text_generator"] = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    tokenizer="microsoft/DialoGPT-medium"
                )
            
            generator = self.huggingface_models["text_generator"]
            
            # Generate response
            response = await asyncio.to_thread(
                generator,
                prompt,
                max_length=1000,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            if response and len(response) > 0:
                return response[0]["generated_text"]
            
            return None
            
        except Exception as e:
            print(f"Hugging Face generation error: {str(e)}")
            # Fallback to template-based generation
            return self._generate_fallback_question(prompt)
    
    def _generate_fallback_question(self, prompt: str) -> str:
        """Fallback question generation when AI services are unavailable"""
        # Extract key information from prompt
        if "multiple choice" in prompt.lower():
            return json.dumps({
                "question_text": "What is the primary concept being tested in this topic?",
                "options": [
                    {"id": "A", "text": "Concept A", "is_correct": False},
                    {"id": "B", "text": "Concept B", "is_correct": True},
                    {"id": "C", "text": "Concept C", "is_correct": False},
                    {"id": "D", "text": "Concept D", "is_correct": False}
                ],
                "explanation": "This question tests understanding of the core concept.",
                "hints": ["Consider the main learning objective", "Think about the key principles"],
                "keywords": ["concept", "understanding", "principle"],
                "estimated_time": 60,
                "bloom_taxonomy_level": "comprehension"
            })
        
        elif "true/false" in prompt.lower():
            return json.dumps({
                "question_text": "The main concept in this topic is fundamental to understanding the subject.",
                "correct_answer": "true",
                "explanation": "This statement is true because the concept is indeed fundamental.",
                "hints": ["Think about the importance of the concept"],
                "keywords": ["concept", "fundamental"],
                "estimated_time": 30,
                "bloom_taxonomy_level": "knowledge"
            })
        
        # Default fallback
        return json.dumps({
            "question_text": "Explain the main concept covered in this topic.",
            "correct_answer": "The main concept involves understanding the key principles and their applications.",
            "explanation": "This question tests comprehension of the topic's core concepts.",
            "keywords": ["concept", "understanding"],
            "estimated_time": 120,
            "bloom_taxonomy_level": "comprehension"
        })
    
    def _parse_ai_response(self, response: str, question_type: QuestionType) -> Optional[Dict[str, Any]]:
        """Parse AI response and validate format"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return None
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            # Validate required fields based on question type
            if question_type == QuestionType.MULTIPLE_CHOICE:
                required_fields = ["question_text", "options", "explanation"]
                if not all(field in data for field in required_fields):
                    return None
                
                # Validate options format
                if not isinstance(data["options"], list) or len(data["options"]) != 4:
                    return None
                
                # Ensure exactly one correct answer
                correct_count = sum(1 for opt in data["options"] if opt.get("is_correct", False))
                if correct_count != 1:
                    return None
            
            elif question_type == QuestionType.TRUE_FALSE:
                required_fields = ["question_text", "correct_answer", "explanation"]
                if not all(field in data for field in required_fields):
                    return None
                
                if data["correct_answer"].lower() not in ["true", "false"]:
                    return None
            
            return data
            
        except json.JSONDecodeError:
            return None
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
            return None
    
    async def _get_subject_info(self, subject_id: str, db: Session) -> Dict[str, Any]:
        """Get subject information"""
        if not db:
            return {"id": subject_id, "name": "General Subject"}
        
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return {"id": subject_id, "name": "Unknown Subject"}
        
        return {
            "id": str(subject.id),
            "name": subject.name,
            "code": subject.code,
            "description": subject.description
        }
    
    async def _get_topic_info(self, topic_id: str, db: Session) -> Dict[str, Any]:
        """Get topic information"""
        if not db:
            return {"id": topic_id, "name": "General Topic"}
        
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return {"id": topic_id, "name": "Unknown Topic"}
        
        return {
            "id": str(topic.id),
            "name": topic.name,
            "description": topic.description,
            "learning_objectives": topic.learning_objectives
        }
    
    async def save_generated_questions(
        self,
        questions_data: List[Dict[str, Any]],
        created_by: str,
        db: Session
    ) -> Tuple[bool, str, List[str]]:
        """Save generated questions to database"""
        try:
            saved_question_ids = []
            
            for question_data in questions_data:
                question = Question(
                    question_text=question_data["question_text"],
                    question_type=question_data["question_type"],
                    difficulty_level=question_data["difficulty_level"],
                    subject_id=question_data["subject_id"],
                    topic_id=question_data.get("topic_id"),
                    grade_level=question_data.get("grade_level"),
                    options=question_data.get("options"),
                    correct_answer=question_data.get("correct_answer"),
                    explanation=question_data.get("explanation"),
                    hints=question_data.get("hints"),
                    keywords=question_data.get("keywords", []),
                    ai_generated=question_data.get("ai_generated", True),
                    ai_model_used=question_data.get("ai_model_used"),
                    generation_prompt=question_data.get("generation_prompt"),
                    generation_metadata=question_data.get("generation_metadata", {}),
                    status=question_data.get("status", QuestionStatus.PENDING_REVIEW.value),
                    created_by=created_by
                )
                
                db.add(question)
                db.flush()  # Get the ID
                saved_question_ids.append(str(question.id))
            
            db.commit()
            
            return True, f"Successfully saved {len(saved_question_ids)} questions", saved_question_ids
            
        except Exception as e:
            db.rollback()
            return False, f"Failed to save questions: {str(e)}", []

    def _get_specialized_prompt(
        self,
        subject_code: str,
        question_type: QuestionType,
        topic_info: Optional[Dict[str, Any]]
    ) -> str:
        """Get specialized prompt based on subject and question type"""

        # Pharmacy-specific prompts
        if subject_code == "PHARM":
            topic_name = topic_info.get("name", "").lower() if topic_info else ""

            if "clinical" in topic_name or question_type == QuestionType.SHORT_ANSWER:
                return self._get_pharmacy_clinical_prompt()
            elif "calculation" in topic_name or "kinetic" in topic_name:
                return self._get_pharmacy_calculation_prompt()
            else:
                # Use specialized pharmacy MCQ prompt
                return """
                Generate a high-quality pharmacy question for {subject} - {topic}.

                Requirements:
                - Difficulty level: {difficulty}
                - Focus on pharmaceutical sciences
                - Include drug names, mechanisms, or clinical applications
                - Test pharmacy-specific knowledge
                - Provide evidence-based explanations

                Context: {context}

                Return in JSON format with question_text, options (if MCQ), explanation, and pharmaceutical_relevance.
                """

        # Default to standard prompts
        return self.prompts.get(question_type, self._get_mcq_prompt())

    def _prepare_specialized_context(
        self,
        subject_code: str,
        topic_info: Optional[Dict[str, Any]],
        base_context: Optional[str]
    ) -> Dict[str, str]:
        """Prepare specialized context variables for different subjects"""

        context = {
            "context": base_context or "general academic context"
        }

        if subject_code == "PHARM":
            context.update({
                "age": "45",
                "gender": "Female",
                "conditions": "Hypertension, Type 2 Diabetes",
                "medications": "Metformin 1000mg BID, Lisinopril 10mg daily",
                "allergies": "NKDA",
                "lab_values": "HbA1c: 7.2%, BP: 145/90 mmHg",
                "calculation_type": "dosing calculation",
                "clinical_scenario": "medication therapy management"
            })

        return context

    def _get_neet_prompts(self) -> Dict[str, str]:
        """Get NEET-specific question prompts"""
        return {
            "physics": """
            Generate a NEET Physics question for {topic}.

            Requirements:
            - Follow NEET syllabus and pattern
            - Difficulty level: {difficulty}
            - Include numerical problems when appropriate
            - Test conceptual understanding
            - Provide detailed solution with formulas
            - Include common mistakes to avoid

            NEET Physics topics: Mechanics, Thermodynamics, Electromagnetism, Optics, Modern Physics

            Return in NEET format with 4 options and detailed explanation.
            """,

            "chemistry": """
            Generate a NEET Chemistry question for {topic}.

            Requirements:
            - Follow NEET syllabus (Physical, Organic, Inorganic Chemistry)
            - Difficulty level: {difficulty}
            - Include chemical equations and structures
            - Test both theoretical and numerical concepts
            - Provide step-by-step solution
            - Include memory tricks for organic reactions

            Context: {context}

            Return in NEET format with proper chemical notation.
            """,

            "biology": """
            Generate a NEET Biology question for {topic}.

            Requirements:
            - Follow NEET syllabus (Botany and Zoology)
            - Difficulty level: {difficulty}
            - Include diagrams description when relevant
            - Test factual knowledge and application
            - Provide detailed biological explanation
            - Include classification and terminology

            Biology areas: Cell Biology, Genetics, Ecology, Human Physiology, Plant Physiology

            Return in NEET format with biological accuracy.
            """
        }

    def _get_jee_prompts(self) -> Dict[str, str]:
        """Get JEE-specific question prompts"""
        return {
            "mathematics": """
            Generate a JEE Mathematics question for {topic}.

            Requirements:
            - Follow JEE Main/Advanced syllabus
            - Difficulty level: {difficulty}
            - Include multiple approaches to solution
            - Test problem-solving skills
            - Provide step-by-step mathematical solution
            - Include shortcuts and tricks

            JEE Math topics: Algebra, Calculus, Coordinate Geometry, Trigonometry, Statistics

            Context: {context}

            Return in JEE format with detailed mathematical working.
            """,

            "physics": """
            Generate a JEE Physics question for {topic}.

            Requirements:
            - Follow JEE Main/Advanced syllabus
            - Difficulty level: {difficulty}
            - Include numerical problem-solving
            - Test conceptual depth and application
            - Provide detailed physics explanation
            - Include relevant formulas and constants

            JEE Physics: Mechanics, Heat & Thermodynamics, Waves & Optics, Electricity & Magnetism, Modern Physics

            Return in JEE format with proper physics notation.
            """,

            "chemistry": """
            Generate a JEE Chemistry question for {topic}.

            Requirements:
            - Follow JEE Main/Advanced syllabus
            - Difficulty level: {difficulty}
            - Include chemical calculations and mechanisms
            - Test both theoretical and numerical skills
            - Provide detailed chemical explanation
            - Include reaction mechanisms for organic chemistry

            JEE Chemistry: Physical Chemistry, Organic Chemistry, Inorganic Chemistry

            Return in JEE format with proper chemical equations.
            """
        }

    def _get_cbse_prompts(self) -> Dict[str, str]:
        """Get CBSE board-specific prompts"""
        return {
            "class_10": """
            Generate a CBSE Class 10 question for {subject} - {topic}.

            Requirements:
            - Follow CBSE Class 10 syllabus and pattern
            - Difficulty level: {difficulty}
            - Include both objective and subjective elements
            - Test NCERT concepts
            - Provide detailed explanation suitable for Class 10 level
            - Include real-life applications

            CBSE Class 10 subjects: Mathematics, Science, Social Science, English, Hindi

            Context: {context}

            Return in CBSE board exam format.
            """,

            "class_12": """
            Generate a CBSE Class 12 question for {subject} - {topic}.

            Requirements:
            - Follow CBSE Class 12 syllabus and pattern
            - Difficulty level: {difficulty}
            - Include analytical and application-based questions
            - Test higher-order thinking skills
            - Provide comprehensive explanation
            - Include case studies when relevant

            CBSE Class 12 subjects: Physics, Chemistry, Mathematics, Biology, Economics, Political Science

            Return in CBSE board exam format with proper marking scheme.
            """
        }

    def _get_state_board_prompts(self) -> Dict[str, str]:
        """Get state board-specific prompts"""
        return {
            "maharashtra": """
            Generate a Maharashtra State Board question for {subject} - {topic}.

            Requirements:
            - Follow Maharashtra State Board syllabus
            - Include Marathi context when relevant
            - Difficulty level: {difficulty}
            - Test state-specific curriculum
            - Provide explanation in simple language
            - Include local examples and case studies

            Context: {context}

            Return in Maharashtra board format.
            """,

            "tamil_nadu": """
            Generate a Tamil Nadu State Board question for {subject} - {topic}.

            Requirements:
            - Follow Tamil Nadu State Board syllabus
            - Include Tamil cultural context when relevant
            - Difficulty level: {difficulty}
            - Test state-specific curriculum
            - Provide clear explanation
            - Include regional examples

            Return in Tamil Nadu board format.
            """
        }

    def _get_entrance_exam_prompts(self) -> Dict[str, str]:
        """Get entrance exam-specific prompts"""
        return {
            "cat": """
            Generate a CAT (Common Admission Test) question for {topic}.

            Requirements:
            - Follow CAT exam pattern and difficulty
            - Section: {section} (Verbal Ability, Data Interpretation, Quantitative Ability)
            - Test analytical and logical reasoning
            - Include time-efficient solution methods
            - Provide detailed explanation with shortcuts
            - Include common traps and how to avoid them

            Context: {context}

            Return in CAT format with strategic solving approach.
            """,

            "gate": """
            Generate a GATE question for {subject} - {topic}.

            Requirements:
            - Follow GATE syllabus and pattern
            - Engineering subject: {subject}
            - Difficulty level: {difficulty}
            - Test technical depth and application
            - Include numerical problems
            - Provide step-by-step technical solution

            GATE subjects: CS, EC, EE, ME, CE, CH, etc.

            Return in GATE format with proper technical notation.
            """
        }

    def _get_cloud_prompts(self) -> Dict[str, str]:
        """Get cloud certification-specific prompts"""
        return {
            "aws": """
            Generate an AWS certification question for {certification_level} - {topic}.

            Requirements:
            - AWS certification: {certification_name}
            - Difficulty level: {difficulty}
            - Test practical AWS knowledge and best practices
            - Include real-world scenarios
            - Focus on AWS services and architecture
            - Provide detailed explanation with AWS documentation references

            AWS Services context: {aws_services}
            Scenario: {context}

            Return in AWS certification format with service-specific details.
            """,

            "azure": """
            Generate a Microsoft Azure certification question for {certification_level} - {topic}.

            Requirements:
            - Azure certification: {certification_name}
            - Difficulty level: {difficulty}
            - Test Azure services and solutions
            - Include hands-on scenarios
            - Focus on Azure architecture and best practices
            - Provide step-by-step Azure solution

            Azure context: {context}

            Return in Azure certification format with proper Azure terminology.
            """,

            "gcp": """
            Generate a Google Cloud Platform certification question for {certification_level} - {topic}.

            Requirements:
            - GCP certification: {certification_name}
            - Difficulty level: {difficulty}
            - Test GCP services and architecture
            - Include practical implementation scenarios
            - Focus on Google Cloud best practices
            - Provide detailed GCP solution approach

            GCP context: {context}

            Return in GCP certification format with Google Cloud specifics.
            """
        }

    def _get_programming_prompts(self) -> Dict[str, str]:
        """Get programming language-specific prompts"""
        return {
            "python": """
            Generate a Python programming question for {specialization} - {topic}.

            Requirements:
            - Python specialization: {specialization}
            - Difficulty level: {difficulty}
            - Include practical coding scenarios
            - Test Python best practices and idioms
            - Focus on {framework} framework when applicable
            - Provide working code examples
            - Include error handling and optimization

            Python context: {context}
            Libraries: {libraries}

            Return with Python code examples and detailed explanation.
            """,

            "java": """
            Generate a Java programming question for {specialization} - {topic}.

            Requirements:
            - Java specialization: {specialization}
            - Difficulty level: {difficulty}
            - Test Java OOP principles and design patterns
            - Include enterprise Java concepts
            - Focus on {framework} framework when applicable
            - Provide complete Java code solutions
            - Include JVM optimization concepts

            Java context: {context}

            Return with Java code examples and enterprise best practices.
            """,

            "javascript": """
            Generate a JavaScript programming question for {specialization} - {topic}.

            Requirements:
            - JavaScript specialization: {specialization}
            - Difficulty level: {difficulty}
            - Test modern JavaScript (ES6+) features
            - Include async/await and Promise concepts
            - Focus on {framework} framework when applicable
            - Provide working JavaScript code
            - Include performance optimization

            JavaScript context: {context}

            Return with modern JavaScript examples and best practices.
            """
        }

    def _get_devops_prompts(self) -> Dict[str, str]:
        """Get DevOps-specific prompts"""
        return {
            "docker": """
            Generate a Docker certification question for {topic}.

            Requirements:
            - Docker concept: {topic}
            - Difficulty level: {difficulty}
            - Test containerization best practices
            - Include Dockerfile optimization
            - Focus on container security and networking
            - Provide practical Docker commands
            - Include multi-stage builds and orchestration

            Docker scenario: {context}

            Return with Docker commands and container architecture.
            """,

            "kubernetes": """
            Generate a Kubernetes certification question for {certification} - {topic}.

            Requirements:
            - Kubernetes certification: {certification}
            - Difficulty level: {difficulty}
            - Test K8s cluster management and troubleshooting
            - Include YAML manifests and kubectl commands
            - Focus on pods, services, and deployments
            - Provide cluster architecture solutions
            - Include security and networking concepts

            Kubernetes scenario: {context}

            Return with K8s manifests and kubectl commands.
            """,

            "cicd": """
            Generate a CI/CD pipeline question for {tool} - {topic}.

            Requirements:
            - CI/CD tool: {tool}
            - Difficulty level: {difficulty}
            - Test pipeline design and automation
            - Include build, test, and deployment stages
            - Focus on DevOps best practices
            - Provide pipeline configuration
            - Include monitoring and rollback strategies

            CI/CD scenario: {context}

            Return with pipeline configuration and DevOps practices.
            """
        }

    def _get_finance_prompts(self) -> Dict[str, str]:
        """Get financial certification-specific prompts"""
        return {
            "ca": """
            Generate a Chartered Accountancy question for {level} - {subject}.

            Requirements:
            - CA level: {level}
            - Subject: {subject}
            - Difficulty level: {difficulty}
            - Test Indian accounting standards and tax laws
            - Include practical accounting scenarios
            - Focus on ICAI syllabus and guidelines
            - Provide step-by-step accounting treatment
            - Include relevant sections and provisions

            CA context: {context}

            Return in CA examination format with proper accounting treatment.
            """,

            "cfa": """
            Generate a CFA (Chartered Financial Analyst) question for {level} - {topic}.

            Requirements:
            - CFA level: {level}
            - Topic area: {topic}
            - Difficulty level: {difficulty}
            - Test investment analysis and portfolio management
            - Include quantitative and qualitative analysis
            - Focus on CFA Institute curriculum
            - Provide detailed financial calculations
            - Include ethical considerations

            CFA context: {context}

            Return in CFA examination format with financial analysis.
            """
        }


# Global AI question generator instance
ai_question_generator = AIQuestionGenerator()
