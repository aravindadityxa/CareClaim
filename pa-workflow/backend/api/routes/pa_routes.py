"""
Claim Request Routes

Handles claim submission, status tracking, and document management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Form
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pathlib import Path
from datetime import datetime
import json
import logging

from core.config import settings
from ..middleware.auth import require_role, User, get_current_user
from ..schemas import pa_schemas
from workflows.claim_processing import process_claim

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/claims", tags=["claims"])

# Simple in-memory cache for demo (replace with database in production)
claim_cache: Dict[str, Dict[str, Any]] = {}
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def process_claim_background(claim_id: UUID, claim_data: Dict[str, Any]):
    """Background task to process claim"""
    try:
        logger.info(f"Processing claim {claim_id} in background")
        result = await process_claim(claim_id, claim_data)
        
        # Update cache with result
        if str(claim_id) in claim_cache:
            claim_cache[str(claim_id)].update(result)
        else:
            claim_cache[str(claim_id)] = result
            
        logger.info(f"Claim {claim_id} processing complete. Decision: {result.get('decision')}")
    except Exception as e:
        logger.error(f"Error processing claim {claim_id}: {str(e)}")
        if str(claim_id) in claim_cache:
            claim_cache[str(claim_id)].update({
                "status": "ERROR",
                "error": str(e),
            })


@router.post("/submit", response_model=pa_schemas.PAStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_claim(
    background_tasks: BackgroundTasks,
    patient_name: str = Form(...),
    patient_id: str = Form(...),
    provider_name: str = Form(...),
    provider_npi: str = Form(...),
    service_date: str = Form(...),
    icd10_codes: str = Form("[]"),
    cpt_codes: str = Form("[]"),
    billed_amount: float = Form(...),
    documents: List[UploadFile] = File(...),
    clinical_notes: Optional[str] = Form(None),
    current_user: User = Depends(require_role(["PROVIDER", "ADMIN"]))
):
    """
    Submit a new claim for processing.
    
    - **patient_name**: Full name of the patient
    - **patient_id**: Patient identifier/member ID
    - **provider_name**: Name of the healthcare provider
    - **provider_npi**: National Provider Identifier (10 digits)
    - **service_date**: Date of service (YYYY-MM-DD)
    - **icd10_codes**: ICD-10 diagnosis codes (comma-separated or JSON array)
    - **cpt_codes**: CPT procedure codes (comma-separated or JSON array)
    - **billed_amount**: Amount billed for the service
    - **documents**: Medical documents (PDFs, images)
    - **clinical_notes**: Optional clinical justification
    """
    
    claim_id = uuid4()
    logger.info(f"Submitting claim {claim_id} for patient {patient_id}")
    
    # Parse codes
    try:
        icd10_list = json.loads(icd10_codes) if icd10_codes.strip().startswith("[") else [
            c.strip() for c in icd10_codes.split(",") if c.strip()
        ]
    except:
        icd10_list = [c.strip() for c in icd10_codes.split(",") if c.strip()]
    
    try:
        cpt_list = json.loads(cpt_codes) if cpt_codes.strip().startswith("[") else [
            c.strip() for c in cpt_codes.split(",") if c.strip()
        ]
    except:
        cpt_list = [c.strip() for c in cpt_codes.split(",") if c.strip()]
    
    # Save uploaded documents
    document_paths = []
    for file in documents:
        if file.filename:
            file_path = UPLOAD_DIR / str(claim_id) / file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            document_paths.append(str(file_path))
    
    # Build claim data
    claim_data = {
        "patient_name": patient_name,
        "patient_id": patient_id,
        "provider_name": provider_name,
        "provider_npi": provider_npi,
        "service_date": service_date,
        "icd10_codes": icd10_list,
        "cpt_codes": cpt_list,
        "billed_amount": billed_amount,
        "document_paths": document_paths,
        "clinical_notes": clinical_notes or "",
        "ocr_confidence": 0.85,
        "text_quality": 0.80,
    }
    
    # Initialize cache entry
    claim_cache[str(claim_id)] = {
        "pa_id": str(claim_id),
        "status": "PROCESSING",
        "created_at": datetime.now().isoformat(),
        "submitted_by": current_user.id,
    }
    
    # Queue background processing
    background_tasks.add_task(process_claim_background, claim_id, claim_data)
    
    logger.info(f"Claim {claim_id} queued for processing")
    
    return {
        "pa_id": str(claim_id),
        "status": "PROCESSING",
        "final_score": None,
        "risk_flag": None,
        "decision": None,
        "auth_code": None,
        "auth_valid_until": None,
        "created_at": datetime.now().isoformat(),
        "decided_at": None,
    }


@router.get("/{claim_id}", response_model=pa_schemas.PADetailResponse)
async def get_claim_status(
    claim_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get the current status and details of a claim."""
    
    claim = claim_cache.get(str(claim_id))
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    return {
        "pa_id": claim.get("pa_id"),
        "status": claim.get("status", "PROCESSING"),
        "final_score": claim.get("final_score"),
        "risk_flag": claim.get("risk_flag"),
        "decision": claim.get("decision"),
        "auth_code": claim.get("auth_code"),
        "auth_valid_until": claim.get("auth_valid_until"),
        "created_at": claim.get("created_at"),
        "decided_at": claim.get("decided_at"),
        "details": {
            "validation_issues": claim.get("validation_issues", []),
            "anomalies": claim.get("anomalies", []),
            "processing_steps": claim.get("processing_steps", []),
        },
    }


