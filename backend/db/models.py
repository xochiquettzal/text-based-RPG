# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from sqlalchemy.orm import relationship
import datetime

# Import Base from the database setup file
# Use relative import
from .database import Base

class PlayerState(Base):
    """Database model representing the state of a player's game session."""
    
    __tablename__ = "player_states"

    session_id = Column(String, primary_key=True, index=True) # Unique ID for the game session
    player_name = Column(String, default="Oyuncu")
    
    # World and Class/Faction Info
    world_id = Column(String, index=True)
    world_name_display = Column(String)
    class_name = Column(String, nullable=True) # Can be race or faction name

    # Core Stats
    health = Column(Integer, default=100)
    
    # Game Progression
    current_location_id = Column(String, nullable=True)
    
    # Complex data stored as JSON
    # Ensure your SQLite version supports JSON or use String and handle serialization/deserialization
    stats = Column(JSON, default={}) # e.g., {"STR": 5, "AGI": 6}
    inventory = Column(JSON, default=[]) # e.g., ["sword", "potion"]
    skills = Column(JSON, default=[]) # e.g., ["Attack", "Heal"]
    history = Column(JSON, default=[]) # List of event dictionaries

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PlayerState(session_id='{self.session_id}', name='{self.player_name}', world='{self.world_id}', class='{self.class_name}')>"
