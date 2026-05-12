"""
Contact form submissions router — public submit + admin management.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.contact_submission import ContactSubmission
from models.admin import Admin
from routers.auth import get_current_admin

router = APIRouter(prefix="/api/contacts", tags=["Contact Submissions"])


# ── Schemas ──────────────────────────────────────────────
class ContactSubmit(BaseModel):
    name: str
    email: str
    subject: str
    message: str


class ContactResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    is_read: bool
    is_archived: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Public Endpoint (no auth) ────────────────────────────
@router.post("/submit", status_code=201)
async def submit_contact(
    data: ContactSubmit,
    db: AsyncSession = Depends(get_db),
):
    submission = ContactSubmission(
        name=data.name,
        email=data.email,
        subject=data.subject,
        message=data.message,
    )
    db.add(submission)
    await db.flush()
    return {"detail": "Message sent successfully. We'll get back to you within 48 hours."}


# ── Admin Endpoints ──────────────────────────────────────
@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    filter: Optional[str] = Query(None, pattern="^(unread|read|archived)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    query = select(ContactSubmission)

    if filter == "unread":
        query = query.where(ContactSubmission.is_read == False, ContactSubmission.is_archived == False)
    elif filter == "read":
        query = query.where(ContactSubmission.is_read == True, ContactSubmission.is_archived == False)
    elif filter == "archived":
        query = query.where(ContactSubmission.is_archived == True)
    else:
        query = query.where(ContactSubmission.is_archived == False)

    result = await db.execute(query.order_by(desc(ContactSubmission.created_at)).limit(limit).offset(offset))
    return result.scalars().all()


@router.get("/count")
async def count_unread(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(
        select(func.count(ContactSubmission.id)).where(
            ContactSubmission.is_read == False,
            ContactSubmission.is_archived == False,
        )
    )
    return {"unread_count": result.scalar()}


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(select(ContactSubmission).where(ContactSubmission.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Submission not found")
    return contact


@router.put("/{contact_id}/read")
async def mark_read(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(select(ContactSubmission).where(ContactSubmission.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Submission not found")

    contact.is_read = True
    await db.flush()
    return {"detail": "Marked as read"}


@router.put("/{contact_id}/archive")
async def archive_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(select(ContactSubmission).where(ContactSubmission.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Submission not found")

    contact.is_archived = True
    await db.flush()
    return {"detail": "Archived"}


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(select(ContactSubmission).where(ContactSubmission.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Submission not found")

    await db.delete(contact)
    return {"detail": "Deleted"}
