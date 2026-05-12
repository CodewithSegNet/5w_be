"""
Events router — CRUD + image upload + public endpoint.
"""
import os, uuid, shutil
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime
from database import get_db
from models.event import Event
from models.admin import Admin
from routers.auth import get_current_admin
from config import get_settings

router = APIRouter(prefix="/api/events", tags=["Events"])
settings = get_settings()

class EventCreate(BaseModel):
    title: str
    description: str
    event_date: Optional[str] = None
    location: Optional[str] = None
    badge: Optional[str] = None
    image_url: Optional[str] = None
    external_link: Optional[str] = None
    link_text: Optional[str] = "View details"
    author: Optional[str] = None
    is_published: bool = False

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[str] = None
    location: Optional[str] = None
    badge: Optional[str] = None
    image_url: Optional[str] = None
    external_link: Optional[str] = None
    link_text: Optional[str] = None
    author: Optional[str] = None
    is_published: Optional[bool] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    event_date: Optional[str]
    location: Optional[str]
    badge: Optional[str]
    image_url: Optional[str]
    external_link: Optional[str]
    link_text: Optional[str]
    author: Optional[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

@router.get("/public", response_model=List[EventResponse])
async def get_public_events(limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.is_published == True).order_by(desc(Event.created_at)).limit(limit))
    return result.scalars().all()

@router.get("/", response_model=List[EventResponse])
async def list_events(limit: int = Query(50), offset: int = Query(0), db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    result = await db.execute(select(Event).order_by(desc(Event.created_at)).limit(limit).offset(offset))
    return result.scalars().all()

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(data: EventCreate, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    event = Event(**data.model_dump())
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, data: EventUpdate, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    await db.flush()
    await db.refresh(event)
    return event

@router.delete("/{event_id}")
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(event)
    return {"detail": "Event deleted"}

@router.post("/{event_id}/upload-image", response_model=EventResponse)
async def upload_event_image(event_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    from utils.cloudinary_upload import upload_image
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, GIF allowed")
    image_url = await upload_image(file, folder="5wof/events")
    event.image_url = image_url
    await db.flush()
    await db.refresh(event)
    return event

@router.post("/upload-image")
async def upload_image_standalone(file: UploadFile = File(...), admin: Admin = Depends(get_current_admin)):
    from utils.cloudinary_upload import upload_image as cloud_upload
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, GIF allowed")
    image_url = await cloud_upload(file, folder="5wof/events")
    return {"image_url": image_url}

