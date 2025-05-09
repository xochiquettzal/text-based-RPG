# -*- coding: utf-8 -*-
import os
import httpx # httpx is an async-capable HTTP client, good for FastAPI
import json
import re # Added for parsing skill checks from AI response
from pathlib import Path # Import Path
from dotenv import load_dotenv
# Import world lore from story_data (adjust path based on new structure)
# Assuming this service is called from other services/api in backend/, the path needs to be relative to that
# Or use absolute imports relative to the project root if PYTHONPATH is set, or relative imports from within backend
from ..data.worlds import WORLDS # Use relative import from sibling directory 'data'

# Construct an absolute path to the .env file relative to this file's location
# ai_service.py (services) -> backend -> .env
DOTENV_PATH = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=DOTENV_PATH)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HTTP_REFERER = os.getenv("HTTP_REFERER", "http://localhost:8000") # Default if not set
X_TITLE = os.getenv("X_TITLE", "Text RPG Adventure") # Default if not set

# Provided model list
MODEL_PREFERENCE = [
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-4-maverick:free",
    "qwen/qwen3-235b-a22b:free",
    "deepseek/deepseek-chat:free",
    "deepseek/deepseek-prover-v2:free"
]

async def get_ai_response(prompt_text: str, player_context: dict = None) -> dict:
    """
    Sends a prompt to the OpenRouter API using a preferred list of models,
    with a fallback mechanism. Includes world lore in the context.

    Args:
        prompt_text: The main text/question for the AI, contextualized by the caller.
        player_context: A dictionary containing player's current state (world_id, class, stats, etc.).

    Returns:
        A dictionary containing the AI's response or an error message.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
        print("HATA: OPENROUTER_API_KEY .env dosyasında ayarlanmamış veya geçersiz.")
        return {"error": "AI servisi konfigüre edilmemiş. Lütfen API anahtarını kontrol edin."}

    # Determine world name and lore for the prompt
    world_id = player_context.get("world_id") if player_context else None
    world_data = WORLDS.get(world_id, {})
    world_name = world_data.get("name", "belirsiz bir dünya")
    lore_summary = world_data.get("lore_summary", "Dünya hakkında ek bilgi yok.")

    base_prompt = (
        f"Sen '{world_name}' adlı dünyada geçen, metin tabanlı bir RPG oyununun anlatıcısısın. " 
        "Oyuncunun hikayesini ve eylemlerinin sonuçlarını yönlendiriyorsun. "
        "Aşağıda genel dünya bilgisi, oyuncunun mevcut durumu ve son yaptığı eylem/seçim belirtilmiştir. " 
        "Bu eylemin/seçimin sonucunu ve ortaya çıkan yeni durumu yaratıcı bir şekilde anlat. "
        "Eğer oyuncu serbest metinle özel bir eylem deniyorsa (örneğin 'Oyuncu şu özel eylemi yapmayı deniyor: ...' gibi bir ifadeyle belirtilmişse), "
        "bu eylemin başarılı olup olmayacağını mevcut durum, karakterin mantıksal yetenekleri ve oyun dünyasının gerçekçiliği çerçevesinde değerlendir. Her özel eylem otomatik olarak başarılı olmamalıdır. "
        "Anlatımının sonunda, oyuncuya yeni durumda yapabileceği 2 veya 3 yeni seçenek sun. "
        "Seçenekleri 'A) Seçenek metni', 'B) Başka bir seçenek metni' gibi, her birini ayrı bir satırda ve net bir şekilde belirt.\n"
        "ARA SIRA, seçeneklerden biri bir YETENEK KONTROLÜ olabilir. Bunu 'Seçenek metni (YETENEK ZORLUK_DERECESİ)' formatında belirt. Örneğin: 'C) Kapıyı kırmaya çalış (Güç DC15)'. Kullanılabilecek yetenekler: strength, dexterity, constitution, intelligence, wisdom, charisma.\n"
        "Eğer sana bir yetenek kontrolünün sonucu (BAŞARILI, BAŞARISIZ, KRİTİK BAŞARI, KRİTİK BAŞARISIZ) verilirse, hikayeyi bu sonuca göre devam ettir.\n\n"
        f"Genel Dünya Bilgisi ({world_name}): {lore_summary}\n\n" # Inject world lore here
    )

    context_str = "Oyuncunun Durumu:\n"
    if player_context:
        # Add specific player details
        if player_context.get("class"):
            context_str += f"- Sınıf/Fraksiyon: {player_context['class']}\n"
        if player_context.get("stats"):
            # Format stats nicely
            stats_str = ", ".join([f"{k.upper()}: {v}" for k, v in player_context['stats'].items()])
            context_str += f"- Özellikler: {stats_str}\n"
        if player_context.get("health"):
            context_str += f"- Can: {player_context['health']}\n"
        if player_context.get("current_scenario_text"): # Text player saw before making the choice/action
             context_str += f"- Önceki Durum Metni: {player_context['current_scenario_text']}\n"
        if player_context.get("skill_check_outcome"): # If there was a skill check
            context_str += f"- Yetenek Kontrolü Sonucu: {player_context['skill_check_outcome']}\n"
        # last_choice_text is now part of the main prompt_text coming in
    else:
        context_str = "Oyuncu durumu hakkında bilgi yok.\n"

    # prompt_text already contains the player's specific action/choice description from the caller
    # If there was a skill check outcome, prompt_text might be more generic like "Continue the story"
    # or it could be the original choice text that led to the skill check.
    # The game_service will decide what prompt_text should be in this case.
    full_prompt = f"{base_prompt}{context_str}\nOyuncunun Son Eylemi/Seçimi (veya Yetenek Kontrolü İsteği): {prompt_text}\n\nAnlatımın ve yeni seçeneklerin:"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": HTTP_REFERER,
        "X-Title": X_TITLE,
    }

    async with httpx.AsyncClient(timeout=30.0) as client: 
        for model_name in MODEL_PREFERENCE:
            print(f"AI modeli deneniyor: {model_name}")
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": full_prompt}],
            }
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()  
                
                response_json = response.json()
                
                if response_json.get("choices") and len(response_json["choices"]) > 0:
                    ai_content = response_json["choices"][0].get("message", {}).get("content")
                    if ai_content:
                        print(f"Başarılı cevap alındı: {model_name}")
                        # Parse AI response into text and choices
                        ai_lines = ai_content.strip().split("\n")
                        story_part_lines = []
                        choice_lines_raw = []
                        parsing_choices_active = False

                        for line_raw in ai_lines:
                            current_line_stripped = line_raw.strip()
                            if not current_line_stripped:
                                continue
                            
                            check_line = current_line_stripped.lstrip(" *") 
                            is_choice_line = False
                            if len(check_line) >= 2 and check_line[0].isalnum() and check_line[1] in (")", "."):
                                is_choice_line = True

                            if is_choice_line:
                                parsing_choices_active = True
                            
                            if parsing_choices_active:
                                choice_lines_raw.append(current_line_stripped)
                            else:
                                story_part_lines.append(current_line_stripped)
                        
                        if story_part_lines and choice_lines_raw:
                            last_story_line_cleaned = story_part_lines[-1].lower().replace('*','').replace(':','').strip()
                            if last_story_line_cleaned == "yeni seçenekler":
                                story_part_lines.pop()

                        parsed_choices_list = []
                        for i, single_choice_raw_line in enumerate(choice_lines_raw):
                            text_to_extract = single_choice_raw_line 
                            marker_end_index = -1
                            idx_paren = text_to_extract.find(')')
                            idx_dot = text_to_extract.find('.')

                            if idx_paren != -1 and (idx_dot == -1 or idx_paren < idx_dot):
                                marker_end_index = idx_paren
                            elif idx_dot != -1:
                                marker_end_index = idx_dot
                            
                            extracted_text = ""
                            if marker_end_index != -1 and marker_end_index < len(text_to_extract) -1:
                                extracted_text = text_to_extract[marker_end_index+1:].strip()
                            else: 
                                cleaned_marker_part = text_to_extract.lstrip(" *")
                                if len(cleaned_marker_part) > 2 and cleaned_marker_part[0].isalnum() and cleaned_marker_part[1] in (")", "."):
                                     pass 
                                else: 
                                     extracted_text = text_to_extract

                            extracted_text = extracted_text.removeprefix("**").removesuffix("**").strip()
                            extracted_text = extracted_text.removeprefix("*").removesuffix("*").strip()

                            if extracted_text:
                                # Try to parse skill check from the extracted_text
                                # Format: "Action text (STAT DC##)" e.g., "Try to lift the rock (Strength DC15)"
                                # Turkish stat names: Güç, Çeviklik, Dayanıklılık, Zeka, Bilgelik, Karizma
                                # English stat names for mapping: strength, dexterity, constitution, intelligence, wisdom, charisma
                                # Regex updated to allow an optional period at the end: \.?$
                                print(f"Attempting to parse skill check from: '{extracted_text}'") # DEBUG
                                skill_check_match = re.search(r"\((strength|dexterity|constitution|intelligence|wisdom|charisma|güç|çeviklik|dayanıklılık|zeka|bilgelik|karizma)\s+DC(\d+)\)\.?$", extracted_text, re.IGNORECASE)
                                choice_item = {"id": chr(65 + i), "text": extracted_text}
                                if skill_check_match:
                                    print(f"Skill check PARSED for choice '{extracted_text}'") # DEBUG
                                    stat_name_raw = skill_check_match.group(1).lower()
                                    dc_value = int(skill_check_match.group(2))
                                    
                                    # Map Turkish stat names to English if necessary for consistency
                                    stat_map = {
                                        "güç": "strength", "çeviklik": "dexterity", "dayanıklılık": "constitution",
                                        "zeka": "intelligence", "bilgelik": "wisdom", "karizma": "charisma"
                                    }
                                    stat_name_english = stat_map.get(stat_name_raw, stat_name_raw) # Default to raw if already English

                                    choice_item["skill_check_stat"] = stat_name_english
                                    choice_item["skill_check_dc"] = dc_value
                                    # Clean the skill check part from the display text (allow optional period)
                                    choice_item["text"] = re.sub(r"\s*\((strength|dexterity|constitution|intelligence|wisdom|charisma|güç|çeviklik|dayanıklılık|zeka|bilgelik|karizma)\s+DC\d+\)\.?$", "", extracted_text, flags=re.IGNORECASE).strip()
                                else: # DEBUG
                                    print(f"NO skill check parsed for choice '{extracted_text}'") # DEBUG
                                
                                parsed_choices_list.append(choice_item)
                        
                        final_story_output = " ".join(story_part_lines)
                        if not final_story_output and not parsed_choices_list and ai_content: 
                            final_story_output = ai_content.strip() 

                        return {
                            "text": final_story_output if final_story_output else "AI bir hikaye oluşturamadı.",
                            "choices": parsed_choices_list,
                            "raw_ai_response": ai_content 
                        }
                print(f"Model {model_name} geçerli bir cevap vermedi veya 'choices' boş: {response_json}")

            except httpx.HTTPStatusError as e:
                print(f"Model {model_name} ile HTTP hatası: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                print(f"Model {model_name} ile bağlantı hatası: {e}")
