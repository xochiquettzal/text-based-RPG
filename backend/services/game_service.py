# -*- coding: utf-8 -*-
import copy
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid # Added for session_id generation in initialize_game

# Use relative imports for data, models, db, and other services
from ..data.characters import player_character_template, CLASS_BASE_STATS, get_class_base_stats
from ..data.scenarios import STARTING_SCENARIOS, INITIAL_SCENARIOS_BY_WORLD, get_starting_scenario
from ..data.worlds import get_world_name 
from ..models.game_models import StartGamePayload, MakeChoicePayload # Import request models (Fixed PlayerChoice -> MakeChoicePayload)
from ..db import crud, models # Import db models and crud functions
from .ai_service import get_ai_response # Import AI service

def initialize_game(db: Session, payload: StartGamePayload) -> Dict[str, Any]:
    """
    Initializes a new player state in the database based on world and class selection.
    Returns the initial game state data (text, choices, session_id, player_info_for_card).
    """
    initial_state_dict = copy.deepcopy(player_character_template)
    initial_state_dict["name"] = payload.player_name
    
    selected_world_id = payload.world_id
    world_name = get_world_name(selected_world_id) 
    if world_name == "Bilinmeyen Dünya":
         return {"error": f"Geçersiz dünya ID'si: {selected_world_id}"}

    initial_state_dict["world_id"] = selected_world_id
    initial_state_dict["world_name_display"] = world_name
    
    # Set class/faction and stats if selected
    if payload.selected_class_or_faction:
        class_data = get_class_base_stats(selected_world_id, payload.selected_class_or_faction)
        if class_data:
            initial_state_dict["class"] = payload.selected_class_or_faction
            stats_to_update = class_data.copy()
            initial_state_dict["skills"] = stats_to_update.pop("skills", []) 
            initial_state_dict["stats"].update(stats_to_update) 
        else:
            print(f"Uyarı: Seçilen sınıf/fraksiyon '{payload.selected_class_or_faction}' dünya '{selected_world_id}' için bulunamadı.")
            initial_state_dict["class"] = f"Bilinmeyen ({payload.selected_class_or_faction})"

    # Determine the starting scenario
    scenario = get_starting_scenario(selected_world_id, payload.selected_class_or_faction)
    if not scenario:
         return {"error": f"Başlangıç senaryosu bulunamadı: Dünya={selected_world_id}, Sınıf={payload.selected_class_or_faction}"}

    start_text = scenario.get("text", "Oyun başlıyor...") # Use .get with fallback
    start_choices = scenario.get("choices", []) # Use .get with fallback
    start_location_id = scenario.get("current_location_id", f"{selected_world_id}_start")

    # Set initial state based on the chosen scenario
    initial_state_dict["current_location_id"] = start_location_id
    initial_state_dict["history"] = [{ 
        "event_type": "game_start",
        "world_id": initial_state_dict["world_id"],
        "class": initial_state_dict["class"], 
        "text": start_text 
    }]
    
    # Create the player state in the database
    try:
        # Pass the prepared dictionary directly to crud function
        db_player_state = crud.create_player_state(db=db, initial_data=initial_state_dict)
    except Exception as e:
        print(f"Error creating player state in DB: {e}")
        return {"error": "Oyuncu durumu veritabanında oluşturulamadı."}

    # Return initial text, choices, session_id, and info for card
    return {
        "text": start_text, 
        "choices": start_choices, 
        "session_id": db_player_state.session_id,
        "player_info_for_card": {
             "name": db_player_state.player_name,
             "class": db_player_state.class_name,
             "health": db_player_state.health,
             "stats": db_player_state.stats 
        }
    }


