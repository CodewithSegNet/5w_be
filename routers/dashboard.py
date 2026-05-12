"""
Dashboard stats router — aggregated overview data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models.blog_post import BlogPost
from models.contact_submission import ContactSubmission
from models.event import Event
from models.admin import Admin
from routers.auth import get_current_admin

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    total_posts = (await db.execute(select(func.count(BlogPost.id)))).scalar() or 0
    published_posts = (await db.execute(select(func.count(BlogPost.id)).where(BlogPost.is_published == True))).scalar() or 0
    draft_posts = total_posts - published_posts

    total_contacts = (await db.execute(select(func.count(ContactSubmission.id)))).scalar() or 0
    unread_contacts = (await db.execute(select(func.count(ContactSubmission.id)).where(ContactSubmission.is_read == False, ContactSubmission.is_archived == False))).scalar() or 0

    total_events = (await db.execute(select(func.count(Event.id)))).scalar() or 0
    published_events = (await db.execute(select(func.count(Event.id)).where(Event.is_published == True))).scalar() or 0

    return {
        "blog": {"total": total_posts, "published": published_posts, "drafts": draft_posts},
        "contacts": {"total": total_contacts, "unread": unread_contacts},
        "events": {"total": total_events, "published": published_events},
    }
