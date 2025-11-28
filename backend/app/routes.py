"""
API routes for TrueTrace AI backend.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user, get_password_hash, verify_password
from app.models import User, Crisis, RumorCluster, Claim, ResultCard
from app.schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    CrisisResponse, RumorClusterResponse, ClaimResponse, ClaimWithCards,
    VerifyRequest, VerifyResponse, PipelineTrigger, PipelineStatus
)
from app.pipeline import run_radar_pipeline
from app.llm import generate_canonical_claim, retrieve_evidence, verify_claim, generate_result_card
from app.utils import paginate_query

router = APIRouter()


# Auth Routes
@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login and set session cookie."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Set user_id in cookie for session management
    response.set_cookie(
        key="user_id",
        value=str(user.id),
        max_age=60 * 60 * 24 * 7,  # 7 days
        httponly=True,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {
        "access_token": "",  # Keep for compatibility but not used
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/auth/logout")
async def logout(response: Response):
    """Logout and clear session cookie."""
    response.delete_cookie(key="user_id")
    return {"message": "Logged out successfully"}


# Crisis Routes
@router.get("/crises", response_model=List[CrisisResponse])
async def list_crises(
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all crises."""
    query = db.query(Crisis)
    
    if status_filter:
        query = query.filter(Crisis.status == status_filter)
    
    query = query.order_by(Crisis.detected_at.desc())
    items, total_count, total_pages = paginate_query(query, page, page_size)
    
    return items


@router.get("/crises/{crisis_id}", response_model=CrisisResponse)
async def get_crisis(
    crisis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific crisis."""
    crisis = db.query(Crisis).filter(Crisis.id == crisis_id).first()
    if not crisis:
        raise HTTPException(status_code=404, detail="Crisis not found")
    return crisis


# Cluster Routes
@router.get("/crises/{crisis_id}/clusters", response_model=List[RumorClusterResponse])
async def list_clusters(
    crisis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List rumor clusters for a crisis."""
    crisis = db.query(Crisis).filter(Crisis.id == crisis_id).first()
    if not crisis:
        raise HTTPException(status_code=404, detail="Crisis not found")
    
    clusters = db.query(RumorCluster).filter(
        RumorCluster.crisis_id == crisis_id
    ).order_by(RumorCluster.created_at.desc()).all()
    
    return clusters


# Claim Routes
@router.get("/claims", response_model=List[ClaimResponse])
async def list_claims(
    crisis_id: Optional[int] = None,
    verdict: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all claims with optional filters."""
    query = db.query(Claim)
    
    if crisis_id:
        query = query.join(RumorCluster).filter(RumorCluster.crisis_id == crisis_id)
    
    if verdict:
        query = query.filter(Claim.verdict == verdict)
    
    query = query.order_by(Claim.created_at.desc())
    items, total_count, total_pages = paginate_query(query, page, page_size)
    
    return items


@router.get("/claims/{claim_id}", response_model=ClaimWithCards)
async def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific claim with its result cards."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    cards = db.query(ResultCard).filter(ResultCard.claim_id == claim_id).all()
    card_dicts = [card.formatted_data for card in cards]
    
    claim_dict = {
        **claim.__dict__,
        "cards": card_dicts
    }
    return claim_dict


# Verification Route
@router.post("/verify", response_model=VerifyResponse)
async def verify_text(
    request: VerifyRequest,
    current_user: User = Depends(get_current_user)
):
    """On-demand verification of free-form text."""
    # Step 1: Normalize into canonical claim
    canonical_claim = await generate_canonical_claim([request.text])
    
    # Step 2: Retrieve evidence
    evidence = await retrieve_evidence(canonical_claim)
    
    # Step 3: Verify claim
    verification_result = await verify_claim(canonical_claim, evidence)
    
    # Step 4: Generate result card (general audience)
    card = await generate_result_card(
        claim=canonical_claim,
        verdict=verification_result.get("verdict", "Uncertain"),
        reasoning=verification_result.get("reasoning", ""),
        evidence=verification_result.get("evidence_citations", []),
        audience_type="general"
    )
    
    return VerifyResponse(
        claim=canonical_claim,
        verdict=verification_result.get("verdict", "Uncertain"),
        confidence_score=verification_result.get("confidence_score", 0.5),
        volatility_score=verification_result.get("volatility_score", 0.5),
        reasoning=verification_result.get("reasoning", ""),
        evidence_citations=verification_result.get("evidence_citations", []),
        card=card
    )


# Pipeline Routes
@router.post("/pipeline/trigger", response_model=PipelineStatus)
async def trigger_pipeline(
    trigger: PipelineTrigger,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger the radar pipeline."""
    # Run pipeline in background
    async def run_pipeline():
        await run_radar_pipeline(db)
    
    background_tasks.add_task(run_pipeline)
    
    return PipelineStatus(
        status="running",
        message="Pipeline started in background",
        last_run=datetime.now()
    )


@router.get("/pipeline/status", response_model=PipelineStatus)
async def get_pipeline_status(
    current_user: User = Depends(get_current_user)
):
    """Get pipeline status."""
    # In production, track actual pipeline status
    return PipelineStatus(
        status="idle",
        message="Pipeline is ready",
        last_run=None
    )