async def process_player_action(db: Session, session_id: str, choice_id: str, choice_text: str) -> Dict[str, Any]:
    """
    Processes player's action, calls AI, updates state in DB.
    Returns the next game state data (text, choices, player_info_for_card).
    """
    db_player_state = crud.get_player_state(db=db, session_id=session_id)
    if not db_player_state:
        return {"error": f"Geçersiz oturum ID'si: {session_id}"}

    # Prepare context for AI using attributes from the ORM object
    current_scenario_text = "Önceki durum bilinmiyor." # Default
    if db_player_state.history and isinstance(db_player_state.history, list) and len(db_player_state.history) > 0:
        last_event = db_player_state.history[-1]
        if isinstance(last_event, dict): # Check if last_event is a dictionary
            if last_event.get("event_type") == "game_start":
                current_scenario_text = last_event.get("text", current_scenario_text)
            elif last_event.get("event_type") == "ai_response":
                current_scenario_text = last_event.get("new_situation_text", current_scenario_text)

    ai_context = {
        "world_id": db_player_state.world_id, 
        "world_name_display": db_player_state.world_name_display,
        "class": db_player_state.class_name, 
        "stats": db_player_state.stats, # Assuming stats is already a dict
        "health": db_player_state.health,
        "last_choice_text": choice_text,
        "current_scenario_text": current_scenario_text
    }

    # Format the input prompt for the AI based on action type
    ai_input_text = ""
    if choice_id == "USER_ACTION":
        ai_input_text = f"Oyuncu şu özel eylemi yapmayı deniyor: \"{choice_text}\". Bu eylemin sonucunu, karakterin yeteneklerini ve mevcut durumu göz önünde bulundurarak gerçekçi bir şekilde anlat. Eylem başarılı olabilir, kısmen başarılı olabilir veya tamamen başarısız olabilir."
    else:
        ai_input_text = f"Oyuncu '{choice_text}' seçeneğini seçti."

    # Call AI service
    ai_response = await get_ai_response(prompt_text=ai_input_text, player_context=ai_context)

    # Prepare data for response and potential DB update
    response_data = {}
    update_data_for_db = {}

    if ai_response.get("error"):
         response_data = {
            "text": f"Bir şeyler ters gitti: {ai_response['error']}. Devam etmek için bir seçenek belirle.",
            "choices": [{"id": "IGNORE", "text": "Hatayı görmezden gel ve devam etmeyi um."}],
             "player_info_for_card": { # Return current info for card consistency
                 "name": db_player_state.player_name,
                 "class": db_player_state.class_name,
                 "health": db_player_state.health,
                 "stats": db_player_state.stats
             }
        }
         # No state update in DB on AI error
    else:
        # Prepare data for updating the player state in DB
        current_history = list(db_player_state.history) if isinstance(db_player_state.history, list) else []
        current_history.append({
            "event_type": "ai_response",
            "choice_made": choice_text,
            "ai_raw_text": ai_response.get("raw_ai_response"), 
            "new_situation_text": ai_response.get("text")
        })
        
        update_data_for_db = {
            "history": current_history
            # TODO: Parse AI response for potential updates to health, location, inventory, stats etc.
            # health = db_player_state.health - 10 # Example
            # update_data_for_db["health"] = health 
        }

        # Update the player state in the database
        updated_db_state = crud.update_player_state(db=db, session_id=session_id, update_data=update_data_for_db)

        if not updated_db_state:
             print(f"Error: Failed to update player state for session {session_id}")
             # Return AI response but indicate potential save failure?
             response_data = {
                "text": ai_response.get("text", "Bir hata oluştu (kayıt edilemedi)."),
                "choices": ai_response.get("choices", []),
                 "player_info_for_card": { # Return info based on attempted update
                     "name": db_player_state.player_name, # Original name
                     "class": db_player_state.class_name, # Original class
                     "health": update_data_for_db.get("health", db_player_state.health), # Attempted health
                     "stats": db_player_state.stats # Original stats
                 }
            }
        else:
            # Return the new narrative and choices + updated card info
            response_data = {
                "text": ai_response.get("text"),
                "choices": ai_response.get("choices"),
                 "player_info_for_card": { 
                     "name": updated_db_state.player_name,
                     "class": updated_db_state.class_name,
                     "health": updated_db_state.health, 
                     "stats": updated_db_state.stats 
                 }
            }

    return response_data
