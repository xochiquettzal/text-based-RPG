# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# --- Request Payloads ---

class StartGamePayload(BaseModel):
    """Payload required to start a new game."""
    player_name: str = "Oyuncu"
    world_id: str # e.g., "dark_fantasy", "animal_kingdom"
    selected_class_or_faction: Optional[str] = None # e.g., "vargar", "ashen_legion"

class MakeChoicePayload(BaseModel):
    """Payload for player making a choice or custom action."""
    session_id: str # Unique ID for the game session
    choice_id: str # e.g., "A", "B", "USER_ACTION"
    choice_text: str # Text of the button clicked or the custom action typed
    # player_state is no longer sent from frontend

# --- Response Models ---

class PlayerInfoForCard(BaseModel):
    """Minimal player info needed to update the character card."""
    name: Optional[str] = None
    class_name: Optional[str] = Field(None, alias="class") # Alias for 'class' keyword
    health: Optional[int] = None
    stats: Optional[Dict[str, Any]] = None

class ChoiceModel(BaseModel):
    """Structure for a single choice option."""
    id: str
    text: str

class StartGameResponse(BaseModel):
    """Response model for starting a new game."""
    text: str
    choices: List[ChoiceModel]
    session_id: str # The newly created session ID
    player_info_for_card: PlayerInfoForCard # Initial info for the card

class MakeChoiceResponse(BaseModel):
    """Response model after processing a player action."""
    text: str
    choices: List[ChoiceModel]
    player_info_for_card: PlayerInfoForCard # Updated info for the card

class ErrorResponse(BaseModel):
    """Model for returning errors."""
    error: str
