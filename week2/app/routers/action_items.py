"""
Action items router.

Handles endpoints for extracting, listing, and managing action items.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .. import db
from ..schemas import (
    ExtractRequest,
    ExtractResponse,
    ActionItemResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    """
    Extract action items from text using heuristic-based extraction.
    
    Optionally saves the input text as a note if save_note is True.
    Returns the extracted action items with their IDs.
    """
    note_id: Optional[int] = None
    if request.save_note:
        note_id = db.insert_note(request.text)

    items = extract_action_items(request.text)
    ids = db.insert_action_items(items, note_id=note_id)
    
    return ExtractResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items)]
    )


@router.get("", response_model=list[ActionItemResponse])
def list_all(
    note_id: Optional[int] = Query(None, description="Filter by note ID")
) -> list[ActionItemResponse]:
    """
    List all action items, optionally filtered by note_id.
    
    Returns action items in descending order by ID (newest first).
    """
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, request: MarkDoneRequest) -> MarkDoneResponse:
    """
    Mark an action item as done or not done.
    
    Raises 404 if the action item doesn't exist.
    """
    # Verify action item exists
    if not db.action_item_exists(action_item_id):
        raise HTTPException(status_code=404, detail="Action item not found")
    
    db.mark_action_item_done(action_item_id, request.done)
    return MarkDoneResponse(id=action_item_id, done=request.done)


