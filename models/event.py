"""
Event model for fashion events, insights, and opportunities.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, func
from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    event_date = Column(String(100), nullable=True)  # e.g. "Spring 2026" or "2024-11-15"
    location = Column(String(255), nullable=True)
    badge = Column(String(50), nullable=True)  # Featured, Past Event, Internal Spotlight
    image_url = Column(String(500), nullable=True)
    external_link = Column(String(500), nullable=True)
    link_text = Column(String(100), default="View details")
    author = Column(String(255), nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
