from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from core.database import get_db
from model.branch_model import Branch
from schema.branch_schema import BranchCreate, BranchUpdate, BranchRead

router = APIRouter(prefix="/branches", tags=["Branches"])


# CREATE
@router.post("/", response_model=BranchRead, status_code=status.HTTP_201_CREATED)
def create_branch(payload: BranchCreate, db: Session = Depends(get_db)):
    branch = Branch(**payload.model_dump())
    try:
        db.add(branch)
        db.commit()
        db.refresh(branch)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Branch already exists or invalid data")
    return branch


# READ ALL
@router.get("/", response_model=List[BranchRead])
def get_branches(db: Session = Depends(get_db)):
    return db.query(Branch).all()


# READ ONE
@router.get("/{branch_id}", response_model=BranchRead)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


# UPDATE
@router.put("/{branch_id}", response_model=BranchRead)
def update_branch(branch_id: int, payload: BranchUpdate, db: Session = Depends(get_db)):
    branch = db.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(branch, key, value)
    try:
        db.commit()
        db.refresh(branch)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")
    return branch


# DELETE
@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(branch)
    db.commit()
    return None