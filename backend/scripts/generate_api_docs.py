#!/usr/bin/env python3
"""
Generate comprehensive API documentation for MEDHASAKTHI
This script creates detailed API documentation with examples
"""
import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_api_documentation():
    """Generate comprehensive API documentation"""
    
    api_docs = {
        "info": {
            "title": "MEDHASAKTHI API Documentation",
            "version": "1.0.0",
            "description": "Comprehensive API documentation for MEDHASAKTHI educational platform",
            "contact": {
                "name": "MEDHASAKTHI Support",
                "email": "support@medhasakthi.com",
                "url": "https://medhasakthi.com"
            },
            "license": {
                "name": "Proprietary",
                "url": "https://medhasakthi.com/license"
            }
        },
        "servers": [
            {
                "url": "https://api.medhasakthi.com/v1",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.medhasakthi.com/v1",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000/api/v1",
                "description": "Development server"
            }
        ],
        "security": [
            {
                "bearerAuth": []
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "paths": {
            # Authentication Endpoints
            "/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "User login",
                    "description": "Authenticate user and return JWT token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 8}
                                    },
                                    "required": ["email", "password"]
                                },
                                "example": {
                                    "email": "user@example.com",
                                    "password": "securepassword123"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "data": {
                                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                            "token_type": "bearer",
                                            "expires_in": 3600,
                                            "user": {
                                                "id": "user-123",
                                                "email": "user@example.com",
                                                "full_name": "John Doe",
                                                "role": "student"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Invalid credentials"
                        }
                    }
                }
            },
            
            # Student Endpoints
            "/student/dashboard": {
                "get": {
                    "tags": ["Student"],
                    "summary": "Get student dashboard data",
                    "description": "Retrieve comprehensive dashboard information for the authenticated student",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Dashboard data retrieved successfully",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "data": {
                                            "student_info": {
                                                "student_id": "STU202401001",
                                                "name": "John Doe",
                                                "class_level": "Class 10",
                                                "section": "A",
                                                "institute_name": "Demo High School"
                                            },
                                            "statistics": {
                                                "total_exams_registered": 5,
                                                "exams_completed": 3,
                                                "average_score": 85.5,
                                                "certificates_earned": 2
                                            },
                                            "recent_exams": [],
                                            "upcoming_exams": []
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # Teacher Endpoints
            "/teacher/dashboard": {
                "get": {
                    "tags": ["Teacher"],
                    "summary": "Get teacher dashboard data",
                    "description": "Retrieve comprehensive dashboard information for the authenticated teacher",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Dashboard data retrieved successfully",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "data": {
                                            "teacher_info": {
                                                "teacher_id": "TCH202401001",
                                                "name": "Jane Smith",
                                                "department": "Mathematics",
                                                "institute_name": "Demo High School"
                                            },
                                            "statistics": {
                                                "total_students": 120,
                                                "classes_handled": 4,
                                                "subjects_taught": 2,
                                                "average_class_performance": 78.5
                                            },
                                            "assigned_classes": [],
                                            "top_performers": [],
                                            "needs_attention": []
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # Independent Learner Endpoints
            "/independent/register": {
                "post": {
                    "tags": ["Independent Learner"],
                    "summary": "Register independent learner",
                    "description": "Register a new independent learner account",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "first_name": {"type": "string"},
                                        "last_name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "phone": {"type": "string"},
                                        "category": {"type": "string", "enum": ["school_student", "college_student", "working_professional", "job_seeker"]},
                                        "education_level": {"type": "string", "enum": ["class_10th", "class_12th", "undergraduate", "postgraduate"]}
                                    },
                                    "required": ["first_name", "last_name", "email", "phone", "category", "education_level"]
                                },
                                "example": {
                                    "first_name": "John",
                                    "last_name": "Doe",
                                    "email": "john.doe@example.com",
                                    "phone": "+91-9876543210",
                                    "category": "working_professional",
                                    "education_level": "undergraduate",
                                    "current_occupation": "Software Developer",
                                    "city": "Mumbai",
                                    "state": "Maharashtra",
                                    "country": "India"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Registration successful",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Independent learner registered successfully",
                                        "data": {
                                            "learner_id": "IL202401123456",
                                            "referral_code": "JOHDOE1234",
                                            "email_verification_required": True
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            "/independent/programs": {
                "get": {
                    "tags": ["Independent Learner"],
                    "summary": "Get available certification programs",
                    "description": "Retrieve list of available certification programs",
                    "parameters": [
                        {
                            "name": "category",
                            "in": "query",
                            "description": "Filter by program category",
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "level",
                            "in": "query",
                            "description": "Filter by difficulty level",
                            "schema": {"type": "string", "enum": ["Beginner", "Intermediate", "Advanced"]}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Programs retrieved successfully",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "data": {
                                            "programs": [
                                                {
                                                    "id": "program-123",
                                                    "program_code": "WD101",
                                                    "title": "Web Development Fundamentals",
                                                    "description": "Learn the basics of web development",
                                                    "category": "Technology",
                                                    "level": "Beginner",
                                                    "base_price": 2000.00,
                                                    "duration_hours": 40,
                                                    "is_featured": True
                                                }
                                            ],
                                            "total_count": 1
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # UPI Payment Endpoints
            "/payments/upi/create-payment": {
                "post": {
                    "tags": ["UPI Payments"],
                    "summary": "Create UPI payment request",
                    "description": "Create a new UPI payment request with QR code",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "amount": {"type": "number", "minimum": 1},
                                        "description": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "phone": {"type": "string"},
                                        "name": {"type": "string"},
                                        "reference_id": {"type": "string"}
                                    },
                                    "required": ["amount", "description"]
                                },
                                "example": {
                                    "amount": 500.00,
                                    "description": "Exam Registration Fee",
                                    "email": "user@example.com",
                                    "phone": "+91-9876543210",
                                    "name": "John Doe",
                                    "reference_id": "exam-123"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Payment request created successfully",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "data": {
                                            "payment_id": "UPI20240120123456ABCD1234",
                                            "amount": 500.00,
                                            "upi_id": "medhasakthi@paytm",
                                            "upi_name": "MEDHASAKTHI Education",
                                            "payment_note": "MEDHASAKTHI-UPI20240120123456ABCD1234",
                                            "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
                                            "upi_deep_link": "upi://pay?pa=medhasakthi@paytm&pn=MEDHASAKTHI%20Education&am=500.0&tn=MEDHASAKTHI-UPI20240120123456ABCD1234&cu=INR",
                                            "expires_at": "2024-01-20T13:30:00",
                                            "instructions": [
                                                "1. Scan the QR code with any UPI app",
                                                "2. Verify the payment details",
                                                "3. Complete the payment using your UPI PIN",
                                                "4. Take a screenshot of the successful payment",
                                                "5. Upload the screenshot for verification"
                                            ],
                                            "require_screenshot": True
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            "/payments/upi/submit-proof/{payment_id}": {
                "post": {
                    "tags": ["UPI Payments"],
                    "summary": "Submit payment proof",
                    "description": "Submit payment proof with transaction ID and screenshot",
                    "parameters": [
                        {
                            "name": "payment_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "transaction_id": {"type": "string"},
                                        "payment_method": {"type": "string"},
                                        "screenshot": {"type": "string", "format": "binary"}
                                    },
                                    "required": ["transaction_id"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Payment proof submitted successfully",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "data": {
                                            "message": "Payment submitted for verification",
                                            "payment_status": "pending",
                                            "verification_status": "pending",
                                            "auto_verified": False
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # Admin Pricing Endpoints
            "/admin/pricing/global-config": {
                "post": {
                    "tags": ["Admin - Pricing"],
                    "summary": "Create global pricing configuration",
                    "description": "Create or update global pricing configuration (Super Admin only)",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "config_name": {"type": "string"},
                                        "base_exam_fee": {"type": "number"},
                                        "base_certification_fee": {"type": "number"},
                                        "student_multiplier": {"type": "number"},
                                        "professional_multiplier": {"type": "number"},
                                        "country_pricing_multipliers": {"type": "object"},
                                        "state_pricing_multipliers": {"type": "object"}
                                    }
                                },
                                "example": {
                                    "config_name": "Updated Pricing 2024",
                                    "base_exam_fee": 500.00,
                                    "base_certification_fee": 1000.00,
                                    "student_multiplier": 0.7,
                                    "professional_multiplier": 1.0,
                                    "country_pricing_multipliers": {
                                        "India": 1.0,
                                        "USA": 2.5
                                    },
                                    "state_pricing_multipliers": {
                                        "Maharashtra": 1.1,
                                        "Karnataka": 1.0
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Pricing configuration created successfully"
                        }
                    }
                }
            }
        },
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication and authorization"
            },
            {
                "name": "Student",
                "description": "Student-specific endpoints"
            },
            {
                "name": "Teacher",
                "description": "Teacher-specific endpoints"
            },
            {
                "name": "Independent Learner",
                "description": "Independent learner registration and management"
            },
            {
                "name": "UPI Payments",
                "description": "UPI payment processing and verification"
            },
            {
                "name": "Admin - Pricing",
                "description": "Super admin pricing configuration"
            }
        ]
    }
    
    return api_docs


def save_documentation():
    """Save API documentation to files"""
    
    print("📚 Generating MEDHASAKTHI API Documentation...")
    
    # Generate API docs
    api_docs = generate_api_documentation()
    
    # Create docs directory
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    # Save OpenAPI JSON
    openapi_file = os.path.join(docs_dir, "openapi.json")
    with open(openapi_file, 'w', encoding='utf-8') as f:
        json.dump(api_docs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI specification saved to: {openapi_file}")
    
    # Generate Markdown documentation
    markdown_content = generate_markdown_docs(api_docs)
    markdown_file = os.path.join(docs_dir, "API_DOCUMENTATION.md")
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Markdown documentation saved to: {markdown_file}")
    
    # Generate Postman collection
    postman_collection = generate_postman_collection(api_docs)
    postman_file = os.path.join(docs_dir, "MEDHASAKTHI_API.postman_collection.json")
    with open(postman_file, 'w', encoding='utf-8') as f:
        json.dump(postman_collection, f, indent=2)
    
    print(f"✅ Postman collection saved to: {postman_file}")
    
    print("\n🎉 API Documentation generated successfully!")
    print("\n📋 Generated Files:")
    print(f"1. OpenAPI Specification: {openapi_file}")
    print(f"2. Markdown Documentation: {markdown_file}")
    print(f"3. Postman Collection: {postman_file}")


def generate_markdown_docs(api_docs):
    """Generate Markdown documentation"""
    
    markdown = f"""# {api_docs['info']['title']}

**Version:** {api_docs['info']['version']}  
**Description:** {api_docs['info']['description']}

## Base URLs

"""
    
    for server in api_docs['servers']:
        markdown += f"- **{server['description']}:** `{server['url']}`\n"
    
    markdown += """
## Authentication

This API uses Bearer Token authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

"""
    
    for path, methods in api_docs['paths'].items():
        for method, details in methods.items():
            markdown += f"### {method.upper()} {path}\n\n"
            markdown += f"**Summary:** {details['summary']}\n\n"
            markdown += f"**Description:** {details['description']}\n\n"
            
            if 'tags' in details:
                markdown += f"**Tags:** {', '.join(details['tags'])}\n\n"
            
            if 'security' in details:
                markdown += "**Authentication:** Required\n\n"
            
            if 'requestBody' in details:
                markdown += "**Request Body:**\n```json\n"
                if 'example' in details['requestBody']['content']['application/json']:
                    markdown += json.dumps(details['requestBody']['content']['application/json']['example'], indent=2)
                markdown += "\n```\n\n"
            
            if 'responses' in details:
                for status_code, response in details['responses'].items():
                    markdown += f"**Response {status_code}:**\n"
                    if 'content' in response and 'application/json' in response['content']:
                        if 'example' in response['content']['application/json']:
                            markdown += "```json\n"
                            markdown += json.dumps(response['content']['application/json']['example'], indent=2)
                            markdown += "\n```\n\n"
            
            markdown += "---\n\n"
    
    return markdown


def generate_postman_collection(api_docs):
    """Generate Postman collection"""
    
    collection = {
        "info": {
            "name": api_docs['info']['title'],
            "description": api_docs['info']['description'],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{jwt_token}}",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000/api/v1",
                "type": "string"
            },
            {
                "key": "jwt_token",
                "value": "",
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Group endpoints by tags
    for path, methods in api_docs['paths'].items():
        for method, details in methods.items():
            item = {
                "name": details['summary'],
                "request": {
                    "method": method.upper(),
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}" + path,
                        "host": ["{{base_url}}"],
                        "path": path.strip('/').split('/')
                    }
                }
            }
            
            if 'requestBody' in details:
                item['request']['header'].append({
                    "key": "Content-Type",
                    "value": "application/json"
                })
                if 'example' in details['requestBody']['content']['application/json']:
                    item['request']['body'] = {
                        "mode": "raw",
                        "raw": json.dumps(details['requestBody']['content']['application/json']['example'], indent=2)
                    }
            
            collection['item'].append(item)
    
    return collection


if __name__ == "__main__":
    save_documentation()
