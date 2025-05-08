import os
import httpx # httpx is an async-capable HTTP client, good for FastAPI
import json
from pathlib import Path # Import Path
from dotenv import load_dotenv
# Import world lore from story_data
from game_logic.story_data import world_lore_summaries

# Construct an absolute path to the .env file
# __file__ is the path to the current script (openrouter_client.py)
# resolve().parent gives the directory of the current script (ai_integration)
# .parent then gives the parent of that directory (backend)
# Then we append '.env'
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
    with a fallback mechanism.

    Args:
        prompt_text: The main text/question for the AI.
        player_context: A dictionary containing player's current state, history, etc.

    Returns:
        A dictionary containing the AI's response or an error message.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
        print("HATA: OPENROUTER_API_KEY .env dosyasında ayarlanmamış veya geçersiz.")
        return {"error": "AI servisi konfigüre edilmemiş. Lütfen API anahtarını kontrol edin."}

    # Determine world name for the prompt, default if not available
    world_name = player_context.get("world_name_display", "belirsiz bir dünya") if player_context else "belirsiz bir dünya"

    base_prompt = (
        f"Sen '{world_name}' adlı dünyada geçen, metin tabanlı bir RPG oyununun anlatıcısısın. " # World name added
        "Oyuncunun hikayesini ve eylemlerinin sonuçlarını yönlendiriyorsun. "
        "Aşağıda oyuncunun mevcut durumu ve son yaptığı eylem/seçim belirtilmiştir. " 
        "Bu eylemin/seçimin sonucunu ve ortaya çıkan yeni durumu yaratıcı bir şekilde anlat. "
        "Eğer oyuncu serbest metinle özel bir eylem deniyorsa (örneğin 'Oyuncu şu özel eylemi yapmayı deniyor: ...' gibi bir ifadeyle belirtilmişse), "
        "bu eylemin başarılı olup olmayacağını mevcut durum, karakterin mantıksal yetenekleri ve oyun dünyasının gerçekçiliği çerçevesinde değerlendir. Her özel eylem otomatik olarak başarılı olmamalıdır. "
        "Anlatımının sonunda, oyuncuya yeni durumda yapabileceği 2 veya 3 yeni seçenek sun. "
        "Seçenekleri 'A) Seçenek metni', 'B) Başka bir seçenek metni' gibi, her birini ayrı bir satırda ve net bir şekilde belirt.\n\n"
    )

    if player_context:
        # Add world lore summary to the context
        world_id = player_context.get("world_id")
        lore_summary = world_lore_summaries.get(world_id, "Dünya hakkında ek bilgi yok.")
        context_str = f"Genel Dünya Bilgisi ({world_name}): {lore_summary}\n\nOyuncunun Durumu:\n"
        
        # Add specific player details
        # world_name_display is already in the base_prompt, world_id might be useful for logic
        # if player_context.get("world_id"):
        #     context_str += f"- Dünya ID: {player_context['world_id']}\n" 
        if player_context.get("class"):
            context_str += f"- Sınıf/Fraksiyon: {player_context['class']}\n"
        if player_context.get("stats"):
            context_str += f"- Özellikler: {player_context['stats']}\n"
        if player_context.get("health"):
            context_str += f"- Can: {player_context['health']}\n"
        if player_context.get("current_scenario_text"): # From previous turn
             context_str += f"- Önceki Durum: {player_context['current_scenario_text']}\n"
        if player_context.get("last_choice_text"): # From previous turn
             context_str += f"- Son Seçimi: {player_context['last_choice_text']}\n"

        full_prompt = f"{base_prompt}{context_str}\nOyuncunun Yeni İsteği/Seçimi: {prompt_text}\n\nAnlatımın ve yeni seçeneklerin:"
    else:
        full_prompt = f"{base_prompt}Oyuncunun İsteği/Seçimi: {prompt_text}\n\nAnlatımın ve yeni seçeneklerin:"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": HTTP_REFERER,
        "X-Title": X_TITLE,
    }

    async with httpx.AsyncClient(timeout=30.0) as client: # 30 saniye timeout
        for model_name in MODEL_PREFERENCE:
            print(f"AI modeli deneniyor: {model_name}")
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": full_prompt}],
                # "max_tokens": 300, # İsteğe bağlı, token sayısını sınırlamak için
                # "temperature": 0.7 # İsteğe bağlı, yaratıcılık seviyesi
            }
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()  # HTTP hataları için exception fırlat (4xx, 5xx)
                
                response_json = response.json()
                
                if response_json.get("choices") and len(response_json["choices"]) > 0:
                    ai_content = response_json["choices"][0].get("message", {}).get("content")
                    if ai_content:
                        print(f"Başarılı cevap alındı: {model_name}")
                        # AI cevabını metin ve seçenekler olarak ayırmaya çalışalım
                        ai_lines = ai_content.strip().split("\n")
                        story_part_lines = []
                        choice_lines_raw = []
                        parsing_choices_active = False

                        for line_raw in ai_lines:
                            current_line_stripped = line_raw.strip()
                            if not current_line_stripped:
                                continue

                            # Temizlenmiş satırda seçenek başlangıcını kontrol et (örn: "A)", "1.", "**B)**")
                            check_line = current_line_stripped.lstrip(" *") # Baştaki boşluk ve yıldızları kaldır
                            
                            # Seçenek satırı mı diye kontrol et (örn: A) veya 1.)
                            # Basit kontrol: ilk karakter alfanumerik, ikincisi ) veya .
                            is_choice_line = False
                            if len(check_line) >= 2 and check_line[0].isalnum() and check_line[1] in (")", "."):
                                is_choice_line = True

                            if is_choice_line:
                                parsing_choices_active = True
                            
                            if parsing_choices_active:
                                choice_lines_raw.append(current_line_stripped)
                            else:
                                story_part_lines.append(current_line_stripped)
                        
                        # Eğer "Yeni Seçenekler:" gibi bir başlık hikaye kısmının sonunda kaldıysa ve seçenekler bulunduysa, çıkar.
                        if story_part_lines and choice_lines_raw:
                            last_story_line_cleaned = story_part_lines[-1].lower().replace('*','').replace(':','').strip()
                            if last_story_line_cleaned == "yeni seçenekler":
                                story_part_lines.pop()

                        parsed_choices_list = []
                        for i, single_choice_raw_line in enumerate(choice_lines_raw):
                            text_to_extract = single_choice_raw_line # Zaten strip edilmişti
                            
                            # İşaretçiden sonraki metni al (örn: "**A)** Metin" -> "Metin")
                            marker_end_index = -1
                            # Parantez veya nokta bul
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
                                # Eğer işaretçi yoksa veya sonunda metin yoksa, satırın kendisi olabilir (temizlenmiş hali)
                                # Bu durum, AI'nın sadece "Seçenek 1" "Seçenek 2" gibi listelediği durumlar için bir yedek olabilir.
                                # Ancak bizim formatımızda işaretçi olmalı.
                                # Eğer işaretçi varsa ama metin yoksa (örn: "A)"), extracted_text boş kalır.
                                cleaned_marker_part = text_to_extract.lstrip(" *")
                                if len(cleaned_marker_part) > 2 and cleaned_marker_part[0].isalnum() and cleaned_marker_part[1] in (")", "."):
                                     pass # Muhtemelen sadece işaretçi, metin yok. extracted_text boş kalacak.
                                else: # İşaretçiye benzemiyor, olduğu gibi al.
                                     extracted_text = text_to_extract


                            # Metnin başındaki ve sonundaki markdown'ı temizle
                            extracted_text = extracted_text.removeprefix("**").removesuffix("**").strip()
                            extracted_text = extracted_text.removeprefix("*").removesuffix("*").strip()

                            if extracted_text: # Sadece metin varsa ekle
                                parsed_choices_list.append({"id": chr(65 + i), "text": extracted_text})
                        
                        final_story_output = " ".join(story_part_lines)
                        if not final_story_output and not parsed_choices_list and ai_content: # Eğer ayrıştırma başarısız olduysa
                            final_story_output = ai_content.strip() # Ham içeriği hikaye olarak kullan

                        return {
                            "text": final_story_output if final_story_output else "AI bir hikaye oluşturamadı.",
                            "choices": parsed_choices_list,
                            "raw_ai_response": ai_content # Ham cevabı da saklayalım
                        }
                print(f"Model {model_name} geçerli bir cevap vermedi veya 'choices' boş: {response_json}")

            except httpx.HTTPStatusError as e:
                print(f"Model {model_name} ile HTTP hatası: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                print(f"Model {model_name} ile bağlantı hatası: {e}")
            except json.JSONDecodeError:
                print(f"Model {model_name} JSON parse hatası. Cevap: {response.text}")
            except Exception as e:
                print(f"Model {model_name} ile bilinmeyen bir hata oluştu: {e}")
        
        print("Tüm AI modelleri denendi ancak başarılı bir cevap alınamadı.")
        return {"error": "AI servisinden cevap alınamadı. Tüm modeller denendi."}

if __name__ == '__main__':
    # Test için basit bir çalıştırma
    import asyncio
    async def test_ai():
        # .env dosyasının doğru yolda olduğundan emin olun veya manuel olarak ayarlayın
        # load_dotenv(dotenv_path='../.env') # Eğer bu dosya doğrudan çalıştırılıyorsa
        # global OPENROUTER_API_KEY, HTTP_REFERER, X_TITLE
        # OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        # HTTP_REFERER = os.getenv("HTTP_REFERER", "http://localhost:8000")
        # X_TITLE = os.getenv("X_TITLE", "Text RPG Adventure")

        print(f"API Key: {OPENROUTER_API_KEY}") # Debug
        
        test_prompt = "Yarı-Ölü'nün peşinden git."
        test_context = {
            "world": "Karanlık Fantezi Dünyası",
            "current_scenario_text": "Kara sislerin sardığı lanetli krallıkta, çatlamış bir yol ayrımındasın...",
            "last_choice_text": "Yarı-Ölü'nün peşinden git."
        }
        response = await get_ai_response(test_prompt, test_context)
        print("\nAI Cevabı:")
        print(json.dumps(response, indent=2, ensure_ascii=False))

    asyncio.run(test_ai())
