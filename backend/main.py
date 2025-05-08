from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import copy # For deep copying player state

# Proje içi importlar
from game_logic.story_data import (
    initial_scenarios_by_world, 
    starting_scenarios, # Import new specific starts
    world_lore_summaries, # Import lore summaries
    player_character_template, 
    class_base_stats
)
from ai_integration.openrouter_client import get_ai_response

app = FastAPI()

# CORS (Cross-Origin Resource Sharing) ayarları
# Frontend'in farklı bir portta (örn: live server) çalışmasına izin vermek için.
origins = [
    "http://localhost",
    "http://localhost:8080", # Yaygın bir live server portu
    "http://127.0.0.1:5500", # VS Code Live Server varsayılan portu
    "null", # Bazen yerel dosyalardan yapılan istekler için 'null' origin gelir
    # Gerekirse frontend'inizin çalıştığı diğer adresleri ekleyin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Tüm metodlara izin ver (GET, POST, vb.)
    allow_headers=["*"], # Tüm header'lara izin ver
)

# Oyuncu durumunu saklamak için basit bir sözlük (production için veritabanı daha iyi olur)
# Bu örnekte, her bir client için ayrı bir state tutmak adına request.state kullanacağız.
# Daha kalıcı bir çözüm için session/cookie veya basit bir DB (örn: SQLite, TinyDB) gerekir.
# Şimdilik, her istekle birlikte tüm oyuncu durumunu alıp göndereceğiz.

class PlayerChoice(BaseModel):
    choice_id: str
    choice_text: str # Oyuncunun tıkladığı seçeneğin metni
    player_state: dict # Frontend'den gelen oyuncu durumu

from typing import Optional # Import Optional

class StartGamePayload(BaseModel):
    player_name: str = "Oyuncu"
    world_id: str # Frontend'den seçilen dünyanın ID'si (örn: "dark_fantasy", "animal_kingdom")
    selected_class_or_faction: Optional[str] = None # Seçilen sınıf/ırk/fraksiyon ID'si

# Oyuncu oturumunu (state) yönetmek için global bir sözlük (basitlik adına)
# Daha iyi bir yaklaşım: Her kullanıcı için benzersiz ID ve session yönetimi
# VEYA frontend'in her istekte state'i göndermesi. Şimdilik ikincisini kullanalım.
# player_sessions = {}


@app.post("/start_game")
async def start_game(payload: StartGamePayload):
    """Oyunu başlatır ve başlangıç senaryosunu döndürür."""
    # player_id = str(uuid.uuid4()) # Benzersiz oyuncu ID'si oluştur
    
    new_player_state = copy.deepcopy(player_character_template)
    new_player_state["name"] = payload.player_name
    
    selected_world_id = payload.world_id
    if selected_world_id not in initial_scenarios_by_world:
        raise HTTPException(status_code=400, detail=f"Geçersiz dünya ID'si: {selected_world_id}")

    chosen_scenario_data = initial_scenarios_by_world[selected_world_id]
    
    new_player_state["world_id"] = chosen_scenario_data["world_id"]
    new_player_state["world_name_display"] = chosen_scenario_data["world_name_display"]
    
    # Set class/faction and stats if selected
    if payload.selected_class_or_faction:
        if selected_world_id in class_base_stats and payload.selected_class_or_faction in class_base_stats[selected_world_id]:
            chosen_class_data = class_base_stats[selected_world_id][payload.selected_class_or_faction]
            new_player_state["class"] = payload.selected_class_or_faction
            # Make sure stats are copied and handle potential differences in stat names
            # For now, assume the structure matches the template or overwrite completely
            new_player_state["stats"] = chosen_class_data.copy() # Copy the whole dict
            # Remove skills from stats if it exists there, assign to skills key
            if "skills" in new_player_state["stats"]:
                 new_player_state["skills"] = new_player_state["stats"].pop("skills", [])
            else:
                 new_player_state["skills"] = [] # Ensure skills list exists
            
            # TODO: Handle different stat keys (e.g., AGI vs STR) if necessary based on world
            print(f"Player class set to: {new_player_state['class']}")
            print(f"Player stats set to: {new_player_state['stats']}")
            print(f"Player skills set to: {new_player_state['skills']}")
        else:
            print(f"Uyarı: Seçilen sınıf/fraksiyon '{payload.selected_class_or_faction}' dünya '{selected_world_id}' için bulunamadı.")
            # Keep default class/stats from template
            new_player_state["class"] = f"Bilinmeyen ({payload.selected_class_or_faction})"


    # Başlangıç senaryosunu oyuncu durumuna ekle
    #     new_player_state["class"] = payload.class_name
    #     new_player_state["stats"] = chosen_class_stats.get("stats", {}).copy()
    #     new_player_state["skills"] = chosen_class_stats.get("skills", []).copy()
    # else:
    #     # Varsayılan bir sınıf veya hata durumu
    #     pass

    # Determine the starting scenario
    start_text = ""
    start_choices = []
    start_location_id = None

    if payload.selected_class_or_faction and \
       selected_world_id in starting_scenarios and \
       payload.selected_class_or_faction in starting_scenarios[selected_world_id]:
        # Use the specific starting scenario for the selected class/faction
        specific_start = starting_scenarios[selected_world_id][payload.selected_class_or_faction]
        start_text = specific_start["text"]
        start_choices = specific_start["choices"]
        start_location_id = specific_start.get("current_location_id", f"{selected_world_id}_{payload.selected_class_or_faction}_start") # Generate fallback ID
        print(f"Using specific start for {payload.selected_class_or_faction} in {selected_world_id}")
    else:
        # Fallback to the generic initial scenario for the world
        generic_start = initial_scenarios_by_world[selected_world_id]
        start_text = generic_start["text"]
        start_choices = generic_start["choices"]
        start_location_id = generic_start.get("current_location_id", f"{selected_world_id}_generic_start")
        print(f"Using generic start for {selected_world_id}")

    # Set initial state based on the chosen scenario
    new_player_state["current_location_id"] = start_location_id
    new_player_state["history"].append({
        "event_type": "game_start",
        "world_id": new_player_state["world_id"],
        "class": new_player_state["class"], # Include selected class in history
        "text": start_text # Use the determined start text
    })
    
    return {
        "text": start_text, # Return the determined start text
        "choices": start_choices, # Return the determined start choices
        "player_state": new_player_state 
    }

