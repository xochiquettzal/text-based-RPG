# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# Use relative imports for models, services, and db dependency
from ..models.game_models import (
    StartGamePayload, 
    MakeChoicePayload, # Renamed from PlayerChoice
    StartGameResponse, # New response model
    MakeChoiceResponse, # New response model
    ErrorResponse
)
from ..services import game_service 
from ..db.database import get_db # Import DB dependency function

router = APIRouter()

@router.post("/start_game", 
             response_model=StartGameResponse, 
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def start_game_route(payload: StartGamePayload, db: Session = Depends(get_db)):
    """
    Starts a new game based on world and optional class/faction selection.
    Initializes player state in the DB and returns the starting scenario and session_id.
    """
    try:
        initial_state_data = game_service.initialize_game(db=db, payload=payload)
        if not initial_state_data or "error" in initial_state_data:
             raise HTTPException(status_code=400, detail=initial_state_data.get("error", "Game initialization failed"))
        
        # Ensure the response matches the StartGameResponse model
        return StartGameResponse(**initial_state_data)
        
    except Exception as e:
        print(f"Error in /start_game: {e}") # Log the error
        raise HTTPException(status_code=500, detail="Internal server error during game start")


@router.post("/make_choice", 
             response_model=MakeChoiceResponse, 
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def make_choice_route(payload: MakeChoicePayload, db: Session = Depends(get_db)):
    """
    Processes a player's choice (button click or custom action) using session_id.
    Retrieves state from DB, calls AI, updates state in DB, and returns the next game state.
    """
    try:
        next_state_data = await game_service.process_player_action(
            db=db, 
            session_id=payload.session_id, 
            choice_id=payload.choice_id, 
            choice_text=payload.choice_text
        )
        
        if not next_state_data or "error" in next_state_data:
             status_code = 400 if "AI servisi" in next_state_data.get("error", "") or "Geçersiz oturum" in next_state_data.get("error", "") else 500
             raise HTTPException(status_code=status_code, detail=next_state_data.get("error", "Failed to process action"))

        # next_state_data is already a MakeChoiceResponse model instance from the service
        return next_state_data

    except HTTPException as e:
        raise e 
    except Exception as e:
        print(f"Error in /make_choice: {e}") # Log the error
        raise HTTPException(status_code=500, detail="Internal server error processing choice")
