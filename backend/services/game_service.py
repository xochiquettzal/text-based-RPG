# -*- coding: utf-8 -*-
import copy
import random # Added for dice rolling
from typing import Dict, Any, Optional, List # Added List
from sqlalchemy.orm import Session
import uuid # Added for session_id generation in initialize_game

# Use relative imports for data, models, db, and other services
from ..models.game_models import ChoiceModel, SkillCheckResultModel # Added SkillCheckResultModel
from ..data.characters import player_character_template, CLASS_BASE_STATS, get_class_base_stats
from ..data.scenarios import STARTING_SCENARIOS, INITIAL_SCENARIOS_BY_WORLD, get_starting_scenario
from ..data.worlds import get_world_name
# Import request models (Fixed PlayerChoice -> MakeChoicePayload)
from ..models.game_models import StartGamePayload, MakeChoicePayload, MakeChoiceResponse 
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


async def process_player_action(db: Session, session_id: str, choice_id: str, choice_text: str) -> MakeChoiceResponse:
    """
    Processes player's action, calls AI, updates state in DB.
    Returns the next game state data (text, choices, player_info_for_card, skill_check_result).
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
            elif last_event.get("event_type") == "skill_check_attempt": # If last event was a skill check
                current_scenario_text = last_event.get("original_situation_text", current_scenario_text)


    ai_context = {
        "world_id": db_player_state.world_id,
        "world_name_display": db_player_state.world_name_display,
        "class": db_player_state.class_name,
        "stats": db_player_state.stats, # Assuming stats is already a dict
        "health": db_player_state.health,
        "current_scenario_text": current_scenario_text
        # "last_choice_text" will be part of ai_input_text or handled by skill check outcome
    }

    ai_input_text = ""
    skill_check_outcome_for_ai = None
    skill_check_result_for_response: Optional[SkillCheckResultModel] = None # Initialize

    # Check if the choice_id corresponds to a choice that was presented by the AI
    # This requires knowing the choices that were last presented to the player.
    # For now, we assume that if choice_id is not "USER_ACTION", it came from AI.
    # A more robust way would be to store last presented choices in player_state.
    # We also need to retrieve the skill_check_stat and skill_check_dc if this choice was a skill check.
    # This information is now part of the AI response's choice objects.
    # We'll need to find the specific choice object that matches choice_id from the *previous* AI response.
    # This is a bit tricky as we don't store the full previous AI response choices directly in the DB state in a structured way.
    # For now, we'll assume the frontend might pass skill_check_stat and dc if it was a skill check option.
    # Or, the AI service needs to return these if it parsed them.
    # Let's assume for now that if choice_id is not USER_ACTION, we look it up from the last history event's choices.

    is_skill_check_choice = False
    skill_stat_to_check = None
    skill_dc_to_beat = None

    if choice_id != "USER_ACTION" and db_player_state.history:
        last_event = db_player_state.history[-1]
        if isinstance(last_event, dict) and last_event.get("event_type") == "ai_response":
            previous_choices_raw = last_event.get("ai_choices") # We need to ensure ai_choices are stored
            if previous_choices_raw and isinstance(previous_choices_raw, list):
                for choice_obj_raw in previous_choices_raw:
                    if isinstance(choice_obj_raw, dict) and choice_obj_raw.get("id") == choice_id:
                        if choice_obj_raw.get("skill_check_stat") and choice_obj_raw.get("skill_check_dc") is not None:
                            is_skill_check_choice = True
                            skill_stat_to_check = choice_obj_raw.get("skill_check_stat")
                            skill_dc_to_beat = choice_obj_raw.get("skill_check_dc")
                            # choice_text here is the one from the payload, which is the user-clicked text
                            break
    
    if is_skill_check_choice and skill_stat_to_check and skill_dc_to_beat is not None:
        outcome, roll, modifier, total_roll = _perform_skill_check(
            player_stats=db_player_state.stats,
            stat_to_check=skill_stat_to_check,
            dc=skill_dc_to_beat
        )
        skill_check_outcome_for_ai = outcome # "KRİTİK BAŞARI", "BAŞARILI", "BAŞARISIZ", "KRİTİK BAŞARISIZ"
        skill_check_result_for_response = SkillCheckResultModel(
            stat_checked=skill_stat_to_check,
            dc=skill_dc_to_beat,
            roll=roll,
            modifier=modifier,
            total_roll=total_roll,
            outcome=outcome
        )
        
        # Update history for the skill check attempt itself
        current_history = list(db_player_state.history) if isinstance(db_player_state.history, list) else []
        current_history.append({
            "event_type": "skill_check_attempt",
            "choice_made": choice_text, # The text of the skill check option
            "stat_checked": skill_stat_to_check,
            "dc": skill_dc_to_beat,
            "roll": roll,
            "modifier": modifier,
            "total_roll": total_roll,
            "outcome": outcome,
            "original_situation_text": current_scenario_text # Save the text before this check
        })
        crud.update_player_state(db=db, session_id=session_id, update_data={"history": current_history})
        # Reload state to get the updated history for the AI context
        db_player_state = crud.get_player_state(db=db, session_id=session_id)

        ai_context["skill_check_outcome"] = skill_check_outcome_for_ai
        # For AI, the "action" is now the outcome of the skill check
        ai_input_text = f"Oyuncu '{choice_text}' yetenek kontrolünü denedi ve sonuç: {skill_check_outcome_for_ai} (Zar: {roll}, Bonus: {modifier}, Toplam: {total_roll} vs DC: {skill_dc_to_beat}). Bu sonuca göre hikayeyi devam ettir."

    elif choice_id == "USER_ACTION":
        ai_input_text = f"Oyuncu şu özel eylemi yapmayı deniyor: \"{choice_text}\". Bu eylemin sonucunu, karakterin yeteneklerini ve mevcut durumu göz önünde bulundurarak gerçekçi bir şekilde anlat. Eylem başarılı olabilir, kısmen başarılı olabilir veya tamamen başarısız olabilir."
    else: # Regular choice, not a skill check
        ai_input_text = f"Oyuncu '{choice_text}' seçeneğini seçti."

    ai_context["last_choice_text"] = choice_text # This is the text of the button clicked or user input

    # Call AI service
    ai_response = await get_ai_response(prompt_text=ai_input_text, player_context=ai_context)

    # Prepare data for response and potential DB update
    # response_data = {} # No longer used, directly return MakeChoiceResponse
    update_data_for_db = {}

    if ai_response.get("error"):
        return MakeChoiceResponse(
            text=f"Bir şeyler ters gitti: {ai_response['error']}. Devam etmek için bir seçenek belirle.",
            choices=[ChoiceModel(id="IGNORE", text="Hatayı görmezden gel ve devam etmeyi um.")],
            player_info_for_card={ # type: ignore
                 "name": db_player_state.player_name,
                 "class": db_player_state.class_name,
                 "health": db_player_state.health,
                 "stats": db_player_state.stats
            },
            skill_check_result=skill_check_result_for_response # Pass it even on AI error if check happened before
        )
    # If we reach here, there was no AI error.
    # Prepare data for updating the player state in DB
    current_history = list(db_player_state.history) if isinstance(db_player_state.history, list) else []
    
    # Store the AI's choices along with the response text for future skill check lookups
    ai_choices_from_response = ai_response.get("choices", [])
    
    current_history.append({
        "event_type": "ai_response",
        "choice_made": choice_text, # The original choice/action text
        "skill_check_outcome_given_to_ai": skill_check_outcome_for_ai, # Null if not a skill check response
        "ai_raw_text": ai_response.get("raw_ai_response"),
        "new_situation_text": ai_response.get("text"),
        "ai_choices": ai_choices_from_response # Store the choices for the next turn
    })
    
    update_data_for_db = {
        "history": current_history
        # TODO: Parse AI response for potential updates to health, location, inventory, stats etc.
        # For example, if AI says "you take 10 damage", we need to parse that.
        # health = db_player_state.health - 10 # Example
        # update_data_for_db["health"] = health
    }

    # Update the player state in the database
    updated_db_state = crud.update_player_state(db=db, session_id=session_id, update_data=update_data_for_db)

    if not updated_db_state:
        print(f"Error: Failed to update player state for session {session_id}")
        # Return AI response but indicate potential save failure?
        return MakeChoiceResponse(
            text=ai_response.get("text", "Bir hata oluştu (kayıt edilemedi)."),
            choices=[ChoiceModel(**choice) for choice in ai_response.get("choices", [])], # type: ignore
            player_info_for_card={ # type: ignore
                    "name": db_player_state.player_name,
                    "class": db_player_state.class_name,
                    "health": update_data_for_db.get("health", db_player_state.health),
                    "stats": updated_db_state.stats if updated_db_state else db_player_state.stats
            },
            skill_check_result=skill_check_result_for_response
        )
    
    # Return the new narrative and choices + updated card info
    return MakeChoiceResponse(
        text=ai_response.get("text"),
        choices=[ChoiceModel(**choice) for choice in ai_choices_from_response], # type: ignore
        player_info_for_card={ # type: ignore
                "name": updated_db_state.player_name,
                "class": updated_db_state.class_name,
                "health": updated_db_state.health,
                "stats": updated_db_state.stats
        },
        skill_check_result=skill_check_result_for_response
    )

# --- Helper function for Skill Checks ---
def _perform_skill_check(player_stats: Dict[str, int], stat_to_check: str, dc: int) -> (str, int, int, int):
    """
    Performs a d20 skill check based on Baldur's Gate / D&D 5e rules.
    Args:
        player_stats: Dictionary of player's statistics (e.g., {"strength": 12, "dexterity": 15}).
        stat_to_check: The stat being checked (e.g., "strength").
        dc: The difficulty class of the check.
    Returns:
        A tuple: (outcome_string, roll, modifier, total_roll)
        Outcome string can be "KRİTİK BAŞARI", "BAŞARILI", "BAŞARISIZ", "KRİTİK BAŞARISIZ".
    """
    stat_value = player_stats.get(stat_to_check.lower(), 10) # Default to 10 if stat not found
    modifier = (stat_value - 10) // 2 # Standard D&D 5e modifier calculation

    roll = random.randint(1, 20)
    total_roll = roll + modifier

    outcome = ""
    if roll == 20:
        outcome = "KRİTİK BAŞARI"
    elif roll == 1:
        outcome = "KRİTİK BAŞARISIZ"
    elif total_roll >= dc:
        outcome = "BAŞARILI"
    else:
        outcome = "BAŞARISIZ"
        
    return outcome, roll, modifier, total_roll
