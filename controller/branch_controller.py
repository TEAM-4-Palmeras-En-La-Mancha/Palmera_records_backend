from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List


from model.branch_model import Branch
from schema.branch_schema import BranchCreate, BranchUpdate, BranchRead


def create_branch(db: Session,payload: BranchCreate):
    branch = Branch(**payload.model_dump())
    try:
        db.add(branch)
        db.commit()
        db.refresh(branch)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Branch already exists or invalid data")
    return branch



def get_branches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Branch).offset(skip).limit(limit).all()


def get_branch(db: Session,branch_id: int):
    branch = db.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


def update_branch(db: Session, branch_id: int, payload: BranchUpdate ):
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


def delete_branch(db: Session, branch_id: int):
    branch = db.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(branch)
    db.commit()
    return None