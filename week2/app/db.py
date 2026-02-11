"""
Database layer for SQLite operations.

Handles all database interactions including table creation,
CRUD operations for notes and action items, and connection management.
"""
from __future__ import annotations

import sqlite3
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def ensure_data_directory_exists() -> None:
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """
    Get a database connection with Row factory enabled.
    
    Returns:
        sqlite3.Connection: Database connection with row_factory set
    """
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """
    Initialize database tables.
    
    Creates notes and action_items tables if they don't exist.
    Safe to call multiple times (idempotent).
    """
    ensure_data_directory_exists()
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            
            # Create notes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            
            # Create action_items table with foreign key constraint
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
                );
                """
            )
            
            # Create index for faster queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_action_items_note_id 
                ON action_items(note_id);
                """
            )
            
            connection.commit()
            logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def insert_note(content: str) -> int:
    """
    Insert a new note into the database.
    
    Args:
        content: Note content text
        
    Returns:
        int: ID of the newly created note
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            connection.commit()
            note_id = int(cursor.lastrowid)
            logger.debug(f"Inserted note with ID: {note_id}")
            return note_id
    except sqlite3.Error as e:
        logger.error(f"Failed to insert note: {e}")
        raise


def list_notes() -> list[sqlite3.Row]:
    """
    List all notes in descending order by ID.
    
    Returns:
        list[sqlite3.Row]: List of note rows
    """
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            return list(cursor.fetchall())
    except sqlite3.Error as e:
        logger.error(f"Failed to list notes: {e}")
        raise


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    """
    Get a single note by ID.
    
    Args:
        note_id: Note ID to retrieve
        
    Returns:
        Optional[sqlite3.Row]: Note row if found, None otherwise
    """
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Failed to get note {note_id}: {e}")
        raise


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    """
    Insert multiple action items in a single transaction.
    
    Args:
        items: List of action item text strings
        note_id: Optional note ID to associate items with
        
    Returns:
        list[int]: List of newly created action item IDs
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    if not items:
        return []
    
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            ids: list[int] = []
            
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cursor.lastrowid))
            
            connection.commit()
            logger.debug(f"Inserted {len(ids)} action items")
            return ids
    except sqlite3.Error as e:
        logger.error(f"Failed to insert action items: {e}")
        raise


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    """
    List action items, optionally filtered by note_id.
    
    Args:
        note_id: Optional note ID to filter by
        
    Returns:
        list[sqlite3.Row]: List of action item rows in descending order by ID
    """
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            
            return list(cursor.fetchall())
    except sqlite3.Error as e:
        logger.error(f"Failed to list action items: {e}")
        raise


def action_item_exists(action_item_id: int) -> bool:
    """
    Check if an action item exists.
    
    Args:
        action_item_id: Action item ID to check
        
    Returns:
        bool: True if action item exists, False otherwise
    """
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM action_items WHERE id = ?", (action_item_id,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Failed to check action item existence: {e}")
        raise


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """
    Mark an action item as done or not done.
    
    Args:
        action_item_id: Action item ID to update
        done: Done status (True for done, False for not done)
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            connection.commit()
            logger.debug(f"Marked action item {action_item_id} as {'done' if done else 'not done'}")
    except sqlite3.Error as e:
        logger.error(f"Failed to mark action item done: {e}")
        raise