@router.post("/{claim_id}/documents", response_model=pa_schemas.DocumentUploadResponse)
async def upload_claim_documents(
    claim_id: UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_role(["PROVIDER", "ADMIN"]))
):
    """Upload additional documents for a claim."""
    
    claim = claim_cache.get(str(claim_id))
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    document_paths = []
    for file in files:
        if file.filename:
            file_path = UPLOAD_DIR / str(claim_id) / file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            document_paths.append(str(file_path))
    
    logger.info(f"Uploaded {len(document_paths)} documents for claim {claim_id}")
    
    return {
        "pa_id": claim.get("pa_id"),
        "uploaded_files": [Path(p).name for p in document_paths],
        "missing_docs": [],
        "status": claim.get("status", "PROCESSING"),
    }


@router.get("/queue/review")
async def get_review_queue(
    current_user: User = Depends(require_role(["ADJUDICATOR", "MEDICAL_DIRECTOR", "ADMIN"]))
):
    """Get claims waiting for human review."""
    
    review_claims = [
        claim for claim in claim_cache.values()
        if claim.get("decision") == "HUMAN_REVIEW" and claim.get("status") == "COMPLETED"
    ]
    
    return {
        "count": len(review_claims),
        "claims": review_claims,
    }


@router.post("/{claim_id}/review")
async def submit_review_decision(
    claim_id: UUID,
    decision: str = Form(...),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(require_role(["ADJUDICATOR", "MEDICAL_DIRECTOR"]))
):
    """Submit a human review decision for a claim."""
    
    claim = claim_cache.get(str(claim_id))
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    if decision not in ["APPROVE", "DENY", "ESCALATE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be APPROVE, DENY, or ESCALATE"
        )
    
    final_decision = "AUTO_APPROVE" if decision == "APPROVE" else "AUTO_DENY"
    
    claim.update({
        "decision": final_decision,
        "reviewed_by": current_user.id,
        "review_notes": notes,
        "reviewed_at": datetime.now().isoformat(),
    })
    
    logger.info(f"Review decision submitted for claim {claim_id}: {decision}")
    
    return {
        "claim_id": str(claim_id),
        "decision": final_decision,
        "status": "COMPLETED",
        "reviewed_at": datetime.now().isoformat(),
    }


@router.get("/")
async def list_claims(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List claims with optional status filtering."""
    
    claims = list(claim_cache.values())
    
    if status_filter:
        claims = [c for c in claims if c.get("status") == status_filter]
    
    return {
        "count": len(claims),
        "claims": claims,
    }