@app.post("/make_choice")
async def make_choice(payload: PlayerChoice):
    """Oyuncunun seçimini işler ve sonucu döndürür."""
    player_state = payload.player_state
    choice_id = payload.choice_id

    if not player_state:
        raise HTTPException(status_code=400, detail="Oyuncu durumu bulunamadı.")

    # Seçilen seçeneğin metnini payload'dan al
    made_choice_text = payload.choice_text

    # Oyuncu durumu ve seçimi AI'ye göndermek için bağlam oluştur
    ai_context = {
        "world_id": player_state.get("world_id"), # AI'ye hangi dünyada olduğunu bildirmek için
        "world_name_display": player_state.get("world_name_display"),
        "class": player_state.get("class"),
        "stats": player_state.get("stats"),
        "health": player_state.get("health"),
        "last_choice_text": made_choice_text # Bu, oyuncunun yaptığı seçimin metni
    }

    # Determine the current scenario text (oyuncunun bu seçimi yapmadan önce gördüğü metin)
    # based on the last history event
    if player_state["history"]:
        last_event = player_state["history"][-1]
        if last_event.get("event_type") == "game_start":
            ai_context["current_scenario_text"] = last_event.get("text")
        elif last_event.get("event_type") == "ai_response":
            ai_context["current_scenario_text"] = last_event.get("new_situation_text")
        else:
            # Fallback or if history structure changes
            # Get the initial text for the current world if possible
            current_world_id = player_state.get("world_id", "dark_fantasy") # Default to dark_fantasy if not set
            fallback_scenario = initial_scenarios_by_world.get(current_world_id, initial_scenarios_by_world["dark_fantasy"])
            ai_context["current_scenario_text"] = fallback_scenario["text"]
    else:
        # Should not happen if start_game was called, but as a safeguard
        current_world_id = player_state.get("world_id", "dark_fantasy")
        fallback_scenario = initial_scenarios_by_world.get(current_world_id, initial_scenarios_by_world["dark_fantasy"])
        ai_context["current_scenario_text"] = fallback_scenario["text"]

    # AI'dan cevap al
    # Oyuncunun eylemini AI için daha açıklayıcı bir metne dönüştür
    ai_input_text = ""
    if payload.choice_id == "USER_ACTION":
        # Bu, frontend'deki handleCustomAction'dan gelen özel ID
        ai_input_text = f"Oyuncu şu özel eylemi yapmayı deniyor: \"{made_choice_text}\". Bu eylemin sonucunu, karakterin yeteneklerini ve mevcut durumu göz önünde bulundurarak gerçekçi bir şekilde anlat. Eylem başarılı olabilir, kısmen başarılı olabilir veya tamamen başarısız olabilir."
    else:
        # Bu, standart bir seçenek butonundan geliyor
        ai_input_text = f"Oyuncu '{made_choice_text}' seçeneğini seçti."

    ai_response = await get_ai_response(prompt_text=ai_input_text, player_context=ai_context)

    if ai_response.get("error"):
        # AI'dan hata gelirse, basit bir yedek cevap veya hata mesajı döndür
        # Bu kısım daha sofistike hale getirilebilir.
        return {
            "text": f"Bir şeyler ters gitti: {ai_response['error']}. Yarı-Ölü'nün peşinden gitmeye karar verdin ama yol aniden karanlığa gömüldü. Ne yapacaksın?",
            "choices": [
                {"id": "RETRY", "text": "Tekrar dene (AI çağrısı)"},
                {"id": "CONTINUE_STATIC", "text": "Statik bir yoldan devam et (AI olmadan)"}
            ],
            "player_state": player_state # Mevcut durumu geri gönder
        }

    # Oyuncu durumunu güncelle (AI'dan gelen yanıta göre)
    player_state["history"].append({
        "event_type": "ai_response",
        "choice_made": made_choice_text,
        "ai_raw_text": ai_response.get("raw_ai_response"), # Ham AI cevabını kaydet
        "new_situation_text": ai_response.get("text")
    })
    # player_state["current_location_id"] = ai_response.get("new_location_id") # AI'dan gelirse

    return {
        "text": ai_response.get("text"),
        "choices": ai_response.get("choices"),
        "player_state": player_state # Güncellenmiş oyuncu durumunu gönder
    }

if __name__ == "__main__":
    import uvicorn
    # Normalde bu dosya doğrudan çalıştırılmaz, `uvicorn backend.main:app --reload` gibi bir komutla çalıştırılır.
    # Ancak test için:
    print("FastAPI uygulamasını başlatmak için terminalde 'uvicorn backend.main:app --reload --port 8000' komutunu çalıştırın.")
    print("Ardından frontend/index.html dosyasını bir tarayıcıda açın.")
    # uvicorn.run(app, host="127.0.0.1", port=8000) # Bu satır CLI'dan çalıştırmayı engeller.
