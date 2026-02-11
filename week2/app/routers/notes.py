"""
Notes router.

Handles endpoints for creating and retrieving notes.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import CreateNoteRequest, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(request: CreateNoteRequest) -> NoteResponse:
    """
    Create a new note.
    
    Returns the created note with its ID and timestamp.
    """
    note_id = db.insert_note(request.content)
    note = db.get_note(note_id)
    
    if note is None:
        raise HTTPException(status_code=500, detail="Failed to create note")
    
    return NoteResponse(
        id=note["id"],
        content=note["content"],
        created_at=note["created_at"],
    )


@router.get("", response_model=list[NoteResponse])
def list_notes() -> list[NoteResponse]:
    """
    List all notes in descending order by ID (newest first).
    
    Returns all notes with their IDs and timestamps.
    """
    rows = db.list_notes()
    return [
        NoteResponse(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """
    Retrieve a single note by ID.
    
    Raises 404 if the note doesn't exist.
    """
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return NoteResponse(
        id=row["id"],
        content=row["content"],
        created_at=row["created_at"],
    )


