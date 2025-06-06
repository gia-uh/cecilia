from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal
from uuid import UUID
from datetime import datetime


class ContactInfo(BaseModel):
    name: str
    institution: str
    email: EmailStr


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class QAExample(BaseModel):
    id: UUID
    contact_info: ContactInfo
    example_type: Literal["Pregunta"]
    tags: List[str]
    context: str
    created_at: datetime
    messages: List[Message]
