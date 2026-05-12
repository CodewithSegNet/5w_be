"""
Blog posts router — CRUD + public endpoint for frontend.
"""
import re, os, uuid, shutil
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.blog_post import BlogPost
from models.admin import Admin
from routers.auth import get_current_admin
from config import get_settings

router = APIRouter(prefix="/api/blog", tags=["Blog Posts"])
settings = get_settings()


# ── Schemas ──────────────────────────────────────────────
class BlogPostCreate(BaseModel):
    title: str
    excerpt: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    author: str
    category: Optional[str] = None
    tags: Optional[str] = None
    external_link: Optional[str] = None
    is_published: bool = False


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    external_link: Optional[str] = None
    is_published: Optional[bool] = None


class BlogPostResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    content: str
    cover_image: Optional[str]
    author: str
    category: Optional[str]
    tags: Optional[str]
    external_link: Optional[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogListResponse(BaseModel):
    posts: List[BlogPostResponse]
    total: int
    page: int
    pages: int


# ── Helpers ──────────────────────────────────────────────
def generate_slug(title: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return slug


# ── Public Endpoints (no auth) ───────────────────────────
@router.get("/public", response_model=BlogListResponse)
async def get_public_posts(
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(BlogPost).where(BlogPost.is_published == True)
    count_query = select(func.count(BlogPost.id)).where(BlogPost.is_published == True)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (BlogPost.title.ilike(search_filter)) |
            (BlogPost.excerpt.ilike(search_filter)) |
            (BlogPost.content.ilike(search_filter)) |
            (BlogPost.author.ilike(search_filter))
        )
        count_query = count_query.where(
            (BlogPost.title.ilike(search_filter)) |
            (BlogPost.excerpt.ilike(search_filter)) |
            (BlogPost.content.ilike(search_filter)) |
            (BlogPost.author.ilike(search_filter))
        )

    if category:
        query = query.where(BlogPost.category == category)
        count_query = count_query.where(BlogPost.category == category)

    if tag:
        tag_filter = f"%{tag}%"
        query = query.where(BlogPost.tags.ilike(tag_filter))
        count_query = count_query.where(BlogPost.tags.ilike(tag_filter))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit

    result = await db.execute(
        query.order_by(desc(BlogPost.created_at)).limit(limit).offset(offset)
    )
    posts = result.scalars().all()
    return BlogListResponse(posts=posts, total=total, page=page, pages=pages)


@router.get("/public/{slug}", response_model=BlogPostResponse)
async def get_public_post_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BlogPost).where(BlogPost.slug == slug, BlogPost.is_published == True)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/public/categories", response_model=List[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BlogPost.category).where(
            BlogPost.is_published == True, BlogPost.category.isnot(None)
        ).distinct()
    )
    return [r[0] for r in result.all() if r[0]]


# ── Admin Endpoints ──────────────────────────────────────
@router.get("/", response_model=List[BlogPostResponse])
async def list_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(
        select(BlogPost).order_by(desc(BlogPost.created_at)).limit(limit).offset(offset)
    )
    return result.scalars().all()


@router.get("/{post_id}", response_model=BlogPostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=BlogPostResponse, status_code=201)
async def create_post(
    data: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    slug = generate_slug(data.title)
    # Ensure unique slug
    result = await db.execute(select(BlogPost).where(BlogPost.slug == slug))
    if result.scalar_one_or_none():
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    post = BlogPost(
        title=data.title,
        slug=slug,
        excerpt=data.excerpt,
        content=data.content,
        cover_image=data.cover_image,
        author=data.author,
        category=data.category,
        is_published=data.is_published,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


@router.put("/{post_id}", response_model=BlogPostResponse)
async def update_post(
    post_id: int,
    data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = data.model_dump(exclude_unset=True)
    if "title" in update_data:
        update_data["slug"] = generate_slug(update_data["title"])

    for key, value in update_data.items():
        setattr(post, key, value)

    await db.flush()
    await db.refresh(post)
    return post


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    return {"detail": "Post deleted"}


# ── Image Upload (Cloudinary) ────────────────────────────
@router.post("/{post_id}/upload-image", response_model=BlogPostResponse)
async def upload_blog_image(post_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    from utils.cloudinary_upload import upload_image
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, GIF allowed")
    image_url = await upload_image(file, folder="5wof/blog")
    post.cover_image = image_url
    await db.flush()
    await db.refresh(post)
    return post


@router.post("/upload-image")
async def upload_blog_image_standalone(file: UploadFile = File(...), admin: Admin = Depends(get_current_admin)):
    from utils.cloudinary_upload import upload_image
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, GIF allowed")
    image_url = await upload_image(file, folder="5wof/blog")
    return {"image_url": image_url}


