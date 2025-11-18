"""
Database Schemas for Ekhaya Legae

Each Pydantic model represents a MongoDB collection (collection name is the lowercase class name).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ------------------------------
# Core public-facing content
# ------------------------------
class Event(BaseModel):
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    location: str = Field(..., description="Location or venue")
    organizer: Optional[str] = Field(None, description="Organizer name")
    capacity: Optional[int] = Field(None, ge=0)
    status: str = Field("published", description="draft | published | cancelled")
    categories: List[str] = Field(default_factory=list)

class Booking(BaseModel):
    event_id: str = Field(..., description="Related event _id")
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    ticket_quantity: int = Field(1, ge=1, le=10)
    notes: Optional[str] = None
    consent_sms: bool = Field(False, description="SMS reminders consent")

class TrainingApplication(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    age: Optional[int] = Field(None, ge=16, le=100)
    highest_qualification: Optional[str] = None
    area: Optional[str] = None
    motivation: Optional[str] = None
    consent_sms: bool = Field(False)

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str

class Story(BaseModel):
    title: str
    body: str
    author: Optional[str] = None
    featured: bool = False

class Partner(BaseModel):
    name: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None

class Resource(BaseModel):
    title: str
    type: str = Field(..., description="pdf | image | video | link")
    url: str
    description: Optional[str] = None
    language: Optional[str] = Field("English")

class SiteStat(BaseModel):
    label: str
    value: int = 0

# Note: The Flames database viewer/tooling can read these schemas via the /schema endpoint
# to assist with validation in no-code views.
