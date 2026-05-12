"""
Blog post model for the Rooted in Opulence blog.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    cover_image = Column(String(500), nullable=True)
    author = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)
    external_link = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
