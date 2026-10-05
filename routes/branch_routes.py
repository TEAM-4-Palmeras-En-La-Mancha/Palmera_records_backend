from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from schema.branch_schema import BranchCreate, BranchUpdate, BranchRead
from controller import branch_controller as controller

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.post("/", response_model=BranchRead, status_code=status.HTTP_201_CREATED)
def create_branch(payload: BranchCreate, db: Session = Depends(get_db)):
    return controller.create_branch(db, payload)


@router.get("/", response_model=List[BranchRead])
def get_branches(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db)
):
    return controller.get_branches(db, skip, limit)


@router.get("/{branch_id}", response_model=BranchRead)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    return controller.get_branch(db, branch_id)


@router.put("/{branch_id}", response_model=BranchRead)
def update_branch(branch_id: int, payload: BranchUpdate, db: Session = Depends(get_db)):
    return controller.update_branch(db,branch_id,payload )


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    controller.delete_branch(db,branch_id)
    return None