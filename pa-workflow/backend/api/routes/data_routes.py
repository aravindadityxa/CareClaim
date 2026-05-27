"""
Data Routes - Reference Data Access

Provides access to reference data like payers, plans, and procedures.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from core.database import get_db
from models.postgres_models import User as DBUser, PayerMaster, PlanMaster
from ..middleware.auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data", tags=["reference-data"])


@router.get("/payers")
async def get_payers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all active payers."""
    try:
        stmt = select(PayerMaster).where(PayerMaster.is_active == True)
        result = await db.execute(stmt)
        payers = result.scalars().all()
        
        return [
            {
                "id": str(payer.payer_id),
                "name": payer.payer_name,
                "isActive": payer.is_active,
            }
            for payer in payers
        ]
    except Exception as e:
        logger.error(f"Error fetching payers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching payers"
        )


@router.get("/plans")
async def get_plans(
    payer_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get plans, optionally filtered by payer."""
    try:
        if payer_id:
            stmt = select(PlanMaster).where(
                PlanMaster.payer_id == payer_id
            )
        else:
            stmt = select(PlanMaster)
        
        result = await db.execute(stmt)
        plans = result.scalars().all()
        
        return [
            {
                "id": str(plan.plan_id),
                "payerId": str(plan.payer_id),
                "name": plan.plan_name,
                "planCode": str(plan.plan_id),
                "paRequired": plan.pa_required,
                "stepTherapyRequired": plan.step_therapy_required,
                "maxQuantity": plan.max_quantity,
            }
            for plan in plans
        ]
    except Exception as e:
        logger.error(f"Error fetching plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching plans"
        )


@router.get("/icd10-codes")
async def get_icd10_codes(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get common ICD-10 diagnosis codes."""
    # In production, this would query a comprehensive ICD-10 database
    # For now, return common codes used in examples
    
    common_codes = [
        {"code": "I10", "description": "Essential (primary) hypertension"},
        {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
        {"code": "J44.9", "description": "Chronic obstructive pulmonary disease, unspecified"},
        {"code": "I50.9", "description": "Heart failure, unspecified"},
        {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified"},
        {"code": "M79.3", "description": "Panniculitis, unspecified"},
        {"code": "R06.02", "description": "Shortness of breath"},
        {"code": "M25.5", "description": "Pain in joint"},
    ]
    
    if search:
        search_lower = search.lower()
        return [
            c for c in common_codes
            if search_lower in c["code"].lower() or search_lower in c["description"].lower()
        ]
    
    return common_codes


@router.get("/cpt-codes")
async def get_cpt_codes(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get common CPT procedure codes."""
    # In production, this would query a comprehensive CPT database
    # For now, return common codes used in examples
    
    common_codes = [
        {"code": "99213", "description": "Office visit, established patient, 20-29 min"},
        {"code": "99214", "description": "Office visit, established patient, 30-39 min"},
        {"code": "99215", "description": "Office visit, established patient, 40-54 min"},
        {"code": "99203", "description": "Office visit, new patient, 30-39 min"},
        {"code": "99204", "description": "Office visit, new patient, 40-54 min"},
        {"code": "70553", "description": "MRI brain with and without contrast"},
        {"code": "71045", "description": "Chest X-ray, 2 views"},
        {"code": "80053", "description": "Comprehensive metabolic panel"},
    ]
    
    if search:
        search_lower = search.lower()
        return [
            c for c in common_codes
            if search_lower in c["code"].lower() or search_lower in c["description"].lower()
        ]
    
    return common_codes


@router.post("/seed-reference-data")
async def seed_reference_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Initialize reference data (for development/testing)."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can seed reference data"
        )
    
    try:
        # Check if payers already exist
        stmt = select(PayerMaster)
        result = await db.execute(stmt)
        existing_payers = result.scalars().all()
        
        if existing_payers:
            return {"message": "Reference data already exists"}
        
        # Create sample payers
        payer1 = PayerMaster(payer_name="Blue Cross Blue Shield", is_active=True)
        payer2 = PayerMaster(payer_name="Aetna", is_active=True)
        payer3 = PayerMaster(payer_name="UnitedHealth", is_active=True)
        
        db.add_all([payer1, payer2, payer3])
        await db.flush()
        
        # Create sample plans
        plan1 = PlanMaster(
            payer_id=payer1.payer_id,
            plan_name="BCBS PPO Standard",
            pa_required=True,
            step_therapy_required=False,
            max_quantity=None
        )
        plan2 = PlanMaster(
            payer_id=payer1.payer_id,
            plan_name="BCBS HMO Plus",
            pa_required=True,
            step_therapy_required=True,
            max_quantity=None
        )
        plan3 = PlanMaster(
            payer_id=payer2.payer_id,
            plan_name="Aetna Choice POS",
            pa_required=True,
            step_therapy_required=False,
            max_quantity=None
        )
        
        db.add_all([plan1, plan2, plan3])
        await db.commit()
        
        return {
            "message": "Reference data seeded successfully",
            "payers_created": 3,
            "plans_created": 3
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error seeding reference data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error seeding reference data"
        )
