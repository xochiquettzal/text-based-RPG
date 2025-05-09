# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid # To generate session IDs

# Use relative imports for models
from . import models # Import the models module from the same directory

def get_player_state(db: Session, session_id: str) -> Optional[models.PlayerState]:
    """Retrieve a player state from the database by session_id."""
    return db.query(models.PlayerState).filter(models.PlayerState.session_id == session_id).first()

def create_player_state(db: Session, initial_data: Dict[str, Any]) -> models.PlayerState:
    """
    Create a new player state in the database.
    Generates a unique session_id.
    """
    session_id = str(uuid.uuid4())
    db_player_state = models.PlayerState(
        session_id=session_id,
        player_name=initial_data.get("name", "Oyuncu"),
        world_id=initial_data.get("world_id"),
        world_name_display=initial_data.get("world_name_display"),
        class_name=initial_data.get("class"),
        health=initial_data.get("health", 100),
        current_location_id=initial_data.get("current_location_id"),
        stats=initial_data.get("stats", {}),
        inventory=initial_data.get("inventory", []),
        skills=initial_data.get("skills", []),
        history=initial_data.get("history", [])
        # created_at and last_updated are handled by the database defaults/triggers
    )
    db.add(db_player_state)
    db.commit()
    db.refresh(db_player_state)
    print(f"Created new player state with session_id: {session_id}") # Debug log
    return db_player_state

def update_player_state(db: Session, session_id: str, update_data: Dict[str, Any]) -> Optional[models.PlayerState]:
    """
    Update an existing player state in the database.
    Only updates fields provided in update_data.
    """
    db_player_state = get_player_state(db, session_id)
    if db_player_state:
        print(f"Updating player state for session_id: {session_id}") # Debug log
        for key, value in update_data.items():
            # Only update attributes that exist in the model and are provided
            if hasattr(db_player_state, key):
                setattr(db_player_state, key, value)
            else:
                 print(f"Warning: Attribute '{key}' not found in PlayerState model during update.")
                 
        # Special handling for JSON fields if needed (e.g., merging instead of replacing)
        # For now, we assume update_data provides the complete new value for JSON fields like history
        
        db.commit()
        db.refresh(db_player_state)
        return db_player_state
    print(f"Update failed: Player state not found for session_id: {session_id}") # Debug log
    return None

def delete_player_state(db: Session, session_id: str) -> bool:
    """Delete a player state from the database."""
    db_player_state = get_player_state(db, session_id)
    if db_player_state:
        db.delete(db_player_state)
        db.commit()
        print(f"Deleted player state for session_id: {session_id}") # Debug log
        return True
    print(f"Delete failed: Player state not found for session_id: {session_id}") # Debug log
    return False
