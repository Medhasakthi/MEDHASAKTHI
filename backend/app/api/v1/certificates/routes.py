"""
Certificate API routes for MEDHASAKTHI
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_teacher_user, get_user_institute_context
from app.services.certificate_generation_service import certificate_generation_service
from app.schemas.certificate import (
    CertificateTemplateCreateSchema,
    CertificateTemplateUpdateSchema,
    CertificateTemplateResponseSchema,
    CertificateCreateSchema,
    CertificateBulkCreateSchema,
    CertificateUpdateSchema,
    CertificateResponseSchema,
    CertificateVerificationSchema,
    CertificateVerificationResponseSchema,
    CertificateGenerationRequestSchema,
    CertificateGenerationResponseSchema,
    CertificateSearchSchema,
    CertificateSearchResponseSchema,
    CertificateStatsSchema
)
from app.models.certificate import (
    Certificate, CertificateTemplate, CertificateGeneration,
    CertificateType, CertificateStatus, ProfessionCategory
)
from app.models.user import User

router = APIRouter()


# Certificate Template Routes
@router.post("/templates", response_model=CertificateTemplateResponseSchema)
async def create_certificate_template(
    template_data: CertificateTemplateCreateSchema,
    current_user: User = Depends(get_teacher_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Create a new certificate template"""
    
    # Check if template code already exists
    existing_template = db.query(CertificateTemplate).filter(
        CertificateTemplate.code == template_data.code
    ).first()
    
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template code already exists"
        )
    
    template = CertificateTemplate(
        name=template_data.name,
        code=template_data.code,
        description=template_data.description,
        certificate_type=template_data.certificate_type.value,
        profession_category=template_data.profession_category.value,
        template_data=template_data.template_data,
        background_image_url=template_data.background_image_url,
        border_style=template_data.border_style,
        logo_position=template_data.logo_position,
        watermark_settings=template_data.watermark_settings,
        dimensions=template_data.dimensions,
        orientation=template_data.orientation,
        version=template_data.version,
        is_default=template_data.is_default
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return CertificateTemplateResponseSchema.from_orm(template)


@router.get("/templates", response_model=List[CertificateTemplateResponseSchema])
async def get_certificate_templates(
    profession_category: Optional[str] = Query(None),
    certificate_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get certificate templates"""
    
    query = db.query(CertificateTemplate)
    
    if profession_category:
        query = query.filter(CertificateTemplate.profession_category == profession_category)
    
    if certificate_type:
        query = query.filter(CertificateTemplate.certificate_type == certificate_type)
    
    if is_active is not None:
        query = query.filter(CertificateTemplate.is_active == is_active)
    
    templates = query.order_by(CertificateTemplate.created_at.desc()).all()
    
    return [CertificateTemplateResponseSchema.from_orm(template) for template in templates]


@router.get("/templates/{template_id}", response_model=CertificateTemplateResponseSchema)
async def get_certificate_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific certificate template"""
    
    template = db.query(CertificateTemplate).filter(
        CertificateTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return CertificateTemplateResponseSchema.from_orm(template)


# Certificate Generation Routes
@router.post("/generate", response_model=CertificateGenerationResponseSchema)
async def generate_certificates(
    request: CertificateGenerationRequestSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_teacher_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Generate certificates"""
    
    try:
        institute_id = str(user_context["institute"].id) if user_context["institute"] else None
        
        if not institute_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Institute context required"
            )
        
        # Add institute_id to all certificate data
        certificates_data = []
        for cert_data in request.certificates:
            cert_dict = cert_data.dict()
            cert_dict["institute_id"] = institute_id
            certificates_data.append(cert_dict)
        
        if request.generation_type == "single" and len(certificates_data) == 1:
            # Generate single certificate
            success, message, certificate = await certificate_generation_service.generate_single_certificate(
                certificates_data[0], request.template_id, db
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=message
                )
            
            return CertificateGenerationResponseSchema(
                success=True,
                message=message,
                generation_id=str(certificate.id),
                certificates_requested=1,
                certificates_generated=1,
                certificates_failed=0,
                processing_time=0.0,
                generated_certificates=[CertificateResponseSchema.from_orm(certificate)]
            )
        
        else:
            # Generate bulk certificates
            success, message, certificates, errors = await certificate_generation_service.generate_bulk_certificates(
                certificates_data, request.template_id, db
            )
            
            return CertificateGenerationResponseSchema(
                success=success,
                message=message,
                generation_id=str(certificates[0].id) if certificates else None,
                certificates_requested=len(certificates_data),
                certificates_generated=len(certificates),
                certificates_failed=len(errors),
                processing_time=0.0,
                generated_certificates=[CertificateResponseSchema.from_orm(cert) for cert in certificates],
                errors=[{"error": error} for error in errors] if errors else None
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating certificates: {str(e)}"
        )


@router.get("/", response_model=CertificateSearchResponseSchema)
async def search_certificates(
    query: Optional[str] = Query(None),
    certificate_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    recipient_email: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Search certificates"""
    
    institute_id = str(user_context["institute"].id) if user_context["institute"] else None
    
    query_obj = db.query(Certificate)
    
    # Filter by institute
    if institute_id:
        query_obj = query_obj.filter(Certificate.institute_id == institute_id)
    
    # Apply filters
    if query:
        query_obj = query_obj.filter(
            Certificate.title.ilike(f"%{query}%") |
            Certificate.recipient_name.ilike(f"%{query}%") |
            Certificate.certificate_number.ilike(f"%{query}%")
        )
    
    if certificate_type:
        query_obj = query_obj.filter(Certificate.certificate_type == certificate_type)
    
    if status:
        query_obj = query_obj.filter(Certificate.status == status)
    
    if recipient_email:
        query_obj = query_obj.filter(Certificate.recipient_email == recipient_email)
    
    # Get total count
    total = query_obj.count()
    
    # Apply pagination
    certificates = query_obj.order_by(Certificate.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    total_pages = (total + limit - 1) // limit
    
    return CertificateSearchResponseSchema(
        certificates=[CertificateResponseSchema.from_orm(cert) for cert in certificates],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{certificate_id}", response_model=CertificateResponseSchema)
async def get_certificate(
    certificate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific certificate"""
    
    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id
    ).first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    return CertificateResponseSchema.from_orm(certificate)


@router.get("/{certificate_id}/download")
async def download_certificate(
    certificate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download certificate PDF"""
    
    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id
    ).first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    if not certificate.pdf_url or not os.path.exists(certificate.pdf_url):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate file not found"
        )
    
    filename = f"{certificate.certificate_number}.pdf"
    return FileResponse(
        certificate.pdf_url,
        media_type="application/pdf",
        filename=filename
    )


@router.post("/verify", response_model=CertificateVerificationResponseSchema)
async def verify_certificate(
    verification_data: CertificateVerificationSchema,
    db: Session = Depends(get_db)
):
    """Verify certificate using verification code"""
    
    is_valid, certificate = certificate_generation_service.verify_certificate(
        verification_data.verification_code, db
    )
    
    verification_details = {
        "verification_code": verification_data.verification_code,
        "verified_at": datetime.now().isoformat()
    }
    
    if is_valid and certificate:
        verification_details.update({
            "certificate_number": certificate.certificate_number,
            "recipient_name": certificate.recipient_name,
            "issued_at": certificate.issued_at.isoformat() if certificate.issued_at else None,
            "valid_until": certificate.valid_until.isoformat() if certificate.valid_until else None
        })
    
    return CertificateVerificationResponseSchema(
        is_valid=is_valid,
        certificate=CertificateResponseSchema.from_orm(certificate) if certificate else None,
        verification_details=verification_details,
        verified_at=datetime.now()
    )
