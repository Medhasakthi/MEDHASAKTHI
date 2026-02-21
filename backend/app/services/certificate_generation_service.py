"""
Certificate Generation Service for MEDHASAKTHI
Handles PDF generation with profession matching, template selection, and data population
"""
import os
import uuid
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import base64

from app.models.certificate import (
    Certificate, CertificateTemplate, CertificateGeneration,
    CertificateType, CertificateStatus, ProfessionCategory
)
from app.models.user import Institute, Student
from app.services.certificate_template_service import certificate_template_service
from app.services.certificate_watermark_service import certificate_watermark_service
from app.core.config import settings


class CertificateGenerationService:
    """Service for generating certificates with profession-specific templates"""
    
    def __init__(self):
        self.output_dir = os.path.join(settings.UPLOAD_DIR, "certificates")
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """Ensure certificate output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "thumbnails"), exist_ok=True)
    
    def generate_certificate_number(self) -> str:
        """Generate unique certificate number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = secrets.token_hex(4).upper()
        return f"MEDH-{timestamp}-{random_part}"
    
    def generate_verification_code(self) -> str:
        """Generate unique verification code"""
        return secrets.token_urlsafe(32)
    
    async def generate_single_certificate(
        self,
        certificate_data: Dict[str, Any],
        template_id: Optional[str] = None,
        db: Session = None
    ) -> Tuple[bool, str, Optional[Certificate]]:
        """Generate a single certificate"""
        
        try:
            # Get or create template
            template = await self._get_or_create_template(
                certificate_data.get("profession_category"),
                certificate_data.get("certificate_type"),
                template_id,
                db
            )
            
            if not template:
                return False, "Failed to get certificate template", None
            
            # Create certificate record
            certificate = Certificate(
                certificate_number=self.generate_certificate_number(),
                verification_code=self.generate_verification_code(),
                title=certificate_data["title"],
                description=certificate_data.get("description"),
                certificate_type=certificate_data["certificate_type"],
                recipient_name=certificate_data["recipient_name"],
                recipient_email=certificate_data["recipient_email"],
                student_id=certificate_data.get("student_id"),
                institute_id=certificate_data["institute_id"],
                issued_by=certificate_data.get("issued_by"),
                subject_name=certificate_data.get("subject_name"),
                course_name=certificate_data.get("course_name"),
                exam_name=certificate_data.get("exam_name"),
                score=certificate_data.get("score"),
                grade=certificate_data.get("grade"),
                completion_date=certificate_data.get("completion_date"),
                template_id=template.id,
                generation_data=certificate_data,
                status=CertificateStatus.DRAFT,
                valid_from=certificate_data.get("valid_from", datetime.now(timezone.utc)),
                valid_until=certificate_data.get("valid_until")
            )
            
            # Generate PDF
            pdf_success, pdf_path, thumbnail_path = await self._generate_certificate_pdf(
                certificate, template, db
            )
            
            if not pdf_success:
                return False, "Failed to generate certificate PDF", None
            
            # Update certificate with file paths
            certificate.pdf_url = pdf_path
            certificate.thumbnail_url = thumbnail_path
            certificate.status = CertificateStatus.GENERATED
            certificate.issued_at = datetime.now(timezone.utc)
            
            # Save to database
            if db:
                db.add(certificate)
                db.commit()
                db.refresh(certificate)
            
            return True, "Certificate generated successfully", certificate
            
        except Exception as e:
            return False, f"Error generating certificate: {str(e)}", None
    
    async def generate_bulk_certificates(
        self,
        certificates_data: List[Dict[str, Any]],
        template_id: Optional[str] = None,
        db: Session = None
    ) -> Tuple[bool, str, List[Certificate], List[str]]:
        """Generate multiple certificates in bulk"""
        
        generated_certificates = []
        errors = []
        batch_id = str(uuid.uuid4())
        
        # Create generation record
        generation = CertificateGeneration(
            batch_id=batch_id,
            generation_type="bulk",
            certificates_requested=len(certificates_data),
            status="processing"
        )
        
        if db:
            db.add(generation)
            db.commit()
        
        start_time = datetime.now()
        
        for i, cert_data in enumerate(certificates_data):
            try:
                success, message, certificate = await self.generate_single_certificate(
                    cert_data, template_id, db
                )
                
                if success and certificate:
                    generated_certificates.append(certificate)
                else:
                    errors.append(f"Certificate {i+1}: {message}")
                    
            except Exception as e:
                errors.append(f"Certificate {i+1}: {str(e)}")
        
        # Update generation record
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        if db and generation:
            generation.certificates_generated = len(generated_certificates)
            generation.certificates_failed = len(errors)
            generation.processing_time = processing_time
            generation.status = "completed" if not errors else "partial"
            generation.completed_at = end_time
            generation.error_details = {"errors": errors} if errors else None
            db.commit()
        
        success_message = f"Generated {len(generated_certificates)} certificates"
        if errors:
            success_message += f" with {len(errors)} errors"
        
        return True, success_message, generated_certificates, errors
    
    async def _get_or_create_template(
        self,
        profession_category: Optional[str],
        certificate_type: str,
        template_id: Optional[str],
        db: Session
    ) -> Optional[CertificateTemplate]:
        """Get existing template or create new one"""
        
        if template_id and db:
            # Use specific template
            template = db.query(CertificateTemplate).filter(
                CertificateTemplate.id == template_id,
                CertificateTemplate.is_active == True
            ).first()
            if template:
                return template
        
        # Get profession category
        prof_category = ProfessionCategory.GENERAL
        if profession_category:
            try:
                prof_category = ProfessionCategory(profession_category)
            except ValueError:
                prof_category = ProfessionCategory.GENERAL
        
        # Get certificate type
        cert_type = CertificateType.COURSE_COMPLETION
        try:
            cert_type = CertificateType(certificate_type)
        except ValueError:
            cert_type = CertificateType.COURSE_COMPLETION
        
        # Look for existing template
        if db:
            template = db.query(CertificateTemplate).filter(
                CertificateTemplate.profession_category == prof_category.value,
                CertificateTemplate.certificate_type == cert_type.value,
                CertificateTemplate.is_active == True
            ).first()
            
            if template:
                return template
        
        # Create new template
        template_config = certificate_template_service.get_template_for_profession(
            prof_category, cert_type
        )
        
        template = CertificateTemplate(
            name=f"{prof_category.value.replace('_', ' ').title()} - {cert_type.value.replace('_', ' ').title()}",
            code=f"{prof_category.value}_{cert_type.value}",
            description=f"Template for {prof_category.value} {cert_type.value} certificates",
            certificate_type=cert_type.value,
            profession_category=prof_category.value,
            template_data=template_config,
            logo_position=template_config.get("logo_position"),
            watermark_settings=template_config.get("watermark_settings"),
            dimensions=template_config.get("dimensions"),
            orientation=template_config.get("orientation", "landscape"),
            is_active=True,
            is_default=True
        )
        
        if db:
            db.add(template)
            db.commit()
            db.refresh(template)
        
        return template
    
    async def _generate_certificate_pdf(
        self,
        certificate: Certificate,
        template: CertificateTemplate,
        db: Session
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate PDF certificate using template"""
        
        try:
            # Create filename
            filename = f"{certificate.certificate_number}.pdf"
            pdf_path = os.path.join(self.output_dir, filename)
            
            # Get template configuration
            template_config = template.template_data
            dimensions = template_config.get("dimensions", {"width": 1200, "height": 850, "dpi": 300})
            
            # Create PDF
            if template_config.get("orientation") == "portrait":
                page_size = (dimensions["width"], dimensions["height"])
            else:
                page_size = (dimensions["width"], dimensions["height"])
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=page_size,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            # Build content
            story = []
            styles = getSampleStyleSheet()
            
            # Create custom styles based on template
            title_style = self._create_title_style(template_config)
            body_style = self._create_body_style(template_config)
            
            # Add title
            title_text = certificate.title
            title_para = Paragraph(title_text, title_style)
            story.append(title_para)
            story.append(Spacer(1, 30))
            
            # Add recipient information
            recipient_text = f"This is to certify that<br/><br/><b>{certificate.recipient_name}</b>"
            recipient_para = Paragraph(recipient_text, body_style)
            story.append(recipient_para)
            story.append(Spacer(1, 20))
            
            # Add certificate details
            if certificate.course_name:
                course_text = f"has successfully completed the course<br/><b>{certificate.course_name}</b>"
                story.append(Paragraph(course_text, body_style))
                story.append(Spacer(1, 15))
            
            if certificate.exam_name:
                exam_text = f"and passed the examination<br/><b>{certificate.exam_name}</b>"
                story.append(Paragraph(exam_text, body_style))
                story.append(Spacer(1, 15))
            
            if certificate.score:
                score_text = f"with a score of <b>{certificate.score}%</b>"
                if certificate.grade:
                    score_text += f" (Grade: <b>{certificate.grade}</b>)"
                story.append(Paragraph(score_text, body_style))
                story.append(Spacer(1, 15))
            
            # Add completion date
            if certificate.completion_date:
                date_text = f"on {certificate.completion_date.strftime('%B %d, %Y')}"
                story.append(Paragraph(date_text, body_style))
                story.append(Spacer(1, 30))
            
            # Add verification information
            verification_text = f"Certificate Number: {certificate.certificate_number}<br/>"
            verification_text += f"Verification Code: {certificate.verification_code}"
            verification_para = Paragraph(verification_text, styles['Normal'])
            story.append(verification_para)
            
            # Build PDF
            doc.build(story)
            
            # Generate thumbnail
            thumbnail_path = await self._generate_thumbnail(pdf_path, certificate.certificate_number)
            
            # Apply watermark (if needed, this would require additional PDF processing)
            # For now, we'll note this as a future enhancement
            
            return True, pdf_path, thumbnail_path
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False, None, None
    
    def _create_title_style(self, template_config: Dict[str, Any]) -> ParagraphStyle:
        """Create title style from template configuration"""
        fonts = template_config.get("fonts", {})
        title_font = fonts.get("title", {})
        colors = template_config.get("colors", {})
        
        return ParagraphStyle(
            'CustomTitle',
            parent=getSampleStyleSheet()['Title'],
            fontSize=title_font.get("size", 36),
            textColor=HexColor(colors.get("primary", "#1a365d")),
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
    
    def _create_body_style(self, template_config: Dict[str, Any]) -> ParagraphStyle:
        """Create body style from template configuration"""
        fonts = template_config.get("fonts", {})
        body_font = fonts.get("body", {})
        colors = template_config.get("colors", {})
        
        return ParagraphStyle(
            'CustomBody',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=body_font.get("size", 18),
            textColor=HexColor(colors.get("secondary", "#2d3748")),
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica'
        )
    
    async def _generate_thumbnail(self, pdf_path: str, certificate_number: str) -> Optional[str]:
        """Generate thumbnail from PDF"""
        try:
            # For now, create a simple placeholder thumbnail
            # In production, you'd use pdf2image or similar library
            thumbnail_filename = f"{certificate_number}_thumb.png"
            thumbnail_path = os.path.join(self.output_dir, "thumbnails", thumbnail_filename)
            
            # Create placeholder thumbnail
            thumbnail = Image.new('RGB', (300, 200), 'white')
            draw = ImageDraw.Draw(thumbnail)
            
            # Add some basic content
            draw.rectangle([10, 10, 290, 190], outline='gray', width=2)
            draw.text((150, 100), "Certificate", fill='black', anchor='mm')
            draw.text((150, 120), certificate_number, fill='gray', anchor='mm')
            
            thumbnail.save(thumbnail_path)
            return thumbnail_path
            
        except Exception as e:
            print(f"Error generating thumbnail: {str(e)}")
            return None
    
    def verify_certificate(self, verification_code: str, db: Session) -> Tuple[bool, Optional[Certificate]]:
        """Verify certificate using verification code"""
        try:
            certificate = db.query(Certificate).filter(
                Certificate.verification_code == verification_code,
                Certificate.status.in_([CertificateStatus.GENERATED, CertificateStatus.ISSUED])
            ).first()
            
            if certificate:
                # Check if certificate is still valid
                now = datetime.now(timezone.utc)
                if certificate.valid_until and certificate.valid_until < now:
                    return False, None
                
                return True, certificate
            
            return False, None
            
        except Exception as e:
            print(f"Error verifying certificate: {str(e)}")
            return False, None


# Initialize global certificate generation service
certificate_generation_service = CertificateGenerationService()
