from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.application_admin import ApplicationStatusUpdate, ApplicationDetailResponse
from app.services.admin_service import AdminService
from app.utils.dependencies import get_current_admin_user as get_current_admin
from app.models.admin_user import AdminUser

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/applications", response_model=List[ApplicationDetailResponse])
async def list_all_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all applications with optional filtering by status"""
    admin_service = AdminService(db)
    return admin_service.list_all_applications(skip, limit, status)


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse)
async def get_application_details(
    application_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get application details by ID"""
    admin_service = AdminService(db)
    return admin_service.get_application_details(application_id)


@router.patch("/applications/{application_id}/status", response_model=ApplicationDetailResponse)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update application status with validation and audit logging"""
    admin_service = AdminService(db)
    return admin_service.update_application_status(
        application_id,
        status_update,
        current_admin.admin_id
    )


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering"""
    admin_service = AdminService(db)
    return admin_service.get_audit_logs(skip, limit, admin_id, action)


@router.get("/applications/{application_id}/shap-report/pdf")
async def download_admin_shap_report_pdf(
    application_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Download SHAP report as PDF (Admin access)"""
    from fastapi import HTTPException
    from fastapi.responses import Response
    from app.services.pdf_service import generate_shap_pdf
    from app.models.application import Application
    
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not application.credit_score:
        raise HTTPException(status_code=404, detail="Credit score not yet generated")
    
    # Generate PDF
    pdf_bytes = generate_shap_pdf(application, application.credit_score)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=SHAP_Report_{application_id}.pdf"
        }
    )
