"""
Simplified Claim Processing Workflow

Replaces complex LangGraph orchestration with deterministic, maintainable logic.
Flow: OCR → Validation → Risk Analysis → Decision
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import json

logger = logging.getLogger(__name__)


class ClaimValidator:
    """Validates extracted claim data against policies"""
    
    @staticmethod
    def validate_medical_codes(icd10_codes: List[str], cpt_codes: List[str]) -> Dict[str, Any]:
        """Validate medical codes are present and properly formatted"""
        issues = []
        
        if not icd10_codes or all(not code.strip() for code in icd10_codes):
            issues.append("No valid ICD-10 diagnosis codes found")
        
        if not cpt_codes or all(not code.strip() for code in cpt_codes):
            issues.append("No valid CPT procedure codes found")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "icd10_count": len([c for c in icd10_codes if c.strip()]) if icd10_codes else 0,
            "cpt_count": len([c for c in cpt_codes if c.strip()]) if cpt_codes else 0,
        }
    
    @staticmethod
    def validate_patient_info(patient_name: str, patient_id: str) -> Dict[str, Any]:
        """Validate patient identification information"""
        issues = []
        
        if not patient_name or not patient_name.strip():
            issues.append("Patient name missing or invalid")
        
        if not patient_id or not patient_id.strip():
            issues.append("Patient ID missing or invalid")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }
    
    @staticmethod
    def validate_provider_info(provider_name: str, provider_npi: str) -> Dict[str, Any]:
        """Validate provider information"""
        issues = []
        
        if not provider_name or not provider_name.strip():
            issues.append("Provider name missing or invalid")
        
        if not provider_npi or not provider_npi.strip():
            issues.append("Provider NPI missing or invalid")
        elif len(provider_npi.strip()) != 10 or not provider_npi.strip().isdigit():
            issues.append("Provider NPI format invalid (must be 10 digits)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }


class RiskAnalyzer:
    """Analyzes claim risk and determines approval likelihood"""
    
    @staticmethod
    def calculate_risk_score(
        ocr_confidence: float,
        validation_issues: List[str],
        extracted_text_quality: float,
    ) -> Dict[str, Any]:
        """Calculate risk score based on claim characteristics"""
        
        base_score = 100.0
        
        # Reduce score based on OCR confidence
        if ocr_confidence < 0.7:
            base_score -= 30
        elif ocr_confidence < 0.85:
            base_score -= 15
        
        # Reduce score for validation issues
        issue_penalty = len(validation_issues) * 10
        base_score -= min(issue_penalty, 40)
        
        # Reduce score for poor text extraction quality
        if extracted_text_quality < 0.7:
            base_score -= 20
        elif extracted_text_quality < 0.85:
            base_score -= 10
        
        # Ensure score is between 0 and 100
        risk_score = max(0, min(100, base_score))
        
        # Determine risk level
        if risk_score >= 85:
            risk_level = "LOW"
        elif risk_score >= 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            "score": risk_score,
            "level": risk_level,
            "factors": [
                f"OCR confidence: {ocr_confidence:.1%}",
                f"Validation issues: {len(validation_issues)}",
                f"Text quality: {extracted_text_quality:.1%}",
            ],
        }
    
    @staticmethod
    def detect_anomalies(claim_data: Dict[str, Any]) -> List[str]:
        """Detect potential anomalies or red flags in claim data"""
        anomalies = []
        
        # Check for unusual amounts
        billed_amount = claim_data.get("billed_amount", 0)
        if billed_amount > 100000:
            anomalies.append("Unusually high billed amount")
        
        # Check for missing required fields
        required_fields = ["patient_name", "provider_name", "service_date", "icd10_codes", "cpt_codes"]
        missing = [f for f in required_fields if not claim_data.get(f)]
        if missing:
            anomalies.append(f"Missing fields: {', '.join(missing)}")
        
        return anomalies


class DecisionEngine:
    """Makes approval/denial decisions for claims"""
    
    @staticmethod
    def make_decision(
        risk_score: float,
        validation_issues: List[str],
        anomalies: List[str],
    ) -> Dict[str, Any]:
        """Determine claim approval decision"""
        
        # Decision logic
        if anomalies:
            decision = "HUMAN_REVIEW"
            reason = "Anomalies detected in claim data"
        elif len(validation_issues) > 2:
            decision = "AUTO_DENY"
            reason = "Multiple validation failures"
        elif risk_score >= 85:
            decision = "AUTO_APPROVE"
            reason = "Low risk claim with sufficient documentation"
        elif risk_score >= 60:
            decision = "HUMAN_REVIEW"
            reason = "Medium risk claim requires human review"
        else:
            decision = "AUTO_DENY"
            reason = "High risk claim does not meet approval criteria"
        
        # Generate authorization code for approvals
        auth_code = None
        valid_until = None
        if decision == "AUTO_APPROVE":
            auth_code = f"PA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            valid_until = (datetime.now() + timedelta(days=90)).isoformat()
        
        return {
            "decision": decision,
            "reason": reason,
            "auth_code": auth_code,
            "valid_until": valid_until,
            "reviewed_at": datetime.now().isoformat(),
        }


async def process_claim(
    claim_id: UUID,
    claim_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Main claim processing workflow
    
    Args:
        claim_id: Unique claim identifier
        claim_data: Extracted and structured claim information
    
    Returns:
        Processing result with decision and details
    """
    
    logger.info(f"Processing claim {claim_id}")
    
    result = {
        "claim_id": str(claim_id),
        "status": "PROCESSING",
        "created_at": datetime.now().isoformat(),
        "processing_steps": [],
    }
    
    try:
        # Step 1: Validate Medical Codes
        logger.info(f"[{claim_id}] Step 1: Validating medical codes")
        codes_validation = ClaimValidator.validate_medical_codes(
            claim_data.get("icd10_codes", []),
            claim_data.get("cpt_codes", []),
        )
        result["processing_steps"].append({
            "name": "Medical Code Validation",
            "status": "PASSED" if codes_validation["valid"] else "FAILED",
            "issues": codes_validation["issues"],
        })
        
        # Step 2: Validate Patient Information
        logger.info(f"[{claim_id}] Step 2: Validating patient information")
        patient_validation = ClaimValidator.validate_patient_info(
            claim_data.get("patient_name", ""),
            claim_data.get("patient_id", ""),
        )
        result["processing_steps"].append({
            "name": "Patient Information Validation",
            "status": "PASSED" if patient_validation["valid"] else "FAILED",
            "issues": patient_validation["issues"],
        })
        
        # Step 3: Validate Provider Information
        logger.info(f"[{claim_id}] Step 3: Validating provider information")
        provider_validation = ClaimValidator.validate_provider_info(
            claim_data.get("provider_name", ""),
            claim_data.get("provider_npi", ""),
        )
        result["processing_steps"].append({
            "name": "Provider Information Validation",
            "status": "PASSED" if provider_validation["valid"] else "FAILED",
            "issues": provider_validation["issues"],
        })
        
        # Collect all validation issues
        all_validation_issues = (
            codes_validation["issues"] +
            patient_validation["issues"] +
            provider_validation["issues"]
        )
        
        # Step 4: Analyze Risk
        logger.info(f"[{claim_id}] Step 4: Analyzing claim risk")
        risk_analysis = RiskAnalyzer.calculate_risk_score(
            ocr_confidence=claim_data.get("ocr_confidence", 0.75),
            validation_issues=all_validation_issues,
            extracted_text_quality=claim_data.get("text_quality", 0.75),
        )
        result["processing_steps"].append({
            "name": "Risk Analysis",
            "status": "COMPLETED",
            "risk_score": risk_analysis["score"],
            "risk_level": risk_analysis["level"],
            "factors": risk_analysis["factors"],
        })
        
        # Step 5: Detect Anomalies
        logger.info(f"[{claim_id}] Step 5: Detecting anomalies")
        anomalies = RiskAnalyzer.detect_anomalies(claim_data)
        result["processing_steps"].append({
            "name": "Anomaly Detection",
            "status": "COMPLETED",
            "anomalies": anomalies,
        })
        
        # Step 6: Make Decision
        logger.info(f"[{claim_id}] Step 6: Making approval decision")
        decision = DecisionEngine.make_decision(
            risk_score=risk_analysis["score"],
            validation_issues=all_validation_issues,
            anomalies=anomalies,
        )
        result["processing_steps"].append({
            "name": "Decision Making",
            "status": "COMPLETED",
            "decision": decision["decision"],
        })
        
        # Build final result
        result.update({
            "status": "COMPLETED",
            "decision": decision["decision"],
            "reason": decision["reason"],
            "risk_score": risk_analysis["score"],
            "risk_level": risk_analysis["level"],
            "auth_code": decision["auth_code"],
            "valid_until": decision["valid_until"],
            "validation_issues": all_validation_issues,
            "anomalies": anomalies,
            "decided_at": datetime.now().isoformat(),
        })
        
        logger.info(f"Claim {claim_id} processing complete. Decision: {decision['decision']}")
        
    except Exception as e:
        logger.error(f"Error processing claim {claim_id}: {str(e)}")
        result.update({
            "status": "ERROR",
            "error": str(e),
            "decided_at": datetime.now().isoformat(),
        })
    
    return result
