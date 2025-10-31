from enum import Enum, StrEnum
from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal
from uuid import UUID, uuid4
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


class YesNoEnum(str, Enum):
    YES = "Yes"
    NO = "No"


TagEnum = StrEnum(
    "TagEnum",
    [
        "arte",
        "ciencia",
        "cultura",
        "deporte",
        "economía",
        "historia",
        "política",
        "salud",
        "casual",
        "geografía",
        "redacción",
        "composición",
        "otros",
    ],
)


class Conversation(BaseModel):
    messages: List[Message] = Field(
        default_factory=list, description="The messages of the conversation"
    )


class Entry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    example_type: Literal["Pregunta", "Instrucción", "Conversación"] = "Conversación"
    tags: List[TagEnum] = Field(description="The labels of the conversation")
    context: str = Field(description="The context of the conversation")
    created_at: datetime = Field(default_factory=datetime.now)
    messages: List[Message] = Field(default_factory=list)


class Classifier(BaseModel):
    classification: YesNoEnum = Field(
        description="The classification of the conversation, whether it is about a topic or not"
    )
