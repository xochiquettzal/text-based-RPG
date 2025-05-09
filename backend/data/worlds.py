# -*- coding: utf-8 -*-

# --- World Definitions ---
# Using dictionaries for easy access and potential future expansion
WORLDS = {
    "dark_fantasy": {
        "id": "dark_fantasy",
        "name": "Karanlık Fantezi Dünyası",
        "lore_summary": "Bu dünya, yıkılmış krallıkların, lanetli varlıkların ve gölgelerde gizlenen tehlikelerin hüküm sürdüğü karanlık bir fantezi diyarıdır. Hayatta kalmak zordur ve güven nadir bulunur. Kül Lejyonu (ölümsüz savaşçılar), Gölge Sendikası (kurnaz casuslar) ve Kadim Kült (kaotik varlıklara tapanlar) ana güçlerdir.",
        "factions": ["ashen_legion", "shadow_syndicate", "primordial_cult"] # Link to factions/classes
    },
    "animal_kingdom": {
        "id": "animal_kingdom",
        "name": "Hayvanların Hüküm Sürdüğü Dünya",
        "lore_summary": "Bu dünya, bilinç kazanmış hayvan ırklarının yaşadığı, doğa ile iç içe bir krallıktır. Vargar (kurtlar), Vulpex (tilkiler), Noctis (baykuşlar) ve Leporim (tavşanlar) gibi ırklar kendi toplumlarını kurmuşlardır. Politika, kurnazlık ve hayatta kalma mücadelesi ön plandadır. Büyük Meşe Konseyi önemli bir toplanma yeridir.",
        "races": ["vargar", "vulpex", "noctis", "leporim"] # Link to races/classes
    }
}

# Function to get lore summary (optional helper)
def get_world_lore_summary(world_id: str) -> str:
    """Retrieves the lore summary for a given world ID."""
    return WORLDS.get(world_id, {}).get("lore_summary", "Dünya hakkında bilgi bulunamadı.")

# Function to get world display name (optional helper)
def get_world_name(world_id: str) -> str:
    """Retrieves the display name for a given world ID."""
    return WORLDS.get(world_id, {}).get("name", "Bilinmeyen Dünya")
