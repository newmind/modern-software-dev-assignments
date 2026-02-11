"""
Pydantic schemas for API request/response validation.

Defines well-typed contracts for all API endpoints to ensure
data validation and clear API documentation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Request schemas
class ExtractRequest(BaseModel):
    """Request schema for action item extraction"""
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the note")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "text": "- Add user authentication\n- Create database schema",
            "save_note": True
        }
    })


class CreateNoteRequest(BaseModel):
    """Request schema for creating a note"""
    content: str = Field(..., min_length=1, description="Note content")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "content": "Meeting notes: Discuss project timeline and deliverables"
        }
    })


class MarkDoneRequest(BaseModel):
    """Request schema for marking action item as done"""
    done: bool = Field(default=True, description="Done status")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "done": True
        }
    })


# Response schemas
class ActionItemResponse(BaseModel):
    """Response schema for a single action item"""
    id: int = Field(..., description="Action item ID")
    text: str = Field(..., description="Action item text")
    done: bool = Field(..., description="Completion status")
    note_id: Optional[int] = Field(None, description="Associated note ID")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": 1,
            "text": "Add user authentication",
            "done": False,
            "note_id": 1,
            "created_at": "2024-01-15 10:30:00"
        }
    })


class ExtractResponse(BaseModel):
    """Response schema for extraction endpoint"""
    note_id: Optional[int] = Field(None, description="Note ID if saved")
    items: list[dict] = Field(..., description="Extracted action items with IDs")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "note_id": 1,
            "items": [
                {"id": 1, "text": "Add user authentication"},
                {"id": 2, "text": "Create database schema"}
            ]
        }
    })


class NoteResponse(BaseModel):
    """Response schema for a single note"""
    id: int = Field(..., description="Note ID")
    content: str = Field(..., description="Note content")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": 1,
            "content": "Meeting notes: Discuss project timeline",
            "created_at": "2024-01-15 10:30:00"
        }
    })


class MarkDoneResponse(BaseModel):
    """Response schema for mark done endpoint"""
    id: int = Field(..., description="Action item ID")
    done: bool = Field(..., description="Updated done status")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": 1,
            "done": True
        }
    })
